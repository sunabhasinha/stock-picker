"""
Tests for the Cup with Handle Strategy (Section 3.2).

The load-bearing test here is the target rule: CWH sells at the technical
target ITSELF, never raised to the lifetime high - the KB flags this as
the main distinguishing rule vs RHS and warns not to conflate them.
"""

import datetime as dt
import unittest

from sunabha_agent.data.models import Candle, PriceSeries, Signal, Universe
from sunabha_agent.strategies.cwh_strategy import CWHStrategy, detect_cwh
from sunabha_agent.strategies.rhs_strategy import detect_rhs

PRIOR_DECLINE = [150, 140, 130, 120, 110, 102, 96, 98]
# neckline 100 | cup to 80 | handle to 92 | base ~92.5-93.2 | green breakout 95
CWH_PATTERN = [100, 97, 90, 80, 85, 93, 100, 96, 92, 92.5, 93, 92.6, 93.2, 95]
# RHS-shaped series (from test_rhs_strategy): first trough 90, second
# (deeper) trough 80 - a valid head-and-shoulders, NOT a cup-and-handle.
RHS_SHAPED = [100, 97, 93, 90, 93, 97, 100, 95, 88, 80, 86, 94, 100,
              96, 92, 92.5, 93, 92.6, 93.2, 95]


def make_candles(closes: list[float], start: dt.date = dt.date(2020, 1, 1)) -> list[Candle]:
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


def evaluate(strategy, closes, universe=Universe.V40, open_trades=None):
    prices = PriceSeries(symbol="TESTCO", candles=make_candles(closes))
    return strategy.evaluate(
        prices=prices,
        fundamentals=None,
        universe=universe,
        open_trades_on_this_stock=open_trades or [],
    )


class TestCWHBuy(unittest.TestCase):
    def setUp(self):
        self.strategy = CWHStrategy()

    def test_buy_fires_on_handle_base_breakout(self):
        signals = evaluate(self.strategy, PRIOR_DECLINE + CWH_PATTERN)
        self.assertEqual(len(signals), 1)
        s = signals[0]
        self.assertEqual(s.action, "BUY")
        self.assertEqual(s.suggested_position_pct, 3.0)
        self.assertTrue(s.requires_human_confirmation)
        self.assertAlmostEqual(s.metadata["neckline"], 100.0)
        self.assertAlmostEqual(s.metadata["cup_low"], 80.0)

    def test_target_is_technical_target_NOT_raised_to_lifetime_high(self):
        # THE key difference from RHS (Section 3.2): tech target = 120,
        # lifetime high = 150 -> CWH's target must stay 120, not 150.
        signals = evaluate(self.strategy, PRIOR_DECLINE + CWH_PATTERN)
        self.assertAlmostEqual(signals[0].target_price, 120.0)
        self.assertAlmostEqual(signals[0].metadata["lifetime_high"], 150.0)

    def test_complex_flag_with_second_handle(self):
        # Cup at 80, one completed handle at 92, then the forming handle
        # whose base breaks out -> 2 handles total = Complex CWH.
        complex_pattern = [100, 97, 90, 80, 85, 93, 100, 96, 92, 95, 100,
                           96.5, 92, 92.5, 93, 92.6, 93.2, 95]
        signals = evaluate(self.strategy, PRIOR_DECLINE + complex_pattern)
        self.assertEqual(len(signals), 1)
        self.assertTrue(signals[0].metadata["is_complex"])

    def test_handle_deeper_than_cup_invalidates_pattern(self):
        # Section 3.2 explicit invalid edge case: a "handle" (84) deeper
        # than the cup (90) is NOT a Cup with Handle.
        bad = [96, 98, 100, 97, 92, 90, 93, 97, 100,
               96, 85, 84, 84.5, 85.2, 84.8, 85.5, 88]
        self.assertIsNone(detect_cwh(make_candles(bad)))

    def test_rhs_and_cwh_are_mutually_exclusive_on_the_same_chart(self):
        # KB Section 3.6 flag 3 (disambiguation): deepest trough FIRST ->
        # cup-with-handle; deepest trough LAST -> head-and-shoulders. Each
        # detector must reject the other's shape.
        rhs_candles = make_candles(PRIOR_DECLINE + RHS_SHAPED)
        cwh_candles = make_candles(PRIOR_DECLINE + CWH_PATTERN)
        self.assertIsNone(detect_cwh(rhs_candles))
        self.assertIsNotNone(detect_rhs(rhs_candles))
        self.assertIsNone(detect_rhs(cwh_candles))
        self.assertIsNotNone(detect_cwh(cwh_candles))

    def test_breakout_at_or_above_neckline_is_not_an_entry(self):
        # Same live-data regression as RHS: an old cup-and-handle neckline
        # must not match a base breakout happening far above it years later
        # (that produced a CWH target BELOW the current price on TITAN).
        stale = PRIOR_DECLINE + CWH_PATTERN[:-5] + [
            110, 150, 210, 300, 390, 400, 401, 400.5, 401.5, 410,
        ]
        self.assertIsNone(detect_cwh(make_candles(stale)))

    def test_strategy_refuses_to_run_outside_v40_and_v40next(self):
        for forbidden in (Universe.V200, Universe.UNCLASSIFIED):
            signals = evaluate(self.strategy, PRIOR_DECLINE + CWH_PATTERN,
                               universe=forbidden)
            self.assertEqual(signals, [], f"must not fire on {forbidden}")


class TestCWHSell(unittest.TestCase):
    def test_sell_fires_at_technical_target(self):
        strategy = CWHStrategy()
        existing = Signal(
            symbol="TESTCO", strategy_name=CWHStrategy.name,
            universe_at_signal_time=Universe.V40, action="BUY",
            trigger_date=dt.date(2020, 1, 5), signal_price=95.0,
            target_price=120.0,
        )
        signals = evaluate(strategy, [110, 112, 114, 116, 118, 121],
                           open_trades=[existing])
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].action, "SELL")
        self.assertTrue(signals[0].requires_human_confirmation)


if __name__ == "__main__":
    unittest.main()
