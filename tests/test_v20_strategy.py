"""
Tests for the V20 Strategy (Section 2.4) - the framework's trickiest
strategy to get right because of the "single-use range" rule (a range can
NEVER be reused after one full buy-sell cycle, even at the identical price)
and the 10%-averaging-gap rule.
"""

import datetime as dt
import unittest

from sunabha_agent.data.models import Candle, PriceSeries, Signal, Universe
from sunabha_agent.strategies.v20_strategy import V20Strategy, find_qualifying_ranges

D0 = dt.date(2020, 1, 1)


def candle(i: int, o: float, h: float, l: float, c: float) -> Candle:
    return Candle(date=D0 + dt.timedelta(days=i), open=o, high=h, low=l, close=c)


class TestFindQualifyingRanges(unittest.TestCase):
    def test_single_green_candle_with_20pct_move_qualifies(self):
        candles = [candle(0, 100, 121, 100, 120)]  # 21% move bottom to top
        ranges = find_qualifying_ranges(candles)
        self.assertEqual(len(ranges), 1)
        self.assertAlmostEqual(ranges[0].lower_line, 100)
        self.assertAlmostEqual(ranges[0].upper_line, 121)

    def test_green_run_under_20pct_does_not_qualify(self):
        candles = [candle(0, 100, 110, 100, 108)]  # 10% move
        ranges = find_qualifying_ranges(candles)
        self.assertEqual(ranges, [])

    def test_red_candle_in_middle_voids_the_run(self):
        # Two big green moves separated by one red candle - per Section 2.4,
        # a red candle in between voids the WHOLE run, it doesn't just
        # split it into two still-valid sub-runs that happen to also qualify.
        candles = [
            candle(0, 100, 115, 100, 114),  # green, +14%
            candle(1, 114, 113, 108, 109),  # RED - voids the run so far
            candle(2, 109, 130, 109, 129),  # green again, starts a NEW run
        ]
        ranges = find_qualifying_ranges(candles)
        # First green candle alone is only 14% - doesn't qualify on its own.
        # Third candle alone: (130-109)/109 = ~19.3% - also doesn't quite qualify alone.
        self.assertEqual(ranges, [])

    def test_multi_candle_green_run_measures_bottom_of_lowest_to_top_of_highest(self):
        # Per Section 2.4: top doesn't have to be the LAST candle in the run.
        candles = [
            candle(0, 100, 110, 100, 108),
            candle(1, 108, 135, 107, 130),  # this candle has the highest high
            candle(2, 130, 132, 125, 128),  # still green, lower high than candle 1
        ]
        ranges = find_qualifying_ranges(candles)
        self.assertEqual(len(ranges), 1)
        self.assertAlmostEqual(ranges[0].lower_line, 100)
        self.assertAlmostEqual(ranges[0].upper_line, 135)


class TestV20StrategySignals(unittest.TestCase):
    def setUp(self):
        self.strategy = V20Strategy()

    def _make_qualifying_range_then_pullback(self, pullback_to: float) -> PriceSeries:
        candles = [
            candle(0, 100, 100, 100, 100),
            candle(1, 100, 125, 100, 124),  # 25% green run -> range [100, 125]
            candle(2, 124, 124, pullback_to, pullback_to),  # pulls back to lower line
        ]
        return PriceSeries(symbol="TESTCO", candles=candles)

    def test_buy_fires_when_price_touches_lower_line(self):
        prices = self._make_qualifying_range_then_pullback(pullback_to=100.0)
        signals = self.strategy.evaluate(
            prices=prices, fundamentals=None, universe=Universe.V40, open_trades_on_this_stock=[]
        )
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].action, "BUY")
        self.assertAlmostEqual(signals[0].signal_price, 100.0)
        self.assertAlmostEqual(signals[0].target_price, 125.0)

    def test_no_buy_if_price_has_not_reached_lower_line(self):
        prices = self._make_qualifying_range_then_pullback(pullback_to=110.0)  # above lower line
        signals = self.strategy.evaluate(
            prices=prices, fundamentals=None, universe=Universe.V40, open_trades_on_this_stock=[]
        )
        self.assertEqual(signals, [])

    def test_sell_fires_when_price_reaches_upper_line_of_tagged_range(self):
        candles = [
            candle(0, 100, 100, 100, 100),
            candle(1, 100, 125, 100, 124),
            candle(2, 124, 124, 100, 100),  # pullback - this is where we'd have bought
            candle(3, 100, 126, 100, 125),  # price recovers to upper line
        ]
        prices = PriceSeries(symbol="TESTCO", candles=candles)
        existing_buy = Signal(
            symbol="TESTCO",
            strategy_name="V20 Strategy",
            universe_at_signal_time=Universe.V40,
            action="BUY",
            trigger_date=D0 + dt.timedelta(days=2),
            signal_price=100.0,
            target_price=125.0,
            metadata={"range_lower": 100.0, "range_upper": 125.0},
        )
        signals = self.strategy.evaluate(
            prices=prices,
            fundamentals=None,
            universe=Universe.V40,
            open_trades_on_this_stock=[existing_buy],
        )
        sell_signals = [s for s in signals if s.action == "SELL"]
        self.assertEqual(len(sell_signals), 1)

    def test_sell_fires_even_when_no_range_is_detectable_in_history(self):
        # Regression: an open trade must ALWAYS be able to exit. The sell
        # keys off the range levels tagged on the trade at entry time - it
        # must not depend on the originating range still being detectable
        # in the loaded candles (e.g. truncated history, or the green run
        # predates the data window).
        candles = [
            candle(0, 100, 100, 100, 100),  # flat: no qualifying range anywhere
            candle(1, 100, 100, 100, 100),
            candle(2, 100, 126, 100, 125),  # price reaches the tagged upper line
        ]
        prices = PriceSeries(symbol="TESTCO", candles=candles)
        existing_buy = Signal(
            symbol="TESTCO",
            strategy_name="V20 Strategy",
            universe_at_signal_time=Universe.V40,
            action="BUY",
            trigger_date=D0,
            signal_price=100.0,
            target_price=125.0,
            metadata={"range_lower": 100.0, "range_upper": 125.0},
        )
        signals = self.strategy.evaluate(
            prices=prices,
            fundamentals=None,
            universe=Universe.V40,
            open_trades_on_this_stock=[existing_buy],
        )
        self.assertEqual([s.action for s in signals], ["SELL"])

    def test_averaging_requires_at_least_10pct_gap_below_first_entry(self):
        # First entry at 100. A second range whose lower line is only 5%
        # below (95) must NOT trigger an average - needs >=10% gap, i.e. <=90.
        candles = [
            candle(0, 100, 100, 100, 100),
            candle(1, 100, 125, 100, 124),  # range A: [100, 125]
            candle(2, 124, 124, 100, 100),  # pulls back to 100 -> first BUY
            candle(3, 100, 122, 100, 120),  # range B forms: needs to qualify
            # (120-95)/95 = 26% qualifying green run ending with a pullback to 95
            candle(4, 120, 120, 95, 95),  # pulls back to 95 - only 5% below first entry
        ]
        prices = PriceSeries(symbol="TESTCO", candles=candles)
        first_buy = Signal(
            symbol="TESTCO",
            strategy_name="V20 Strategy",
            universe_at_signal_time=Universe.V40,
            action="BUY",
            trigger_date=D0 + dt.timedelta(days=2),
            signal_price=100.0,
            metadata={"range_lower": 100.0, "range_upper": 125.0},
        )
        signals = self.strategy.evaluate(
            prices=prices,
            fundamentals=None,
            universe=Universe.V40,
            open_trades_on_this_stock=[first_buy],
        )
        buy_or_average = [s for s in signals if s.action in ("BUY", "AVERAGE")]
        self.assertEqual(
            buy_or_average,
            [],
            "Should not average when the new range's lower line is only 5% below "
            "the first entry - Section 2.4 requires >=10%.",
        )

    def test_max_three_concurrent_trades_enforced(self):
        # Section 2.4: max 3 concurrent trades per stock under V20.
        existing_trades = [
            Signal(
                symbol="TESTCO",
                strategy_name="V20 Strategy",
                universe_at_signal_time=Universe.V40,
                action="BUY",
                trigger_date=D0,
                signal_price=100.0,
                metadata={"range_lower": 100.0, "range_upper": 130.0},
            ),
            Signal(
                symbol="TESTCO",
                strategy_name="V20 Strategy",
                universe_at_signal_time=Universe.V40,
                action="AVERAGE",
                trigger_date=D0,
                signal_price=85.0,
                metadata={"range_lower": 85.0, "range_upper": 130.0},
            ),
            Signal(
                symbol="TESTCO",
                strategy_name="V20 Strategy",
                universe_at_signal_time=Universe.V40,
                action="AVERAGE",
                trigger_date=D0,
                signal_price=70.0,
                metadata={"range_lower": 70.0, "range_upper": 130.0},
            ),
        ]
        candles = [
            candle(0, 100, 100, 100, 100),
            candle(1, 100, 161, 100, 160),  # huge qualifying range
            candle(2, 160, 160, 50, 50),  # would otherwise trigger a 4th entry
        ]
        prices = PriceSeries(symbol="TESTCO", candles=candles)
        signals = self.strategy.evaluate(
            prices=prices,
            fundamentals=None,
            universe=Universe.V40,
            open_trades_on_this_stock=existing_trades,
        )
        new_entries = [s for s in signals if s.action in ("BUY", "AVERAGE")]
        self.assertEqual(new_entries, [], "Must not exceed 3 concurrent V20 trades on one stock")


if __name__ == "__main__":
    unittest.main()
