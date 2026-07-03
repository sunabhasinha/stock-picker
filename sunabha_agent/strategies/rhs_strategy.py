"""
Strategy 4: Reverse Head & Shoulder (RHS).

Source: master_strategy_kb.md Section 3.1 and the consolidated pseudocode.

Geometry: left shoulder(s) -> head -> right shoulder, where the three (or
more) connecting points between them lie on a HORIZONTAL neckline (sloped
necklines are explicitly invalid per the course), and the head is strictly
the deepest point of the whole pattern. More than 3 connecting points means
extra shoulders -> "Complex RHS", flagged as higher-confidence.

Buy: at the FIRST right shoulder's own base-formation breakout (green
candle, closing basis) - NOT at the neckline breakout the textbooks teach.
Sell: at MAX(technical target, lifetime high) - the course's reasoning is
that an operator accumulating at this scale is targeting at least the
lifetime high. This is the key difference from Cup with Handle, which
never raises its target to the lifetime high.

Every signal carries requires_human_confirmation=True: the KB (Section 3.6
flag 1) is explicit that pattern recognition is fuzzier than Strategies
1-3 and should be human-reviewed, never auto-executed.

No averaging within RHS itself - averaging on top of an RHS entry is
Strategy 6 (V10), a separate strategy layered on the open RHS window.
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
class RHSPattern:
    neckline: float
    head_low: float
    shoulder_lows: tuple[float, ...]  # left shoulders, chronological
    right_shoulder_low: float
    peak_indices: tuple[int, ...]  # the connecting points, chronological
    is_complex: bool  # more than one left shoulder (Section 3.1 rule 3)
    breakout: BaseBreakout


def detect_rhs(candles) -> RHSPattern | None:
    """
    Find an RHS pattern whose right-shoulder base breakout fired on the
    LATEST candle. Returns None for "no pattern" and "not enough data"
    alike, per the base-class no-raise contract.

    Head placement: the head is the trough between the LAST two connecting
    points. Anything after the final connecting point is the right shoulder
    (we always buy at the FIRST right shoulder, so at signal time exactly
    one right shoulder exists - Section 3.1 buy rule).
    """
    breakout = detect_base_breakout(candles)
    if breakout is None:
        return None

    for chain in neckline_chains(candles, find_pivot_highs(candles)):
        if len(chain) < 3:  # RHS needs >= 3 connecting points
            continue
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

        head_low = trough_lows[-1]
        shoulder_lows = tuple(trough_lows[:-1])
        if any(head_low >= s for s in shoulder_lows):
            continue  # head must be strictly the deepest point (rule 4)

        neckline = neckline_level(candles, chain)
        if breakout.breakout_close >= neckline:
            # Section 3.1: the buy is the right shoulder's own base breakout,
            # BEFORE price has reached/broken the neckline. A close already
            # at/above the neckline means this is not that entry - and, on
            # decades-long histories, it is how a years-old neckline gets
            # spuriously matched against today's far-higher prices (found
            # live: TITAN "breaking out" at 4404 vs a 1201 neckline).
            continue
        right_shoulder = candles[chain[-1] + 1 : len(candles) - 1]
        right_shoulder_low = min(c.low for c in right_shoulder)
        if right_shoulder_low <= head_low or right_shoulder_low >= neckline:
            continue  # the right shoulder must dip, but never below the head

        return RHSPattern(
            neckline=neckline,
            head_low=head_low,
            shoulder_lows=shoulder_lows,
            right_shoulder_low=right_shoulder_low,
            peak_indices=tuple(chain),
            is_complex=len(chain) > 3,
            breakout=breakout,
        )
    return None


class RHSStrategy(Strategy):
    name = "Reverse Head & Shoulder Strategy"
    allowed_universes = (Universe.V40, Universe.V40_NEXT)
    max_concurrent_trades_per_stock = 1  # V10 averaging is its own strategy;
    # the combined 3-trade / 9% ceiling across RHS+V10 is the portfolio
    # layer's job (Section 3.3 combined sizing)
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

        # --- SELL: the target was fixed at entry (stored on the Signal);
        # the pattern itself is long gone by the time price reaches it, so
        # the sell check must not depend on re-detecting anything.
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
                            f"Price {close:.2f} reached the target "
                            f"{trade.target_price:.2f} fixed at entry (higher of "
                            f"technical target and lifetime high, Section 3.1). "
                            f"Full exit - no partial booking (Section 3.5)."
                        ),
                        metadata={"closes_trade_entered_on": trade.trigger_date.isoformat()},
                    )
                ]

        if open_own:
            return []  # one RHS trade per stock; averaging belongs to V10

        pattern = detect_rhs(prices.candles)
        if pattern is None:
            return []

        tech_target = technical_target(pattern.neckline, pattern.head_low)
        lifetime_high = prices.lifetime_high
        final_target = max(tech_target, lifetime_high)  # Section 3.1: always
        # sell at whichever of (technical target, lifetime high) is HIGHER
        potential_gain_pct = (tech_target - close) / close * 100
        at_high = neckline_at_lifetime_high(pattern.neckline, lifetime_high)
        if at_high and potential_gain_pct < MIN_GAIN_RECOMMENDED_PCT:
            return []  # hard 40% minimum when the pattern forms at the ATH

        return [
            Signal(
                symbol=prices.symbol,
                strategy_name=self.name,
                universe_at_signal_time=universe,
                action="BUY",
                trigger_date=trigger_date,
                signal_price=close,
                target_price=final_target,
                suggested_position_pct=3.0,
                requires_human_confirmation=True,  # Section 3.6 flag 1: pattern
                # candidates are fuzzy - a human must eyeball the chart first
                rationale=(
                    f"{'Complex ' if pattern.is_complex else ''}Reverse Head & "
                    f"Shoulder candidate: horizontal neckline {pattern.neckline:.2f}, "
                    f"head low {pattern.head_low:.2f}, right-shoulder base breakout "
                    f"closed green at {close:.2f}. Technical target "
                    f"{tech_target:.2f}, lifetime high {lifetime_high:.2f} -> "
                    f"selling at the higher, {final_target:.2f}. Potential gain to "
                    f"technical target {potential_gain_pct:.1f}% "
                    f"({'meets' if potential_gain_pct >= MIN_GAIN_RECOMMENDED_PCT else 'below'} "
                    f"the recommended 40% filter). REQUIRES HUMAN CONFIRMATION of "
                    f"the pattern before any trade. Expect a long, possibly "
                    f"sideways holding period (Section 3.1: 105 to 600+ days in "
                    f"cited examples)."
                ),
                metadata={
                    "neckline": pattern.neckline,
                    "head_low": pattern.head_low,
                    "technical_target": tech_target,
                    "lifetime_high": lifetime_high,
                    "is_complex": pattern.is_complex,
                    "potential_gain_pct": potential_gain_pct,
                    "meets_recommended_gain_filter": potential_gain_pct
                    >= MIN_GAIN_RECOMMENDED_PCT,
                    "neckline_at_lifetime_high": at_high,
                },
            )
        ]
