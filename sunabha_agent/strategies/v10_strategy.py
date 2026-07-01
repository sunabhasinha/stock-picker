"""
Strategy 6: V10.

Source: master_strategy_kb.md Section 3.3 and the consolidated pseudocode.

V10 is NOT a standalone pattern detector - it is the averaging mechanism
for RHS and CWH, active ONLY while a parent RHS or CWH trade is open on
the stock. Inside that window:

  BUY:  price pulls back >= 10% from the rolling peak reached since the
        window opened. Target = that peak (the level it fell from), a
        short round-trip - NOT the parent trade's technical target.
  AVERAGE: a second V10 entry requires a >= 5% gap below the previous
        open V10 entry (same gap structure as Knoxville). Max 2 concurrent
        V10 trades on top of the 1 parent trade = 3 total / 9% per stock;
        the combined ceiling across strategies is the portfolio layer's job.
  SELL: each V10 trade exits, in full, at its own stored peak target.

IMPORTANT CALLER CONTRACT: unlike the self-contained strategies, V10 needs
to see the parent RHS/CWH trades in `open_trades_on_this_stock`, not just
its own - the caller must pass ALL open trades on the stock. With no
parent trade present, V10 emits nothing, by definition.

Signals inherit requires_human_confirmation=True: the 10% trigger itself
is mechanical, but its validity rests entirely on the parent pattern trade,
which was itself a human-confirmed candidate (Section 3.6 flag 1).
"""

from __future__ import annotations

from sunabha_agent.data.models import Fundamentals, PriceSeries, Signal, Universe
from sunabha_agent.strategies.base import Strategy
from sunabha_agent.strategies.cwh_strategy import CWHStrategy
from sunabha_agent.strategies.rhs_strategy import RHSStrategy

V10_PULLBACK_PCT = 10.0
V10_AVERAGING_MIN_GAP_PCT = 5.0
V10_MAX_CONCURRENT_TRADES = 2

PARENT_STRATEGY_NAMES = (RHSStrategy.name, CWHStrategy.name)


class V10Strategy(Strategy):
    name = "V10 Strategy"
    allowed_universes = (Universe.V40, Universe.V40_NEXT)  # inherited from
    # RHS/CWH - V10 cannot exist without a parent trade from one of them
    max_concurrent_trades_per_stock = V10_MAX_CONCURRENT_TRADES
    max_allocation_pct_per_stock = 6.0  # V10's own 3%+3%; the 9% combined
    # ceiling with the parent trade is enforced at the portfolio layer
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
        if not prices.candles:
            return []

        close = prices.latest.close
        trigger_date = prices.latest.date
        open_v10 = [
            s
            for s in open_trades_on_this_stock
            if s.strategy_name == self.name and s.action in ("BUY", "AVERAGE")
        ]

        signals: list[Signal] = []

        # --- SELL, per individual V10 trade: back at the peak it fell from.
        # Deliberately checked BEFORE the parent-window gate: an open V10
        # trade must still be able to exit even if its parent RHS/CWH trade
        # already closed - only NEW entries require an active parent window.
        for trade in open_v10:
            if trade.target_price is not None and close >= trade.target_price:
                signals.append(
                    Signal(
                        symbol=prices.symbol,
                        strategy_name=self.name,
                        universe_at_signal_time=universe,
                        action="SELL",
                        trigger_date=trigger_date,
                        signal_price=close,
                        requires_human_confirmation=True,
                        rationale=(
                            f"Price {close:.2f} returned to {trade.target_price:.2f}, "
                            f"the peak this V10 entry pulled back from. Exiting "
                            f"this V10 trade only, in full (Section 3.3) - the "
                            f"parent RHS/CWH trade keeps running toward its own "
                            f"target."
                        ),
                        metadata={"closes_trade_entered_on": trade.trigger_date.isoformat()},
                    )
                )

        # --- BUY / AVERAGE requires an active parent RHS/CWH window.
        parents = [
            s
            for s in open_trades_on_this_stock
            if s.strategy_name in PARENT_STRATEGY_NAMES and s.action == "BUY"
        ]
        if not parents:
            return signals  # no active window -> no new V10 entries

        # The window opens at the (earliest) parent entry. The rolling peak
        # is measured ONLY inside the window - highs from before the parent
        # trade are irrelevant to the 10% pullback (Section 3.3).
        window_start = min(p.trigger_date for p in parents)
        window = [c for c in prices.candles if c.date >= window_start]
        if not window:
            return signals
        local_peak = max(c.high for c in window)

        if (
            len(open_v10) < self.max_concurrent_trades_per_stock
            and close <= local_peak * (1 - V10_PULLBACK_PCT / 100)
        ):
            is_first = not open_v10
            gap_ok = is_first or close <= (
                open_v10[-1].signal_price * (1 - V10_AVERAGING_MIN_GAP_PCT / 100)
            )
            if gap_ok:
                signals.append(
                    Signal(
                        symbol=prices.symbol,
                        strategy_name=self.name,
                        universe_at_signal_time=universe,
                        action="BUY" if is_first else "AVERAGE",
                        trigger_date=trigger_date,
                        signal_price=close,
                        target_price=local_peak,  # sell back at the level it fell from
                        suggested_position_pct=3.0,
                        requires_human_confirmation=True,
                        rationale=(
                            f"Price {close:.2f} is >= {V10_PULLBACK_PCT:.0f}% below "
                            f"the peak {local_peak:.2f} reached inside the active "
                            f"RHS/CWH window (opened {window_start.isoformat()}). "
                            f"V10 target is that peak itself. "
                            + (
                                "First V10 entry in this window."
                                if is_first
                                else f"Averaging: >= {V10_AVERAGING_MIN_GAP_PCT:.0f}% "
                                f"below the previous open V10 entry at "
                                f"{open_v10[-1].signal_price:.2f}."
                            )
                        ),
                        metadata={
                            "window_start": window_start.isoformat(),
                            "local_peak": local_peak,
                            "parent_strategy": parents[0].strategy_name,
                        },
                    )
                )

        return signals
