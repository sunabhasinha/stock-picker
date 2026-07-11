# ADR-0005: Product pivot — multi-user hosted app around a pure engine

Context: The project is pivoting from a single-user localhost tool to a
production app: login/logout, per-user portfolios and dashboards, users
picking stocks and tracking progress. This collides deliberately with
three standing rules: AGENTS.md invariant #6 (localhost-only), ADR-0002
(stdlib-only), and the course's Section 3.5 single-user philosophy that
the current web UI cites.

Decision:
1. ENGINE STAYS PURE. Everything in `sunabha_agent/` (strategies, gate,
   category engine, checklist, scan orchestration) remains a
   dependency-free, I/O-free library, auditable against the KB. The
   product IMPORTS it and never modifies it. ADR-0002 continues to
   govern the engine unchanged.
2. A NEW APPLICATION SHELL gets its own rules: PostgreSQL (managed, via
   Supabase) for user data, SQLAlchemy 2.0 as the storage layer, Alembic
   migrations from the first table, FastAPI when the current http.server
   UI is succeeded (a later milestone). Shell dependencies are allowed
   and tracked in their own requirements, never imported by the engine.
3. AUTHENTICATION IS NEVER HAND-ROLLED. Login/logout/sessions/passwords
   come from the managed provider (Supabase Auth). Per-user data
   isolation is enforced IN the database via row-level security, not
   only in application code.
4. THE HUMAN-CONFIRMATION BOUNDARY (ADR-0003) BECOMES STRUCTURAL:
   signals are persisted as events carrying the user's response
   (pending/confirmed/dismissed). Nothing auto-executes, in any milestone,
   for any user. This is non-negotiable in the hosted product exactly as
   it is in the local tool.
5. STAGED, NOT ONE GO: (M1) data layer + migrations, proven against the
   existing single-user flows; (M2) auth + user-bound portfolios;
   (M3) per-user dashboard, confirm/dismiss, scheduled scans. Each
   milestone is its own spec + PR.

Amendments: AGENTS.md invariant #6 (localhost-only) remains TRUE for the
local tool and is amended only when the hosted shell ships (M2+).
Supersedes ADR-0002 only for the application shell, not the engine.

Consequences: the engine's testability and KB-traceability are preserved
while the product grows; the price is a two-zone codebase (pure core,
dependency-bearing shell) whose boundary must be policed — the shell's
MODULE.md and the drift gate carry that duty. Choosing managed
Postgres+Auth trades some lock-in for not owning the two highest-risk
prod problems (credentials, data isolation).
