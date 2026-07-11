# Module: screening (the fundamental gate)

Purpose: the non-negotiable quality layer (KB §4.14) — V200 quantitative
qualification, the promoter-pledging hard disqualifier, soft flags, and
ROCE/D-E tiering used for ranking.

Provides: `screen(fundamentals, universe) -> ScreeningReport`,
`qualifies_for_v200`, `roce_tier`, `debt_equity_tier`,
`fails_pledging_disqualifier`.

Depends on: data.models only.

Invariants:
- Pledging formula is promoter_holding% x pledging%-of-holding, NEVER the
  pledging percent alone (KB §4.10; a test exists specifically for this).
- Tiering ranks, it never disqualifies. Soft flags attach, never reject.
- `debt_to_equity=None` fails the V200 gate (known data gap — Screener's
  default ratios omit it; see ROADMAP item 2).

Blast radius: the portfolio engine calls `screen()` before ANY strategy
runs — changes here silently change which stocks can signal at all, in
every category. Threshold changes must cite a KB section.

Tests: tests/test_fundamental_gate.py (written against real cited figures).
