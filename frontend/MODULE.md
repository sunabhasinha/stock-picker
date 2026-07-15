# Module: frontend (zone 3 — React + TypeScript, ADR-0007)

Purpose: the product UI. React 18 + TypeScript strict, Vite, Tailwind v4,
shadcn/ui components VENDORED into src/components/ui (readable and
editable by agents and the drift gate — that's why shadcn).

## Design principles (owner directive 2026-07-15 — treat as invariants)
- MINIMAL AND FRIENDLY over feature-dense: one clear action per screen,
  plain-language copy, no jargon in user-facing text.
- Simple flows: a new user must get from landing to signed-in dashboard
  without instructions. Every dead end links to the next sensible step.
- Visual restraint: the neutral token palette in src/index.css, one
  accent color (primary blue), generous whitespace, no decoration that
  doesn't communicate. New UI matches this or amends this card first.
- Honest states: loading, empty, and error states are designed, not
  afterthoughts; error text says what to DO, not just what failed.
- "Nothing executes trades" stays visible in the shell — product
  identity, not boilerplate (ADR-0003).

Provides: pages (/login /register /verify /reset + authenticated Shell
at /), vendored ui components (button/card/input/label), the ONE fetch
wrapper (src/api/client.ts — same-origin, uniform-401 redirect), and
generated API types (src/api/schema.d.ts — DO NOT edit; regenerate with
`npm run gen:api`).

Depends on: the shell's HTTP API only, via the OpenAPI contract
(frontend/openapi.json -> schema.d.ts). No direct engine knowledge.
Runtime deps: react, react-router-dom, cva/clsx/tailwind-merge.

Invariants:
- SAME-ORIGIN ONLY (ADR-0007): dev = Vite proxy to :8000; prod = FastAPI
  serves dist/. No CORS config may ever be added without amending
  ADR-0007.
- No token/credential handling in JS — the session is an httpOnly cookie
  the browser manages; login submits a form, nothing more.
- schema.d.ts is generated; CI fails if it drifts from the server's
  OpenAPI (the zone contract).
- TypeScript strict; `npm run build` (typecheck + build) must pass.

Blast radius: leaf zone — nothing imports frontend. But it RENDERS the
shell's API shapes: server response-model changes land here via
regenerated types (a compile error, by design, not a runtime surprise).

Commands: `npm run dev` (proxied dev server), `npm run build`,
`npm run gen:api`. Demo without secrets: `python3 scripts/dev_server.py`.

Tests: typecheck + build in CI (frontend job); SPA serving covered in
tests/test_auth.py::TestSPAServing. Component tests: deliberately out of
scope until the dashboard lands (spec).
