# Module: portfolio (the Category engine — top-level switchboard)

Purpose: the four KB §6.2 Categories, signal generation for ONE selected
category, §4.20 candidate ranking, §6.3 holding reconciliation, shadow
tracking.

Provides: `CategoryEngine`, `CATEGORY_1..4` / `PRESET_CATEGORIES`,
`custom_category`, `ReconciliationAction`, `shadow_signals`.

Depends on: data.models, screening.fundamental_gate, ALL strategy classes,
research (via TurnaroundStrategy injection).

Invariants:
- No default category — the caller must pick exactly one (KB §6.3).
- The fundamental gate runs BEFORE any strategy; gate-fail = no signals.
- Nothing fires outside the category's universe (this is also what narrows
  Strategy 7 to V40 under Category 2).
- Trade routing: each strategy gets only ITS OWN open trades, except V10
  which gets all (see strategies/MODULE.md).
- A gate-failing loss-maker reconciles to REVIEW, never auto-sell (the KB
  never commands a sale — inferred handling, flagged as such).

Blast radius: scan and web build directly on this. Category definitions
changing = every scan's output changes.

Tests: tests/test_category_engine.py.
