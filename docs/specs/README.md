# Specs (L2 — intent)

One file per feature: what should be TRUE when the work is done. The human
writes this (10 minutes); the agent implements from it. Everything not
constrained here is delegated judgment — which the implementer must exercise
AND record (PR judgment-calls section + journal), never decide silently.

Why this layer exists: this project's journal review (2026-07-11) found
"agent guessed" fired in 5 of 8 build sessions, always because intent was
stated qualitatively. The fix is quantifying tolerances up front.

Note: the strategy rules themselves are specified by `master_strategy_kb.md`
(the course knowledge base) — that document IS the L2 spec for all trading
logic and is never restated here. This directory is for features built
AROUND that logic (UI, tooling, data plumbing).

Lifecycle: `status: proposed` -> `accepted` (ready to build) -> `done`
(link the PR). Keep specs after completion — they are the onboarding trail.

Use `TEMPLATE.md`.
