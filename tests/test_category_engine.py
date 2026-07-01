"""
Tests for the portfolio Category engine (Sections 6.2/6.3, plus the
Section 4.20 ranking hierarchy).

The engine is the switchboard: exactly one category runs, nothing fires
outside its universe or strategy set, the fundamental gate is applied
before any strategy, and held positions are reconciled via the Section
6.3 logic the course says answers nearly every stock-specific question.
"""

import datetime as dt
import unittest

from sunabha_agent.data.models import Candle, CompanyType, Fundamentals, PriceSeries, Signal, Universe
from sunabha_agent.portfolio.category_engine import (
    CATEGORY_1,
    CATEGORY_2,
    CATEGORY_3,
    CATEGORY_4,
    PRESET_CATEGORIES,
    CategoryEngine,
    ReconciliationAction,
    custom_category,
    shadow_signals,
)
from sunabha_agent.strategies.knoxville_strategy import KnoxvilleStrategy
from sunabha_agent.strategies.sma_strategy import SMAStrategy
from sunabha_agent.strategies.v20_strategy import V20Strategy


def flat_candles(price, n, start=dt.date(2020, 1, 1)):
    return [
        Candle(date=start + dt.timedelta(days=i), open=price, high=price,
               low=price, close=price)
        for i in range(n)
    ]


def sma_buy_series():
    """200 flat days at 100, then a sharp decline: fires the SMA buy
    condition (200>50>20>close) and nothing else."""
    candles = flat_candles(100.0, 200)
    last = candles[-1].date
    for i, p in enumerate([90, 80, 70, 60, 50, 40, 30, 20, 10, 5], start=1):
        candles.append(Candle(date=last + dt.timedelta(days=i), open=p, high=p,
                              low=p, close=p))
    return PriceSeries(symbol="TESTCO", candles=candles)


def make_fundamentals(**overrides):
    defaults = dict(
        symbol="TESTCO",
        as_of=dt.date(2024, 6, 30),
        company_type=CompanyType.STANDARD,
        market_cap_cr=50000.0,
        revenue_ttm_cr=5000.0,
        net_profit_ttm_cr=800.0,
        roce_pct=35.0,
        debt_to_equity=0.05,
        promoter_holding_pct=50.0,
        promoter_pledging_pct_of_holding=0.0,
    )
    defaults.update(overrides)
    return Fundamentals(**defaults)


def make_signal(universe, gain_pct, price=100.0):
    return Signal(
        symbol="TESTCO", strategy_name="X", universe_at_signal_time=universe,
        action="BUY", trigger_date=dt.date(2024, 1, 1), signal_price=price,
        target_price=price * (1 + gain_pct / 100),
    )


def open_trade(strategy_name, entry_price, trigger=dt.date(2024, 1, 5), **metadata):
    return Signal(
        symbol="TESTCO", strategy_name=strategy_name,
        universe_at_signal_time=Universe.V40, action="BUY",
        trigger_date=trigger, signal_price=entry_price, metadata=metadata,
    )


class TestCategoryPresets(unittest.TestCase):
    def test_presets_match_section_6_2_exactly(self):
        self.assertEqual(len(CATEGORY_1.strategy_classes), 1)  # LTH only
        self.assertEqual(len(CATEGORY_2.strategy_classes), 8)  # all 8
        self.assertEqual(CATEGORY_2.universes, (Universe.V40,))
        # Category 3 explicitly EXCLUDES Knoxville, V20, Strategy 7, LTH
        names = {c.__name__ for c in CATEGORY_3.strategy_classes}
        self.assertEqual(names, {"SMAStrategy", "RHSStrategy", "CWHStrategy",
                                 "V10Strategy"})
        self.assertEqual(CATEGORY_4.strategy_classes, (V20Strategy,))
        self.assertEqual(len(CATEGORY_4.universes), 3)  # broadest universe
        self.assertEqual(len(PRESET_CATEGORIES), 4)


class TestSignalGeneration(unittest.TestCase):
    def test_nothing_fires_outside_the_category_universe(self):
        # Category 2 is V40 ONLY (Section 6.2) - a V40_NEXT stock must be
        # silent even though its price series would fire SMA on V40.
        engine = CategoryEngine(CATEGORY_2)
        signals = engine.evaluate_stock(sma_buy_series(), None,
                                        Universe.V40_NEXT, [])
        self.assertEqual(signals, [])

    def test_only_enabled_strategies_run(self):
        prices = sma_buy_series()
        # Category 4 (V20 only): the SMA setup means nothing to it.
        self.assertEqual(
            CategoryEngine(CATEGORY_4).evaluate_stock(prices, None, Universe.V40, []),
            [],
        )
        # Category 2 (all 8): SMA fires, exactly once.
        signals = CategoryEngine(CATEGORY_2).evaluate_stock(prices, None,
                                                            Universe.V40, [])
        self.assertEqual([s.strategy_name for s in signals], [SMAStrategy.name])

    def test_fundamental_gate_blocks_all_signals(self):
        # Section 4.14: the gate is the non-negotiable layer. 50% holding
        # x 30% pledged = 15% of the company pledged >= the 10% disqualifier.
        bad = make_fundamentals(promoter_pledging_pct_of_holding=30.0)
        signals = CategoryEngine(CATEGORY_2).evaluate_stock(
            sma_buy_series(), bad, Universe.V40, []
        )
        self.assertEqual(signals, [])

    def test_soft_flags_ride_along_on_signals(self):
        f = make_fundamentals(under_merger=True)
        signals = CategoryEngine(CATEGORY_2).evaluate_stock(
            sma_buy_series(), f, Universe.V40, []
        )
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].metadata["category"], "category_2")
        self.assertTrue(any("merger" in flag.lower()
                            for flag in signals[0].metadata["screening_soft_flags"]))

    def test_category2_cross_strategy_10pct_gap(self):
        # Section 6.2: a new entry from a DIFFERENT strategy must be >=10%
        # below the preceding trade. SMA close here is 5.0.
        engine = CategoryEngine(CATEGORY_2)
        prices = sma_buy_series()
        # Open Knoxville trade at 5.5: 5.0 is only ~9% below -> blocked.
        blocked = engine.evaluate_stock(
            prices, None, Universe.V40,
            [open_trade(KnoxvilleStrategy.name, 5.5)],
        )
        self.assertEqual(blocked, [])
        # Open Knoxville trade at 10: 5.0 is 50% below -> allowed.
        allowed = engine.evaluate_stock(
            prices, None, Universe.V40,
            [open_trade(KnoxvilleStrategy.name, 10.0)],
        )
        self.assertEqual([s.strategy_name for s in allowed], [SMAStrategy.name])

    def test_v10_sees_all_trades_but_others_see_only_their_own(self):
        # The SMA strategy must NOT be blocked by another strategy's open
        # trade (it gets only its own), while V10 must find its parent CWH
        # trade (it gets everything) - both through the same engine call.
        closes = [190, 200, 150, 120, 100, 105, 110, 115, 120, 116, 112, 108]
        candles, prev = [], closes[0]
        for i, c in enumerate(closes):
            candles.append(Candle(date=dt.date(2020, 1, 1) + dt.timedelta(days=i),
                                  open=prev, high=max(prev, c), low=min(prev, c),
                                  close=c))
            prev = c
        prices = PriceSeries(symbol="TESTCO", candles=candles)
        parent = open_trade("Cup with Handle Strategy", 100.0,
                            trigger=dt.date(2020, 1, 5))
        parent.target_price = 140.0
        signals = CategoryEngine(CATEGORY_3).evaluate_stock(
            prices, None, Universe.V40, [parent]
        )
        self.assertEqual([s.strategy_name for s in signals], ["V10 Strategy"])
        self.assertEqual(signals[0].action, "BUY")


class TestRanking(unittest.TestCase):
    def test_universe_beats_gain(self):
        # Section 4.20 level 1: V40 first, even against a bigger V200 gain.
        v200_big = (make_signal(Universe.V200, 50.0), None)
        v40_small = (make_signal(Universe.V40, 20.0), None)
        ranked = CategoryEngine.rank_candidates([v200_big, v40_small])
        self.assertEqual(ranked[0][0].universe_at_signal_time, Universe.V40)

    def test_higher_gain_wins_within_a_universe(self):
        lo = (make_signal(Universe.V40, 25.0), None)
        hi = (make_signal(Universe.V40, 60.0), None)
        ranked = CategoryEngine.rank_candidates([lo, hi])
        self.assertEqual(ranked[0][0].target_price, 160.0)

    def test_tier_breaks_ties_between_similar_gains(self):
        # 22% vs 24% land in the same 5%-wide similarity bucket, so the
        # ROCE/D-E tier decides: best-tier fundamentals win despite the
        # slightly lower gain (Section 4.20 level 3).
        best = (make_signal(Universe.V40, 22.0),
                make_fundamentals(roce_pct=35.0, debt_to_equity=0.05))
        very_good = (make_signal(Universe.V40, 24.0),
                     make_fundamentals(roce_pct=25.0, debt_to_equity=0.20))
        ranked = CategoryEngine.rank_candidates([very_good, best])
        self.assertAlmostEqual(ranked[0][0].target_price, 122.0)


class TestReconciliation(unittest.TestCase):
    def setUp(self):
        self.engine = CategoryEngine(CATEGORY_4)
        self.flat = PriceSeries(symbol="TESTCO", candles=flat_candles(100.0, 30))

    def test_open_enabled_trade_means_strategy_applies(self):
        rec = self.engine.reconcile_holding(
            self.flat, make_fundamentals(), Universe.V40,
            [open_trade(V20Strategy.name, 90.0, range_upper=999.0)],
            average_cost=90.0,
        )
        self.assertEqual(rec.action, ReconciliationAction.STRATEGY_APPLIES)

    def test_profitable_with_no_strategy_exits(self):
        rec = self.engine.reconcile_holding(
            self.flat, make_fundamentals(), Universe.V40, [], average_cost=50.0
        )
        self.assertEqual(rec.action, ReconciliationAction.EXIT_PROFITABLE)

    def test_at_loss_with_passing_gate_holds(self):
        rec = self.engine.reconcile_holding(
            self.flat, make_fundamentals(), Universe.V40, [], average_cost=150.0
        )
        self.assertEqual(rec.action, ReconciliationAction.HOLD_AWAIT_RECOVERY)

    def test_at_loss_with_failing_gate_flags_for_review(self):
        # Pledging disqualifier now trips: the Section 6.3 'hold and wait'
        # was conditional on passing the gate - surface for review.
        bad = make_fundamentals(promoter_pledging_pct_of_holding=30.0)
        rec = self.engine.reconcile_holding(
            self.flat, bad, Universe.V40, [], average_cost=150.0
        )
        self.assertEqual(rec.action, ReconciliationAction.REVIEW_QUALITY_GATE_FAILED)

    def test_at_loss_without_fundamentals_holds_but_says_gate_unverified(self):
        rec = self.engine.reconcile_holding(
            self.flat, None, Universe.V40, [], average_cost=150.0
        )
        self.assertEqual(rec.action, ReconciliationAction.HOLD_AWAIT_RECOVERY)
        self.assertIn("NOT verified", rec.rationale)


class TestCustomCategoryAndShadow(unittest.TestCase):
    def test_custom_category_5_plus(self):
        # Section 6.6 flag 2: the presets are illustrative; users may build
        # their own subset-and-universe combination.
        cat = custom_category(
            "category_5", "My combo", (SMAStrategy, V20Strategy),
            (Universe.V40, Universe.V40_NEXT),
        )
        signals = CategoryEngine(cat).evaluate_stock(
            sma_buy_series(), None, Universe.V40, []
        )
        self.assertEqual([s.strategy_name for s in signals], [SMAStrategy.name])

    def test_custom_category_validates_inputs(self):
        with self.assertRaises(ValueError):
            custom_category("x", "empty", (), (Universe.V40,))
        with self.assertRaises(ValueError):
            custom_category("x", "no universe", (SMAStrategy,), ())
        with self.assertRaises(ValueError):
            custom_category("x", "not a strategy", (str,), (Universe.V40,))

    def test_shadow_signals_cover_the_non_selected_categories(self):
        # Section 6.3's recommended feature: while trading one category,
        # observe what the other three WOULD have signalled.
        shadows = shadow_signals(sma_buy_series(), None, Universe.V40,
                                 active_category_key="category_2")
        self.assertEqual(set(shadows), {"category_1", "category_3", "category_4"})
        # Category 3 includes SMA -> it would have fired; Category 4 (V20
        # only) would have stayed silent.
        self.assertEqual([s.strategy_name for s in shadows["category_3"]],
                         [SMAStrategy.name])
        self.assertEqual(shadows["category_4"], [])


if __name__ == "__main__":
    unittest.main()
