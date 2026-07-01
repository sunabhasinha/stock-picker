"""
Tests for the SMA Strategy (Section 2.2).

We build synthetic candle series engineered to land SMA(200)/SMA(50)/SMA(20)
in specific orderings relative to Close, rather than testing against messy
real data - that way each test isolates exactly one condition from the
buy/sell rule.
"""

import datetime as dt
import unittest

from sunabha_agent.data.models import Candle, PriceSeries, Universe
from sunabha_agent.strategies.sma_strategy import SMAStrategy, simple_moving_average


def flat_candles(price: float, n: int, start: dt.date = dt.date(2020, 1, 1)) -> list[Candle]:
    """n identical flat candles - useful as a base before splicing in a tail
    that creates the SMA ordering we want to test."""
    return [
        Candle(date=start + dt.timedelta(days=i), open=price, high=price, low=price, close=price)
        for i in range(n)
    ]


class TestSimpleMovingAverage(unittest.TestCase):
    def test_returns_none_when_insufficient_history(self):
        self.assertIsNone(simple_moving_average([1, 2, 3], period=200))

    def test_plain_average_not_exponential(self):
        closes = [10.0] * 19 + [30.0]  # 20 values: nineteen 10s and one 30
        result = simple_moving_average(closes, period=20)
        expected = (19 * 10.0 + 30.0) / 20
        self.assertAlmostEqual(result, expected)


class TestSMAStrategyBuySignal(unittest.TestCase):
    def setUp(self):
        self.strategy = SMAStrategy()

    def test_buy_fires_when_200_above_50_above_20_above_close(self):
        # Engineer a falling-price series: long flat history at 100, then a
        # sharp recent drop, so SMA(200) > SMA(50) > SMA(20) > current close.
        candles = flat_candles(100.0, 200)
        # Now append a declining tail so the short averages pull below the long one.
        last_date = candles[-1].date
        decline_prices = [90, 80, 70, 60, 50, 40, 30, 20, 10, 5]
        for i, p in enumerate(decline_prices, start=1):
            candles.append(
                Candle(date=last_date + dt.timedelta(days=i), open=p, high=p, low=p, close=p)
            )
        prices = PriceSeries(symbol="TESTCO", candles=candles)

        signals = self.strategy.evaluate(
            prices=prices,
            fundamentals=None,
            universe=Universe.V40,
            open_trades_on_this_stock=[],
        )

        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].action, "BUY")
        self.assertEqual(signals[0].symbol, "TESTCO")

    def test_no_buy_signal_when_not_enough_history(self):
        candles = flat_candles(100.0, 50)  # well under 200 days
        prices = PriceSeries(symbol="TESTCO", candles=candles)
        signals = self.strategy.evaluate(
            prices=prices, fundamentals=None, universe=Universe.V40, open_trades_on_this_stock=[]
        )
        self.assertEqual(signals, [])

    def test_strategy_refuses_to_run_outside_v40(self):
        # Section 2.2: SMA strategy is V40-ONLY - must not fire on V40_NEXT or V200
        candles = flat_candles(100.0, 200)
        last_date = candles[-1].date
        for i, p in enumerate([90, 80, 70, 60, 50, 40, 30, 20, 10, 5], start=1):
            candles.append(
                Candle(date=last_date + dt.timedelta(days=i), open=p, high=p, low=p, close=p)
            )
        prices = PriceSeries(symbol="TESTCO", candles=candles)

        for forbidden_universe in (Universe.V40_NEXT, Universe.V200, Universe.UNCLASSIFIED):
            signals = self.strategy.evaluate(
                prices=prices,
                fundamentals=None,
                universe=forbidden_universe,
                open_trades_on_this_stock=[],
            )
            self.assertEqual(
                signals, [], f"SMA strategy must not fire on {forbidden_universe}"
            )

    def test_no_averaging_second_buy_blocked_if_already_holding(self):
        from sunabha_agent.data.models import Signal

        candles = flat_candles(100.0, 200)
        last_date = candles[-1].date
        for i, p in enumerate([90, 80, 70, 60, 50, 40, 30, 20, 10, 5], start=1):
            candles.append(
                Candle(date=last_date + dt.timedelta(days=i), open=p, high=p, low=p, close=p)
            )
        prices = PriceSeries(symbol="TESTCO", candles=candles)

        existing_trade = Signal(
            symbol="TESTCO",
            strategy_name="SMA Strategy",
            universe_at_signal_time=Universe.V40,
            action="BUY",
            trigger_date=dt.date(2020, 1, 1),
            signal_price=95.0,
        )

        signals = self.strategy.evaluate(
            prices=prices,
            fundamentals=None,
            universe=Universe.V40,
            open_trades_on_this_stock=[existing_trade],
        )
        # Section 2.2: "no averaging - only one trade per stock under this strategy"
        self.assertEqual(signals, [])


if __name__ == "__main__":
    unittest.main()
