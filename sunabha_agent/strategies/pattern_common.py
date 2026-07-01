"""
Shared geometric primitives for the chart-pattern strategies:
RHS (Section 3.1), Cup with Handle (Section 3.2).

The course defines these patterns visually, not numerically - the KB's own
build flags (Section 3.6, items 1 and 2) say the neckline horizontality and
"base formation" tightness have no precise thresholds in the source
material, and recommend a human-in-the-loop architecture rather than full
automation. That is exactly what this module supports: it finds CANDIDATE
patterns using conservative, documented tolerances, and the strategies
built on it mark every signal requires_human_confirmation=True. The
tolerances below are our defaults, not course rules - each one is a module
constant precisely so it can be tuned without touching detection logic.
"""

from __future__ import annotations

from dataclasses import dataclass

from sunabha_agent.data.models import Candle

#: Bars on each side that must be strictly lower/higher for a pivot.
PIVOT_WINDOW = 2
#: Max spread between neckline connecting points, as % of the lowest one.
#: Section 3.1 demands a "perfectly horizontal" neckline; real data needs
#: SOME tolerance, so this is kept tight. Sloped necklines must fail this.
NECKLINE_TOLERANCE_PCT = 2.0
#: Base formation ("3 candles can be enough, or it might need more" -
#: Section 3.6 flag 2). We require at least 3, and cap how wide the base's
#: body range may be relative to its bottom.
BASE_MIN_CANDLES = 3
BASE_MAX_RANGE_PCT = 5.0
#: Section 3.1 optional filter: >=40% potential gain recommended; becomes a
#: HARD requirement when the neckline forms at/near the lifetime high.
MIN_GAIN_RECOMMENDED_PCT = 40.0
#: How close (in %) the neckline must be to the lifetime high for the 40%
#: rule to switch from recommended to mandatory. "At or near" is the
#: course's wording; the 5% is our reading of "near".
LIFETIME_HIGH_PROXIMITY_PCT = 5.0


def find_pivot_highs(candles: list[Candle], window: int = PIVOT_WINDOW) -> list[int]:
    """
    Indices whose CLOSE is strictly the highest within +/- window bars.

    Closes, not highs: daily candles routinely open at the prior close, so
    a high-based pivot ties with its neighbour and strict comparison never
    fires. The connecting LEVEL of a pivot is still read from the candle
    body (see neckline_level) per the Section 3.1 wick rules.
    """
    out = []
    for i in range(window, len(candles) - window):
        c = candles[i].close
        if all(candles[j].close < c for j in range(i - window, i + window + 1) if j != i):
            out.append(i)
    return out


def find_pivot_lows(candles: list[Candle], window: int = PIVOT_WINDOW) -> list[int]:
    out = []
    for i in range(window, len(candles) - window):
        c = candles[i].close
        if all(candles[j].close > c for j in range(i - window, i + window + 1) if j != i):
            out.append(i)
    return out


def neckline_chains(
    candles: list[Candle],
    pivot_high_indices: list[int],
    tolerance_pct: float = NECKLINE_TOLERANCE_PCT,
) -> list[list[int]]:
    """
    Split consecutive pivot highs into maximal runs whose connecting levels
    all lie within tolerance of each other. Each run of length >= 2 is a
    candidate horizontal neckline (Section 3.1 rule 2: sloped necklines are
    explicitly invalid, so a run breaks the moment a pivot falls outside
    the band).

    Connecting levels are candle BODY TOPS: Section 3.1 rule 5 says wicks
    may be crossed/ignored when drawing the neckline, but a green candle's
    body must never be crossed - working from body tops respects both.
    """
    chains: list[list[int]] = []
    current: list[int] = []
    for idx in pivot_high_indices:
        if not current:
            current = [idx]
            continue
        levels = [candles[j].body_top for j in current] + [candles[idx].body_top]
        lo, hi = min(levels), max(levels)
        if lo > 0 and (hi - lo) / lo * 100 <= tolerance_pct:
            current.append(idx)
        else:
            chains.append(current)
            current = [idx]
    if current:
        chains.append(current)
    return [c for c in chains if len(c) >= 2]


def neckline_level(candles: list[Candle], chain: list[int]) -> float:
    """The horizontal neckline for a chain: the highest body top among the
    connecting points, so the line never cuts through any of their bodies."""
    return max(candles[i].body_top for i in chain)


@dataclass(frozen=True)
class BaseBreakout:
    """A base formation whose breakout is confirmed on the LATEST candle."""

    base_start: int  # index of the first candle in the base
    base_end: int  # index of the last base candle (the one before breakout)
    base_top: float
    base_bottom: float
    breakout_close: float


def detect_base_breakout(
    candles: list[Candle],
    min_base: int = BASE_MIN_CANDLES,
    max_range_pct: float = BASE_MAX_RANGE_PCT,
) -> BaseBreakout | None:
    """
    Section 3.1 rule (b)-(d): base formation (sideways body range, wicks
    ignored per Section 3.2), then a GREEN candle closing above that range,
    confirmed on a CLOSING basis. The breakout candle must be the latest
    candle - this function answers "did a base breakout fire TODAY".

    The base is extended backwards as far as the candles keep satisfying
    both the range-tightness constraint and staying below the breakout
    close, so the reported extent is the widest defensible base.
    """
    if len(candles) < min_base + 1:
        return None
    breakout = candles[-1]
    if not breakout.is_green:
        return None

    best: BaseBreakout | None = None
    for n in range(min_base, len(candles)):
        base = candles[-1 - n : -1]
        top = max(c.body_top for c in base)
        bottom = min(c.body_bottom for c in base)
        if bottom <= 0 or (top - bottom) / bottom * 100 > max_range_pct:
            break  # adding older candles only widens the range further
        if breakout.close <= top:
            break  # older candles only raise the top; no point continuing
        best = BaseBreakout(
            base_start=len(candles) - 1 - n,
            base_end=len(candles) - 2,
            base_top=top,
            base_bottom=bottom,
            breakout_close=breakout.close,
        )
    return best


def technical_target(neckline: float, deepest_low: float) -> float:
    """Section 3.1 target rule: project the head/cup depth upward from the
    neckline. (Linear scale is assumed throughout - Section 3.1 rule 6.)"""
    return neckline + (neckline - deepest_low)


def neckline_at_lifetime_high(
    neckline: float,
    lifetime_high: float,
    proximity_pct: float = LIFETIME_HIGH_PROXIMITY_PCT,
) -> bool:
    """Is the pattern forming at/near the all-time high? If so, the 40%
    minimum-gain filter is mandatory, not just recommended (Section 3.1 /
    3.2 Q&A rule)."""
    return neckline >= lifetime_high * (1 - proximity_pct / 100)
