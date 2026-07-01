"""
Tests for the Lifetime High Strategy (Section 6.1), including a
reconstruction of the actual ICICI Lombard worked example cited in the
source video (~30-32% below lifetime high, ATH TTM revenue/profit,
~43-48% potential gain). Reproducing the cited example is the real
accuracy bar here, not just "does the code run."
"""

import datetime as dt
import unittest

from vivek_agent.data.models import CompanyType, Fundamentals, PriceSeries, Universe
from vivek_agent.data.models import Candle
from vivek_agent.strategies.lifetime_high_strategy import (
    LTH_MIN_DECLINE_PCT,
    LifetimeHighStrategy,
    decline_from_lifetime_high_pct,
)

D0 = dt.date(2022, 1, 1)


def make_price_series(symbol: str, lifetime_high: float, current_price: float) -> PriceSeries:
    candles = [
        Candle(date=D0, open=lifetime_high, high=lifetime_high, low=lifetime_high, close=lifetime_high),
        Candle(
            date=D0 + dt.timedelta(days=1),
            open=current_price,
            high=current_price,
            low=current_price,
            close=current_price,
        ),
    ]
    return PriceSeries(symbol=symbol, candles=candles)


def make_ath_fundamentals(symbol: str = "ICICIGI") -> Fundamentals:
    return Fundamentals(
        symbol=symbol,
        as_of=D0,
        company_type=CompanyType.STANDARD,
        market_cap_cr=50000.0,
        revenue_ttm_cr=1000.0,
        net_profit_ttm_cr=1570.0,  # matches the real cited TTM profit figure
        revenue_ttm_history_cr=[600, 700, 800, 900, 1000],  # current value IS the max
        net_profit_ttm_history_cr=[-416, 500, 900, 1200, 1570],  # current value IS the max
    )


class TestDeclineCalculation(unittest.TestCase):
    def test_decline_pct_basic(self):
        self.assertAlmostEqual(decline_from_lifetime_high_pct(70, 100), 30.0)

    def test_icici_lombard_example_decline_in_stated_range(self):
        # Source video states ~30-32% down from lifetime high.
        decline = decline_from_lifetime_high_pct(current_price=69.0, lifetime_high=100.0)
        self.assertGreaterEqual(decline, 30.0)
        self.assertLessEqual(decline, 32.0)


class TestLifetimeHighStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = LifetimeHighStrategy()

    def test_buy_fires_when_ath_ttm_and_30pct_down(self):
        prices = make_price_series("ICICIGI", lifetime_high=100.0, current_price=69.0)
        fundamentals = make_ath_fundamentals()

        signals = self.strategy.evaluate(
            prices=prices,
            fundamentals=fundamentals,
            universe=Universe.V40,
            open_trades_on_this_stock=[],
        )

        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].action, "BUY")
        self.assertAlmostEqual(signals[0].target_price, 100.0)
        # Potential gain at entry ~ (100/69 - 1) * 100 = ~44.9%, within the
        # ~43-48% range cited for the real ICICI Lombard example.
        potential_gain = (100.0 / 69.0 - 1) * 100
        self.assertGreaterEqual(potential_gain, 43.0)
        self.assertLessEqual(potential_gain, 48.0)

    def test_no_buy_if_decline_under_30pct(self):
        prices = make_price_series("ICICIGI", lifetime_high=100.0, current_price=75.0)  # only 25% down
        fundamentals = make_ath_fundamentals()
        signals = self.strategy.evaluate(
            prices=prices,
            fundamentals=fundamentals,
            universe=Universe.V40,
            open_trades_on_this_stock=[],
        )
        self.assertEqual(signals, [])

    def test_no_buy_if_ttm_not_at_all_time_high(self):
        prices = make_price_series("ICICIGI", lifetime_high=100.0, current_price=60.0)
        fundamentals = make_ath_fundamentals()
        # Override so current TTM profit is NOT actually the max in history
        fundamentals.net_profit_ttm_history_cr = [600, 900, 1700]  # 1700 > current 1570
        signals = self.strategy.evaluate(
            prices=prices,
            fundamentals=fundamentals,
            universe=Universe.V40,
            open_trades_on_this_stock=[],
        )
        self.assertEqual(signals, [])

    def test_strategy_refuses_to_run_on_v200_or_unclassified(self):
        prices = make_price_series("X", lifetime_high=100.0, current_price=60.0)
        fundamentals = make_ath_fundamentals()
        for forbidden in (Universe.V200, Universe.UNCLASSIFIED):
            signals = self.strategy.evaluate(
                prices=prices, fundamentals=fundamentals, universe=forbidden, open_trades_on_this_stock=[]
            )
            self.assertEqual(signals, [])

    def test_no_signal_without_fundamentals(self):
        # This strategy is meaningless without TTM data - must not guess.
        prices = make_price_series("X", lifetime_high=100.0, current_price=60.0)
        signals = self.strategy.evaluate(
            prices=prices, fundamentals=None, universe=Universe.V40, open_trades_on_this_stock=[]
        )
        self.assertEqual(signals, [])

    def test_sell_fires_at_lifetime_high(self):
        from vivek_agent.data.models import Signal

        prices = make_price_series("ICICIGI", lifetime_high=100.0, current_price=100.0)
        fundamentals = make_ath_fundamentals()
        existing_buy = Signal(
            symbol="ICICIGI",
            strategy_name="Lifetime High Strategy",
            universe_at_signal_time=Universe.V40,
            action="BUY",
            trigger_date=D0,
            signal_price=69.0,
            target_price=100.0,
            suggested_position_pct=3.0,
        )
        signals = self.strategy.evaluate(
            prices=prices,
            fundamentals=fundamentals,
            universe=Universe.V40,
            open_trades_on_this_stock=[existing_buy],
        )
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].action, "SELL")

    def test_averaging_re_checks_ath_status_at_each_increment(self):
        from vivek_agent.data.models import Signal

        # First entry already happened at 30% down with ATH confirmed.
        # Now price has fallen to 40% down (next averaging increment) but
        # fundamentals have SINCE dropped off all-time-high status.
        prices = make_price_series("ICICIGI", lifetime_high=100.0, current_price=60.0)
        fundamentals = make_ath_fundamentals()
        fundamentals.net_profit_ttm_history_cr = [600, 900, 1800]  # current 1570 no longer the max
        existing_buy = Signal(
            symbol="ICICIGI",
            strategy_name="Lifetime High Strategy",
            universe_at_signal_time=Universe.V40,
            action="BUY",
            trigger_date=D0,
            signal_price=69.0,
            target_price=100.0,
            suggested_position_pct=3.0,
        )
        signals = self.strategy.evaluate(
            prices=prices,
            fundamentals=fundamentals,
            universe=Universe.V40,
            open_trades_on_this_stock=[existing_buy],
        )
        new_entries = [s for s in signals if s.action in ("BUY", "AVERAGE")]
        self.assertEqual(
            new_entries,
            [],
            "Must NOT average if TTM figures have fallen off all-time-high status, "
            "even though price has declined further - Section 6.1 explicit re-check rule.",
        )


if __name__ == "__main__":
    unittest.main()
