"""
Live data fetchers: Screener.in for fundamentals, NSE for daily OHLC.

This is the ONLY module allowed to know where data comes from - strategy
and screening logic stay data-source-agnostic (CLAUDE.md dependency
rule). It is also deliberately stdlib-only (urllib + html.parser +
http.cookiejar): "requests or equivalent" - urllib is the equivalent, and
it keeps pyyaml as the project's sole external dependency.

Two course rules are load-bearing here:

1. CONSOLIDATED figures, always (Section 4.11). We request Screener.in's
   /consolidated/ URL directly. The site's toggle label is INVERTED
   relative to what is displayed - a "View Standalone" link means the
   page IS showing consolidated (and vice versa); see
   is_showing_consolidated(), which encodes exactly that trap. A company
   with no subsidiaries has no toggle at all - standalone is then the
   correct, only option (the rule's explicit fallback).

2. FULL listing history for prices (CLAUDE.md rule 6): lifetime_high is
   wrong if history is truncated, and RHS/CWH/LTH/Strategy 7 all key off
   it. FULL_HISTORY_START predates NSE's own 1994 launch, so fetching
   from it guarantees nothing is missed for any listing.

Both fetchers take an injectable `transport` (url -> body) so tests run
fully offline and callers can swap in their own HTTP stack, caching, or
rate limiting.
"""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from html.parser import HTMLParser
from http.cookiejar import CookieJar
from typing import Callable, Optional

from sunabha_agent.data.models import Candle, CompanyType, Fundamentals, PriceSeries

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

# --------------------------------------------------------------------------
# Screener.in fundamentals
# --------------------------------------------------------------------------

SCREENER_CONSOLIDATED_URL = "https://www.screener.in/company/{symbol}/consolidated/"


def is_showing_consolidated(html: str) -> Optional[bool]:
    """
    The Section 4.11 inversion, encoded: Screener.in's toggle is labeled
    with what you would switch TO, not what is currently displayed.

      "View Standalone" present   -> the page IS consolidated (True)
      "View Consolidated" present -> the page IS standalone   (False)
      neither                     -> single-statement company (None) -
                                     standalone is then the correct fallback
    """
    if "View Standalone" in html:
        return True
    if "View Consolidated" in html:
        return False
    return None


def _parse_number(raw: str) -> Optional[float]:
    """'₹ 1,23,456 Cr.' -> 123456.0 ; '32.5 %' -> 32.5 ; '' -> None."""
    cleaned = (
        raw.replace("₹", "").replace("Cr.", "").replace("Cr", "")
        .replace("%", "").replace(",", "").strip()
    )
    if not cleaned or cleaned in ("-", "--"):
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _norm(label: str) -> str:
    """Screener row labels carry expander suffixes ('Net Profit +')."""
    return label.replace("+", "").strip().lower()


def rolling_ttm(quarterly: list[float]) -> list[float]:
    """TTM series from quarterly figures: sum of each trailing 4 quarters.
    The Fundamentals model wants TTM histories (Section 4.12 context) and
    Screener only publishes quarterly + annual - this is the bridge."""
    return [sum(quarterly[i - 3 : i + 1]) for i in range(3, len(quarterly))]


class _ScreenerHTMLParser(HTMLParser):
    """Extracts the three structures we need: the top-ratios list, and the
    tables inside <section id='quarters'> / <section id='shareholding'>.
    Everything else on the page is ignored, which keeps this tolerant of
    Screener's cosmetic markup changes."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ratios: dict[str, str] = {}
        self.tables: dict[str, list[list[str]]] = {}  # section id -> rows
        self._section: Optional[str] = None
        self._in_ratios_ul = False
        self._in_li = False
        self._in_name_span = False
        self._li_name: list[str] = []
        self._li_value: list[str] = []
        self._row: Optional[list[str]] = None
        self._cell: Optional[list[str]] = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "section":
            self._section = attrs.get("id")
        elif tag == "ul" and attrs.get("id") == "top-ratios":
            self._in_ratios_ul = True
        elif tag == "li" and self._in_ratios_ul:
            self._in_li, self._li_name, self._li_value = True, [], []
        elif tag == "span" and self._in_li and "name" in (attrs.get("class") or ""):
            self._in_name_span = True
        elif tag == "tr" and self._section:
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []

    def handle_endtag(self, tag):
        if tag == "section":
            self._section = None
        elif tag == "ul" and self._in_ratios_ul:
            self._in_ratios_ul = False
        elif tag == "li" and self._in_li:
            name = " ".join("".join(self._li_name).split())
            value = " ".join("".join(self._li_value).split())
            if name:
                self.ratios[name] = value
            self._in_li = False
        elif tag == "span" and self._in_name_span:
            self._in_name_span = False
        elif tag in ("td", "th") and self._cell is not None and self._row is not None:
            self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None
        elif tag == "tr" and self._row is not None and self._section:
            if self._row:
                self.tables.setdefault(self._section, []).append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)
        elif self._in_li:
            (self._li_name if self._in_name_span else self._li_value).append(data)


def _table_row(rows: list[list[str]], *labels: str) -> list[float]:
    """Numeric values of the first row whose label matches (normalized)."""
    wanted = {_norm(l) for l in labels}
    for row in rows:
        if row and _norm(row[0]) in wanted:
            return [v for cell in row[1:] if (v := _parse_number(cell)) is not None]
    return []


def parse_screener_html(
    html: str,
    symbol: str,
    company_type: CompanyType = CompanyType.STANDARD,
    listed_on_nse: Optional[bool] = None,
) -> Fundamentals:
    """Pure function from page HTML to a Fundamentals snapshot - separated
    from fetching so it is unit-testable against fixture HTML."""
    p = _ScreenerHTMLParser()
    p.feed(html)

    quarters = p.tables.get("quarters", [])
    shareholding = p.tables.get("shareholding", [])

    quarterly_revenue = _table_row(quarters, "Sales", "Revenue")
    quarterly_net_profit = _table_row(quarters, "Net Profit")
    quarterly_other_income = _table_row(quarters, "Other Income")
    quarterly_tax = _table_row(quarters, "Tax %")

    revenue_ttm_history = rolling_ttm(quarterly_revenue)
    profit_ttm_history = rolling_ttm(quarterly_net_profit)

    def holding(*labels: str) -> float:
        values = _table_row(shareholding, *labels)
        return values[-1] if values else 0.0  # latest reporting period

    def ratio(name: str) -> Optional[float]:
        return _parse_number(p.ratios.get(name, ""))

    return Fundamentals(
        symbol=symbol,
        as_of=date.today(),
        company_type=company_type,
        market_cap_cr=ratio("Market Cap") or 0.0,
        revenue_ttm_cr=revenue_ttm_history[-1] if revenue_ttm_history else 0.0,
        net_profit_ttm_cr=profit_ttm_history[-1] if profit_ttm_history else 0.0,
        revenue_ttm_history_cr=revenue_ttm_history,
        net_profit_ttm_history_cr=profit_ttm_history,
        quarterly_revenue_cr=quarterly_revenue,
        quarterly_net_profit_cr=quarterly_net_profit,
        quarterly_other_income_cr=quarterly_other_income,
        quarterly_effective_tax_rate_pct=quarterly_tax,
        roce_pct=ratio("ROCE"),
        roe_pct=ratio("ROE"),
        debt_to_equity=ratio("Debt to equity"),
        promoter_holding_pct=holding("Promoters"),
        promoter_pledging_pct_of_holding=ratio("Pledged percentage") or 0.0,
        fii_pct=holding("FIIs"),
        dii_pct=holding("DIIs"),
        public_pct=holding("Public"),
        listed_on_nse=listed_on_nse,
    )


def _default_html_transport(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


class ScreenerFetcher:
    """Fetches one company's fundamentals from Screener.in (consolidated
    view, per Section 4.11 - see the module docstring for the label trap)."""

    def __init__(self, transport: Optional[Callable[[str], str]] = None):
        self._transport = transport or _default_html_transport

    def fetch(
        self,
        symbol: str,
        company_type: CompanyType = CompanyType.STANDARD,
        listed_on_nse: Optional[bool] = None,
    ) -> Fundamentals:
        # company_type and listed_on_nse are caller-supplied: whether a
        # company is a bank/NBFC (Section 4.8) or NSE-listed (Section 5.0)
        # is not reliably derivable from the Screener page itself. A
        # successful NSEFetcher pull for the same symbol is the natural
        # evidence for listed_on_nse=True.
        html = self._transport(SCREENER_CONSOLIDATED_URL.format(symbol=symbol))
        return parse_screener_html(html, symbol, company_type, listed_on_nse)


# --------------------------------------------------------------------------
# NSE daily OHLC
# --------------------------------------------------------------------------

#: Predates NSE's own 1994 launch: fetching from here guarantees the FULL
#: listing history for every symbol, which lifetime_high requires
#: (CLAUDE.md rule 6 / models.py caveat).
FULL_HISTORY_START = date(1992, 1, 1)

NSE_HOME_URL = "https://www.nseindia.com/"
NSE_HISTORY_URL = (
    "https://www.nseindia.com/api/historical/cm/equity"
    "?symbol={symbol}&series=[%22EQ%22]&from={start}&to={end}"
)
_CHUNK = timedelta(days=364)  # the NSE endpoint rejects ranges much past a year


class _NSEJsonTransport:
    """NSE's API refuses cookie-less clients: warm up a session against the
    homepage once, then reuse the jar for API calls."""

    def __init__(self):
        self._opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(CookieJar())
        )
        self._warm = False

    def __call__(self, url: str) -> dict:
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        if not self._warm:
            self._opener.open(
                urllib.request.Request(NSE_HOME_URL, headers=headers), timeout=30
            ).read()
            self._warm = True
        with self._opener.open(
            urllib.request.Request(url, headers=headers), timeout=30
        ) as response:
            return json.loads(response.read().decode("utf-8"))


def _candle_from_nse_row(row: dict) -> Optional[Candle]:
    try:
        return Candle(
            date=datetime.strptime(row["CH_TIMESTAMP"], "%Y-%m-%d").date(),
            open=float(row["CH_OPENING_PRICE"]),
            high=float(row["CH_TRADE_HIGH_PRICE"]),
            low=float(row["CH_TRADE_LOW_PRICE"]),
            close=float(row["CH_CLOSING_PRICE"]),
            volume=int(row.get("CH_TOT_TRADED_QTY", 0)),
        )
    except (KeyError, TypeError, ValueError):
        return None  # malformed row: skip it rather than lose the whole pull


class NSEFetcher:
    """Fetches daily OHLC from NSE's historical API in year-sized chunks,
    from FULL_HISTORY_START by default - never a truncated window."""

    def __init__(
        self,
        transport: Optional[Callable[[str], dict]] = None,
        throttle_seconds: float = 0.5,
    ):
        self._transport = transport or _NSEJsonTransport()
        self._throttle = throttle_seconds

    def fetch_full_history(
        self,
        symbol: str,
        start: date = FULL_HISTORY_START,
        end: Optional[date] = None,
    ) -> PriceSeries:
        end = end or date.today()
        candles_by_date: dict[date, Candle] = {}

        chunk_start = start
        while chunk_start <= end:
            chunk_end = min(chunk_start + _CHUNK, end)
            url = NSE_HISTORY_URL.format(
                symbol=urllib.parse.quote(symbol),
                start=chunk_start.strftime("%d-%m-%Y"),
                end=chunk_end.strftime("%d-%m-%Y"),
            )
            body = self._transport(url)
            for row in body.get("data", []):
                candle = _candle_from_nse_row(row)
                if candle is not None:
                    candles_by_date[candle.date] = candle  # dedupe on date
            chunk_start = chunk_end + timedelta(days=1)
            if self._throttle and chunk_start <= end:
                time.sleep(self._throttle)

        return PriceSeries(
            symbol=symbol,
            candles=[candles_by_date[d] for d in sorted(candles_by_date)],
        )
