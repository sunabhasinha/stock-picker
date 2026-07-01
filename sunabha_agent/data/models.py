"""
Core data models for the Vivek Singhal strategy engine.

Every strategy, screener, and portfolio rule in this codebase consumes and
produces these shapes. Keeping them in one place means a strategy never has
to guess what fields are available - and it means we can swap the actual
data source (screener.in scraper, NSE API, manual CSV import) without
touching any strategy code.

Reference: master_strategy_kb.md, Section 4.1 - "almost all financial data
exists in two forms: per-share and whole-company". We standardize on
whole-company figures (crore INR) throughout, since that's what the course
uses for every threshold (e.g. "net profit > 200 crore").
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class Universe(str, Enum):
    """The three stock-quality universes defined in Video 1."""

    V40 = "V40"
    V40_NEXT = "V40_NEXT"
    V200 = "V200"
    UNCLASSIFIED = "UNCLASSIFIED"  # not in any of the three - most strategies
    # must refuse to run on this, except Strategy 7 (NSE-wide).


class CompanyType(str, Enum):
    """
    Drives which V200 branch and which debt/equity exemption applies.
    Per Section 1.3 / 4.8: banks, NBFCs, and *functionally* lending
    businesses (e.g. margin-lending brokers like Angel One) are exempted
    from the standard debt/equity ceiling and use ROE instead of ROCE.
    """

    STANDARD = "STANDARD"
    BANK = "BANK"
    NBFC = "NBFC"
    FUNCTIONALLY_LENDING = "FUNCTIONALLY_LENDING"  # e.g. margin-trading brokers


@dataclass(frozen=True)
class Candle:
    """One daily OHLC candle. Immutable - candles don't get rewritten."""

    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int = 0

    @property
    def is_green(self) -> bool:
        return self.close > self.open

    @property
    def is_red(self) -> bool:
        return self.close < self.open

    @property
    def body_top(self) -> float:
        """Top of the candle BODY (not the wick) - needed for the RHS/CWH
        neckline rule: 'the body of a green candle must never be crossed'."""
        return max(self.open, self.close)

    @property
    def body_bottom(self) -> float:
        return min(self.open, self.close)


@dataclass
class PriceSeries:
    """Ordered daily candles for one stock, oldest first."""

    symbol: str
    candles: list[Candle] = field(default_factory=list)

    @property
    def latest(self) -> Candle:
        if not self.candles:
            raise ValueError(f"No candles loaded for {self.symbol}")
        return self.candles[-1]

    @property
    def lifetime_high(self) -> float:
        """
        Highest CLOSING price in the available history.

        IMPORTANT CAVEAT (flag for the user, not silently swept under the rug):
        this is only the lifetime high *within the data we have loaded*. If a
        stock has 15+ years of history and we only loaded 5 years of candles,
        this number is WRONG. Every strategy that depends on lifetime_high
        (RHS, CWH, Strategy 7, Strategy 8/LTH) is only as accurate as the
        depth of history fetched. The data layer must fetch full listing
        history for this number to be trustworthy - this is called out
        explicitly in the data fetcher and again in the accuracy checklist.
        """
        if not self.candles:
            raise ValueError(f"No candles loaded for {self.symbol}")
        return max(c.high for c in self.candles)

    def closes(self) -> list[float]:
        return [c.close for c in self.candles]

    def slice_last_n(self, n: int) -> "PriceSeries":
        return PriceSeries(symbol=self.symbol, candles=self.candles[-n:])


@dataclass
class Fundamentals:
    """
    A snapshot of fundamental data for one stock, as of a given quarter/date.

    Field names map directly to the screener.in fields referenced throughout
    master_strategy_kb.md. Net profit, revenue are TTM (trailing twelve
    months) unless explicitly marked _quarterly - the course is explicit
    (Section 4.12, Strategy 8) that TTM, not single-quarter, is what most
    rules key off of.
    """

    symbol: str
    as_of: date
    company_type: CompanyType

    market_cap_cr: float  # crore INR
    revenue_ttm_cr: float
    net_profit_ttm_cr: float
    revenue_ttm_history_cr: list[float] = field(default_factory=list)  # oldest->newest, for ATH checks
    net_profit_ttm_history_cr: list[float] = field(default_factory=list)

    # quarterly figures, most recent last - needed for the YoY (not QoQ)
    # comparison rule in Section 4.12 and the "one bad quarter" rule in 4.15
    quarterly_revenue_cr: list[float] = field(default_factory=list)
    quarterly_net_profit_cr: list[float] = field(default_factory=list)
    quarterly_other_income_cr: list[float] = field(default_factory=list)
    quarterly_effective_tax_rate_pct: list[float] = field(default_factory=list)

    roce_pct: Optional[float] = None  # non-BFSI companies
    roe_pct: Optional[float] = None  # banks / NBFC / functionally-lending
    debt_to_equity: Optional[float] = None  # None/ignored for BANK/NBFC/FUNCTIONALLY_LENDING

    promoter_holding_pct: float = 0.0
    promoter_pledging_pct_of_holding: float = 0.0  # % of PROMOTER's OWN holding pledged, not of company
    fii_pct: float = 0.0
    dii_pct: float = 0.0
    public_pct: float = 0.0
    hni_pct: float = 0.0  # subset of public_pct, individually >1% holders

    fixed_assets_cr: Optional[float] = None
    cwip_cr: Optional[float] = None  # Capital Work In Progress
    depreciation_quarterly_cr: list[float] = field(default_factory=list)

    listed_year: Optional[int] = None
    business_incorporated_year: Optional[int] = None  # may predate listing - Section 1.2 Condition 2
    sector: Optional[str] = None
    sector_rank_by_sales: Optional[int] = None
    sector_rank_by_profit: Optional[int] = None
    is_psu: bool = False
    under_merger: bool = False  # Section 6.4 situational risk flag

    @property
    def weak_hands_pct(self) -> float:
        """Retail public only, excluding HNIs. Section 4.9 formula."""
        return self.public_pct - self.hni_pct

    @property
    def strong_hands_pct(self) -> float:
        return self.promoter_holding_pct + self.fii_pct + self.dii_pct + self.hni_pct

    @property
    def pledged_pct_of_total_company(self) -> float:
        """The number that actually matters for the Section 4.10 disqualifier -
        promoter_holding% * pledging%-of-that-holding, NOT pledging% alone."""
        return self.promoter_holding_pct * (self.promoter_pledging_pct_of_holding / 100.0)

    def is_ttm_at_all_time_high(self) -> bool:
        """Used by Strategy 8 (LTH) and the 'one bad quarter' rule context.
        Revenue AND profit must BOTH be at ATH simultaneously."""
        if not self.revenue_ttm_history_cr or not self.net_profit_ttm_history_cr:
            return False
        rev_ath = self.revenue_ttm_cr >= max(self.revenue_ttm_history_cr)
        profit_ath = self.net_profit_ttm_cr >= max(self.net_profit_ttm_history_cr)
        return rev_ath and profit_ath


@dataclass
class Signal:
    """
    The universal output type every strategy produces. This is what the
    portfolio layer, the screening gate, and (eventually) any UI consume.
    Nothing downstream should need to know strategy-specific internals.
    """

    symbol: str
    strategy_name: str
    universe_at_signal_time: Universe
    action: str  # "BUY" or "SELL" or "AVERAGE"
    trigger_date: date
    signal_price: float
    target_price: Optional[float] = None  # None for strategies with no fixed target yet known
    suggested_position_pct: float = 3.0  # of total portfolio, per course default
    requires_human_confirmation: bool = False  # True for RHS/CWH pattern candidates, Strategy 7
    rationale: str = ""  # human-readable explanation, always populated - never a silent black box
    confidence_tier: Optional[str] = None  # e.g. "best" / "very_good" from ROCE/D-E tiering
    metadata: dict = field(default_factory=dict)  # strategy-specific extra detail for debugging/audit
