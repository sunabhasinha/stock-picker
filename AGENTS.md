# AGENTS.md — constitution (L1)

Read this first. It is deliberately small and stable. Detail lives in the
scoped layers below — load them on demand, not all at once.

## What this project is
A Python trading-signal agent implementing the 8 strategies, screening gate,
and portfolio rules of Vivek Singhal's course. **Every threshold in code must
trace to a section number in `master_strategy_kb.md`** (the L2 spec for all
strategy logic). Signals are candidates for a HUMAN to review — nothing in
this codebase executes trades, ever.

## Gates (must pass before any commit)
```bash
python3 -m unittest discover -s tests   # all tests green, no exceptions
```
For changes observable in the running app: also verify live (run the scan or
web UI against real data) — unit-green has missed boundary bugs three times
in this repo's history (see journal.md review 2026-07-11).

## Invariants (non-negotiable)
1. No stop-loss anywhere — foundational course rule (`uses_stop_loss=False`).
2. Pattern/turnaround signals always set `requires_human_confirmation=True`.
3. Quarterly comparisons are YoY, never sequential QoQ (KB §4.12).
4. `lifetime_high` requires FULL listing history — never truncate price data.
5. Dependencies — two zones (ADR-0005): the ENGINE (`sunabha_agent/`) is
   stdlib-only, with `pyyaml` (config) and `yfinance` (fetcher-only, lazily
   imported) the only exceptions, and NEVER imports `app/`. The application
   SHELL (`app/`) may carry dependencies (`app/requirements.txt`). New
   engine deps require an ADR.
6. Web UI binds to 127.0.0.1 only — single-user local tool by design.

## Context layers — where everything lives
| Layer | Question it answers | Location |
|---|---|---|
| L1 Constitution | what is this / what must hold | this file |
| L2 Intent | what should be true | `master_strategy_kb.md` (strategy rules), `docs/specs/` (features) |
| L3 Decisions | why is it like this | `docs/decisions/` (ADRs, append-only) |
| L4 Map | what does my change affect | `MODULE.md` in each package |
| L5 Gates | is it correct | `tests/`, CI (`.github/workflows/ci.yml`) |
| Loop | what are we learning | `journal.md` (append-only + weekly reviews) |
| Backlog | what's next | `ROADMAP.md` |

## Working rules for any agent (any model)
- Before changing a module, read its `MODULE.md`; update it in the SAME
  commit if your change alters its interface, dependencies, or blast radius
  (CI enforces this; escape hatch: `[no-doc-update]` in the commit message
  with a reason).
- Spec silent on an edge case? Make a reasonable choice and RECORD it (PR
  "judgment calls" section + journal entry). Value-laden choices get
  escalated to a human, not decided silently.
- Append a 5-line session entry to `journal.md` at session end (template at
  the top of that file).
- Commit/push only when asked. Branch from `main`; PRs carry a judgment-calls
  section.

## Tool adapters
Claude Code also reads `CLAUDE.md`, which carries the detailed build state
and history for this project. Other agents: `CLAUDE.md` is worth reading as
an extended map, but THIS file is the authority if they ever disagree.
