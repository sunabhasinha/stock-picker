# CLAUDE.md — Stock Picker (Sunabha Agent)

## What this project is

A Python trading-signal agent built from the complete course notes of Vivek Singhal's stock market workshop. The **single source of truth** for all strategy rules, thresholds, and rationale is `master_strategy_kb.md` (in the root of the repo, or download from the chat session that built this). Every threshold in the code should trace back to a section number in that doc. If you're unsure whether a rule is implemented correctly, check the doc — not intuition.

## Run the tests first, before touching anything

```bash
# from the repo root
python3 -m unittest discover -s tests -v
```

All 42 tests must pass before any PR/commit. The tests are intentionally written against specific numbers from the source doc (e.g. ICICI Lombard's real cited 30-32% decline, Angel One's actual NBFC exemption figures) — not just "reasonable-sounding" synthetic cases. If a test fails after your change, the doc section number in the test's docstring tells you exactly what rule is being enforced.

## Project structure

```
stock-picker/
├── sunabha_agent/
│   ├── data/
│   │   ├── models.py          # Candle, PriceSeries, Fundamentals, Signal — the shared data shapes
│   │   └── universe_lists.py  # Loads the curated V40/V40Next lists from config/
│   ├── screening/
│   │   └── fundamental_gate.py  # V200 qualification, pledging disqualifier, ROCE/D-E tiering
│   ├── strategies/
│   │   ├── base.py            # Strategy ABC — the interface all 8 strategies implement
│   │   ├── sma_strategy.py    # Strategy 1: SMA (V40 only, no averaging)
│   │   ├── v20_strategy.py    # Strategy 3: V20 (V40+V40Next+V200, max 3 concurrent)
│   │   └── lifetime_high_strategy.py  # Strategy 8: LTH (V40+V40Next, ATH TTM trigger)
│   ├── portfolio/             # EMPTY — next to build: Category 1-4 framework
│   └── research/              # EMPTY — next to build: Strategy 7 LLM-assisted checklist
├── config/
│   └── v40_v40next.yaml       # Curated V40/V40Next stock lists (low-turnover, hand-maintained)
└── tests/
    ├── test_fundamental_gate.py
    ├── test_sma_strategy.py
    ├── test_v20_strategy.py
    └── test_lifetime_high_strategy.py
```

## What's built vs what's still needed

### ✅ Done (42 tests passing)
- Data models (Candle, PriceSeries, Fundamentals, Signal, Universe enum)
- V40/V40Next curated list loader
- Fundamental screening gate (V200 hard gate + pledging disqualifier + ROCE/D-E tiering + soft flags)
- Strategy 1: SMA (fully tested, including the no-averaging and V40-only constraints)
- Strategy 3: V20 (fully tested, including single-use ranges and 10% averaging gap)
- Strategy 8: Lifetime High / LTH (fully tested, including the ATH re-check on averaging)

### 🔲 Next up (in priority order)

**1. Strategy 2: Knoxville Divergence** (`sunabha_agent/strategies/knoxville_strategy.py`)
- Find the actual "Knoxville Divergence" Pine Script source on TradingView first
  (the master KB explicitly flags this as a dependency rather than re-deriving it)
- Settings: bars_back=200, RSI period=14, momentum period=20
- Averaging: 5% gap required. Max 2 concurrent trades.
- Universe: V40 only

**2. Strategy 4/5/6: RHS, CWH, V10** (`sunabha_agent/strategies/rhs_strategy.py` etc.)
- These are geometric pattern-matching — see Section 3.1/3.2/3.3 in master KB
- IMPORTANT: These must set `requires_human_confirmation=True` on every Signal they emit.
  The master KB flags these explicitly as "fuzzier" than the other strategies.
  The system should never auto-execute based on these alone without a human glance.

**3. Strategy 7: Three Times in Three Years** (`sunabha_agent/strategies/turnaround_strategy.py`)
- This is the Claude agent piece, not pure code — it needs a tool that:
  a) checks the quantitative conditions (67% decline, 50% still down at signal time)
  b) calls an LLM to research "is the reason for the decline still applicable?"
  c) returns a structured checklist output the user reviews before any trade
- See `sunabha_agent/research/` — that's the right module for this

**4. Portfolio-construction layer** (`sunabha_agent/portfolio/category_engine.py`)
- The four named Categories from Section 6.2 of the master KB
- Each Category is a config: which strategies are enabled + which universe
- This is the engine's top-level "switchboard" — nothing should run without a Category selected

**5. Live data fetcher** (`sunabha_agent/data/fetcher.py`)
- Currently all tests use synthetic data — a real data source is needed
- Screener.in for fundamentals (note the UI-label inversion bug documented in Section 4.11)
- NSE for daily OHLC — must fetch FULL listing history for lifetime_high to be reliable
  (this is flagged explicitly in models.py as a known accuracy risk)

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
- The data fetcher (when built) will need `requests` or equivalent. Keep it in the fetcher only — strategy logic must remain data-source-agnostic.
