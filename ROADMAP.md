# ROADMAP — Stock Picker (Sunabha Agent)

Status as of **2026-07-04**: the original build plan is complete and live-verified.
All 8 strategies, the fundamental gate, the Category engine, live data
(Screener.in + Yahoo), the CLI scan, and the browser UI are built, with 161
passing tests. This doc logs what remains, with enough context to pick any item
up cold. Keep it updated as items land (same convention as CLAUDE.md).

## How to run the tool today

```bash
python3 -m sunabha_agent.web            # browser UI at http://127.0.0.1:8788/
python3 -m sunabha_agent.scan --category category_2 [--symbols TCS,TITAN] [--positions positions.json]
```

One-time machine setup: `pip install pyyaml yfinance`; on macOS with
python.org Python, also run "Install Certificates.command" (else every HTTPS
fetch fails with SSL certificate errors).

---

## Product pivot track (ADR-0005 — multi-user hosted app)

Staged milestones, each its own spec + PR. The engine stays a pure library
throughout; the shell carries the dependencies.

- **M1 — user data layer** (`docs/specs/user-data-layer.md`, DONE 2026-07-13):
  Supabase Postgres + SQLAlchemy + Alembic; portfolios/holdings/
  signal_events/scan_runs/shadow_signals; RLS from day one; proven against
  existing single-user flows.
- **M2 — auth** (`docs/specs/auth-layer.md`, ADR-0006, DONE 2026-07-13): OWN auth,
  learning-weighted — argon2id, server-side opaque sessions, verification/
  reset flows, throttling, FastAPI server. Hosted serving still pending
  (amends AGENTS.md #6 when it ships).
- **M3 — product**: per-user dashboard, confirm/dismiss on signals,
  scheduled scans writing signal_events.

Note: pivot items subsume parts of the backlog below (shadow-performance
persistence lands in M1's shadow_signals table).

## Backlog (in order of practical value)

### 1. On-disk cache for fetched data
- **Problem:** every scan re-pulls the FULL price history and the Screener page
  for every symbol. A full V40 scan takes minutes, hammers both sources, and
  repeat scans the same day redo 100% of the work.
- **Shape:** a cache layer wrapping both fetchers (they already take injectable
  `transport` callables — a caching transport is the natural seam). Keyed
  symbol + date; prices can be cached incrementally (append new candles instead
  of re-fetching 30 years). Suggested location: `sunabha_agent/data/cache.py`,
  files under `~/.sunabha_agent/cache/` or a repo-local `.cache/` (gitignored).
- **Care:** `lifetime_high` needs the full history — an incremental cache must
  never silently truncate old candles (CLAUDE.md rule 6).

### 2. debt_to_equity source for the V200 gate
- **Problem:** Screener.in's default top-ratios block does NOT include debt to
  equity, so `Fundamentals.debt_to_equity` comes back `None`, and the V200 gate
  treats `None` as failing — V200 qualification can't fully evaluate yet.
- **Options:** (a) parse Screener's balance-sheet section and compute
  borrowings/equity ourselves; (b) a logged-in Screener session with a custom
  ratio column; (c) another source. Option (a) is likely simplest and keeps the
  no-login design.
- **Where:** `sunabha_agent/data/fetcher.py` (`parse_screener_html`), tests in
  `tests/test_fetcher.py` with an extended fixture.

### 3. Shadow-performance persistence (Section 6.3 recommended feature)
- **Problem:** `shadow_signals()` (category_engine.py) already computes what the
  non-selected categories WOULD have signalled today, but nothing stores it —
  so after the 1-year commitment there's no comparative record to decide
  whether to switch categories.
- **Shape:** append each day's shadow signals to a local JSONL/SQLite log keyed
  by date + category; a small report command ("how would category_3 have done
  this year?"). Shadow trades are hypothetical — never executed, never mixed
  with real positions.

### 4. V200 screening pass over the full NSE list
- **Problem:** V20 (Category 4) is allowed on V200 stocks, but no V200 list
  exists — it's a live quantitative screen (Section 1.3), not a curated file,
  and the scan currently requires V200 symbols to be passed explicitly.
- **Shape:** a periodic job that walks the full NSE symbol list (needs a source
  for that list — NSE's equity master CSV or similar), runs
  `qualifies_for_v200()` on each, and writes a dated V200 candidate list the
  scanner can consume. Depends on item 1 (cache) to be polite about ~1,600
  fetches; blocked on item 2 (debt_to_equity) for correct gating.

### Smaller / opportunistic
- **Positions UI:** the web UI takes holdings as raw JSON — a small add/edit
  form would remove the most error-prone manual step.
- **Scheduled daily run:** cron/launchd invoking the scan and writing the
  report to a file (or notifying) — the web UI already renders any saved report
  shape.
- **Knoxville tolerance review:** min-lookback 4 bars came from the reference
  ports, not the course (documented in knoxville_strategy.py) — worth a
  sensitivity check against real charts someday.
- **Pattern-tolerance calibration:** the RHS/CWH tolerances in
  `pattern_common.py` (neckline 2%, base 5%, pivot window 2, "near lifetime
  high" 5%) are our defaults, not course rules — revisit once there's a corpus
  of human-confirmed/rejected candidates to calibrate against.

## Known caveats (documented, accepted for now)
- Pattern detection is candidate-finding for HUMAN review — every RHS/CWH/V10/
  Strategy 7 signal carries `requires_human_confirmation=True` by design.
- Strategy 7's Claude research provider has no live web access — it answers
  UNCLEAR rather than guessing; open questions ride along in the signal.
- Yahoo prices are split-adjusted (TradingView basis). If a symbol's Yahoo
  ticker differs from the NSE symbol beyond the `.NS` suffix, the fetch errors
  and the scan reports it (that's how the two config typos were caught).
