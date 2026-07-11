# Module: app layer (scan.py, web.py, static/)

Purpose: the user-facing runners. scan.py wires universe list -> fetchers
-> gate -> CategoryEngine -> ranked report (CLI:
`python3 -m sunabha_agent.scan --category ...`). web.py serves the local
single-page UI (`python3 -m sunabha_agent.web`, http://127.0.0.1:8788/).

Provides: `DailyScanner` (with optional progress callback), `ScanReport`,
`positions_from_dict`, `format_report` (scan.py); `WebApp`, `serve`, the
JSON API (web.py); static/index.html (no framework, no build step).

Depends on: everything below it (data, screening via engine, portfolio,
research). Nothing depends on THIS layer — it is the top.

Invariants:
- Web server binds 127.0.0.1 only; single-user tool (AGENTS.md #6).
- One scanner = one committed category, no default.
- Per-symbol errors are captured in the report, never fatal to a scan.
- Exits render before buy candidates. Held symbols always get scanned.
- A successful SYMBOL.NS price pull supplies `listed_on_nse=True`
  (ADR-0004).
- positions-JSON format (`positions_from_dict`) is the holdings contract —
  UI features build on it, not around it (see docs/specs/holdings-page.md).

Blast radius: leaf — changes here affect users, not the engine. But
serializers in web.py mirror Signal/report shapes: model changes land here.

Tests: tests/test_scan.py (fake fetchers), tests/test_web.py (real HTTP
server on an ephemeral port, fake scanner factory — zero network).
