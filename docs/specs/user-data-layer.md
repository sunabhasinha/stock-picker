# Spec: User data layer (product pivot, milestone 1)
status: done (applied to Supabase 2026-07-13 — six tables, RLS active, seeded user verified in dashboard)
governed by: ADR-0005

Goal: a persistent data layer for user data — portfolios, holdings, signal
history — proven against the EXISTING single-user flows before any auth
exists. After this milestone the local app can read/write the database
instead of (alongside) positions.json, and every scan can persist its
signals as events.

Acceptance:
- Schema exists as Alembic migrations (from the very first table), applied
  to a Supabase Postgres project AND runnable against local Postgres for
  development/tests
- Tables: users, portfolios, holdings, signal_events, scan_runs,
  shadow_signals — shaped as below
- portfolios carry exactly ONE category key + commitment start date
  (Section 6.3 pick-one rule made structural); multiple portfolios per
  user allowed (Section 6.4)
- holdings normalize the existing positions-JSON shape; a round-trip
  positions_from_dict <-> DB is lossless (tested)
- signal_events persist a scan's signals with full rationale/metadata
  snapshot and a response field: pending | confirmed | dismissed;
  append-only (responses update the row's response, never the snapshot)
- scan_runs persist ScanReport summaries (when, category, symbols, errors)
- A repository layer (application shell, NOT the engine) exposes this to
  the existing scan/web code paths; the engine imports nothing from it
- Existing file-based flows keep working (back-compat until M2)
- Row-level security policies exist from day one (single seeded user for
  now) so M2 auth binds to enforcement that already works

Invariants (inherited + ADR-0005):
- `sunabha_agent/` engine stays pure — no DB imports anywhere inside it
- Nothing executes trades; signal_events model decisions, not orders
- Migrations are forward-only in history (no editing applied migrations)
- Secrets (DB URL, keys) via environment, never committed

Out of scope (later milestones): login/logout UI, session handling,
per-user dashboards, scheduled scans, multi-user web serving, FastAPI
replacement of http.server.

Deliberately left to the implementer: exact column types/indexes, local
dev database arrangement (container vs Supabase local), repository API
shape.
NOT left open: Postgres via Supabase (ADR-0005); SQLAlchemy 2.0 + Alembic;
signal snapshots stored as JSONB (schema of signals is still evolving);
RLS from the first migration; engine purity.
