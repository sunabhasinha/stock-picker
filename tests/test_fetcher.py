"""
Tests for the live data fetchers (Screener.in fundamentals, NSE OHLC).

Everything runs offline against fixture HTML/JSON via injected
transports. The two course rules under test: the Section 4.11
consolidated-view label inversion, and the full-listing-history
requirement for prices (CLAUDE.md rule 6).
"""

import datetime as dt
import unittest

from sunabha_agent.data.fetcher import (
    FULL_HISTORY_START,
    NSEFetcher,
    ScreenerFetcher,
    YahooPriceFetcher,
    _parse_number,
    is_showing_consolidated,
    parse_screener_html,
    rolling_ttm,
)

FIXTURE_HTML = """
<html><body>
<a href="/company/TESTCO/">View Standalone</a>
<ul id="top-ratios">
  <li><span class="name">Market Cap</span> ₹ <span class="number">1,23,456</span> Cr.</li>
  <li><span class="name">ROCE</span> <span class="number">32.5</span> %</li>
  <li><span class="name">ROE</span> <span class="number">28.0</span> %</li>
  <li><span class="name">Debt to equity</span> <span class="number">0.05</span></li>
  <li><span class="name">Pledged percentage</span> <span class="number">2.50</span> %</li>
</ul>
<section id="quarters">
<table>
<tr><th></th><th>Dec 2022</th><th>Mar 2023</th><th>Jun 2023</th><th>Sep 2023</th>
    <th>Dec 2023</th><th>Mar 2024</th><th>Jun 2024</th><th>Sep 2024</th></tr>
<tr><td>Sales +</td><td>100</td><td>110</td><td>105</td><td>120</td>
    <td>115</td><td>125</td><td>130</td><td>140</td></tr>
<tr><td>Other Income</td><td>2</td><td>3</td><td>1</td><td>2</td>
    <td>2</td><td>15</td><td>2</td><td>3</td></tr>
<tr><td>Net Profit +</td><td>10</td><td>12</td><td>8</td><td>9</td>
    <td>11</td><td>13</td><td>9</td><td>15</td></tr>
<tr><td>Tax %</td><td>25</td><td>24</td><td>26</td><td>25</td>
    <td>25</td><td>2</td><td>25</td><td>24</td></tr>
</table>
</section>
<section id="shareholding">
<table>
<tr><td>Promoters +</td><td>50.1</td><td>52.5</td></tr>
<tr><td>FIIs +</td><td>19.0</td><td>20.1</td></tr>
<tr><td>DIIs +</td><td>10.0</td><td>10.4</td></tr>
<tr><td>Public +</td><td>20.9</td><td>17.0</td></tr>
</table>
</section>
</body></html>
"""


def nse_row(day, o, h, low, c, vol=1000):
    return {
        "CH_TIMESTAMP": day,
        "CH_OPENING_PRICE": o,
        "CH_TRADE_HIGH_PRICE": h,
        "CH_TRADE_LOW_PRICE": low,
        "CH_CLOSING_PRICE": c,
        "CH_TOT_TRADED_QTY": vol,
    }


class TestNumberParsing(unittest.TestCase):
    def test_indian_formats(self):
        self.assertEqual(_parse_number("₹ 1,23,456 Cr."), 123456.0)
        self.assertEqual(_parse_number("32.5 %"), 32.5)
        self.assertEqual(_parse_number("0.05"), 0.05)
        self.assertIsNone(_parse_number(""))
        self.assertIsNone(_parse_number("-"))
        self.assertIsNone(_parse_number("Sep 2024"))

    def test_rolling_ttm(self):
        self.assertEqual(rolling_ttm([10, 12, 8, 9, 11]), [39, 40])
        self.assertEqual(rolling_ttm([10, 12]), [])  # under 4 quarters


class TestConsolidatedInversion(unittest.TestCase):
    def test_section_4_11_label_inversion(self):
        # The toggle names what you'd switch TO, not what's displayed:
        self.assertIs(is_showing_consolidated("... View Standalone ..."), True)
        self.assertIs(is_showing_consolidated("... View Consolidated ..."), False)
        # No toggle at all = no subsidiaries = standalone is correct fallback
        self.assertIsNone(is_showing_consolidated("<html>no toggle here</html>"))

    def test_fetcher_requests_the_consolidated_url(self):
        requested = []

        def transport(url):
            requested.append(url)
            return FIXTURE_HTML

        ScreenerFetcher(transport=transport).fetch("TESTCO")
        self.assertEqual(len(requested), 1)
        self.assertIn("/company/TESTCO/consolidated/", requested[0])


class TestScreenerParsing(unittest.TestCase):
    def setUp(self):
        self.f = parse_screener_html(FIXTURE_HTML, "TESTCO", listed_on_nse=True)

    def test_top_ratios(self):
        self.assertEqual(self.f.market_cap_cr, 123456.0)
        self.assertEqual(self.f.roce_pct, 32.5)
        self.assertEqual(self.f.roe_pct, 28.0)
        self.assertEqual(self.f.debt_to_equity, 0.05)
        self.assertEqual(self.f.promoter_pledging_pct_of_holding, 2.5)

    def test_quarterly_rows(self):
        self.assertEqual(self.f.quarterly_revenue_cr,
                         [100, 110, 105, 120, 115, 125, 130, 140])
        self.assertEqual(self.f.quarterly_net_profit_cr,
                         [10, 12, 8, 9, 11, 13, 9, 15])
        self.assertEqual(self.f.quarterly_other_income_cr,
                         [2, 3, 1, 2, 2, 15, 2, 3])
        self.assertEqual(self.f.quarterly_effective_tax_rate_pct,
                         [25, 24, 26, 25, 25, 2, 25, 24])

    def test_ttm_histories_are_rolling_4_quarter_sums(self):
        self.assertEqual(self.f.revenue_ttm_history_cr, [435, 450, 465, 490, 510])
        self.assertEqual(self.f.net_profit_ttm_history_cr, [39, 40, 41, 42, 48])
        self.assertEqual(self.f.revenue_ttm_cr, 510)
        self.assertEqual(self.f.net_profit_ttm_cr, 48)

    def test_shareholding_uses_latest_period(self):
        self.assertEqual(self.f.promoter_holding_pct, 52.5)
        self.assertEqual(self.f.fii_pct, 20.1)
        self.assertEqual(self.f.dii_pct, 10.4)
        self.assertEqual(self.f.public_pct, 17.0)

    def test_caller_supplied_flags_pass_through(self):
        self.assertIs(self.f.listed_on_nse, True)
        # And the default is None (unknown) - never assumed True
        self.assertIsNone(parse_screener_html(FIXTURE_HTML, "TESTCO").listed_on_nse)


class TestYahooPriceFetcher(unittest.TestCase):
    def test_appends_nse_suffix_and_uppercases(self):
        requested = []

        def transport(yahoo_symbol):
            requested.append(yahoo_symbol)
            return []

        YahooPriceFetcher(transport=transport).fetch_full_history("titan")
        self.assertEqual(requested, ["TITAN.NS"])

    def test_maps_rows_sorts_and_drops_nan_days(self):
        nan = float("nan")
        rows = [
            {"date": dt.date(2020, 1, 7), "open": 102, "high": 106, "low": 101,
             "close": 105, "volume": 500},
            {"date": dt.date(2020, 1, 6), "open": 100, "high": 103, "low": 99,
             "close": 101, "volume": 400},
            # the in-progress trading day Yahoo returns as NaN - must be dropped
            {"date": dt.date(2020, 1, 8), "open": nan, "high": nan, "low": nan,
             "close": nan, "volume": 0},
        ]
        series = YahooPriceFetcher(transport=lambda s: rows).fetch_full_history("TITAN")
        self.assertEqual(series.symbol, "TITAN")
        self.assertEqual([c.date.day for c in series.candles], [6, 7])
        self.assertEqual(series.latest.close, 105)


class TestNSEFetcher(unittest.TestCase):
    def test_full_history_starts_before_nse_existed(self):
        # CLAUDE.md rule 6: lifetime_high needs the FULL listing history.
        # Default start (1992) predates NSE's own 1994 launch.
        requested = []

        def transport(url):
            requested.append(url)
            return {"data": []}

        NSEFetcher(transport=transport, throttle_seconds=0).fetch_full_history(
            "TESTCO", end=dt.date(1992, 12, 31)
        )
        self.assertEqual(FULL_HISTORY_START, dt.date(1992, 1, 1))
        self.assertIn("from=01-01-1992", requested[0])

    def test_chunks_merge_dedupe_and_sort(self):
        def transport(url):
            if "from=01-01-2020" in url:
                return {"data": [
                    nse_row("2020-03-02", 102, 106, 101, 105),
                    nse_row("2020-01-06", 100, 103, 99, 101),
                ]}
            return {"data": [
                nse_row("2020-03-02", 102, 106, 101, 105),  # duplicate date
                nse_row("2021-01-04", 110, 115, 109, 114, vol=2000),
            ]}

        series = NSEFetcher(transport=transport, throttle_seconds=0).fetch_full_history(
            "TESTCO", start=dt.date(2020, 1, 1), end=dt.date(2021, 6, 1)
        )
        self.assertEqual(series.symbol, "TESTCO")
        self.assertEqual([c.date.isoformat() for c in series.candles],
                         ["2020-01-06", "2020-03-02", "2021-01-04"])
        latest = series.latest
        self.assertEqual((latest.open, latest.high, latest.low, latest.close,
                          latest.volume), (110, 115, 109, 114, 2000))

    def test_malformed_rows_are_skipped_not_fatal(self):
        def transport(url):
            return {"data": [
                {"CH_TIMESTAMP": "2020-01-06"},  # missing prices
                nse_row("2020-01-07", 100, 101, 99, 100),
            ]}

        series = NSEFetcher(transport=transport, throttle_seconds=0).fetch_full_history(
            "TESTCO", start=dt.date(2020, 1, 1), end=dt.date(2020, 1, 31)
        )
        self.assertEqual(len(series.candles), 1)


if __name__ == "__main__":
    unittest.main()
