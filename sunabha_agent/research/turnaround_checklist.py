"""
Strategy 7 ("Three Times in Three Years") checklist machinery.

Source: master_strategy_kb.md Section 5.1 (the 10 conditions) and the
consolidated pseudocode.

The KB flags this strategy as THE strongest human-in-the-loop candidate in
the whole framework (Section 5.5 flag 1): conditions 1, 6 and 7 are pure
arithmetic, condition 2 is a data-driven classification, but conditions
3-5 ("the reason for the decline no longer applies", "proven track
record", "good future growth prospect") are open-ended business-research
tasks. This module therefore produces a structured CHECKLIST rather than
a bare yes/no: every condition becomes a ChecklistItem with a status of
PASS / FAIL / NEEDS_RESEARCH (plus INFO for the exit rules and the
non-computable condition 10, kept for source fidelity).

Research items can be delegated to a pluggable ResearchProvider (e.g. the
Claude-backed one in claude_research.py); with no provider they stay
NEEDS_RESEARCH and carry the exact question a human should answer. Either
way the final output is something the user reviews before any trade -
the strategy layer never treats this checklist as auto-executable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional, Protocol

from sunabha_agent.data.models import Fundamentals, PriceSeries

# Section 5.1 hard numeric thresholds (course rules).
MIN_HISTORICAL_DECLINE_PCT = 67.0  # Condition 1
MIN_DECLINE_AT_SIGNAL_PCT = 50.0  # Condition 7

# Condition 2 classification thresholds. The KB gives the three categories
# but NO numeric cutoffs for "revenue declined" / "profit declined" - these
# are OUR diagnostic defaults, and the classification is explicitly
# diagnostic-only (Section 5.5 flag 2): it never gates eligibility.
REVENUE_IMPACT_PCT = 10.0
PROFIT_IMPACT_PCT = 20.0


class ChecklistStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NEEDS_RESEARCH = "NEEDS_RESEARCH"
    INFO = "INFO"  # informational item (exit rules, condition 10) - never gates


@dataclass(frozen=True)
class ResearchAnswer:
    status: ChecklistStatus  # PASS / FAIL / NEEDS_RESEARCH only
    detail: str


class ResearchProvider(Protocol):
    """Anything that can answer an open-ended research question about a
    stock - an LLM call, a human-entered answer, a cached prior answer."""

    def research(self, question: str, context: dict) -> ResearchAnswer: ...


@dataclass(frozen=True)
class ChecklistItem:
    condition_number: int
    title: str
    status: ChecklistStatus
    detail: str
    research_question: Optional[str] = None  # set on NEEDS_RESEARCH items

    def as_dict(self) -> dict:
        return {
            "condition": self.condition_number,
            "title": self.title,
            "status": self.status.value,
            "detail": self.detail,
            "research_question": self.research_question,
        }


@dataclass
class TurnaroundChecklist:
    symbol: str
    as_of: date
    items: list[ChecklistItem] = field(default_factory=list)
    decline_category: Optional[str] = None  # "A" / "B" / "C" / None

    def _gating_items(self) -> list[ChecklistItem]:
        """Conditions 1-7 gate entry; 8-10 are exit rules / mindset (INFO)."""
        return [i for i in self.items if 1 <= i.condition_number <= 7]

    @property
    def has_hard_failures(self) -> bool:
        return any(i.status == ChecklistStatus.FAIL for i in self._gating_items())

    @property
    def is_fully_confirmed(self) -> bool:
        """Every gating condition is a confirmed PASS - nothing failed AND
        nothing still awaiting research."""
        return all(i.status == ChecklistStatus.PASS for i in self._gating_items())

    @property
    def open_research_questions(self) -> list[str]:
        return [
            i.research_question
            for i in self._gating_items()
            if i.status == ChecklistStatus.NEEDS_RESEARCH and i.research_question
        ]

    def as_dicts(self) -> list[dict]:
        return [i.as_dict() for i in self.items]


def _post_peak_decline_pct(prices: PriceSeries) -> float:
    """Condition 1 measures the HISTORICAL fall: lifetime high down to the
    lowest low AFTER that high (not the current price - that's Condition 7)."""
    candles = prices.candles
    peak_idx = max(range(len(candles)), key=lambda i: candles[i].high)
    lifetime_high = candles[peak_idx].high
    trough = min(c.low for c in candles[peak_idx:])
    if lifetime_high <= 0:
        return 0.0
    return (lifetime_high - trough) / lifetime_high * 100


def _drawdown_pct(series: list[float]) -> float:
    """Peak-to-subsequent-trough drawdown of a fundamental series, in %."""
    if not series:
        return 0.0
    peak_idx = max(range(len(series)), key=lambda i: series[i])
    peak = series[peak_idx]
    if peak <= 0:
        return 0.0
    trough = min(series[peak_idx:])
    return (peak - trough) / peak * 100


def _classify_decline(fundamentals: Fundamentals) -> tuple[Optional[str], str]:
    """Condition 2's A/B/C classification (diagnostic only - shapes HOW
    conditions 3-6 get verified, never gates by itself)."""
    rev = fundamentals.revenue_ttm_history_cr
    profit = fundamentals.net_profit_ttm_history_cr
    if not rev or not profit:
        return None, "TTM revenue/profit history unavailable - cannot classify."

    rev_dd = _drawdown_pct(rev)
    profit_dd = _drawdown_pct(profit)
    if rev_dd >= REVENUE_IMPACT_PCT:
        return "A", (
            f"Category A - business itself impacted: TTM revenue drew down "
            f"{rev_dd:.0f}% from its peak (profit drawdown {profit_dd:.0f}%)."
        )
    if profit_dd >= PROFIT_IMPACT_PCT:
        return "B", (
            f"Category B - business intact but profitability impacted: revenue "
            f"held (drawdown {rev_dd:.0f}%) while TTM net profit drew down "
            f"{profit_dd:.0f}% (e.g. interest cost, operating leverage)."
        )
    return "C", (
        f"Category C - business AND financials intact (revenue drawdown "
        f"{rev_dd:.0f}%, profit drawdown {profit_dd:.0f}%): the price fall was "
        f"sentiment/panic-driven."
    )


def _research_item(
    number: int,
    title: str,
    question: str,
    context: dict,
    researcher: Optional[ResearchProvider],
) -> ChecklistItem:
    """Delegate a qualitative condition to the provider if there is one,
    otherwise leave it NEEDS_RESEARCH carrying the question verbatim."""
    if researcher is not None:
        answer = researcher.research(question, context)
        return ChecklistItem(
            condition_number=number,
            title=title,
            status=answer.status,
            detail=answer.detail,
            research_question=question if answer.status == ChecklistStatus.NEEDS_RESEARCH else None,
        )
    return ChecklistItem(
        condition_number=number,
        title=title,
        status=ChecklistStatus.NEEDS_RESEARCH,
        detail="No research provider configured - answer this manually.",
        research_question=question,
    )


def build_checklist(
    prices: PriceSeries,
    fundamentals: Optional[Fundamentals],
    researcher: Optional[ResearchProvider] = None,
) -> TurnaroundChecklist:
    """Evaluate the 10 conditions of Section 5.1 for one stock."""
    symbol = prices.symbol
    close = prices.latest.close
    lifetime_high = prices.lifetime_high
    checklist = TurnaroundChecklist(symbol=symbol, as_of=prices.latest.date)
    items = checklist.items

    # --- Condition 1: fell >= 67% from lifetime high at some point.
    historical_decline = _post_peak_decline_pct(prices)
    items.append(
        ChecklistItem(
            1,
            "Historical decline >= 67% from lifetime high",
            ChecklistStatus.PASS
            if historical_decline >= MIN_HISTORICAL_DECLINE_PCT
            else ChecklistStatus.FAIL,
            f"Post-peak decline {historical_decline:.1f}% from lifetime high "
            f"{lifetime_high:.2f} (threshold {MIN_HISTORICAL_DECLINE_PCT:.0f}%).",
        )
    )

    # --- Condition 2: classify the decline (diagnostic, never gates).
    if fundamentals is not None:
        category, detail = _classify_decline(fundamentals)
    else:
        category, detail = None, "No fundamentals provided - cannot classify."
    checklist.decline_category = category
    items.append(
        ChecklistItem(
            2,
            "Decline cause classified (A: business / B: financials / C: sentiment)",
            ChecklistStatus.PASS if category else ChecklistStatus.NEEDS_RESEARCH,
            detail,
            research_question=None
            if category
            else f"Classify the cause of {symbol}'s price decline into Category "
            f"A (business impacted), B (profitability impacted), or C "
            f"(sentiment only).",
        )
    )

    research_context = {
        "symbol": symbol,
        "decline_category": category,
        "revenue_ttm_history_cr": fundamentals.revenue_ttm_history_cr if fundamentals else [],
        "net_profit_ttm_history_cr": fundamentals.net_profit_ttm_history_cr
        if fundamentals
        else [],
        "sector": fundamentals.sector if fundamentals else None,
    }

    # --- Condition 3: the reason must no longer exist TODAY. Open-ended
    # current-events verification - the core research task of this strategy.
    items.append(
        _research_item(
            3,
            "Reason for the decline no longer applies today",
            f"{symbol}'s decline was classified as Category {category or '?'} "
            f"({detail}) Verify whether the specific cause of that decline has "
            f"been resolved/expired and no longer applies today (Section 5.1 "
            f"Condition 3). Cite the evidence.",
            research_context,
            researcher,
        )
    )

    # --- Condition 4: proven pre-decline track record. A weak quantitative
    # proxy exists (did revenue AND profit grow INTO their peaks?), so use it
    # for a PASS, but never hard-FAIL on data that may simply be truncated.
    cond4 = None
    if fundamentals is not None:
        rev = fundamentals.revenue_ttm_history_cr
        profit = fundamentals.net_profit_ttm_history_cr
        if len(rev) >= 4 and len(profit) >= 4:
            if max(rev) > rev[0] and max(profit) > profit[0]:
                cond4 = ChecklistItem(
                    4,
                    "Proven track record before the decline",
                    ChecklistStatus.PASS,
                    f"Revenue grew {rev[0]:.0f} -> peak {max(rev):.0f} cr and net "
                    f"profit {profit[0]:.0f} -> peak {max(profit):.0f} cr before "
                    f"the decline.",
                )
    if cond4 is None:
        cond4 = _research_item(
            4,
            "Proven track record before the decline",
            f"Verify {symbol} had a demonstrated history of solid revenue and "
            f"profit growth BEFORE its decline - a previously-good business "
            f"that hit a specific problem, not a perennial struggler "
            f"(Section 5.1 Condition 4).",
            research_context,
            researcher,
        )
    items.append(cond4)

    # --- Condition 5: good future growth prospect - pure Video 1-style
    # qualitative judgment, always a research task.
    items.append(
        _research_item(
            5,
            "Good future growth prospect",
            f"Assess {symbol}'s future growth prospects using the Video 1 "
            f"framework (low penetration / long growth runway) - re-confirm for "
            f"this specific company, do not assume from conditions 1-4 "
            f"(Section 5.1 Condition 5).",
            research_context,
            researcher,
        )
    )

    # --- Condition 6: latest quarterly result shows clear improvement.
    # YoY comparison, NEVER sequential QoQ (Section 4.12 - seasonality).
    quarters = fundamentals.quarterly_net_profit_cr if fundamentals else []
    if len(quarters) >= 5:
        latest, yoy = quarters[-1], quarters[-5]
        is_record = latest >= max(quarters)
        improved = latest > yoy
        items.append(
            ChecklistItem(
                6,
                "Latest quarterly result shows clear improvement (YoY)",
                ChecklistStatus.PASS if improved else ChecklistStatus.FAIL,
                f"Latest quarterly net profit {latest:.0f} cr vs same quarter "
                f"last year {yoy:.0f} cr"
                + (" - a new quarterly RECORD." if is_record and improved else "."),
            )
        )
    else:
        items.append(
            ChecklistItem(
                6,
                "Latest quarterly result shows clear improvement (YoY)",
                ChecklistStatus.NEEDS_RESEARCH,
                "Fewer than 5 quarters of net profit history - cannot compute "
                "the YoY comparison (Section 4.12 forbids sequential QoQ).",
                research_question=f"Does {symbol}'s latest quarterly result show "
                f"clear YoY improvement, ideally a new quarterly record?",
            )
        )

    # --- Condition 7: STILL >= 50% below lifetime high right now.
    current_decline = (
        (lifetime_high - close) / lifetime_high * 100 if lifetime_high > 0 else 0.0
    )
    items.append(
        ChecklistItem(
            7,
            "Price still >= 50% below lifetime high at signal time",
            ChecklistStatus.PASS
            if current_decline >= MIN_DECLINE_AT_SIGNAL_PCT
            else ChecklistStatus.FAIL,
            f"Current price {close:.2f} is {current_decline:.1f}% below lifetime "
            f"high {lifetime_high:.2f} (threshold {MIN_DECLINE_AT_SIGNAL_PCT:.0f}% - "
            f"if the market already re-rated the stock, the entry window is closed).",
        )
    )

    # --- Conditions 8-10: exit rules and mindset, recorded for review
    # completeness (INFO - they never gate entry).
    items.append(
        ChecklistItem(
            8,
            "Exit rule: book profit at +100% within 12 months",
            ChecklistStatus.INFO,
            "Default exit (Section 5.1 Condition 8). The instructor's own "
            "documented deviation (JP Power) is a user-level override, never "
            "silent agent behavior (Section 5.5 flag 3).",
        )
    )
    items.append(
        ChecklistItem(
            9,
            "Exit rule: else hold (no time limit) until the original lifetime high",
            ChecklistStatus.INFO,
            "No stop-loss, no re-evaluation deadline - explicitly a multi-year "
            "hold if necessary (Section 5.1 Condition 9).",
        )
    )
    items.append(
        ChecklistItem(
            10,
            "Mindset condition ('blessings') - not computable",
            ChecklistStatus.INFO,
            "Logged for source fidelity (Section 5.1 Condition 10). Operational "
            "proxy already covered: do not panic-sell during long flat periods.",
        )
    )
    return checklist
