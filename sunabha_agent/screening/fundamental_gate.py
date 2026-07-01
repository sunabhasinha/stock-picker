"""
The fundamental screening gate.

This is the layer the course treats as non-negotiable (master_strategy_kb.md
Section 4.14: "stock selection is more important than technical analysis").
No strategy signal should ever be surfaced to the user without first passing
through here.

Three things happen in this module, in this order of authority:

1. HARD GATES - V200 quantitative qualification, and the promoter-pledging
   disqualifier. Fail either of these and the stock is rejected outright,
   no matter what a chart pattern says.
2. SOFT FLAGS - weak-hands concentration, situational risk flags (merger,
   structural decline, sector caution). These don't reject a stock, but
   they get attached to it so the user sees the caveat.
3. TIERING - ROCE / Debt-Equity "best" vs "very good" bands, used only for
   RANKING when multiple stocks already passed the hard gates and there's
   limited capital to choose between them (Section 4.6, 4.8, 4.20).

V40 / V40 Next membership is NOT computed here - those are qualitative,
sector-leadership judgments (Section 1.2) that this course's own creator
maintains as a curated list rather than re-deriving live. We load that list
from config/v40_v40next.yaml (transcribed directly from the user-supplied
data) and treat it as authoritative. V200 membership, by contrast, IS a
pure quantitative screen and so it's fully computed here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from sunabha_agent.data.models import CompanyType, Fundamentals, Universe


class GateResult(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


@dataclass
class ScreeningReport:
    """Full, transparent record of why a stock passed or failed. Every field
    here exists so the agent never has to say 'trust me' - it can always show
    its work, which matters a lot more than usual given this is real money."""

    symbol: str
    universe: Universe
    gate_result: GateResult
    fail_reasons: list[str]
    soft_flags: list[str]
    roce_tier: str | None  # "best" | "very_good" | "fails_gate" | "n/a (BFSI)"
    debt_equity_tier: str | None
    pledged_pct_of_total_company: float


# ---------------------------------------------------------------------------
# V200 qualification (Section 1.3, refined by Section 4.6/4.8 tiering)
# ---------------------------------------------------------------------------

V200_NET_PROFIT_FLOOR_CR = 200.0
V200_ROCE_FLOOR_PCT = 20.0
V200_ROE_FLOOR_PCT = 10.0  # banks / NBFC / functionally-lending
V200_DEBT_EQUITY_CEILING = 0.25


def is_bfsi_exempt(company_type: CompanyType) -> bool:
    """Banks, NBFCs, and functionally-lending businesses (margin-lending
    brokers, etc.) skip the ROCE/debt-equity test and use ROE instead.
    Section 1.3 exception, generalized in Section 4.8 to cover Angel-One-
    style functional NBFCs even without formal NBFC registration."""
    return company_type in (
        CompanyType.BANK,
        CompanyType.NBFC,
        CompanyType.FUNCTIONALLY_LENDING,
    )


def qualifies_for_v200(f: Fundamentals) -> tuple[bool, list[str]]:
    """Returns (qualifies, reasons_for_failure)."""
    reasons: list[str] = []

    if f.net_profit_ttm_cr <= V200_NET_PROFIT_FLOOR_CR:
        reasons.append(
            f"TTM net profit {f.net_profit_ttm_cr:.1f}cr does not exceed "
            f"{V200_NET_PROFIT_FLOOR_CR:.0f}cr floor"
        )

    if is_bfsi_exempt(f.company_type):
        if f.roe_pct is None or f.roe_pct <= V200_ROE_FLOOR_PCT:
            reasons.append(
                f"ROE {f.roe_pct} does not exceed {V200_ROE_FLOOR_PCT:.0f}% floor "
                f"(BFSI/functionally-lending company - debt/equity not applicable)"
            )
    else:
        if f.roce_pct is None or f.roce_pct <= V200_ROCE_FLOOR_PCT:
            reasons.append(
                f"ROCE {f.roce_pct} does not exceed {V200_ROCE_FLOOR_PCT:.0f}% floor"
            )
        if f.debt_to_equity is None or f.debt_to_equity >= V200_DEBT_EQUITY_CEILING:
            reasons.append(
                f"Debt/Equity {f.debt_to_equity} does not stay below "
                f"{V200_DEBT_EQUITY_CEILING} ceiling"
            )

    return (len(reasons) == 0, reasons)


# ---------------------------------------------------------------------------
# Hard disqualifier: promoter pledging (Section 4.10)
# ---------------------------------------------------------------------------

PLEDGING_DISQUALIFIER_THRESHOLD_PCT = 10.0


def fails_pledging_disqualifier(f: Fundamentals) -> tuple[bool, str | None]:
    """
    promoter_holding% * pledging%-of-that-holding >= 10% of TOTAL company
    shares => reject outright, regardless of every other qualifying metric.

    This is the one rule in the whole framework explicitly described as
    zero-tolerance ("never compromise in selection of a company... there is
    no need to take any risk") - Section 4.10. It overrides V40/V40Next
    membership too: a stock can be on the curated V40 list and still get
    rejected here if pledging has since crossed this line, since pledging
    is a live, fast-moving figure that a static list can't capture.
    """
    pct = f.pledged_pct_of_total_company
    if pct >= PLEDGING_DISQUALIFIER_THRESHOLD_PCT:
        return True, (
            f"Promoter pledging disqualifier triggered: {pct:.2f}% of total "
            f"company shares are pledged by promoters "
            f"({f.promoter_holding_pct:.1f}% holding x "
            f"{f.promoter_pledging_pct_of_holding:.1f}% pledged of that holding), "
            f">= {PLEDGING_DISQUALIFIER_THRESHOLD_PCT:.0f}% threshold."
        )
    return False, None


# ---------------------------------------------------------------------------
# Soft flags (Section 4.9, 6.4) - never reject, always attach as a caveat
# ---------------------------------------------------------------------------

WEAK_HANDS_SOFT_CAUTION_PCT = 30.0


def compute_soft_flags(f: Fundamentals) -> list[str]:
    flags: list[str] = []

    if f.weak_hands_pct > WEAK_HANDS_SOFT_CAUTION_PCT:
        flags.append(
            f"Weak-hands (retail public, excl. HNI) holding is "
            f"{f.weak_hands_pct:.1f}%, above the {WEAK_HANDS_SOFT_CAUTION_PCT:.0f}% "
            f"soft-caution threshold (Section 4.9). Not disqualifying, but worth noting."
        )

    if f.under_merger:
        flags.append(
            "Stock is currently subject to an announced merger/amalgamation. "
            "Section 6.4 flags minority-shareholder compression risk in such "
            "situations as a named, recurring pattern (Tata group examples) - "
            "review deal terms manually before treating any signal as reliable."
        )

    return flags


# ---------------------------------------------------------------------------
# Tiering for ranking (Section 4.6, 4.8) - NOT used to disqualify
# ---------------------------------------------------------------------------


def roce_tier(f: Fundamentals) -> str:
    if is_bfsi_exempt(f.company_type):
        return "n/a (BFSI - ROE used instead, see roe_pct)"
    if f.roce_pct is None:
        return "unknown"
    if f.roce_pct > 30:
        return "best"
    if f.roce_pct > 20:
        return "very_good"
    return "fails_gate"


def debt_equity_tier(f: Fundamentals) -> str:
    if is_bfsi_exempt(f.company_type):
        return "n/a (BFSI - debt/equity not applicable)"
    if f.debt_to_equity is None:
        return "unknown"
    if f.debt_to_equity < 0.10:
        return "best"
    if f.debt_to_equity < 0.25:
        return "very_good"
    return "fails_gate"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def screen(f: Fundamentals, declared_universe: Universe) -> ScreeningReport:
    """
    Run the full gate for one stock.

    `declared_universe` comes from the curated V40/V40Next list lookup (done
    by the caller, see sunabha_agent.data.universe_lists) OR is computed here
    on the fly for V200 candidates. The pledging disqualifier and soft flags
    apply uniformly regardless of which universe a stock claims membership in.
    """
    fail_reasons: list[str] = []

    if declared_universe == Universe.V200:
        qualifies, reasons = qualifies_for_v200(f)
        if not qualifies:
            fail_reasons.extend(reasons)

    pledging_fails, pledging_reason = fails_pledging_disqualifier(f)
    if pledging_fails:
        fail_reasons.append(pledging_reason)  # type: ignore[arg-type]

    soft_flags = compute_soft_flags(f)

    return ScreeningReport(
        symbol=f.symbol,
        universe=declared_universe,
        gate_result=GateResult.FAIL if fail_reasons else GateResult.PASS,
        fail_reasons=fail_reasons,
        soft_flags=soft_flags,
        roce_tier=roce_tier(f),
        debt_equity_tier=debt_equity_tier(f),
        pledged_pct_of_total_company=f.pledged_pct_of_total_company,
    )
