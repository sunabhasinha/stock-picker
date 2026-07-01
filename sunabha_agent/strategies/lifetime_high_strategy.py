"""
Strategy 8: "Lifetime High Strategy" (LTH).

Source: master_strategy_kb.md Section 6.1.

BUY when, simultaneously:
  - TTM revenue is at its all-time high, AND
  - TTM net profit is at its all-time high, AND
  - current price is >= 30% below the stock's lifetime high.

SELL target = the stock's own lifetime high. No fixed time limit.

Averaging: every additional 10-percentage-point increment of decline from
lifetime high (40%, 50%, ...) permits another entry, but ONLY if TTM
revenue/profit are STILL at all-time highs at that later point in time -
re-checked at each averaging opportunity, not assumed to still hold from
the initial entry. Max comfortable allocation: up to 10% (higher than the
framework's normal ~9% ceiling, per Section 6.1's explicit justification).

V40 / V40 Next only.
"""

from __future__ import annotations

from sunabha_agent.data.models import Fundamentals, PriceSeries, Signal, Universe
from sunabha_agent.strategies.base import Strategy

LTH_MIN_DECLINE_PCT = 30.0
LTH_AVERAGING_DECLINE_INCREMENT_PCT = 10.0
LTH_MAX_ALLOCATION_PCT = 10.0  # explicitly higher than the framework's usual ~9% ceiling


def decline_from_lifetime_high_pct(current_price: float, lifetime_high: float) -> float:
    if lifetime_high <= 0:
        return 0.0
    return (lifetime_high - current_price) / lifetime_high * 100


class LifetimeHighStrategy(Strategy):
    name = "Lifetime High Strategy"
    allowed_universes = (Universe.V40, Universe.V40_NEXT)
    max_concurrent_trades_per_stock = 4  # 3% initial + room for several 10%-decline averages,
    # bounded in practice by the 10% allocation ceiling enforced below, not by a fixed trade count
    max_allocation_pct_per_stock = LTH_MAX_ALLOCATION_PCT
    uses_stop_loss = False

    def evaluate(
        self,
        prices: PriceSeries,
        fundamentals: Fundamentals | None,
        universe: Universe,
        open_trades_on_this_stock: list[Signal],
    ) -> list[Signal]:
        if not self.can_run_on(universe):
            return []
        if fundamentals is None:
            return []  # this strategy is meaningless without TTM fundamentals - don't guess

        current_price = prices.latest.close
        trigger_date = prices.latest.date
        lifetime_high = prices.lifetime_high
        decline_pct = decline_from_lifetime_high_pct(current_price, lifetime_high)
        at_ath = fundamentals.is_ttm_at_all_time_high()

        open_buys = [s for s in open_trades_on_this_stock if s.action in ("BUY", "AVERAGE")]
        total_allocated_pct = sum(s.suggested_position_pct for s in open_buys)

        # --- SELL: target reached
        if open_buys and current_price >= lifetime_high:
            return [
                Signal(
                    symbol=prices.symbol,
                    strategy_name=self.name,
                    universe_at_signal_time=universe,
                    action="SELL",
                    trigger_date=trigger_date,
                    signal_price=current_price,
                    rationale=(
                        f"Price {current_price:.2f} reached the lifetime high "
                        f"{lifetime_high:.2f}. Exiting all open LTH positions "
                        f"on this stock per Section 6.1."
                    ),
                )
            ]

        # --- BUY / AVERAGE
        if not at_ath:
            return []  # fundamentals no longer at ATH - the entire thesis requires this,
            # at both initial entry AND every averaging point (Section 6.1 explicit re-check rule)

        if decline_pct < LTH_MIN_DECLINE_PCT:
            return []

        is_first_trade = len(open_buys) == 0

        if is_first_trade:
            position_pct = 3.0
        else:
            # Only average at each further 10-point decline increment, and only
            # if we still have room under the 10% total-allocation ceiling.
            declines_already_captured = len(open_buys)  # 1 entry = initial 30%, each
            # subsequent entry should correspond to one more 10-point increment
            required_next_decline = LTH_MIN_DECLINE_PCT + (
                declines_already_captured * LTH_AVERAGING_DECLINE_INCREMENT_PCT
            )
            if decline_pct < required_next_decline:
                return []
            if total_allocated_pct + 3.0 > LTH_MAX_ALLOCATION_PCT:
                return []
            position_pct = 3.0

        return [
            Signal(
                symbol=prices.symbol,
                strategy_name=self.name,
                universe_at_signal_time=universe,
                action="BUY" if is_first_trade else "AVERAGE",
                trigger_date=trigger_date,
                signal_price=current_price,
                target_price=lifetime_high,
                suggested_position_pct=position_pct,
                rationale=(
                    f"TTM revenue and net profit are BOTH at all-time highs while "
                    f"price is {decline_pct:.1f}% below lifetime high "
                    f"({lifetime_high:.2f}). Per Section 6.1, this is read as "
                    f"sentiment/macro-driven mispricing in an already-vetted "
                    f"{universe.value} company, not a business problem. "
                    f"Potential gain to lifetime high: "
                    f"{(lifetime_high / current_price - 1) * 100:.1f}%."
                ),
                metadata={
                    "lifetime_high": lifetime_high,
                    "decline_pct": decline_pct,
                    "ttm_revenue_cr": fundamentals.revenue_ttm_cr,
                    "ttm_net_profit_cr": fundamentals.net_profit_ttm_cr,
                },
            )
        ]
