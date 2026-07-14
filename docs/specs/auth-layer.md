# Spec: Auth layer — registration, login, user-bound data (M2)
status: done (live-verified 2026-07-13 — migration 0002 on Supabase; register -> verify -> login walked in browser)
governed by: ADR-0005, ADR-0006 (own auth, learning-weighted — amends
ADR-0005 clause 3)

Goal: users can register and log in against OUR backend; every API
request runs as a verified user; all M1 data (portfolios, holdings,
signal history) is bound to and isolated per user. Security is the
primary acceptance dimension; building and UNDERSTANDING each flow is an
explicit goal of this milestone.

## The security model (read first — this is what review approves)

1. PASSWORDS: argon2id (argon2-cffi), unique salt per hash (library
   default), no pepper for now. Our code never logs, echoes, or stores a
   plaintext password anywhere, including error paths.
2. SESSIONS: server-side opaque tokens — 256-bit random, stored HASHED
   (sha256) in a sessions table with created/expires/revoked columns.
   Delivered as httpOnly + Secure + SameSite=Lax cookies. Logout revokes
   server-side (the cookie dying is not the mechanism). Password change
   revokes ALL of the user's sessions. No JWTs (ADR-0006 rationale).
3. IDENTITY FOR DATA ACCESS: the user id attached to the request comes
   only from the session row looked up by the (hashed) cookie token —
   never from any client-supplied field.
4. DATABASE ENFORCEMENT (unchanged M1 design, now real): migration 0002
   creates a dedicated non-superuser role for the shell (no BYPASSRLS,
   least-privilege grants); the repository opens each request transaction
   with SET LOCAL app.user_id = <session user id>; the M1 RLS policies
   enforce isolation in the database even if application code is buggy.
5. FLOWS with hashed, single-use, expiring tokens:
   - Email verification: register -> account exists unverified -> token
     link -> verified. Unverified users cannot log in.
   - Password reset: request -> token link -> new password -> all
     sessions revoked. Response identical whether the email exists or not.
   Email delivery is a pluggable transport: DEV transport prints the link
   to the server log (no email vendor needed to build/test the flows);
   SMTP transport is a config swap later.
6. ABUSE RESISTANCE: one uniform 401 for every authentication failure;
   argon2 verification runs even when the email is unknown (timing
   uniformity); login throttling per-account and per-IP with lockout
   backoff, counters in the DB; all state-changing routes require the
   session cookie + an Origin/Referer check (SameSite=Lax as first line,
   origin check as second).
7. NOTHING EXECUTES TRADES — unchanged and structural (ADR-0003), worth
   restating in the layer that will someday face the internet.

## Acceptance

- Register (email+password) -> unverified account; verification link
  (dev transport: printed to log) -> verified; only then login succeeds
- Login sets the httpOnly session cookie; logout revokes server-side;
  password change revokes every session for that user
- Every /api/* route requires a valid unexpired session; otherwise a
  single-shape 401 with no detail leakage
- First verified login ensures the users row; portfolios created after
  are bound to that user
- CROSS-USER TEST (the gate): two registered users; automated attempts to
  read/write each other's portfolios, holdings, and signal events fail at
  BOTH layers — the API (401/404, never data) and the repository layer
  run directly against RLS with the wrong app.user_id
- Throttling test: N rapid failed logins lock the account with uniform
  responses; a reset-flow token works once and never twice
- Migration 0002: sessions, auth_tokens, login_attempts tables (tokens
  stored hashed); users gains password_hash + email_verified_at; the
  app role with least-privilege grants; RLS on new tables
- Server: FastAPI + uvicorn in app/ (ADR-0005), serving login/register
  pages and the authenticated API; the stdlib http.server local tool
  remains untouched
- .env.example updated (app role DATABASE_URL, cookie/secret settings);
  no secret in code or logs

## Invariants (inherited + M2-specific)

- Engine purity: sunabha_agent/ gains zero knowledge of auth
- No password, token, cookie value, or Authorization material in logs or
  error bodies, ever
- AGENTS.md #6 (localhost-only) stays TRUE until an actual hosted deploy;
  the app must be deployable (no baked localhost assumptions) but this
  milestone does not deploy it
- Auth flow changes are spec-reviewed: no new flow (e.g. "remember me",
  magic links) lands without amending this spec first

## Out of scope (M3+)

Social/OAuth login, MFA, magic links, account deletion/export, per-user
dashboard UI, confirm/dismiss UI, scheduled scans, hosted deployment,
real SMTP provider selection

## Deliberately left to the implementer

FastAPI project layout under app/, cookie/table naming, token TTLs
(document chosen values in app/MODULE.md), lockout thresholds (document
likewise), test fixtures for time control

## NOT left open

argon2id; opaque server-side sessions (no JWTs); httpOnly cookies (no
localStorage); tokens stored hashed; identity only from the session row;
non-superuser DB role + SET LOCAL app.user_id; email verification
required before login; uniform 401s incl. timing; pluggable email
transport with dev-log default; FastAPI
