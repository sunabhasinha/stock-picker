# Spec: React frontend foundation (M3 step 1)
status: done (live-verified 2026-07-16 — full loop in browser: register -> verify (SPA page) -> login -> shell -> portfolio created; served by FastAPI from dist)
governed by: ADR-0007 (stack + same-origin serving), ADR-0006 (auth model)

Goal: stand up the frontend/ zone and rebuild the auth experience in
React + TypeScript + shadcn/ui, ending with a logged-in shell page that
proves the full loop: Vite dev proxy -> FastAPI -> session cookie ->
authenticated API call -> typed response rendered.

Acceptance:
- frontend/ scaffold: Vite + React + TypeScript strict mode + Tailwind +
  shadcn/ui initialized; `npm run dev` proxies /api and /auth to :8000;
  `npm run build` emits static files FastAPI serves at / (replacing
  app/static/auth.html)
- Pages: /login (sign in), /register (create account + "check the server
  log in dev mode" hint - the M2 friction-log UX fix), /verify (consumes
  the token link), /reset (request + confirm) - all shadcn components
- Auth loop works in the browser end to end via the dev proxy AND via
  the built bundle served by FastAPI (both verified)
- A minimal authenticated shell page after login: shows /api/me identity,
  lists portfolios (/api/portfolios), has a working logout - the M3
  dashboard will grow inside this shell
- TypeScript API types are GENERATED from FastAPI's /openapi.json
  (openapi-typescript); a repo script regenerates them; CI fails on type
  drift
- One thin fetch wrapper: same-origin credentials, uniform-401 handling
  (redirect to /login), no other hand-written request plumbing
- CI: frontend job (install, typecheck, build) + drift gate covers
  frontend/ -> frontend/MODULE.md
- frontend/MODULE.md card written (zone purpose, contract = openapi.json,
  invariants, blast radius)

Invariants (inherited + zone-3-specific):
- SAME-ORIGIN ONLY (ADR-0007): no CORS config anywhere; dev uses the
  Vite proxy, prod is served by FastAPI
- No token/credential handling in JS beyond submitting the login form:
  the session lives in the httpOnly cookie the browser manages
- "Nothing executes trades" appears in the UI shell exactly as it does
  in the current pages
- Engine (zone 1) untouched, incl. its stdlib local-tool UI
- node_modules/ and build output gitignored; package-lock.json committed

Out of scope (later M3 steps): the dashboard itself (signals list,
confirm/dismiss, portfolio detail, scan-on-demand), dark mode, routing
beyond the pages above, component testing infrastructure, hosting

Deliberately left to the implementer: exact shadcn components, folder
layout inside frontend/src, router choice (react-router vs tanstack),
form validation library
NOT left open: Vite; TypeScript strict; Tailwind + shadcn/ui; generated
API types from openapi.json; same-origin proxy/serving; the four pages
+ authenticated shell as the deliverable
