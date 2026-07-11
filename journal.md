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
