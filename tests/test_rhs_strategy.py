"""
Tests for the Reverse Head & Shoulder Strategy (Section 3.1).

Pattern series are built from close paths (each candle opens at the prior
close), engineered so pivot/neckline/base detection has exactly one clean
candidate per test. The stated depths mirror the KB geometry: horizontal
neckline at 100, shoulders shallower than the head, base + green breakout
in the right shoulder.
"""

import datetime as dt
import unittest

from sunabha_agent.data.models import Candle, PriceSeries, Signal, Universe
from sunabha_agent.strategies.rhs_strategy import RHSStrategy, detect_rhs

PRIOR_DECLINE = [150, 140, 130, 120, 110, 102, 96, 98]
# neckline 100 | LS to 90 | head to 80 | RS to 92 | base ~92.5-93.2 | green breakout 95
RHS_PATTERN = [100, 97, 93, 90, 93, 97, 100, 95, 88, 80, 86, 94, 100,
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


class TestRHSBuy(unittest.TestCase):
    def setUp(self):
        self.strategy = RHSStrategy()

    def test_buy_fires_on_right_shoulder_base_breakout(self):
        signals = evaluate(self.strategy, PRIOR_DECLINE + RHS_PATTERN)
        self.assertEqual(len(signals), 1)
        s = signals[0]
        self.assertEqual(s.action, "BUY")
        self.assertEqual(s.suggested_position_pct, 3.0)
        # Section 3.6 flag 1: pattern candidates are NEVER auto-executed
        self.assertTrue(s.requires_human_confirmation)
        self.assertFalse(s.metadata["is_complex"])
        self.assertAlmostEqual(s.metadata["neckline"], 100.0)
        self.assertAlmostEqual(s.metadata["head_low"], 80.0)

    def test_target_is_higher_of_technical_target_and_lifetime_high(self):
        # Section 3.1: tech target = 100 + (100-80) = 120, but lifetime high
        # is 150 (from the prior decline) -> the sell target must be 150.
        signals = evaluate(self.strategy, PRIOR_DECLINE + RHS_PATTERN)
        self.assertAlmostEqual(signals[0].metadata["technical_target"], 120.0)
        self.assertAlmostEqual(signals[0].target_price, 150.0)

    def test_complex_pattern_flagged_when_multiple_left_shoulders(self):
        # Two left shoulders (90 and 88), then the head at 80 - a "Complex
        # RHS", called out as MORE reliable (Section 3.1 rule 3).
        complex_pattern = [100, 97, 93, 90, 93, 97, 100, 96, 92, 88, 92, 96, 100,
                           95, 88, 80, 86, 94, 100,
                           96, 92, 92.5, 93, 92.6, 93.2, 95]
        signals = evaluate(self.strategy, PRIOR_DECLINE + complex_pattern)
        self.assertEqual(len(signals), 1)
        self.assertTrue(signals[0].metadata["is_complex"])

    def test_sloped_neckline_is_rejected(self):
        # Section 3.1 rule 2: connecting points at 100/104/108 are NOT a
        # horizontal neckline - the instructor explicitly rejects sloped
        # necklines, contradicting textbook teaching.
        sloped = [96, 98, 100, 97, 93, 90, 93, 99, 104, 100, 92, 84, 90, 100, 108,
                  103, 99, 99.5, 100, 99.6, 100.2, 103]
        self.assertIsNone(detect_rhs(make_candles(sloped)))

    def test_no_signal_without_green_breakout_candle(self):
        # Same pattern but the final candle closes red - Section 3.1 buy
        # rule (c)/(d): the breakout must be a GREEN candle on a closing basis.
        red_ending = PRIOR_DECLINE + RHS_PATTERN[:-1] + [92.0]
        signals = evaluate(self.strategy, red_ending)
        self.assertEqual(signals, [])

    def test_shoulder_deeper_than_head_is_rejected(self):
        # Section 3.1 rule 4: the head must be the deepest point. Left
        # shoulder at 75 is deeper than the "head" at 80 -> invalid.
        bad = [100, 97, 88, 75, 88, 97, 100, 95, 88, 80, 86, 94, 100,
               96, 92, 92.5, 93, 92.6, 93.2, 95]
        self.assertIsNone(detect_rhs(make_candles(PRIOR_DECLINE + bad)))

    def test_hard_40pct_gain_required_when_neckline_at_lifetime_high(self):
        # No prior decline: the neckline (100) IS the lifetime high. With a
        # head at 80 the potential gain is only ~26% -> hard-rejected
        # (Section 3.1 Q&A: 40% becomes mandatory at the lifetime high).
        at_high = [96, 98] + RHS_PATTERN
        self.assertEqual(evaluate(self.strategy, at_high), [])

        # Same situation but a much deeper head (55): tech target 145,
        # gain ~53% >= 40% -> allowed.
        deep_head = [96, 98, 100, 97, 93, 90, 93, 97, 100,
                     95, 88, 78, 66, 55, 68, 82, 94, 100,
                     96, 92, 92.5, 93, 92.6, 93.2, 95]
        signals = evaluate(self.strategy, deep_head)
        self.assertEqual(len(signals), 1)
        self.assertTrue(signals[0].metadata["neckline_at_lifetime_high"])
        self.assertAlmostEqual(signals[0].target_price, 145.0)

    def test_breakout_at_or_above_neckline_is_not_an_entry(self):
        # Section 3.1: the buy is the right shoulder's base breakout BEFORE
        # price reaches the neckline. Found live on full listing histories:
        # without this check a years-old neckline (TITAN's 1201) matched a
        # base breakout at today's far-higher price (4404), producing a
        # "candidate" with a negative gain to target. A stale pattern far
        # below today's price must yield nothing.
        stale = PRIOR_DECLINE + RHS_PATTERN[:-5] + [
            110, 150, 210, 300, 390, 400, 401, 400.5, 401.5, 410,
        ]  # huge rally after the old pattern, then a base + green breakout at 410
        self.assertIsNone(detect_rhs(make_candles(stale)))

    def test_strategy_refuses_to_run_outside_v40_and_v40next(self):
        for forbidden in (Universe.V200, Universe.UNCLASSIFIED):
            signals = evaluate(self.strategy, PRIOR_DECLINE + RHS_PATTERN,
                               universe=forbidden)
            self.assertEqual(signals, [], f"must not fire on {forbidden}")

    def test_no_second_buy_while_trade_open(self):
        # Max 1 RHS trade per stock - averaging is Strategy 6 (V10), not RHS.
        existing = Signal(
            symbol="TESTCO", strategy_name=RHSStrategy.name,
            universe_at_signal_time=Universe.V40, action="BUY",
            trigger_date=dt.date(2020, 1, 5), signal_price=95.0,
            target_price=999.0,
        )
        signals = evaluate(self.strategy, PRIOR_DECLINE + RHS_PATTERN,
                           open_trades=[existing])
        self.assertEqual(signals, [])


class TestRHSSell(unittest.TestCase):
    def test_sell_fires_when_target_reached_without_redetecting_pattern(self):
        # By the time price reaches the target the pattern is long gone -
        # the exit must key off the target fixed at entry, nothing else.
        strategy = RHSStrategy()
        existing = Signal(
            symbol="TESTCO", strategy_name=RHSStrategy.name,
            universe_at_signal_time=Universe.V40, action="BUY",
            trigger_date=dt.date(2020, 1, 5), signal_price=95.0,
            target_price=150.0,
        )
        signals = evaluate(strategy, [140, 142, 144, 146, 148, 151],
                           open_trades=[existing])
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].action, "SELL")
        self.assertTrue(signals[0].requires_human_confirmation)


if __name__ == "__main__":
    unittest.main()
