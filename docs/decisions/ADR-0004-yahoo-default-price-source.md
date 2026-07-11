# ADR-0004: Yahoo Finance is the default price source (NSE kept as alternative)

Context: First live run (2026-07-04, PR #8): NSE's own API sits behind
Akamai bot protection and 403s scripted clients. Yahoo's chart data for
SYMBOL.NS returns the FULL listing history in one request (TITAN.NS:
7,657 candles back to 1996), split-adjusted — the same price basis a
TradingView chart shows, which is what every lifetime-high rule in the
KB assumes.

Decision: `YahooPriceFetcher` (via `yfinance`, lazily imported per
ADR-0002) is the default price source in the scan. `NSEFetcher` stays in
the codebase as the alternative for anyone who can get past the blocking.
In-progress trading days arrive as NaN and are dropped. A successful
SYMBOL.NS pull doubles as the evidence for Strategy 7's `listed_on_nse`
gate (KB Section 5.0).

Consequences: full-history accuracy for lifetime_high with one request
per symbol; a third-party dependency on Yahoo's continued tolerance —
the scheduled fetcher canary on ROADMAP.md is the mitigation.
