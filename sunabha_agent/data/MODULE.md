# Module: data (models, universe lists, fetchers)

Purpose: the shared data shapes every layer consumes, the curated
V40/V40Next list loader, and ALL network data access.

Provides: `Candle`, `PriceSeries`, `Fundamentals`, `Signal`, `Universe`,
`CompanyType` (models.py); `UniverseRegistry` (universe_lists.py);
`ScreenerFetcher`, `YahooPriceFetcher` (default price source, ADR-0004),
`NSEFetcher` (fetcher.py).

Depends on: stdlib; `pyyaml` (universe_lists); `yfinance` lazily
(fetcher default transport only) — see ADR-0002.

Invariants:
- `Signal`/`Fundamentals`/`Candle` field changes ripple EVERYWHERE — see
  blast radius. Additive optional fields only, unless touching all layers.
- `lifetime_high` must see full listing history (AGENTS.md #4).
- Fetchers take injectable `transport`; tests never touch the network.
- Screener fetch uses the /consolidated/ URL; `is_showing_consolidated`
  encodes the KB §4.11 label inversion.

Blast radius: models.py is the widest interface in the repo — every
strategy, the gate, the engine, scan, and the web serializers consume it.
fetcher.py changes affect scan and web only. universe_lists changes
affect scan defaults.

Tests: tests/test_fetcher.py (fixtures mirror live site structures —
re-verify live after parser changes, see journal 2026-07-04).
