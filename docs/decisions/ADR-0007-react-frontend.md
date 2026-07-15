# ADR-0007: React + TypeScript frontend (third zone), same-origin serving

Context: The product needs real UI (M3: per-user dashboard, signal
review). The owner chose React + TypeScript with shadcn/ui. Until now
the repo had two zones (pure Python engine; Python shell). A JS frontend
adds a third, with its own toolchain, and needs the same boundary
discipline as the first two.

Decision:
1. THIRD ZONE: `frontend/` — React 18 + TypeScript, built with Vite,
   styled with Tailwind CSS, components from shadcn/ui. shadcn is chosen
   deliberately for the agentic workflow: it vendors component SOURCE
   into the repo (no black-box component library), so agents read and
   modify UI components under the same drift-gate rules as everything
   else.
2. SAME-ORIGIN SERVING, ALWAYS — this is the security-preserving clause:
   - dev: Vite dev server proxies /api/* and /auth/* to FastAPI (:8000)
   - prod: `vite build` output is served BY FastAPI as static files
   Consequence: the M2 model (httpOnly session cookies, SameSite=Lax,
   origin-check middleware, uniform 401s) carries over UNCHANGED. No
   CORS surface is ever opened; introducing one would amend this ADR.
3. THE OPENAPI SPEC IS THE CONTRACT between zones 2 and 3: TypeScript
   API types are generated from FastAPI's /openapi.json, so the frontend
   cannot silently drift from the backend. Hand-written request code is
   limited to a thin fetch wrapper (credentials: same-origin, uniform
   401 handling).
4. SCOPE OF REPLACEMENT: the React app supersedes app/static/auth.html
   (the M2 placeholder). The ENGINE's stdlib web UI
   (sunabha_agent/web.py + static/) remains the single-user local tool -
   zone 1 is untouched, per ADR-0005 clause 1.
5. BOUNDARIES EXTEND: frontend/MODULE.md card; the drift gate learns the
   frontend/ zone; CI gains a frontend job (typecheck + build). Node LTS
   becomes a dev prerequisite for zone 3 only - zones 1 and 2 build and
   test without it.

Consequences: UI development gains a mainstream toolchain and component
system at the cost of a Node toolchain in the repo (lockfile, node_modules,
build step - all confined to frontend/). The same-origin rule keeps auth
untouched; the OpenAPI-generated types keep the zones honest; the price
is that frontend PRs must regenerate types when the API changes (CI
catches a mismatch as a type error).
