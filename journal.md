# Journal — session notes. Append-only. Reviewed weekly.

Template:
## <date> — <task, one line>
- Stepped in: <no / what the human had to correct or redirect>
- Agent guessed: <no / what was ambiguous, and what was chosen>
- Caught late: <no / anything tests or review missed until later>
- Chores: <the mechanical steps performed this session>

---

## 2026-07-02 — Fix broken rename, add master KB (PR #1) [backfilled]
- Stepped in: yes — project had been renamed (vivek_agent -> sunabha_agent)
  with every import left stale; whole suite was red on arrival
- Agent guessed: no
- Caught late: repo had committed .pyc/.DS_Store and no .gitignore
- Chores: branch, commit, PR, post-merge sync, CLAUDE.md updated

## 2026-07-02 — Strategy 2: Knoxville Divergence (PR #2) [backfilled]
- Stepped in: no
- Agent guessed: yes — KB doesn't define min divergence lookback (took 4 from
  the open-source ports) or momentum form (ratio, matching both ports)
- Caught late: no
- Chores: branch, commit, PR with judgment-calls section, sync, CLAUDE.md

## 2026-07-02 — Strategies 4/5/6: RHS, CWH, V10 (PR #3) [backfilled]
- Stepped in: no
- Agent guessed: yes — KB leaves neckline tolerance (2%), base tightness (5%),
  pivot window (2), "near lifetime high" (5%) unquantified; all made constants
- Caught late: no (but see 07-04 — two of these detectors had a latent bug)
- Chores: branch, commit, PR, sync, CLAUDE.md

## 2026-07-02 — Strategy 7 + research checklist (PR #4) [backfilled]
- Stepped in: no
- Agent guessed: yes — Condition 2's A/B/C drawdown thresholds (10%/20%);
  NSE gate made default-closed (None refuses); BUY candidates may carry open
  research questions
- Caught late: no
- Chores: branch, commit, PR, sync, CLAUDE.md

## 2026-07-02 — Portfolio Category engine (PR #5) [backfilled]
- Stepped in: no
- Agent guessed: yes — "similar potential gain" bucketed at 5%; gate-failing
  loss-maker gets REVIEW not auto-sell (KB never commands a sale)
- Caught late: no
- Chores: branch, commit, PR, sync, CLAUDE.md

## 2026-07-02 — Live data fetcher (PR #6) [backfilled]
- Stepped in: no
- Agent guessed: no (course rules were explicit; Section 4.11 inversion encoded)
- Caught late: flagged at the time — parsers tested only against fixtures,
  not live sites
- Chores: branch, commit, PR, sync, CLAUDE.md

## 2026-07-02 — Daily-scan runner (PR #7) [backfilled]
- Stepped in: no
- Agent guessed: no
- Caught late: YES — building the scan flushed out a real V20 bug: sell check
  sat behind range detection, so open trades couldn't always exit. 151 green
  tests had not caught it. Also: pyyaml wasn't even installed locally — no
  prior test imported the YAML loader.
- Chores: branch, commit, PR, sync, CLAUDE.md

## 2026-07-04 — Live-data validation + web UI (PR #8) [backfilled]
- Stepped in: no (user asked "when can I test with real data?" — pivoted to
  doing it live immediately)
- Agent guessed: yes — switched default price source to Yahoo/yfinance after
  NSE 403'd (fetcher-only dep allowed by CLAUDE.md)
- Caught late: YES, three live-data bugs invisible to all 155 unit tests:
  (1) RHS/CWH matched decades-old necklines against today's breakouts;
  (2) two ticker typos in the curated config; (3) macOS SSL certs missing.
- Chores: branch, 2 commits, PR, sync, CLAUDE.md; plus browser verification

## 2026-07-11 — ROADMAP.md + agentic-SDLC discussion [backfilled]
- Stepped in: yes — course-correct on where the roadmap commit should live
  (moved off local main onto a branch, kept checked out)
- Agent guessed: no
- Caught late: no
- Chores: doc commit on branch; no code (discussion session)

## 2026-07-11 — OBSERVE setup: global CLAUDE.md, journal.md, PR #9
- Stepped in: no
- Agent guessed: yes — user asked for "a CLAUDE.md for this project too";
  project already had a load-bearing one, so created journal.md instead of
  overwriting (confirmed by outcome)
- Caught late: no
- Chores: created ~/.claude/CLAUDE.md (journaling habit + working habits),
  backfilled journal from PRs 1-8, committed on branch, PR #9, merged, sync

## 2026-07-12 — L1-L5 context-layer scaffold (agentic-SDLC orchestration)
- Stepped in: yes — redirected from "build the holdings UI page" to "build
  the orchestration instead"; the worked example became the seeded spec
- Agent guessed: yes — kept CLAUDE.md as the Claude adapter rather than
  gutting it, AGENTS.md made the authority (recorded in ADR-0001); drift
  gate escape hatch chosen as a commit-message marker
- Caught late: no (drift script self-tested on fail/pass/opt-out paths
  before trusting it in CI)
- Chores: AGENTS.md, docs/specs (README+template+holdings example),
  4 backfilled ADRs, 6 MODULE.md cards, CI workflow + drift check,
  CLAUDE.md pointer, branch, PR

## 2026-07-12 — Product pivot kickoff: ADR-0005 + M1 spec (docs only)
- Stepped in: no (direction set explicitly: prod app, DB first, staged)
- Agent guessed: no — the load-bearing choices (Supabase Postgres, managed
  auth, engine purity, staged milestones) were recommended and accepted in
  discussion before writing; recorded in ADR-0005 rather than as silent
  defaults
- Caught late: no (no code — documents only, per our own workflow: spec
  and decision before schema)
- Chores: ADR-0005, docs/specs/user-data-layer.md, ROADMAP pivot track,
  journal. CI workflow still parked on ci-workflow branch awaiting token
  workflow scope.

## 2026-07-12 — M1: user data layer (app/ shell, first two-zone PR)
- Stepped in: no (built from the spec + ADR-0005 alone — the cold-start test)
- Agent guessed: yes — recorded in code/card: open_trades stored as JSON
  (trades are strategy-owned snapshots, not a fourth table); tests run the
  ORM on in-memory SQLite while the Postgres-only migration (JSONB, RLS) is
  validated via offline SQL generation; RLS keys on current_setting
  ('app.user_id') so local Postgres works, auth.uid() swap deferred to M2
- Caught late: no (engine purity enforced by a mechanical test, not habit)
- Chores: app/ package (models, repository, session, alembic + migration
  0001), 8 new tests (169), app/MODULE.md, drift gate learned the app/
  zone, AGENTS.md invariant #5 rewritten for two zones, CLAUDE.md, spec
  status. Exit criterion MET 2026-07-13: user applied migration 0001 to
  their Supabase project themselves (secret never entered agent context) —
  six tables + RLS + seeded user verified in the dashboard. Friction log
  for review: zsh comment gotcha, missing psycopg driver, @-in-password
  URL parsing, direct-vs-pooler host, stale shell env after editing .env,
  and a password FRAGMENT leaking via a traceback (password rotated).

## 2026-07-13 — M1 merged (PR #12) + CI gates live (PR #13)
- Stepped in: no (user ran gh auth refresh themselves - account action)
- Agent guessed: yes — rebased the parked ci-workflow branch onto main and
  amended it to install sqlalchemy+alembic so app/ shell tests run in CI
  rather than skip (psycopg/yfinance still deliberately absent)
- Caught late: no — CI's maiden run green on both jobs (tests 169, drift 6s)
- Chores: sync after #12, rebase/amend/push parked branch, PR #13, watch
  first CI run, sync after #13. All loose ends now closed; next: M2 spec.

## 2026-07-13 — M2 auth: spec + ADR-0006 pivot + implementation
- Stepped in: yes — TWICE, both load-bearing: (1) asked for the managed-vs-
  own-auth trade-off before approving the spec; (2) chose to weight
  LEARNING, pivoting ADR-0006 from Supabase Auth to library-assisted own
  auth. The workflow's review point did its job: the pivot happened in
  documents, before code.
- Agent guessed: yes — recorded in MODULE.md/service.py: session TTL 7d,
  token TTLs 24h/1h, lockout 5/email + 20/IP per 15min, min password 10;
  JWTs dropped for server-side opaque sessions (revocability); app_rls as
  NOLOGIN role assumed via SET LOCAL ROLE (no second credential).
- Caught late: near-miss caught during implementation — failed-login
  rollback would have erased the throttling ledger (attempt now commits
  before the raise). RLS-layer cross-user test requires Postgres: gated
  on TEST_DATABASE_URL, skips on CI (documented).
- Chores: spec + ADR rewrite, migration 0002, app/auth package, FastAPI
  server + static page, 17 new tests (186), MODULE.md/.env.example/
  CLAUDE.md/ROADMAP updates. Exit criterion MET: migration 0002 applied
  (Supabase killed the pooled connection on the bare GRANT-to-postgres —
  worked around via dashboard SQL editor + pg_has_role guard in the
  migration), register->verify->login walked in the browser.
  Friction log: (1) connection string pasted into env.py by accident —
  removed, rotation advised, SECOND paste-leak incident -> review item;
  (2) "no email sent" confusion — the dev transport prints to the server
  log by design; the page's vague message is enumeration resistance
  working, but first-run UX should say where to look in dev mode.

## 2026-07-14 — M2 merged (PR #14) + architecture diagram workflow
- Stepped in: no (M2 merge was the user's gate; CI green on maiden run)
- Agent guessed: yes — tool choice for the requested block diagram:
  Mermaid GENERATED from ast import analysis (not hand-drawn, not an
  image), enforced stale-or-fail by a dedicated workflow; growth plan =
  L0 zones forever + L1 per-package, L2 split past ~12 packages
- Caught late: no (generator determinism + edge honesty covered by 3
  tests; the diagram already renders the M2 auth topology correctly)
- Chores: sync after #14, generator script + workflow + generated doc +
  tests (189), this entry. ADR-0007 + react-frontend spec drafted and
  awaiting the react build to ride with.

---

# Reviews

## Review — 2026-07-11 (covering PRs #1-#8)
1. "Agent guessed" fired in 5 of 8 build sessions, always the same root
   cause: the KB defines rules qualitatively and leaves tolerances/thresholds
   unquantified. Handling that worked well here (documented constants +
   judgment-calls section in every PR) — keep that pattern as a rule.
   -> Already codified in global CLAUDE.md working habits.
2. Chores were IDENTICAL in all 8 sessions: branch -> commit -> PR with
   judgment calls -> post-merge sync -> CLAUDE.md bookkeeping.
   -> Top CODIFY candidate: a reusable PR ritual + post-merge-sync command.
3. "Caught late" clustered entirely at layer boundaries: unit-green but
   integration-broken (V20 exit), code-right but data-wrong (config typos),
   environment (SSL, missing dep). Unit tests never caught these; running
   the real thing always did.
   -> Pattern named: add a live-canary layer to the gate stack for any
   project that touches external data. (CODIFY/AUTOMATE later: scheduled
   fetcher canary is already item on ROADMAP.md.)
4. Interventions per PR: ~0.25 (2 in 8) — both were context/state issues
   (broken rename on arrival; where a commit should live), never code
   logic. Suggests delegation-readiness is high for well-specified build
   tasks in this codebase.
