# ADR-0006: Own auth (library-assisted), server-side sessions, RLS under
# a non-superuser role

Context: M2 brings registration/login. ADR-0005 clause 3 said "never
hand-rolled" and named Supabase Auth. Before building, the trade-off was
discussed explicitly (2026-07-13): managed auth wins on security-review
burden and shipping speed; own auth wins on control, portability, no
external dependency in the login path, and LEARNING — which the project
owner explicitly chose to weight. The genuinely dangerous option (writing
crypto/flows from scratch) was never on the table; the chosen path is
library-assisted own auth on primitives that are industry standard.

Decision — AMENDS ADR-0005 clause 3: authentication is built in the
application shell, with these non-negotiable primitives:

  1. PASSWORDS: argon2id via a maintained library (argon2-cffi). Never a
     home-grown hash, never reversible, never logged. Passwords cross the
     wire only over TLS in production.
  2. SESSIONS: server-side OPAQUE tokens (secrets.token_urlsafe), stored
     HASHED in the sessions table with expiry and revocation. No JWTs:
     for a first-party single-backend app, opaque sessions are simpler,
     instantly revocable, and have no algorithm/verification foot-guns.
     Cookies: httpOnly + Secure + SameSite=Lax; never localStorage, never
     URLs, never logs.
  3. USER ID FOR DATA ACCESS comes only from the server-side session row
     — never from any client-supplied value.
  4. DATABASE ENFORCEMENT unchanged from the M1 design: the shell
     connects as a dedicated non-superuser role (no BYPASSRLS), and the
     repository opens each request's transaction with
     SET LOCAL app.user_id = <session's user id>, so the M1 RLS policies
     bind independently of application code. (The M1 note anticipating a
     swap to Supabase's auth.uid() is superseded — that only applies to
     PostgREST-style access, which we do not use.)
  5. FLOWS built, not improvised: email verification and password reset
     use single-use, expiring, unguessable tokens stored hashed; email
     DELIVERY is a pluggable transport (console/log in dev, SMTP provider
     later) so the flows are real before an email vendor exists.
  6. ABUSE RESISTANCE: uniform error responses (no user-enumeration
     oracle, including timing: hash verification runs even for unknown
     emails), per-account and per-IP login throttling, sessions revoked
     on password change.

Consequences: the project owns auth's maintenance tail and audit burden
— accepted knowingly for the learning value; the security posture leans
on the invariants above plus the cross-user access test as an acceptance
gate. The provider question stays reversible: everything downstream of
"a verified user id enters the request" is identity-source-agnostic, so
a later migration to managed auth (or Keycloak/Ory) would swap only the
front of the chain. Supabase remains the database (ADR-0005 clauses 1-2
unchanged); its Auth product is simply not used.
