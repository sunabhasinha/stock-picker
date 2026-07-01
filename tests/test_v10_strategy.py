"""
Tests for the V10 Strategy (Section 3.3).

V10 is an averaging overlay, not a standalone detector: no open RHS/CWH
parent trade means no new V10 entries, full stop. The pullback peak is
measured only INSIDE the parent window - highs from before the parent
entry must be invisible to it.
"""

import datetime as dt
import unittest

from sunabha_agent.data.models import Candle, PriceSeries, Signal, Universe
from sunabha_agent.strategies.cwh_strategy import CWHStrategy
from sunabha_agent.strategies.rhs_strategy import RHSStrategy
from sunabha_agent.strategies.v10_strategy import V10Strategy

START = dt.date(2020, 1, 1)
# Pre-window highs up to 200, then the parent window opens at index 4
# (price 100), rallies to a peak of 120, and pulls back 10% to 108.
BASE_CLOSES = [190, 200, 150, 120, 100, 105, 110, 115, 120, 116, 112, 108]
WINDOW_OPEN = START + dt.timedelta(days=4)


def make_candles(closes: list[float], start: dt.date = START) -> list[Candle]:
    candles, prev = [], closes[0]
    for i, c in enumerate(closes):
        candles.append(
            Candle(
                date=start + dt.timedelta(days=i),
                open=prev,
                high=max(prev, c),
                low=min(prev, c),
                close=c,
            )
        )
        prev = c
    return candles


def parent_trade(strategy_name: str = CWHStrategy.name) -> Signal:
    return Signal(
        symbol="TESTCO", strategy_name=strategy_name,
        universe_at_signal_time=Universe.V40, action="BUY",
        trigger_date=WINDOW_OPEN, signal_price=100.0, target_price=140.0,
    )


def v10_trade(entry_price: float, target: float, action: str = "BUY") -> Signal:
    return Signal(
        symbol="TESTCO", strategy_name=V10Strategy.name,
        universe_at_signal_time=Universe.V40, action=action,
        trigger_date=START + dt.timedelta(days=9), signal_price=entry_price,
        target_price=target,
    )


def evaluate(closes, open_trades, universe=Universe.V40):
    prices = PriceSeries(symbol="TESTCO", candles=make_candles(closes))
    return V10Strategy().evaluate(
        prices=prices,
        fundamentals=None,
        universe=universe,
        open_trades_on_this_stock=open_trades,
    )


class TestV10Entry(unittest.TestCase):
    def test_buy_fires_on_10pct_pullback_inside_parent_window(self):
        signals = evaluate(BASE_CLOSES, [parent_trade()])
        self.assertEqual(len(signals), 1)
        s = signals[0]
        self.assertEqual(s.action, "BUY")
        self.assertEqual(s.suggested_position_pct, 3.0)
        self.assertTrue(s.requires_human_confirmation)

    def test_peak_is_measured_inside_window_only(self):
        # Pre-window high is 200; window peak is 120. The V10 target must
        # be the WINDOW peak (Section 3.3: the peak reached since the
        # window opened), proving 200 was ignored.
        signals = evaluate(BASE_CLOSES, [parent_trade()])
        self.assertAlmostEqual(signals[0].target_price, 120.0)

    def test_no_signal_without_open_parent_trade(self):
        # Two-stage qualification (Section 3.3): pullback alone is NOT
        # enough - an open RHS or CWH trade must exist first.
        self.assertEqual(evaluate(BASE_CLOSES, []), [])

    def test_rhs_parent_also_qualifies(self):
        signals = evaluate(BASE_CLOSES, [parent_trade(RHSStrategy.name)])
        self.assertEqual([s.action for s in signals], ["BUY"])

    def test_no_signal_when_pullback_under_10pct(self):
        # Peak 120, close 109 -> only a 9.2% pullback.
        closes = BASE_CLOSES[:-1] + [109]
        self.assertEqual(evaluate(closes, [parent_trade()]), [])

    def test_averaging_requires_5pct_gap_below_previous_v10_entry(self):
        # One open V10 at 108. At 104 the gap is ~3.7% -> blocked. At 102
        # (>= 5% below 108) -> AVERAGE, same gap structure as Knoxville.
        open_trades = [parent_trade(), v10_trade(108.0, target=120.0)]
        self.assertEqual(evaluate(BASE_CLOSES + [104], open_trades), [])
        signals = evaluate(BASE_CLOSES + [104, 102], open_trades)
        self.assertEqual([s.action for s in signals], ["AVERAGE"])
        self.assertAlmostEqual(signals[0].target_price, 120.0)

    def test_max_two_concurrent_v10_trades(self):
        open_trades = [
            parent_trade(),
            v10_trade(108.0, target=120.0),
            v10_trade(102.0, target=120.0, action="AVERAGE"),
        ]
        self.assertEqual(evaluate(BASE_CLOSES + [104, 102, 95], open_trades), [])

    def test_strategy_refuses_to_run_outside_v40_and_v40next(self):
        for forbidden in (Universe.V200, Universe.UNCLASSIFIED):
            signals = evaluate(BASE_CLOSES, [parent_trade()], universe=forbidden)
            self.assertEqual(signals, [], f"must not fire on {forbidden}")


class TestV10Exit(unittest.TestCase):
    def test_sell_fires_when_price_returns_to_the_pullback_peak(self):
        # Entry at 108 after the pullback from 120; price grinds back to
        # 121 -> exit at the peak level it fell from, NOT the parent's
        # target (Section 3.3: a fixed short round-trip).
        closes = BASE_CLOSES + [112, 118, 121]
        open_trades = [parent_trade(), v10_trade(108.0, target=120.0)]
        signals = evaluate(closes, open_trades)
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].action, "SELL")
        self.assertTrue(signals[0].requires_human_confirmation)

    def test_open_v10_trade_can_still_exit_after_parent_closed(self):
        # Edge case: the parent RHS/CWH trade already hit its own target
        # and closed. An orphaned open V10 trade must still be able to
        # exit - only NEW entries require an active parent window.
        closes = BASE_CLOSES + [112, 118, 121]
        signals = evaluate(closes, [v10_trade(108.0, target=120.0)])
        self.assertEqual([s.action for s in signals], ["SELL"])


class TestCourseInvariants(unittest.TestCase):
    def test_no_stop_loss_and_ceilings(self):
        strategy = V10Strategy()
        self.assertFalse(strategy.uses_stop_loss)
        self.assertEqual(strategy.max_concurrent_trades_per_stock, 2)
        # V10's own ceiling is 6% (3%+3%); the combined 9% with the parent
        # trade is the portfolio layer's job (Section 3.3).
        self.assertEqual(strategy.max_allocation_pct_per_stock, 6.0)


if __name__ == "__main__":
    unittest.main()
