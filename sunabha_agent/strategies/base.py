"""
Base interface every strategy implements.

Why a base class at all, given how different these 8 strategies are
(indicator-based vs pure price-action vs fundamental-trigger vs geometric
pattern matching)? Because the portfolio layer (Category 1-4 selection,
Section 6.2) needs to treat them uniformly: enable a strategy, feed it
price/fundamental data, get back zero or more Signal objects. The
differences between strategies live entirely inside evaluate(), never in
how the rest of the system talks to them.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from sunabha_agent.data.models import Fundamentals, PriceSeries, Signal, Universe


class Strategy(ABC):
    """All 8 strategies from master_strategy_kb.md subclass this."""

    #: Human-readable name, used in Signal.strategy_name and logs.
    name: str = "UNNAMED_STRATEGY"

    #: Which universes this strategy is even allowed to run on. Enforced by
    #: can_run_on() below - every strategy MUST respect this, since running
    #: e.g. SMA strategy on a V200 stock directly contradicts Section 2.2.
    allowed_universes: tuple[Universe, ...] = ()

    #: Per-strategy max concurrent open trades on a single stock, and the
    #: resulting max portfolio allocation - both taken directly from each
    #: strategy's section in master_strategy_kb.md. Used by the portfolio
    #: layer to enforce position-sizing ceilings, not by the strategy itself.
    max_concurrent_trades_per_stock: int = 1
    max_allocation_pct_per_stock: float = 3.0
    uses_stop_loss: bool = False  # ALWAYS False across all 8 strategies - kept
    # explicit here (rather than just omitted) so a future contributor adding
    # a 9th strategy has to consciously override it, not accidentally inherit
    # silence on a point the whole course is emphatic about.

    def can_run_on(self, universe: Universe) -> bool:
        return universe in self.allowed_universes

    @abstractmethod
    def evaluate(
        self,
        prices: PriceSeries,
        fundamentals: Fundamentals | None,
        universe: Universe,
        open_trades_on_this_stock: list[Signal],
    ) -> list[Signal]:
        """
        Look at the latest data for one stock and return any new signals
        (BUY / SELL / AVERAGE). Returns an empty list if nothing fires.

        `open_trades_on_this_stock` lets a strategy see its own prior
        entries on this symbol, which is required for every averaging rule
        in the framework (Knoxville's 5% gap, V20's 10% gap, LTH's 10%
        decline increments, etc.) - none of these can be evaluated without
        knowing what's already open.

        Implementations must NOT raise on missing/incomplete data - return
        an empty list and let the caller's logging layer note the gap. A
        crashed strategy should never silently take down signal generation
        for every other stock in the universe.
        """
        raise NotImplementedError
