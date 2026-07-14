# Module: app (the application shell — ADR-0005 zone 2)

Purpose: the dependency-bearing product shell around the pure engine.
M1: the user data layer (ORM, repository, migrations). M2: own auth
(ADR-0006) — registration/login/logout, email verification, password
reset, server-side sessions — and the FastAPI server.

Provides: `app.db.models` (M1 tables + AuthSession, AuthToken,
LoginAttempt; users gained password_hash/email_verified_at),
`app.db.repository.Repository`, `app.db.session` (DATABASE_URL wiring +
`rls_transaction` — the per-request app_rls + app.user_id chain),
`app.auth` (security primitives, AuthService flows, pluggable
EmailTransport with a console dev transport), `app.server.create_app`
(run: `uvicorn app.server:app --port 8000`; generated API docs at
/docs and /redoc), migrations under `app/migrations/`.

M2 security tunables (spec left these to the implementer — recorded
here and in app/auth/service.py): session TTL 7d; verify token TTL 24h;
reset token TTL 1h; throttle window 15min with lockout at 5 failures
per email / 20 per IP; min password length 10 (length over composition,
NIST 800-63B). Session cookie `sp_session`: httpOnly + SameSite=Lax;
Secure via APP_COOKIE_SECURE=1 — REQUIRED in any deployment, off only
for plain-http local dev. Role model: `app_rls` is NOLOGIN (no second
credential) and is assumed per-transaction via SET LOCAL ROLE, which
auto-reverts; auth flow tables have RLS enabled with NO app_rls
policies (deny-all — only the owner-role auth service touches them).

Depends on: `sunabha_agent` (Position/ScanReport/signal serialization,
PRESET_CATEGORIES) — NEVER the reverse; engine purity is enforced by a
test (tests/test_app_db.py::TestEnginePurity). Third-party: sqlalchemy,
alembic, psycopg, fastapi, uvicorn, argon2-cffi, httpx — listed in
app/requirements.txt, allowed here by ADR-0005, forbidden in the engine
by ADR-0002.

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

Invariants added by M2 (ADR-0006, full list in docs/specs/auth-layer.md):
identity comes ONLY from the session row (hashed cookie token lookup);
one uniform 401 for every auth failure incl. timing (argon2 runs even
for unknown emails); passwords/tokens/cookies never logged or echoed;
flow tokens single-use, expiring, hashed at rest; password change/reset
revokes every session; state-changing requests origin-checked.

Tests: tests/test_app_db.py (data layer) and tests/test_auth.py (every
spec acceptance gate: lifecycle, uniform 401s, single-use tokens,
revocation, throttling lockout, cookie flags, origin check, cross-user
isolation at the API layer). SQLite in-memory; skips cleanly when shell
deps absent. The RLS layer of the cross-user gate needs real Postgres:
gated on TEST_DATABASE_URL (run locally against Supabase). Migrations
validated by offline SQL generation + real application at deploy time.
