"""
Strategy 5: Cup with Handle (CWH).

Source: master_strategy_kb.md Section 3.2 and the consolidated pseudocode.

Structurally "an RHS without the left shoulder": the pattern opens directly
with the cup (the deepest trough, analogous to the head), followed by
handle(s) (analogous to right shoulders, each strictly shallower than the
cup - a handle as deep as the cup INVALIDATES the pattern). Two or more
handles -> "Complex CWH", higher confidence.

Buy: identical mechanism to RHS - the FIRST handle's base-formation
breakout (green candle, closing basis).

Sell - THE key difference from RHS (Section 3.2 flags this explicitly as
the main distinguishing rule): the technical target IS the final target.
It is never raised to the lifetime high. Do not conflate with RHS.

Every signal carries requires_human_confirmation=True (Section 3.6 flag 1).
Averaging is Strategy 6 (V10), layered on the open CWH window.
"""

from __future__ import annotations

from dataclasses import dataclass

from sunabha_agent.data.models import Fundamentals, PriceSeries, Signal, Universe
from sunabha_agent.strategies.base import Strategy
from sunabha_agent.strategies.pattern_common import (
    MIN_GAIN_RECOMMENDED_PCT,
    BaseBreakout,
    detect_base_breakout,
    find_pivot_highs,
    neckline_at_lifetime_high,
    neckline_chains,
    neckline_level,
    technical_target,
)


@dataclass(frozen=True)
class CWHPattern:
    neckline: float
    cup_low: float
    handle_lows: tuple[float, ...]  # completed handles between connecting points
    forming_handle_low: float  # the handle whose base just broke out
    peak_indices: tuple[int, ...]
    is_complex: bool  # 2+ handles total (Section 3.2)
    breakout: BaseBreakout


def detect_cwh(candles) -> CWHPattern | None:
    """
    Find a CWH whose handle base breakout fired on the LATEST candle.

    The cup is the trough between the FIRST two connecting points; every
    later trough is a handle and must be strictly shallower than the cup.
    This placement is also what disambiguates CWH from RHS on the same
    neckline chain (KB Section 3.6 flag 3): RHS requires the LAST
    inter-peak trough to be the deepest (the head), CWH the FIRST (the
    cup) - the two cannot both match one chain. "No left shoulder before
    the cup" is not machine-checked; it is part of what the human
    confirmation step is for.
    """
    breakout = detect_base_breakout(candles)
    if breakout is None:
        return None

    for chain in neckline_chains(candles, find_pivot_highs(candles)):
        if chain[-1] >= breakout.base_start:
            continue  # base must form after the last connecting point

        trough_lows = []
        for a, b in zip(chain, chain[1:]):
            between = candles[a + 1 : b]
            if not between:
                break
            trough_lows.append(min(c.low for c in between))
        if len(trough_lows) != len(chain) - 1:
            continue

        cup_low = trough_lows[0]
        handle_lows = tuple(trough_lows[1:])
        if any(h <= cup_low for h in handle_lows):
            continue  # a handle as deep as the cup invalidates the pattern

        neckline = neckline_level(candles, chain)
        forming = candles[chain[-1] + 1 : len(candles) - 1]
        forming_handle_low = min(c.low for c in forming)
        if forming_handle_low <= cup_low or forming_handle_low >= neckline:
            continue  # the forming handle must dip, but stay above the cup

        return CWHPattern(
            neckline=neckline,
            cup_low=cup_low,
            handle_lows=handle_lows,
            forming_handle_low=forming_handle_low,
            peak_indices=tuple(chain),
            is_complex=len(chain) >= 3,  # inter-peak handle(s) + the forming one
            breakout=breakout,
        )
    return None


class CWHStrategy(Strategy):
    name = "Cup with Handle Strategy"
    allowed_universes = (Universe.V40, Universe.V40_NEXT)
    max_concurrent_trades_per_stock = 1  # averaging is V10's job; combined
    # 3-trade / 9% ceiling enforced by the portfolio layer (Section 3.3)
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
        if len(prices.candles) < 2:
            return []

        close = prices.latest.close
        trigger_date = prices.latest.date
        open_own = [s for s in open_trades_on_this_stock if s.action == "BUY"]

        # --- SELL: fixed technical target from entry time; must not depend
        # on the (long-gone) pattern still being detectable.
        for trade in open_own:
            if trade.target_price is not None and close >= trade.target_price:
                return [
                    Signal(
                        symbol=prices.symbol,
                        strategy_name=self.name,
                        universe_at_signal_time=universe,
                        action="SELL",
                        trigger_date=trigger_date,
                        signal_price=close,
                        requires_human_confirmation=True,
                        rationale=(
                            f"Price {close:.2f} reached the technical target "
                            f"{trade.target_price:.2f} fixed at entry. CWH sells "
                            f"at the technical target itself - never raised to "
                            f"the lifetime high (Section 3.2 key difference from "
                            f"RHS). Full exit, no partial booking."
                        ),
                        metadata={"closes_trade_entered_on": trade.trigger_date.isoformat()},
                    )
                ]

        if open_own:
            return []  # one CWH trade per stock; averaging belongs to V10

        pattern = detect_cwh(prices.candles)
        if pattern is None:
            return []

        final_target = technical_target(pattern.neckline, pattern.cup_low)
        lifetime_high = prices.lifetime_high
        potential_gain_pct = (final_target - close) / close * 100
        at_high = neckline_at_lifetime_high(pattern.neckline, lifetime_high)
        if at_high and potential_gain_pct < MIN_GAIN_RECOMMENDED_PCT:
            return []  # hard 40% minimum at the ATH (generalized to CWH in Q&A)

        return [
            Signal(
                symbol=prices.symbol,
                strategy_name=self.name,
                universe_at_signal_time=universe,
                action="BUY",
                trigger_date=trigger_date,
                signal_price=close,
                target_price=final_target,  # NEVER max()'d with lifetime high
                suggested_position_pct=3.0,
                requires_human_confirmation=True,
                rationale=(
                    f"{'Complex ' if pattern.is_complex else ''}Cup with Handle "
                    f"candidate: horizontal neckline {pattern.neckline:.2f}, cup "
                    f"low {pattern.cup_low:.2f}, handle base breakout closed "
                    f"green at {close:.2f}. Target is the technical target "
                    f"{final_target:.2f} itself - NOT raised to the lifetime "
                    f"high {lifetime_high:.2f} (Section 3.2). Potential gain "
                    f"{potential_gain_pct:.1f}% "
                    f"({'meets' if potential_gain_pct >= MIN_GAIN_RECOMMENDED_PCT else 'below'} "
                    f"the recommended 40% filter). REQUIRES HUMAN CONFIRMATION "
                    f"of the pattern before any trade."
                ),
                metadata={
                    "neckline": pattern.neckline,
                    "cup_low": pattern.cup_low,
                    "technical_target": final_target,
                    "lifetime_high": lifetime_high,
                    "is_complex": pattern.is_complex,
                    "potential_gain_pct": potential_gain_pct,
                    "meets_recommended_gain_filter": potential_gain_pct
                    >= MIN_GAIN_RECOMMENDED_PCT,
                    "neckline_at_lifetime_high": at_high,
                },
            )
        ]
