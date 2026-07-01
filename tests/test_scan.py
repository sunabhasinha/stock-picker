"""
Tests for the daily-scan runner.

Fake fetchers and a hand-built registry throughout: the scan's job is
wiring (universe filter -> fetch -> gate -> engine -> ranked report) and
resilience (one bad symbol never kills the scan) - the underlying layers
have their own suites.
"""

import datetime as dt
import unittest

from sunabha_agent.data.models import Candle, CompanyType, Fundamentals, PriceSeries, Universe
from sunabha_agent.data.universe_lists import UniverseEntry, UniverseRegistry
from sunabha_agent.portfolio.category_engine import CATEGORY_2, ReconciliationAction
from sunabha_agent.scan import DailyScanner, format_report, positions_from_dict


def flat_candles(price, n, start=dt.date(2020, 1, 1)):
    return [
        Candle(date=start + dt.timedelta(days=i), open=price, high=price,
               low=price, close=price)
        for i in range(n)
    ]


def sma_buy_series(symbol):
    candles = flat_candles(100.0, 200)
    last = candles[-1].date
    for i, p in enumerate([90, 80, 70, 60, 50, 40, 30, 20, 10, 5], start=1):
        candles.append(Candle(date=last + dt.timedelta(days=i), open=p, high=p,
                              low=p, close=p))
    return PriceSeries(symbol=symbol, candles=candles)


def passing_fundamentals(symbol, listed_on_nse=None):
    return Fundamentals(
        symbol=symbol, as_of=dt.date(2024, 6, 30),
        company_type=CompanyType.STANDARD, market_cap_cr=50000.0,
        revenue_ttm_cr=5000.0, net_profit_ttm_cr=800.0,
        roce_pct=35.0, debt_to_equity=0.05,
        promoter_holding_pct=50.0, promoter_pledging_pct_of_holding=0.0,
        # Latest quarter DOWN YoY (8 vs 11): Strategy 7's condition 6 hard-
        # fails, so the deliberately-crashed price fixtures below don't also
        # fire turnaround candidates and muddy the assertions.
        quarterly_net_profit_cr=[10, 12, 8, 9, 11, 13, 9, 8],
        listed_on_nse=listed_on_nse,
    )


class FakePriceFetcher:
    def __init__(self, series_by_symbol):
        self.series = series_by_symbol

    def fetch_full_history(self, symbol):
        if symbol not in self.series:
            raise ConnectionError("symbol not found on NSE")
        return self.series[symbol]


class FakeFundamentalsFetcher:
    def __init__(self):
        self.calls = []

    def fetch(self, symbol, company_type=CompanyType.STANDARD, listed_on_nse=None):
        self.calls.append((symbol, company_type, listed_on_nse))
        return passing_fundamentals(symbol, listed_on_nse)


REGISTRY = UniverseRegistry([
    UniverseEntry("ALPHA", Universe.V40, "IT", CompanyType.STANDARD),
    UniverseEntry("BETA", Universe.V40_NEXT, "FMCG", CompanyType.STANDARD),
])


def make_scanner(series_by_symbol):
    return DailyScanner(
        CATEGORY_2,
        registry=REGISTRY,
        price_fetcher=FakePriceFetcher(series_by_symbol),
        fundamentals_fetcher=FakeFundamentalsFetcher(),
    )


class TestScan(unittest.TestCase):
    def test_default_symbols_respect_the_category_universe(self):
        # Category 2 is V40 only: BETA (V40_NEXT) must not be scanned.
        scanner = make_scanner({"ALPHA": sma_buy_series("ALPHA")})
        self.assertEqual(scanner.default_symbols(), ["ALPHA"])

    def test_end_to_end_buy_candidate(self):
        scanner = make_scanner({"ALPHA": sma_buy_series("ALPHA")})
        report = scanner.scan()
        self.assertEqual(len(report.ranked_candidates), 1)
        signal, fundamentals = report.ranked_candidates[0]
        self.assertEqual(signal.symbol, "ALPHA")
        self.assertEqual(signal.action, "BUY")
        self.assertEqual(fundamentals.symbol, "ALPHA")
        self.assertEqual(report.errors, [])

    def test_nse_success_supplies_the_strategy7_listing_evidence(self):
        # The scan passes listed_on_nse=True to the fundamentals fetcher
        # because the NSE price pull just succeeded (Section 5.0 gate).
        scanner = make_scanner({"ALPHA": sma_buy_series("ALPHA")})
        scanner.scan()
        self.assertEqual(scanner.fundamentals_fetcher.calls,
                         [("ALPHA", CompanyType.STANDARD, True)])

    def test_one_bad_symbol_never_kills_the_scan(self):
        scanner = make_scanner({"ALPHA": sma_buy_series("ALPHA")})
        report = scanner.scan(symbols=["BROKEN", "ALPHA"])
        self.assertEqual(len(report.ranked_candidates), 1)  # ALPHA still scanned
        self.assertEqual(len(report.errors), 1)
        self.assertIn("BROKEN", report.errors[0])

    def test_exits_are_separated_from_buy_candidates(self):
        # Open V20 trade tagged range_upper=4.0; the close (5.0) breaches it
        # -> a SELL, reported in exit_signals, not among candidates.
        positions = positions_from_dict({
            "ALPHA": {
                "average_cost": 100.0,
                "open_trades": [{
                    "strategy_name": "V20 Strategy", "action": "BUY",
                    "entry_price": 100.0, "entry_date": "2020-03-01",
                    "metadata": {"range_upper": 4.0},
                }],
            },
        })
        scanner = make_scanner({"ALPHA": sma_buy_series("ALPHA")})
        report = scanner.scan(positions=positions)
        self.assertEqual([s.action for s in report.exit_signals], ["SELL"])
        self.assertEqual(report.exit_signals[0].strategy_name, "V20 Strategy")
        # And the position got a Section 6.3 reconciliation verdict
        self.assertEqual(report.reconciliations[0].action,
                         ReconciliationAction.STRATEGY_APPLIES)

    def test_held_symbols_are_scanned_even_outside_the_scan_list(self):
        # GAMMA is UNCLASSIFIED (outside Category 2's universe): no signals
        # may fire, but the holding still gets reconciled - profitable with
        # no applicable strategy -> exit and redeploy.
        gamma = PriceSeries(symbol="GAMMA", candles=flat_candles(100.0, 30))
        scanner = make_scanner({"ALPHA": sma_buy_series("ALPHA"), "GAMMA": gamma})
        report = scanner.scan(
            positions={"GAMMA": positions_from_dict(
                {"GAMMA": {"average_cost": 50.0}})["GAMMA"]},
        )
        self.assertIn("GAMMA", report.scanned_symbols)
        gamma_rec = next(r for r in report.reconciliations if r.symbol == "GAMMA")
        self.assertEqual(gamma_rec.action, ReconciliationAction.EXIT_PROFITABLE)
        # ...and no signals leaked from outside the category universe
        self.assertTrue(all(s.symbol != "GAMMA"
                            for s, _ in report.ranked_candidates))


class TestPositionsParsing(unittest.TestCase):
    def test_positions_from_dict(self):
        positions = positions_from_dict({
            "tcs": {
                "average_cost": 3200.5,
                "open_trades": [{
                    "strategy_name": "Lifetime High Strategy",
                    "entry_price": 3100, "entry_date": "2024-02-01",
                    "target_price": 4100,
                }],
            },
        })
        self.assertIn("TCS", positions)
        trade = positions["TCS"].open_trades[0]
        self.assertEqual(trade.action, "BUY")  # default
        self.assertEqual(trade.trigger_date, dt.date(2024, 2, 1))
        self.assertEqual(trade.target_price, 4100.0)


class TestFormatting(unittest.TestCase):
    def test_report_text_covers_all_sections(self):
        scanner = make_scanner({"ALPHA": sma_buy_series("ALPHA")})
        report = scanner.scan(symbols=["ALPHA", "BROKEN"])
        text = format_report(report)
        self.assertIn("category_2", text)
        self.assertIn("BUY ALPHA", text)
        self.assertIn("== ERRORS", text)
        self.assertIn("BROKEN", text)

    def test_empty_day_states_the_idle_capital_rule(self):
        gamma = PriceSeries(symbol="ALPHA", candles=flat_candles(100.0, 30))
        scanner = make_scanner({"ALPHA": gamma})
        text = format_report(scanner.scan())
        self.assertIn("hold cash", text)
        self.assertIn("never substitute", text.lower())


if __name__ == "__main__":
    unittest.main()
