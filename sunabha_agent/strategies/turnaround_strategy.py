"""
Strategy 7: "Three Times in Three Years" (turnaround strategy).

Source: master_strategy_kb.md Section 5 and the consolidated pseudocode.

The only strategy in the framework whose universe is ALL NSE-listed
stocks - it is allowed to run on UNCLASSIFIED, which every other strategy
refuses. The real gate is `Fundamentals.listed_on_nse`, which must be
explicitly True (None = unverified = no signal; ~3,500 BSE-only listings
are ineligible, Section 5.0).

Entry: the 10-condition checklist (research/turnaround_checklist.py).
This strategy emits a BUY CANDIDATE when nothing on the checklist has
outright FAILED; any still-open research questions ride along in the
signal so the human can finish them - the KB calls this strategy the
strongest human-in-the-loop case in the framework, so every signal is
requires_human_confirmation=True and the checklist itself is the real
deliverable.

Exit (Sections 5.1 conditions 8-9):
  - +100% gain within 12 months of entry -> SELL (default rule; the
    instructor's own documented JP Power deviation is a USER override,
    never silent agent behavior - Section 5.5 flag 3).
  - After 12 months, the 100% trigger lapses: hold, with no time limit,
    until price reaches the ORIGINAL lifetime high (as recorded at entry).

3% position, single entry (no averaging - explicit in Section 5.2),
no stop-loss.
"""

from __future__ import annotations

from datetime import timedelta

from sunabha_agent.data.models import Fundamentals, PriceSeries, Signal, Universe
from sunabha_agent.research.turnaround_checklist import (
    ResearchProvider,
    build_checklist,
)
from sunabha_agent.strategies.base import Strategy

TWELVE_MONTHS = timedelta(days=365)
GAIN_TARGET_PCT = 100.0


class TurnaroundStrategy(Strategy):
    name = "Three Times in Three Years Strategy"
    # NSE-wide: the sole strategy allowed on UNCLASSIFIED stocks. The
    # binding eligibility check is listed_on_nse below, not the universe.
    allowed_universes = (
        Universe.V40,
        Universe.V40_NEXT,
        Universe.V200,
        Universe.UNCLASSIFIED,
    )
    max_concurrent_trades_per_stock = 1  # single-entry, no averaging (5.2)
    max_allocation_pct_per_stock = 3.0
    uses_stop_loss = False

    def __init__(self, researcher: ResearchProvider | None = None):
        self._researcher = researcher

    def evaluate(
        self,
        prices: PriceSeries,
        fundamentals: Fundamentals | None,
        universe: Universe,
        open_trades_on_this_stock: list[Signal],
    ) -> list[Signal]:
        if not self.can_run_on(universe):
            return []
        if not prices.candles:
            return []

        close = prices.latest.close
        trigger_date = prices.latest.date
        open_own = [s for s in open_trades_on_this_stock if s.action == "BUY"]

        # --- SELL (conditions 8/9). Checked before any entry logic so an
        # open position can always exit, whatever the checklist says today.
        for trade in open_own:
            held = trigger_date - trade.trigger_date
            gain_pct = (
                (close - trade.signal_price) / trade.signal_price * 100
                if trade.signal_price > 0
                else 0.0
            )
            # The lifetime high the thesis was built on, frozen at entry -
            # falling back to today's if an old signal predates the field.
            lifetime_high_ref = trade.metadata.get(
                "lifetime_high_at_entry", prices.lifetime_high
            )

            if held <= TWELVE_MONTHS and gain_pct >= GAIN_TARGET_PCT:
                return [
                    self._sell(
                        prices, universe, close, trigger_date,
                        rationale=(
                            f"+{gain_pct:.0f}% in {held.days} days - the 100%-"
                            f"within-12-months exit (Condition 8). Booking in "
                            f"full. Holding on for a bigger target is a "
                            f"documented USER override (JP Power example), "
                            f"never applied silently."
                        ),
                        trade=trade,
                    )
                ]
            if close >= lifetime_high_ref:
                return [
                    self._sell(
                        prices, universe, close, trigger_date,
                        rationale=(
                            f"Price {close:.2f} reached the original lifetime "
                            f"high {lifetime_high_ref:.2f} recorded at entry - "
                            f"the Condition 9 exit after a {held.days}-day hold."
                        ),
                        trade=trade,
                    )
                ]
        if open_own:
            return []  # single-entry strategy: never average, never re-enter

        # --- Hard NSE gate (Section 5.0): must be explicitly True.
        # None means unverified - refuse rather than assume.
        if fundamentals is None or fundamentals.listed_on_nse is not True:
            return []

        checklist = build_checklist(prices, fundamentals, self._researcher)
        if checklist.has_hard_failures:
            return []

        open_questions = checklist.open_research_questions
        return [
            Signal(
                symbol=prices.symbol,
                strategy_name=self.name,
                universe_at_signal_time=universe,
                action="BUY",
                trigger_date=trigger_date,
                signal_price=close,
                target_price=close * 2,  # the Condition 8 default; Condition 9's
                # lifetime-high fallback lives in metadata
                suggested_position_pct=3.0,
                requires_human_confirmation=True,  # Section 5.5 flag 1: the
                # strongest human-in-the-loop case in the entire framework
                rationale=(
                    f"Turnaround candidate (decline Category "
                    f"{checklist.decline_category or '?'}): every computable "
                    f"condition passed"
                    + (
                        f", but {len(open_questions)} research question(s) "
                        f"remain OPEN - complete them before trading: "
                        + " | ".join(open_questions)
                        if open_questions
                        else " and all research conditions are confirmed"
                    )
                    + ". Exit plan: +100% within 12 months, else hold to the "
                    f"lifetime high {prices.lifetime_high:.2f}. REQUIRES HUMAN "
                    f"CONFIRMATION."
                ),
                metadata={
                    "checklist": checklist.as_dicts(),
                    "decline_category": checklist.decline_category,
                    "open_research_questions": open_questions,
                    "fully_confirmed": checklist.is_fully_confirmed,
                    "lifetime_high_at_entry": prices.lifetime_high,
                },
            )
        ]

    def _sell(self, prices, universe, close, trigger_date, rationale, trade) -> Signal:
        return Signal(
            symbol=prices.symbol,
            strategy_name=self.name,
            universe_at_signal_time=universe,
            action="SELL",
            trigger_date=trigger_date,
            signal_price=close,
            requires_human_confirmation=True,
            rationale=rationale,
            metadata={"closes_trade_entered_on": trade.trigger_date.isoformat()},
        )
