# Module: research (Strategy 7's checklist machinery)

Purpose: the 10-condition turnaround checklist (KB §5.1) as structured
data, with qualitative conditions delegated to a pluggable
ResearchProvider.

Provides: `build_checklist`, `TurnaroundChecklist`, `ChecklistStatus`,
`ResearchProvider` protocol (turnaround_checklist.py);
`ClaudeResearchProvider` (claude_research.py, stdlib urllib, ANTHROPIC_API_KEY).

Depends on: data.models. No third-party deps (ADR-0002).

Invariants:
- Conditions 1/6/7 are computed (67% decline uses the POST-PEAK trough;
  condition 6 is YoY per KB §4.12); condition 2 is diagnostic-only.
- Research answers degrade to NEEDS_RESEARCH on ANY error — never crash,
  never guess: the provider is instructed to answer UNCLEAR without
  current data (ADR-0003).
- INFO items (8/9/10) never gate.

Blast radius: consumed only by TurnaroundStrategy and (via it) the
engine/scan. Checklist dict shape appears in signal metadata rendered by
the web UI.

Tests: tests/test_turnaround_checklist.py (provider tested with fake
transports — offline).
