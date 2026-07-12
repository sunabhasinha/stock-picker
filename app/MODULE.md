# Module: app (the application shell — ADR-0005 zone 2)

Purpose: the dependency-bearing product shell around the pure engine.
M1 scope: the user data layer — ORM models, repository, Alembic
migrations against Supabase/any Postgres.

Provides: `app.db.models` (User, Portfolio, Holding, SignalEvent,
ScanRun, ShadowSignal; LOCAL_USER_ID), `app.db.repository.Repository`
(the ONLY database vocabulary the product uses), `app.db.session`
(DATABASE_URL wiring, Supabase URL normalization), migrations under
`app/migrations/` (`alembic -c app/alembic.ini upgrade head`).

Depends on: `sunabha_agent` (Position/ScanReport/signal serialization) —
NEVER the reverse; engine purity is enforced by a test
(tests/test_app_db.py::TestEnginePurity). Third-party: sqlalchemy,
alembic, psycopg — listed in app/requirements.txt, allowed here by
ADR-0005, forbidden in the engine by ADR-0002.

Invariants:
- signal_events snapshots are immutable; only response/responded_at
  change, and only via Repository.respond_to_signal (ADR-0003 made
  structural — there is deliberately no "executed" response).
- portfolios carry exactly ONE category + commitment date (KB §6.3).
- holdings round-trip losslessly with scan.positions_from_dict — that
  JSON shape is the contract; change it in scan.py and here together.
- RLS from migration 0001, keyed on current_setting('app.user_id')
  until M2 swaps to auth.uid(); the M1 seeded user is LOCAL_USER_ID.
- Migrations are forward-only; DATABASE_URL via environment only.

Blast radius: nothing imports app yet (M1 is foundation) — consumers
arrive in M2/M3. Schema changes = new migration + this card. The
signal-snapshot shape mirrors web.signal_to_dict: changes there land here.

Tests: tests/test_app_db.py — SQLite in-memory for repository logic
(skips cleanly when shell deps absent, keeping the engine suite
zero-dependency); the Postgres-only migration (JSONB, RLS) is validated
by offline SQL generation, and against real Postgres at deploy time.
