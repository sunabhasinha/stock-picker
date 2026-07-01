"""
Strategy 3: V20 Strategy.

Source: master_strategy_kb.md Section 2.4.

1. Find a maximal run of consecutive GREEN candles (zero red candles inside).
2. If (high of run - low of run) / (low of run) >= 20%, register a range:
   {lower_line = low of run, upper_line = high of run}.
3. BUY when price touches/falls to lower_line.
4. SELL when price touches/rises to upper_line of the SAME range.
5. A range is single-use: once a buy-sell cycle completes on it, it can
   NEVER be reused, even if price returns to the same level later. A fresh
   20%+ green-candle run is required for the next trade.
6. Averaging: a second range's lower_line may be entered only if it's
   >=10% below the first trade's entry price. Max 3 concurrent trades.

Applicable to V40, V40 Next, AND V200 - the broadest single-strategy
universe in the framework. Entries/exits can trigger intraday in real
trading (GTT order territory) but this module only needs daily candles to
detect when a price level has been crossed; the execution layer decides
how to actually place the order.
"""

from __future__ import annotations

from dataclasses import dataclass

from vivek_agent.data.models import Candle, Fundamentals, PriceSeries, Signal, Universe
from vivek_agent.strategies.base import Strategy

V20_MIN_MOVE_PCT = 20.0
V20_AVERAGING_MIN_GAP_PCT = 10.0
V20_MAX_CONCURRENT_TRADES = 3


@dataclass
class V20Range:
    lower_line: float
    upper_line: float
    start_index: int  # index into the candle list where the green run started
    end_index: int
    used: bool = False  # a range is single-use once a full buy-sell cycle completes


def find_qualifying_ranges(candles: list[Candle]) -> list[V20Range]:
    """
    Scan for every maximal run of consecutive green candles whose
    (high - low) / low >= 20%. Returns ranges in chronological order.

    NOTE on "maximal run": a single red candle anywhere inside voids that
    run per Section 2.4 ("if a red candle appears in between, void"). This
    function restarts the run the instant a red candle appears - it does
    NOT allow re-including a green sub-run that happens to also qualify on
    its own once split by a red candle; each maximal green run is evaluated
    once, as a whole.
    """
    ranges: list[V20Range] = []
    run_start: int | None = None

    for i, candle in enumerate(candles):
        if candle.is_green:
            if run_start is None:
                run_start = i
        else:
            if run_start is not None:
                _maybe_register_range(candles, run_start, i - 1, ranges)
            run_start = None

    if run_start is not None:
        _maybe_register_range(candles, run_start, len(candles) - 1, ranges)

    return ranges


def _maybe_register_range(
    candles: list[Candle], start: int, end: int, ranges: list[V20Range]
) -> None:
    run = candles[start : end + 1]
    low = min(c.low for c in run)
    high = max(c.high for c in run)
    if low <= 0:
        return
    move_pct = (high - low) / low * 100
    if move_pct >= V20_MIN_MOVE_PCT:
        ranges.append(V20Range(lower_line=low, upper_line=high, start_index=start, end_index=end))


class V20Strategy(Strategy):
    name = "V20 Strategy"
    allowed_universes = (Universe.V40, Universe.V40_NEXT, Universe.V200)
    max_concurrent_trades_per_stock = V20_MAX_CONCURRENT_TRADES
    max_allocation_pct_per_stock = 9.0
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

        candles = prices.candles
        if len(candles) < 2:
            return []

        ranges = find_qualifying_ranges(candles)
        if not ranges:
            return []

        current_price = prices.latest.close
        trigger_date = prices.latest.date
        signals: list[Signal] = []

        open_buys = [s for s in open_trades_on_this_stock if s.action in ("BUY", "AVERAGE")]
        first_entry_price = open_buys[0].signal_price if open_buys else None

        # --- SELL check: does current price hit the upper line of any range
        # we have an open trade tagged against? We identify "tagged against"
        # via metadata written at entry time (range_lower/range_upper).
        for trade in open_buys:
            tagged_upper = trade.metadata.get("range_upper")
            if tagged_upper is not None and current_price >= tagged_upper:
                signals.append(
                    Signal(
                        symbol=prices.symbol,
                        strategy_name=self.name,
                        universe_at_signal_time=universe,
                        action="SELL",
                        trigger_date=trigger_date,
                        signal_price=current_price,
                        rationale=(
                            f"Price {current_price:.2f} reached the upper line "
                            f"{tagged_upper:.2f} of the range this trade was "
                            f"entered against. Exiting per Section 2.4 - this "
                            f"specific range is now spent and cannot be reused."
                        ),
                        metadata={"closes_trade_entered_on": trade.trigger_date.isoformat()},
                    )
                )

        # --- BUY check: does current price touch the lower line of an
        # unused range, and do we have room (under max concurrent trades,
        # and if averaging, is the gap >=10% below the first entry)?
        if len(open_buys) < self.max_concurrent_trades_per_stock:
            for r in ranges:
                if r.used:
                    continue
                if current_price > r.lower_line:
                    continue  # price hasn't come down to this range yet

                is_first_trade = first_entry_price is None
                gap_ok = (
                    is_first_trade
                    or r.lower_line <= first_entry_price * (1 - V20_AVERAGING_MIN_GAP_PCT / 100)
                )
                if not gap_ok:
                    continue

                signals.append(
                    Signal(
                        symbol=prices.symbol,
                        strategy_name=self.name,
                        universe_at_signal_time=universe,
                        action="BUY" if is_first_trade else "AVERAGE",
                        trigger_date=trigger_date,
                        signal_price=current_price,
                        target_price=r.upper_line,
                        suggested_position_pct=3.0,
                        rationale=(
                            f"Price {current_price:.2f} touched the lower line "
                            f"{r.lower_line:.2f} of a qualifying 20%+ green-candle "
                            f"range (upper line {r.upper_line:.2f}). "
                            + (
                                "First entry on this range."
                                if is_first_trade
                                else f"Averaging: >= {V20_AVERAGING_MIN_GAP_PCT:.0f}% "
                                f"below first entry at {first_entry_price:.2f}."
                            )
                        ),
                        metadata={"range_lower": r.lower_line, "range_upper": r.upper_line},
                    )
                )
                break  # one new entry per evaluation call is enough; re-run next bar

        return signals
