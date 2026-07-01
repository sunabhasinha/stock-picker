"""
The portfolio-construction layer: the four Categories from Section 6.2,
the cross-strategy candidate ranking from Section 4.20, and the
existing-portfolio reconciliation logic from Section 6.3.

This is the engine's top-level switchboard. The course's single most
emphasized rule (Section 6.3): pick EXACTLY ONE category and commit to it
for at least a year - mixing strategies/universes outside the chosen
category is a discipline failure, not a feature. Accordingly, nothing in
this module runs without a Category selected: CategoryEngine has no
default category, and it refuses to emit signals for stocks outside the
category's universe or from strategies outside the category's set.

The four presets are exactly the course's four. They are also just
presets: Section 6.6 flag 2 says the categories are illustrative
combinations of fully-modular building blocks, so custom_category()
exists for a user-defined "Category 5+".

Open-trade routing rule (important, easy to get wrong): each strategy is
handed only ITS OWN open trades, per the Strategy base-class contract
("see its own prior entries") - EXCEPT V10, whose documented caller
contract requires ALL open trades on the stock so it can find its parent
RHS/CWH trade.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from sunabha_agent.data.models import Fundamentals, PriceSeries, Signal, Universe
from sunabha_agent.research.turnaround_checklist import ResearchProvider
from sunabha_agent.screening.fundamental_gate import GateResult, screen
from sunabha_agent.strategies.base import Strategy
from sunabha_agent.strategies.cwh_strategy import CWHStrategy
from sunabha_agent.strategies.knoxville_strategy import KnoxvilleStrategy
from sunabha_agent.strategies.lifetime_high_strategy import LifetimeHighStrategy
from sunabha_agent.strategies.rhs_strategy import RHSStrategy
from sunabha_agent.strategies.sma_strategy import SMAStrategy
from sunabha_agent.strategies.turnaround_strategy import TurnaroundStrategy
from sunabha_agent.strategies.v10_strategy import V10Strategy
from sunabha_agent.strategies.v20_strategy import V20Strategy

#: Category 2's multi-signal rule: a subsequent entry on the same stock
#: (from a DIFFERENT strategy) must be >=10% below the preceding trade.
CROSS_STRATEGY_GAP_PCT = 10.0
#: Section 4.20 tie-breaker 3 applies "among candidates with SIMILAR
#: potential gain" - the KB gives no number for "similar", so we bucket
#: gains this wide before letting the ROCE/D-E tier decide.
GAIN_SIMILARITY_BUCKET_PCT = 5.0


@dataclass(frozen=True)
class Category:
    key: str
    name: str
    universes: tuple[Universe, ...]
    strategy_classes: tuple[type[Strategy], ...]
    max_allocation_pct_per_stock: float
    #: Category 2 only: min % gap below the previous trade for a new entry
    #: from a different strategy. None = no cross-strategy entries expected
    #: (single-strategy categories) or no such rule given.
    cross_strategy_gap_pct: Optional[float] = None
    idle_capital_note: str = (
        "If no qualifying opportunity exists, hold un-deployed capital in "
        "CASH. Never substitute a strategy outside this category to stay "
        "invested (Section 6.2)."
    )


CATEGORY_1 = Category(
    key="category_1",
    name="Lifetime High Strategy Only",
    universes=(Universe.V40, Universe.V40_NEXT),
    strategy_classes=(LifetimeHighStrategy,),
    max_allocation_pct_per_stock=10.0,  # per LTH's own averaging rules (6.1)
)

CATEGORY_2 = Category(
    key="category_2",
    name="All 8 Strategies, V40 Only",
    universes=(Universe.V40,),  # V40 Next and V200 explicitly excluded -
    # this gate is also what narrows the normally-NSE-wide Strategy 7 to
    # V40 names under this category (Section 6.2)
    strategy_classes=(
        SMAStrategy,
        KnoxvilleStrategy,
        V20Strategy,
        RHSStrategy,
        CWHStrategy,
        V10Strategy,
        TurnaroundStrategy,
        LifetimeHighStrategy,
    ),
    max_allocation_pct_per_stock=10.0,  # ~9-10% thumb-rule ceiling (6.2)
    cross_strategy_gap_pct=CROSS_STRATEGY_GAP_PCT,
)

CATEGORY_3 = Category(
    key="category_3",
    name="Four Named Strategies, V40 + V40 Next",
    universes=(Universe.V40, Universe.V40_NEXT),
    strategy_classes=(SMAStrategy, RHSStrategy, CWHStrategy, V10Strategy),
    max_allocation_pct_per_stock=9.0,  # 3% RHS/CWH + 3%+3% V10 (Section 3.3)
)

CATEGORY_4 = Category(
    key="category_4",
    name="V20 Only",
    universes=(Universe.V40, Universe.V40_NEXT, Universe.V200),
    strategy_classes=(V20Strategy,),
    max_allocation_pct_per_stock=9.0,
    idle_capital_note=(
        "If no qualifying V20 range exists, hold cash. Entry AND exit are "
        "both known in advance -> fully automatable via GTT orders "
        "(Section 6.2's 'set and forget' category)."
    ),
)

PRESET_CATEGORIES: dict[str, Category] = {
    c.key: c for c in (CATEGORY_1, CATEGORY_2, CATEGORY_3, CATEGORY_4)
}


def custom_category(
    key: str,
    name: str,
    strategy_classes: tuple[type[Strategy], ...],
    universes: tuple[Universe, ...],
    max_allocation_pct_per_stock: float = 9.0,
    cross_strategy_gap_pct: Optional[float] = None,
) -> Category:
    """A user-defined 'Category 5+' (Section 6.6 flag 2): the 8 strategies
    and 3 universes are modular building blocks; the four presets are just
    the course's named examples."""
    if not strategy_classes:
        raise ValueError("A category must enable at least one strategy.")
    if not universes:
        raise ValueError("A category must include at least one universe.")
    for cls in strategy_classes:
        if not (isinstance(cls, type) and issubclass(cls, Strategy)):
            raise ValueError(f"{cls!r} is not a Strategy subclass.")
    return Category(
        key=key,
        name=name,
        universes=tuple(universes),
        strategy_classes=tuple(strategy_classes),
        max_allocation_pct_per_stock=max_allocation_pct_per_stock,
        cross_strategy_gap_pct=cross_strategy_gap_pct,
    )


class ReconciliationAction(str, Enum):
    """Section 6.3's existing-portfolio reconciliation outcomes."""

    STRATEGY_APPLIES = "STRATEGY_APPLIES"  # follow that strategy's own exit
    EXIT_PROFITABLE = "EXIT_PROFITABLE"  # no strategy applies + in profit
    HOLD_AWAIT_RECOVERY = "HOLD_AWAIT_RECOVERY"  # no strategy + at a loss, gate OK
    REVIEW_QUALITY_GATE_FAILED = "REVIEW_QUALITY_GATE_FAILED"  # at a loss AND
    # the fundamental gate now fails. The KB conditions holding on passing
    # the gate but never explicitly commands a sale - surfaced for review
    # rather than auto-sold (inferred handling, flagged as such).


@dataclass
class HoldingReconciliation:
    symbol: str
    action: ReconciliationAction
    rationale: str
    signals_today: list[Signal] = field(default_factory=list)


class CategoryEngine:
    """Runs one selected Category. There is deliberately no default - the
    caller must have picked one (Section 6.3's core rule)."""

    def __init__(self, category: Category, researcher: ResearchProvider | None = None):
        self.category = category
        self.strategies: list[Strategy] = [
            cls(researcher) if cls is TurnaroundStrategy else cls()
            for cls in category.strategy_classes
        ]

    # ------------------------------------------------------------------
    # Signal generation
    # ------------------------------------------------------------------

    def evaluate_stock(
        self,
        prices: PriceSeries,
        fundamentals: Fundamentals | None,
        universe: Universe,
        open_trades_on_this_stock: list[Signal],
    ) -> list[Signal]:
        """All of the selected category's signals for one stock, today."""
        if universe not in self.category.universes:
            return []  # outside the category's universe: nothing may fire

        # Section 4.14: the fundamental gate is the non-negotiable layer -
        # no strategy signal is surfaced for a stock that fails it.
        soft_flags: list[str] = []
        if fundamentals is not None:
            report = screen(fundamentals, universe)
            if report.gate_result == GateResult.FAIL:
                return []
            soft_flags = report.soft_flags

        signals: list[Signal] = []
        for strategy in self.strategies:
            signals.extend(
                strategy.evaluate(
                    prices=prices,
                    fundamentals=fundamentals,
                    universe=universe,
                    open_trades_on_this_stock=self._trades_for(
                        strategy, open_trades_on_this_stock
                    ),
                )
            )

        signals = self._apply_cross_strategy_gap(signals, open_trades_on_this_stock)

        for s in signals:
            s.metadata.setdefault("category", self.category.key)
            if soft_flags:
                s.metadata.setdefault("screening_soft_flags", soft_flags)
        return signals

    @staticmethod
    def _trades_for(strategy: Strategy, open_trades: list[Signal]) -> list[Signal]:
        """Each strategy sees only its own open trades - except V10, whose
        documented contract needs ALL trades to find its parent RHS/CWH."""
        if isinstance(strategy, V10Strategy):
            return open_trades
        return [t for t in open_trades if t.strategy_name == strategy.name]

    def _apply_cross_strategy_gap(
        self, signals: list[Signal], open_trades: list[Signal]
    ) -> list[Signal]:
        """Category 2's multi-signal rule (Section 6.2): a NEW entry while
        other trades are open on the stock must be >=10% below the most
        recent open trade's entry. AVERAGE signals are exempt - same-strategy
        averaging is governed by each strategy's own gap rule."""
        gap = self.category.cross_strategy_gap_pct
        open_entries = [t for t in open_trades if t.action in ("BUY", "AVERAGE")]
        if gap is None or not open_entries:
            return signals

        last_entry = max(open_entries, key=lambda t: t.trigger_date)
        ceiling = last_entry.signal_price * (1 - gap / 100)
        kept = []
        for s in signals:
            if s.action == "BUY" and s.signal_price > ceiling:
                continue  # gap not met - skip this new entry, keep the rest
            kept.append(s)
        return kept

    # ------------------------------------------------------------------
    # Candidate ranking (Section 4.20 tie-breaking hierarchy)
    # ------------------------------------------------------------------

    @staticmethod
    def rank_candidates(
        candidates: list[tuple[Signal, Fundamentals | None]],
    ) -> list[tuple[Signal, Fundamentals | None]]:
        """
        Order buy candidates when there are more of them than capital slots:
          1. V40 over V40 Next over V200 (universe quality first);
          2. then higher potential gain %;
          3. among SIMILAR gains (same 5%-wide bucket - our reading of the
             KB's unquantified "similar"), the better ROCE/D-E tier.
        """
        universe_rank = {
            Universe.V40: 0,
            Universe.V40_NEXT: 1,
            Universe.V200: 2,
            Universe.UNCLASSIFIED: 3,
        }

        def gain_pct(signal: Signal) -> float:
            # Pattern strategies record the KB's own gain definition
            # (to the TECHNICAL target) in metadata; otherwise derive from
            # target_price; strategies with event-based exits have no
            # knowable gain and rank below quantified ones.
            if "potential_gain_pct" in signal.metadata:
                return float(signal.metadata["potential_gain_pct"])
            if signal.target_price is not None and signal.signal_price > 0:
                return (signal.target_price - signal.signal_price) / signal.signal_price * 100
            return 0.0

        def tier_score(fundamentals: Fundamentals | None) -> int:
            if fundamentals is None:
                return 4  # unknown ranks below any known tier
            from sunabha_agent.screening.fundamental_gate import (
                debt_equity_tier,
                roce_tier,
            )

            score = 0
            for tier in (roce_tier(fundamentals), debt_equity_tier(fundamentals)):
                if tier == "best":
                    score += 0
                elif tier.startswith("n/a"):  # BFSI: tiering not applicable
                    score += 1
                elif tier == "very_good":
                    score += 1
                else:
                    score += 2
            return score

        def key(item: tuple[Signal, Fundamentals | None]):
            signal, fundamentals = item
            gain = gain_pct(signal)
            return (
                universe_rank.get(signal.universe_at_signal_time, 3),
                -(gain // GAIN_SIMILARITY_BUCKET_PCT),  # coarse bucket first
                tier_score(fundamentals),  # tier breaks ties inside a bucket
                -gain,  # exact gain last
            )

        return sorted(candidates, key=key)

    # ------------------------------------------------------------------
    # Existing-portfolio reconciliation (Section 6.3, final Video 6 form)
    # ------------------------------------------------------------------

    def reconcile_holding(
        self,
        prices: PriceSeries,
        fundamentals: Fundamentals | None,
        universe: Universe,
        open_trades_on_this_stock: list[Signal],
        average_cost: float,
    ) -> HoldingReconciliation:
        """The answer to 'I hold X, what do I do?' - the logic the course
        says resolves nearly every stock-specific question (Section 6.4)."""
        symbol = prices.symbol
        close = prices.latest.close
        enabled_names = {s.name for s in self.strategies}

        signals_today = self.evaluate_stock(
            prices, fundamentals, universe, open_trades_on_this_stock
        )
        # A strategy "applies" if we hold an open trade under an enabled
        # strategy (its own exit rules govern - positions always complete
        # under their original rules) or an enabled strategy signalled today.
        has_open_enabled_trade = any(
            t.strategy_name in enabled_names
            and t.action in ("BUY", "AVERAGE")
            for t in open_trades_on_this_stock
        )
        if has_open_enabled_trade or signals_today:
            return HoldingReconciliation(
                symbol=symbol,
                action=ReconciliationAction.STRATEGY_APPLIES,
                rationale=(
                    "A strategy from the active category applies - hold/exit "
                    "strictly at that strategy's own defined target, nothing "
                    "else (Section 6.3)."
                ),
                signals_today=signals_today,
            )

        if close > average_cost:
            return HoldingReconciliation(
                symbol=symbol,
                action=ReconciliationAction.EXIT_PROFITABLE,
                rationale=(
                    f"No enabled strategy applies and the position is "
                    f"profitable ({close:.2f} vs cost {average_cost:.2f}) - "
                    f"exit and redeploy into the category's next qualifying "
                    f"opportunity, or hold cash per the idle-capital rule: "
                    f"{self.category.idle_capital_note}"
                ),
            )

        if fundamentals is not None:
            report = screen(fundamentals, universe)
            if report.gate_result == GateResult.FAIL:
                return HoldingReconciliation(
                    symbol=symbol,
                    action=ReconciliationAction.REVIEW_QUALITY_GATE_FAILED,
                    rationale=(
                        "At a loss AND the stock now fails the fundamental "
                        "gate: " + "; ".join(report.fail_reasons) + ". The "
                        "course conditions 'hold and wait' on still passing "
                        "the gate (Section 6.3) but never explicitly commands "
                        "a sale - review this position manually (inferred "
                        "handling, flagged as such)."
                    ),
                )

        return HoldingReconciliation(
            symbol=symbol,
            action=ReconciliationAction.HOLD_AWAIT_RECOVERY,
            rationale=(
                "No enabled strategy applies and the position is at a loss - "
                "hold and wait for recovery"
                + (
                    " (fundamental gate passes)"
                    if fundamentals is not None
                    else " (fundamentals unavailable - gate NOT verified; fetch "
                    "them to confirm the company still qualifies)"
                )
                + ". Do not sell at a loss out of impatience (Section 6.3)."
            ),
        )


def shadow_signals(
    prices: PriceSeries,
    fundamentals: Fundamentals | None,
    universe: Universe,
    active_category_key: str | None = None,
    researcher: ResearchProvider | None = None,
) -> dict[str, list[Signal]]:
    """
    Section 6.3's recommended shadow-tracking feature: what each
    NON-selected preset category would have signalled today, so the user
    has real comparative data after the 1-year commitment period. Shadow
    categories are evaluated with no open positions (they are hypothetical
    books) and their signals must never be executed.
    """
    return {
        key: CategoryEngine(category, researcher).evaluate_stock(
            prices, fundamentals, universe, open_trades_on_this_stock=[]
        )
        for key, category in PRESET_CATEGORIES.items()
        if key != active_category_key
    }
