# ADR-0002: Stdlib-only core; dependencies confined to the fetcher

Context: Strategy/screening/portfolio logic must stay transparent,
auditable against the KB, and zero-friction to test. Network data access
is the only part that genuinely needs outside help.

Decision: Pure stdlib for all core logic and the web UI (http.server, no
framework, no build step). Exceptions: `pyyaml` (config loading) and
`yfinance` (price data; lazily imported so only the default transport
needs it). All network access lives in `sunabha_agent/data/fetcher.py`;
every fetcher takes an injectable `transport` so the test suite never
touches the network. Any new dependency requires a new ADR.

Consequences: tests run in milliseconds with no setup; strategy code reads
like the KB it implements; the price of admission is writing small amounts
of code (HTML parsing, HTTP) that a library would give for free.
