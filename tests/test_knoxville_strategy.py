"""
Tests for the Knoxville Divergence Strategy (Section 2.3).

The divergence definition itself is replicated from the two open-source
ports of Rob Booker's indicator cited in the strategy module docstring
(momentum turning while price still extends, confirmed by an RSI extreme
inside the lookback window). The synthetic series below are engineered to
hit or miss exactly one leg of that definition at a time.
"""

import datetime as dt
import unittest

from sunabha_agent.data.models import Candle, PriceSeries, Signal, Universe
from sunabha_agent.strategies.knoxville_strategy import (
    KD_AVERAGING_MIN_GAP_PCT,
    KnoxvilleStrategy,
    detect_knoxville_divergence,
    ratio_momentum,
    wilder_rsi,
)


def flat_candle(day: dt.date, price: float) -> Candle:
    return Candle(date=day, open=price, high=price, low=price, close=price)


def build_series(daily_pct_changes: list[float], start_price: float = 100.0) -> list[Candle]:
    """One flat OHLC candle per entry; each entry is that day's % change."""
    candles = []
    price = start_price
    day = dt.date(2020, 1, 1)
    for i, pct in enumerate(daily_pct_changes):
        price = price * (1 + pct / 100)
        candles.append(flat_candle(day + dt.timedelta(days=i), price))
    return candles


def bullish_divergence_series() -> list[Candle]:
    """
    Flat warmup, then a STEEP decline, then a GENTLE decline that still
    makes marginal new lows every day. On the final bar: price is at its
    lowest (new low), still below every earlier close, RSI is deeply
    oversold from the long decline, but 20-bar momentum has risen versus
    the steep phase because the fall decelerated - the exact bullish
    Knoxville setup ("downtrend line end point").
    """
    return build_series([0.0] * 40 + [-2.0] * 30 + [-0.05] * 10)


def bearish_divergence_series() -> list[Candle]:
    """Exact mirror: steep rally, then a decelerating grind to marginal new
    highs - momentum falling while price still rises, RSI overbought."""
    return build_series([0.0] * 40 + [2.0] * 30 + [0.05] * 10)


def open_trade(entry_price: float, action: str = "BUY") -> Signal:
    return Signal(
        symbol="TESTCO",
        strategy_name="Knoxville Divergence Strategy",
        universe_at_signal_time=Universe.V40,
        action=action,
        trigger_date=dt.date(2020, 1, 15),
        signal_price=entry_price,
    )


class TestIndicatorMath(unittest.TestCase):
    def test_rsi_is_100_on_pure_uptrend_and_0_on_pure_downtrend(self):
        rising = [100.0 + i for i in range(30)]
        falling = [100.0 - i for i in range(30)]
        self.assertAlmostEqual(wilder_rsi(rising)[-1], 100.0)
        self.assertAlmostEqual(wilder_rsi(falling)[-1], 0.0)

    def test_rsi_none_during_warmup(self):
        closes = [100.0 + i for i in range(30)]
        rsi = wilder_rsi(closes, period=14)
        self.assertIsNone(rsi[13])
        self.assertIsNotNone(rsi[14])

    def test_momentum_is_ratio_form_not_difference(self):
        # The reference implementations (MQL4 iMomentum / cTrader
        # MomentumOscillator) both use close/close[n]*100.
        closes = [100.0] * 20 + [110.0]
        mom = ratio_momentum(closes, period=20)
        self.assertAlmostEqual(mom[-1], 110.0)
        self.assertIsNone(mom[19])


class TestDivergenceDetection(unittest.TestCase):
    def test_bullish_divergence_detected_on_decelerating_decline(self):
        result = detect_knoxville_divergence(bullish_divergence_series())
        self.assertIsNotNone(result)
        self.assertEqual(result.kind, "BULLISH")
        # The oversold confirmation must be genuinely oversold
        self.assertLessEqual(result.rsi_extreme, 30.0)

    def test_bearish_divergence_detected_on_decelerating_rally(self):
        result = detect_knoxville_divergence(bearish_divergence_series())
        self.assertIsNotNone(result)
        self.assertEqual(result.kind, "BEARISH")
        self.assertGreaterEqual(result.rsi_extreme, 70.0)

    def test_no_divergence_on_flat_series(self):
        self.assertIsNone(detect_knoxville_divergence(build_series([0.0] * 100)))

    def test_no_bullish_signal_on_bounce_day(self):
        # Section 2.3: the line's end point is a price attempting to reverse
        # FROM a low - a day that already bounced (higher low than yesterday)
        # is not at the window low, so no divergence may fire.
        candles = bullish_divergence_series()
        last = candles[-1]
        bounce_price = last.close * 1.01
        candles.append(flat_candle(last.date + dt.timedelta(days=1), bounce_price))
        self.assertIsNone(detect_knoxville_divergence(candles))

    def test_insufficient_history_returns_none_not_error(self):
        # Base-class contract: missing data must never raise.
        self.assertIsNone(detect_knoxville_divergence(build_series([-2.0] * 10)))
        self.assertIsNone(detect_knoxville_divergence([]))


class TestKnoxvilleBuyAndAveraging(unittest.TestCase):
    def setUp(self):
        self.strategy = KnoxvilleStrategy()
        self.prices = PriceSeries(symbol="TESTCO", candles=bullish_divergence_series())
        self.close = self.prices.latest.close

    def test_buy_fires_on_bullish_divergence(self):
        signals = self.strategy.evaluate(
            prices=self.prices,
            fundamentals=None,
            universe=Universe.V40,
            open_trades_on_this_stock=[],
        )
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].action, "BUY")
        # Section 2.3: 3% of portfolio per trade
        self.assertEqual(signals[0].suggested_position_pct, 3.0)
        # Exit is an event (next uptrend end point), not a knowable price
        self.assertIsNone(signals[0].target_price)

    def test_strategy_refuses_to_run_outside_v40(self):
        # Section 2.3: Knoxville is V40 ONLY, same restriction as SMA
        for forbidden in (Universe.V40_NEXT, Universe.V200, Universe.UNCLASSIFIED):
            signals = self.strategy.evaluate(
                prices=self.prices,
                fundamentals=None,
                universe=forbidden,
                open_trades_on_this_stock=[],
            )
            self.assertEqual(signals, [], f"must not fire on {forbidden}")

    def test_averaging_blocked_when_gap_under_5_percent(self):
        # Entry chosen so today's close is only ~4% below it - Section 2.3
        # requires >= 5%, and cites a real ~2.25% case that was NOT averaged.
        entry = self.close / 0.96
        signals = self.strategy.evaluate(
            prices=self.prices,
            fundamentals=None,
            universe=Universe.V40,
            open_trades_on_this_stock=[open_trade(entry)],
        )
        self.assertEqual(signals, [])

    def test_averaging_allowed_at_or_beyond_5_percent_gap(self):
        entry = self.close / 0.90  # close is 10% below entry
        signals = self.strategy.evaluate(
            prices=self.prices,
            fundamentals=None,
            universe=Universe.V40,
            open_trades_on_this_stock=[open_trade(entry)],
        )
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].action, "AVERAGE")
        self.assertEqual(signals[0].suggested_position_pct, 3.0)

    def test_gap_is_measured_from_first_entry_not_latest(self):
        # Section 2.3 / consolidated pseudocode: the 5% gap is against the
        # FIRST trade's entry price.
        gap_fraction = 1 - KD_AVERAGING_MIN_GAP_PCT / 100
        first_entry = self.close / (gap_fraction * 0.99)  # close IS >5% below this
        self.assertLess(self.close, first_entry * gap_fraction)
        signals = self.strategy.evaluate(
            prices=self.prices,
            fundamentals=None,
            universe=Universe.V40,
            open_trades_on_this_stock=[open_trade(first_entry)],
        )
        self.assertEqual([s.action for s in signals], ["AVERAGE"])

    def test_no_third_trade_even_with_huge_gap(self):
        # Max 2 concurrent trades per stock (1 initial + 1 average)
        signals = self.strategy.evaluate(
            prices=self.prices,
            fundamentals=None,
            universe=Universe.V40,
            open_trades_on_this_stock=[
                open_trade(self.close * 4),
                open_trade(self.close * 2, action="AVERAGE"),
            ],
        )
        self.assertEqual(signals, [])


class TestKnoxvilleSell(unittest.TestCase):
    def setUp(self):
        self.strategy = KnoxvilleStrategy()
        self.prices = PriceSeries(symbol="TESTCO", candles=bearish_divergence_series())

    def test_sell_fires_on_first_uptrend_endpoint_and_closes_everything(self):
        # Section 2.3: both the original and averaged trade share the same
        # exit - the first uptrend line end point after entry.
        signals = self.strategy.evaluate(
            prices=self.prices,
            fundamentals=None,
            universe=Universe.V40,
            open_trades_on_this_stock=[
                open_trade(50.0),
                open_trade(45.0, action="AVERAGE"),
            ],
        )
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].action, "SELL")
        self.assertTrue(signals[0].metadata["closes_all_open_trades"])

    def test_bearish_divergence_without_open_position_is_ignored(self):
        signals = self.strategy.evaluate(
            prices=self.prices,
            fundamentals=None,
            universe=Universe.V40,
            open_trades_on_this_stock=[],
        )
        self.assertEqual(signals, [])


class TestCourseInvariants(unittest.TestCase):
    def test_no_stop_loss_and_allocation_ceiling(self):
        # Foundational course rule: no stop-loss, ever. Allocation ceiling
        # is 6% (3% + 3% averaged) per Section 2.3.
        strategy = KnoxvilleStrategy()
        self.assertFalse(strategy.uses_stop_loss)
        self.assertEqual(strategy.max_allocation_pct_per_stock, 6.0)
        self.assertEqual(strategy.max_concurrent_trades_per_stock, 2)


if __name__ == "__main__":
    unittest.main()
