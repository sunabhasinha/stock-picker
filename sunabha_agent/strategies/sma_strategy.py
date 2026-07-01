"""
Strategy 1: Simple Moving Average (SMA) Strategy.

Source: master_strategy_kb.md Section 2.2.

BUY when, on closing price:  SMA(200) > SMA(50) > SMA(20) > Close
SELL when the exact inverse: Close > SMA(20) > SMA(50) > SMA(200)

V40 only. No averaging (max 1 trade per stock, ever, under this strategy).
No stop-loss. Execution is next-day-open after a close confirms the signal -
that timing detail is the caller's (execution layer's) job, not this
strategy's; this module only decides WHETHER a signal fires on a given
day's close.
"""

from __future__ import annotations

from datetime import date

from vivek_agent.data.models import Fundamentals, PriceSeries, Signal, Universe
from vivek_agent.strategies.base import Strategy


def simple_moving_average(closes: list[float], period: int) -> float | None:
    """Plain SMA, not exponential/weighted - the course is explicit that
    only the simple variant is used (Section 2.2)."""
    if len(closes) < period:
        return None
    return sum(closes[-period:]) / period


class SMAStrategy(Strategy):
    name = "SMA Strategy"
    allowed_universes = (Universe.V40,)
    max_concurrent_trades_per_stock = 1
    max_allocation_pct_per_stock = 3.0
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

        closes = prices.closes()
        sma200 = simple_moving_average(closes, 200)
        sma50 = simple_moving_average(closes, 50)
        sma20 = simple_moving_average(closes, 20)
        if sma200 is None or sma50 is None or sma20 is None:
            return []  # not enough history yet - not an error, just not ready

        close = prices.latest.close
        trigger_date = prices.latest.date
        has_open_trade = len(open_trades_on_this_stock) > 0

        # BUY: 200 > 50 > 20 > Close, and we don't already hold one (no averaging)
        if sma200 > sma50 > sma20 > close and not has_open_trade:
            return [
                Signal(
                    symbol=prices.symbol,
                    strategy_name=self.name,
                    universe_at_signal_time=universe,
                    action="BUY",
                    trigger_date=trigger_date,
                    signal_price=close,
                    target_price=None,  # SMA strategy has no fixed price target -
                    # the exit IS the opposite SMA condition firing, not a static level
                    suggested_position_pct=self.max_allocation_pct_per_stock,
                    requires_human_confirmation=False,
                    rationale=(
                        f"SMA(200)={sma200:.2f} > SMA(50)={sma50:.2f} > "
                        f"SMA(20)={sma20:.2f} > Close={close:.2f}. Per Section 2.2, "
                        f"this implies long/medium/short-term traders are all "
                        f"underwater simultaneously - maximum pessimism zone, "
                        f"historically where large patient capital steps in."
                    ),
                    metadata={"sma200": sma200, "sma50": sma50, "sma20": sma20},
                )
            ]

        # SELL: exact inverse, only relevant if we have an open BUY to close
        if close > sma20 > sma50 > sma200 and has_open_trade:
            return [
                Signal(
                    symbol=prices.symbol,
                    strategy_name=self.name,
                    universe_at_signal_time=universe,
                    action="SELL",
                    trigger_date=trigger_date,
                    signal_price=close,
                    rationale=(
                        f"Close={close:.2f} > SMA(20)={sma20:.2f} > "
                        f"SMA(50)={sma50:.2f} > SMA(200)={sma200:.2f}. Exact "
                        f"inverse of the buy condition - exiting the position "
                        f"opened earlier under this strategy."
                    ),
                    metadata={"sma200": sma200, "sma50": sma50, "sma20": sma20},
                )
            ]

        return []
