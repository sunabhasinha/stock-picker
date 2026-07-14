# CLAUDE.md — Stock Picker (Sunabha Agent)

> **Read `AGENTS.md` first** — it is the tool-agnostic constitution (L1) and
> the authority if the two ever disagree (ADR-0001). This file is the Claude
> adapter carrying the detailed build state and history. The context layers:
> specs in `docs/specs/`, decisions in `docs/decisions/`, per-module maps in
> `MODULE.md` files, learning loop in `journal.md`, backlog in `ROADMAP.md`.

## What this project is

A Python trading-signal agent built from the complete course notes of Vivek Singhal's stock market workshop. The **single source of truth** for all strategy rules, thresholds, and rationale is `master_strategy_kb.md` (in the root of the repo, or download from the chat session that built this). Every threshold in the code should trace back to a section number in that doc. If you're unsure whether a rule is implemented correctly, check the doc — not intuition.

## Run the tests first, before touching anything

```bash
# from the repo root
python3 -m unittest discover -s tests -v
```

All 186 tests must pass before any PR/commit. The tests are intentionally written against specific numbers from the source doc (e.g. ICICI Lombard's real cited 30-32% decline, Angel One's actual NBFC exemption figures) — not just "reasonable-sounding" synthetic cases. If a test fails after your change, the doc section number in the test's docstring tells you exactly what rule is being enforced.

## Project structure

```
stock-picker/
├── sunabha_agent/
│   ├── data/
│   │   ├── models.py          # Candle, PriceSeries, Fundamentals, Signal — the shared data shapes
│   │   ├── universe_lists.py  # Loads the curated V40/V40Next lists from config/
│   │   └── fetcher.py         # Screener.in fundamentals + NSE full-history OHLC (stdlib only)
│   ├── screening/
│   │   └── fundamental_gate.py  # V200 qualification, pledging disqualifier, ROCE/D-E tiering
│   ├── strategies/
│   │   ├── base.py            # Strategy ABC — the interface all 8 strategies implement
│   │   ├── sma_strategy.py    # Strategy 1: SMA (V40 only, no averaging)
│   │   ├── knoxville_strategy.py  # Strategy 2: Knoxville Divergence (V40 only, max 2 concurrent)
│   │   ├── v20_strategy.py    # Strategy 3: V20 (V40+V40Next+V200, max 3 concurrent)
│   │   ├── pattern_common.py  # Shared geometry: pivots, neckline chains, base breakouts
│   │   ├── rhs_strategy.py    # Strategy 4: Reverse H&S (V40+V40Next, human-confirmed)
│   │   ├── cwh_strategy.py    # Strategy 5: Cup with Handle (V40+V40Next, human-confirmed)
│   │   ├── v10_strategy.py    # Strategy 6: V10 averaging overlay on open RHS/CWH trades
│   │   ├── turnaround_strategy.py  # Strategy 7: Three Times in Three Years (NSE-wide)
│   │   └── lifetime_high_strategy.py  # Strategy 8: LTH (V40+V40Next, ATH TTM trigger)
│   ├── portfolio/
│   │   └── category_engine.py # The four Section 6.2 Categories, ranking, reconciliation
│   └── research/
│       ├── turnaround_checklist.py  # Strategy 7's 10-condition checklist machinery
│       └── claude_research.py       # Claude-backed ResearchProvider (stdlib urllib only)
│   ├── scan.py                # Daily-scan runner + CLI (python3 -m sunabha_agent.scan)
│   ├── web.py                 # Local web UI backend (python3 -m sunabha_agent.web)
│   └── static/index.html      # The single-page scan UI (no build step, no framework)
├── app/                       # The application SHELL (ADR-0005) — dependency-bearing zone
│   ├── db/                    # models.py, repository.py, session.py (+rls_transaction)
│   ├── auth/                  # M2 own auth (ADR-0006): argon2id, sessions, flows
│   ├── server.py              # FastAPI product API (uvicorn app.server:app; docs at /docs)
│   ├── static/auth.html       # minimal register/login page
│   ├── migrations/            # Alembic; RLS from 0001; app_rls role from 0002
│   └── requirements.txt       # shell-only deps (engine never imports these)
├── config/
│   └── v40_v40next.yaml       # Curated V40/V40Next stock lists (low-turnover, hand-maintained)
└── tests/
    ├── test_fundamental_gate.py
    ├── test_sma_strategy.py
    ├── test_knoxville_strategy.py
    ├── test_v20_strategy.py
    ├── test_rhs_strategy.py
    ├── test_cwh_strategy.py
    ├── test_v10_strategy.py
    ├── test_turnaround_checklist.py
    ├── test_turnaround_strategy.py
    ├── test_category_engine.py
    ├── test_fetcher.py
    ├── test_scan.py
    ├── test_web.py
    ├── test_app_db.py
    ├── test_auth.py
    └── test_lifetime_high_strategy.py
```

## What's built vs what's still needed

### ✅ Done (186 tests passing)
- Data models (Candle, PriceSeries, Fundamentals, Signal, Universe enum)
- V40/V40Next curated list loader
- Fundamental screening gate (V200 hard gate + pledging disqualifier + ROCE/D-E tiering + soft flags)
- Strategy 1: SMA (fully tested, including the no-averaging and V40-only constraints)
- Strategy 2: Knoxville Divergence (fully tested; divergence detection replicated from the
  two open-source ports of Rob Booker's indicator cited in the module docstring — the
  TradingView original is closed-source. Bullish = momentum rising + price falling + new
  window low + RSI ≤30 in window; bearish is the mirror with RSI ≥70. 5% averaging gap,
  max 2 concurrent, V40 only)
- Strategy 3: V20 (fully tested, including single-use ranges and 10% averaging gap)
- Strategy 4/5/6: RHS, CWH, V10 (fully tested. Every signal sets
  `requires_human_confirmation=True` per the KB's Section 3.6 build flag — these are
  candidate-finders for a human to review, never auto-execute. The tolerances the KB
  leaves undefined (neckline horizontality 2%, base tightness 5%, pivot window 2,
  "near lifetime high" 5%) are documented constants in `pattern_common.py`, not course
  rules. RHS sells at max(technical target, lifetime high); CWH at technical target
  ONLY; V10 is an averaging overlay that needs ALL open trades passed in, not just its
  own, to see its parent RHS/CWH trade)
- Strategy 7: Three Times in Three Years (fully tested. The 10-condition checklist lives
  in `research/turnaround_checklist.py`: conditions 1/6/7 are computed (67% decline uses
  the POST-PEAK trough, not current price; condition 6 is YoY per Section 4.12; condition
  7 is current price ≥50% down), condition 2's A/B/C classification is diagnostic-only
  with our own 10%/20% drawdown thresholds, and conditions 3-5 delegate to a pluggable
  `ResearchProvider` — `claude_research.py` is the Claude-backed one (stdlib urllib, no
  new deps, degrades to NEEDS_RESEARCH on any error, instructs the model to answer
  UNCLEAR without current data). The strategy emits a BUY candidate when nothing FAILED,
  with open research questions in the signal; `requires_human_confirmation=True` always.
  NSE gate: `Fundamentals.listed_on_nse` must be explicitly True — None refuses. Exit:
  +100% within 12 months (lapses after!), else hold to the lifetime high frozen at entry)
- Strategy 8: Lifetime High / LTH (fully tested, including the ATH re-check on averaging)
- Portfolio Category engine (fully tested. The four Section 6.2 presets plus
  `custom_category()` for a user-defined "Category 5+". `CategoryEngine` requires a
  Category — no default, per the pick-exactly-one rule. It runs the fundamental gate
  before any strategy (Section 4.14), refuses stocks outside the category's universe,
  and routes each strategy only ITS OWN open trades — except V10, which gets all of them
  to find its parent RHS/CWH trade. Category 2's cross-strategy 10% entry gap is engine-
  enforced (AVERAGE signals exempt — per-strategy gap rules govern those). Also:
  `rank_candidates()` implements the Section 4.20 hierarchy (universe > gain > ROCE/D-E
  tier within 5%-wide "similar gain" buckets — the bucket width is ours), Section 6.3's
  `reconcile_holding()` (a gate-failing loss-maker gets REVIEW, not an auto-sell — the
  KB never explicitly commands a sale), and `shadow_signals()` for the recommended
  track-the-other-categories feature)

- Live data fetcher (`data/fetcher.py`, fully tested offline via injected transports.
  `ScreenerFetcher` requests the /consolidated/ URL per Section 4.11 and
  `is_showing_consolidated()` encodes the label-inversion trap ("View Standalone" visible
  means the page IS consolidated). TTM histories are bridged from quarterly rows via
  rolling 4-quarter sums. `company_type` and `listed_on_nse` are caller-supplied — not
  derivable from the page; a successful NSE pull is the natural evidence for the latter.
  `NSEFetcher` pulls year-sized chunks from 1992 (predates NSE itself) so lifetime_high
  always sees the FULL listing history, with cookie warm-up, dedupe, and throttling.
  Stdlib urllib only — pyyaml remains the sole external dependency.
  LIVE-VERIFIED (July 2026): Screener.in parsing works against the real site (TITAN:
  market cap, ROCE, shareholding, 13 quarters all correct; consolidated view confirmed).
  NSE's own API 403s scripted clients (Akamai) — `YahooPriceFetcher` is therefore the
  DEFAULT price source: `yfinance` (lazily imported, fetcher-only dep) pulls the full
  listing history in one request (TITAN.NS: 7,657 candles back to 1996), split-adjusted
  — the TradingView price basis the KB's rules assume. In-progress trading days arrive
  as NaN and are dropped. Screener does NOT expose debt_to_equity in default top ratios
  — it comes back None; the V200 gate treats None as failing, so V200 candidates need
  that field from another source or a computed fallback (known gap).
  Machine setup needed once: `pip install pyyaml yfinance` and, for python.org Python
  on macOS, run "Install Certificates.command" or all HTTPS fetches fail with SSL
  certificate errors.)

- Daily-scan runner (`scan.py`, fully tested with fake fetchers. One selected Category
  per scanner (no default). Default scope = curated symbols inside the category's
  universe; V200 and NSE-wide symbols must be passed explicitly (no static list exists
  for either). NSE price-pull success supplies `listed_on_nse=True` to fundamentals.
  Positions JSON enables exits + Section 6.3 reconciliation; held symbols are always
  scanned even if outside the scan list. Per-symbol errors are captured, never fatal.
  CLI: `python3 -m sunabha_agent.scan --category category_2 [--symbols ...]
  [--positions positions.json]`. Building it flushed out a real V20 bug: the sell check
  used to sit behind range detection, so an open trade couldn't exit if its originating
  range wasn't re-detectable — now fixed with a regression test.)

- Local web UI (`web.py` + `static/index.html`, live-verified in a browser. Stdlib
  http.server bound to 127.0.0.1 only — single-user local tool, per the course's
  explicit no-community philosophy (Section 3.5). Category picker (the four presets from
  /api/categories), optional symbol narrowing, optional holdings JSON for exits +
  reconciliation. Scans run as background jobs with per-symbol progress polling
  (POST /api/scan -> job_id, GET /api/scan/<id>). DailyScanner.scan grew an optional
  progress(done,total,symbol) callback for this. Signal cards show action/strategy/
  universe/sizing badges, the human-confirmation warning, fundamentals line, full
  rationale, and expandable metadata. Run: `python3 -m sunabha_agent.web` then open
  http://127.0.0.1:8788/.)

### 🔲 Next up

The build plan is COMPLETE end-to-end. **The maintained backlog lives in `ROADMAP.md`**
(with per-item context for picking work up cold). Summary:
- An on-disk cache for fetched data (full history per symbol per day is wasteful)
- debt_to_equity source for the V200 gate (not in Screener's default top ratios)
- Shadow-performance persistence (Section 6.3's recommended comparison feature)
- A V200 screening pass over the full NSE list to maintain a V200 candidate list

## Key rules that are VERY easy to get wrong (read this before coding)

1. **Pledging disqualifier formula**: it's `promoter_holding_pct * (pledging_pct_of_holding / 100)`, NOT just the pledging percentage alone. The test `test_formula_is_not_pledging_percent_alone` exists specifically for this.

2. **Quarterly comparison is always YoY, never QoQ** (Section 4.12). The business is seasonal. Never compare June quarter to March quarter as a growth signal.

3. **V20 ranges are single-use**: once a buy-sell cycle completes on a range, it is spent. A fresh 20%+ green-candle run is required for the next trade, even at the identical price level.

4. **LTH averaging re-checks ATH status at EVERY averaging point**, not just at initial entry. If TTM fundamentals have since dropped off all-time-high, do NOT average even if the price has fallen further.

5. **Screener.in toggle label inversion**: when the Screener.in button reads "View Consolidated," you're currently looking at Standalone data. The button shows what you'd switch TO, not what's currently displayed.

6. **Lifetime high must use full listing history** — if only 5 years of candles are loaded for a 15-year-old company, `PriceSeries.lifetime_high` will return a wrong number. See the comment in `models.py`.

7. **No stop-loss, ever** — all 8 strategies use `uses_stop_loss = False`. This is not an oversight; it's a foundational rule of the course. If a future strategy implementation sets this to True, that should be a deliberate, documented, flagged change.

## Dependency notes

- Pure Python stdlib only for all strategy/screening logic (no pandas, no numpy) — keeps the logic transparent and the test setup zero-friction.
- `pyyaml` for config loading (the only external dependency so far).
- The data fetcher ended up needing NO new dependency — it uses stdlib `urllib` +
  `html.parser` + `http.cookiejar` ("requests or equivalent" — urllib is the equivalent).
  All network access stays in `data/fetcher.py`; strategy logic remains data-source-agnostic,
  and both fetchers take an injectable `transport` so tests never touch the network.
