"""
Tests for Strategy 7: "Three Times in Three Years" (Section 5).

The entry side rides on the checklist (tested in
test_turnaround_checklist.py); here we test the strategy contract: the
NSE hard gate, candidate emission with open research questions, the
single-entry rule, and the two-phase exit (100% within 12 months, then
lifetime-high-only).
"""

import datetime as dt
import unittest

from sunabha_agent.data.models import Candle, CompanyType, Fundamentals, PriceSeries, Signal, Universe
from sunabha_agent.strategies.turnaround_strategy import TurnaroundStrategy

CRASH_AND_PARTIAL_RECOVERY = [200, 250, 300, 250, 180, 120, 80, 60, 70, 90, 110, 120]


def make_candles(closes, start=dt.date(2020, 1, 1)):
    candles, prev = [], closes[0]
    for i, c in enumerate(closes):
        candles.append(
            Candle(date=start + dt.timedelta(days=i), open=prev,
                   high=max(prev, c), low=min(prev, c), close=c)
        )
        prev = c
    return candles


def make_fundamentals(**overrides):
    defaults = dict(
        symbol="TESTCO",
        as_of=dt.date(2024, 6, 30),
        company_type=CompanyType.STANDARD,
        market_cap_cr=5000.0,
        revenue_ttm_cr=650.0,
        net_profit_ttm_cr=45.0,
        revenue_ttm_history_cr=[500, 600, 700, 1000, 700, 600, 650],
        net_profit_ttm_history_cr=[50, 60, 70, 100, 40, 30, 45],
        quarterly_net_profit_cr=[10, 12, 8, 9, 11, 13, 9, 10, 20],
        listed_on_nse=True,
    )
    defaults.update(overrides)
    return Fundamentals(**defaults)


def evaluate(closes=None, fundamentals=None, universe=Universe.UNCLASSIFIED,
             open_trades=None):
    prices = PriceSeries(
        symbol="TESTCO", candles=make_candles(closes or CRASH_AND_PARTIAL_RECOVERY)
    )
    return TurnaroundStrategy().evaluate(
        prices=prices,
        fundamentals=fundamentals,
        universe=universe,
        open_trades_on_this_stock=open_trades or [],
    ), prices


def open_trade(entry_price, days_held, latest_date, **metadata):
    return Signal(
        symbol="TESTCO", strategy_name=TurnaroundStrategy.name,
        universe_at_signal_time=Universe.UNCLASSIFIED, action="BUY",
        trigger_date=latest_date - dt.timedelta(days=days_held),
        signal_price=entry_price, metadata=metadata,
    )


class TestEntry(unittest.TestCase):
    def test_buy_candidate_emitted_with_open_research_questions(self):
        signals, prices = evaluate(fundamentals=make_fundamentals())
        self.assertEqual(len(signals), 1)
        s = signals[0]
        self.assertEqual(s.action, "BUY")
        self.assertEqual(s.suggested_position_pct, 3.0)
        # Section 5.5 flag 1: strongest human-in-the-loop case anywhere
        self.assertTrue(s.requires_human_confirmation)
        # No researcher configured -> conditions 3 and 5 remain open, and
        # the signal must say so rather than pretend they're confirmed
        self.assertFalse(s.metadata["fully_confirmed"])
        self.assertGreaterEqual(len(s.metadata["open_research_questions"]), 2)
        # Default exit: 100% gain (Condition 8); lifetime high in metadata
        self.assertAlmostEqual(s.target_price, 240.0)
        self.assertAlmostEqual(s.metadata["lifetime_high_at_entry"], 300.0)
        self.assertEqual(s.metadata["decline_category"], "A")

    def test_runs_on_unclassified_universe_unlike_every_other_strategy(self):
        # Section 5.0: NSE-wide, not V40/V40Next/V200-restricted
        for universe in Universe:
            signals, _ = evaluate(fundamentals=make_fundamentals(), universe=universe)
            self.assertEqual(len(signals), 1, f"should fire on {universe}")

    def test_nse_gate_is_hard_and_defaults_closed(self):
        # Section 5.0: not NSE-listed -> ineligible regardless of the
        # checklist. None (unknown) must also refuse - never assume listed.
        for flag in (False, None):
            signals, _ = evaluate(fundamentals=make_fundamentals(listed_on_nse=flag))
            self.assertEqual(signals, [], f"listed_on_nse={flag} must not fire")
        signals, _ = evaluate(fundamentals=None)
        self.assertEqual(signals, [])

    def test_no_signal_when_a_condition_hard_fails(self):
        # Price re-rated to 190 (~37% below high) -> Condition 7 fails.
        rerated = [200, 250, 300, 250, 180, 120, 80, 60, 120, 160, 180, 190]
        signals, _ = evaluate(closes=rerated, fundamentals=make_fundamentals())
        self.assertEqual(signals, [])

    def test_single_entry_no_averaging_ever(self):
        # Section 5.2: single-entry strategy. Open trade at 100, price 120:
        # no exit condition met, and no second BUY may be emitted.
        _, prices = evaluate(fundamentals=make_fundamentals())
        latest = prices.latest.date
        signals, _ = evaluate(
            fundamentals=make_fundamentals(),
            open_trades=[open_trade(100.0, days_held=30, latest_date=latest,
                                    lifetime_high_at_entry=300.0)],
        )
        self.assertEqual(signals, [])


class TestExit(unittest.TestCase):
    DOUBLED = [200, 250, 300, 250, 180, 120, 80, 60, 70, 90, 110, 121]

    def test_condition8_sell_at_100pct_gain_within_12_months(self):
        _, prices = evaluate(closes=self.DOUBLED, fundamentals=None)
        latest = prices.latest.date
        # Entry 60, close 121 -> +101.7% after 300 days (inside 12 months)
        signals, _ = evaluate(
            closes=self.DOUBLED,
            open_trades=[open_trade(60.0, days_held=300, latest_date=latest,
                                    lifetime_high_at_entry=300.0)],
        )
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].action, "SELL")
        self.assertTrue(signals[0].requires_human_confirmation)

    def test_condition8_lapses_after_12_months(self):
        # Same +101.7% gain but 400 days in: the 100% trigger no longer
        # applies - Condition 9 says hold until the lifetime high (300).
        _, prices = evaluate(closes=self.DOUBLED, fundamentals=None)
        latest = prices.latest.date
        signals, _ = evaluate(
            closes=self.DOUBLED,
            open_trades=[open_trade(60.0, days_held=400, latest_date=latest,
                                    lifetime_high_at_entry=300.0)],
        )
        self.assertEqual(signals, [])

    def test_condition9_sell_at_original_lifetime_high_any_time(self):
        recovered = [200, 250, 300, 250, 180, 120, 80, 60, 150, 250, 290, 301]
        _, prices = evaluate(closes=recovered, fundamentals=None)
        latest = prices.latest.date
        signals, _ = evaluate(
            closes=recovered,
            open_trades=[open_trade(60.0, days_held=500, latest_date=latest,
                                    lifetime_high_at_entry=300.0)],
        )
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].action, "SELL")
        self.assertIn("lifetime", signals[0].rationale.lower())


class TestCourseInvariants(unittest.TestCase):
    def test_no_stop_loss_single_trade_3pct(self):
        strategy = TurnaroundStrategy()
        self.assertFalse(strategy.uses_stop_loss)
        self.assertEqual(strategy.max_concurrent_trades_per_stock, 1)
        self.assertEqual(strategy.max_allocation_pct_per_stock, 3.0)


if __name__ == "__main__":
    unittest.main()
