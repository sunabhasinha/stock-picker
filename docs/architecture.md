# Architecture — block diagrams

**AUTO-GENERATED — do not edit by hand.** Derived from import
analysis of the actual code. Regenerate after structural changes:

```bash
python3 .github/scripts/generate_architecture.py
```

CI (architecture workflow) fails any PR where this file is stale.

Growth plan: the L0 diagram stays zone-level forever; L1 diagrams
are one-node-per-package (files never appear); a zone exceeding
~12 packages gets split into per-package L2 sections.

## L0 — zones and external systems

```mermaid
flowchart LR
    user(["User / Browser"])
    eng["Engine (pure Python, KB-traceable)"]
    shell["Shell (FastAPI, auth, DB)"]
    ext_claude(("Claude API"))
    ext_nse(("NSE"))
    ext_postgres(("Supabase Postgres"))
    ext_screener(("Screener.in"))
    ext_yahoo(("Yahoo Finance"))
    eng --> ext_claude
    eng --> ext_nse
    eng --> ext_screener
    eng --> ext_yahoo
    shell --> eng
    shell --> ext_postgres
    user --> eng
    user --> shell
```

## L1 — Zone 1 — Engine (pure Python, KB-traceable)

```mermaid
flowchart TD
    subgraph eng_zone["Zone 1 — Engine (pure Python, KB-traceable)"]
        eng_data["data"]
        eng_portfolio["portfolio"]
        eng_research["research"]
        eng_scan["scan<br/><i>CLI</i>"]
        eng_screening["screening"]
        eng_strategies["strategies"]
        eng_web["web<br/><i>local web UI</i>"]
    end
    ext_claude(("Claude API"))
    ext_nse(("NSE"))
    ext_screener(("Screener.in"))
    ext_yahoo(("Yahoo Finance"))
    eng_portfolio --> eng_data
    eng_portfolio --> eng_research
    eng_portfolio --> eng_screening
    eng_portfolio --> eng_strategies
    eng_research --> eng_data
    eng_scan --> eng_data
    eng_scan --> eng_portfolio
    eng_scan --> eng_research
    eng_screening --> eng_data
    eng_strategies --> eng_data
    eng_strategies --> eng_research
    eng_web --> eng_data
    eng_web --> eng_portfolio
    eng_web --> eng_scan
    eng_data --> ext_nse
    eng_data --> ext_screener
    eng_data --> ext_yahoo
    eng_research --> ext_claude
```

## L1 — Zone 2 — Shell (FastAPI, auth, DB)

```mermaid
flowchart TD
    subgraph shell_zone["Zone 2 — Shell (FastAPI, auth, DB)"]
        shell_auth["auth"]
        shell_db["db"]
        shell_migrations["migrations"]
        shell_server["server<br/><i>HTTP API</i>"]
    end
    ext_postgres(("Supabase Postgres"))
    shell_auth --> shell_db
    shell_migrations --> shell_db
    shell_server --> shell_auth
    shell_server --> shell_db
    shell_db --> eng_x_data["sunabha_agent/data"]
    shell_db --> eng_x_scan["sunabha_agent/scan"]
    shell_db --> eng_x_web["sunabha_agent/web"]
    shell_server --> eng_x_portfolio["sunabha_agent/portfolio"]
    shell_db --> ext_postgres
    shell_migrations --> ext_postgres
    shell_server --> ext_postgres
```

## L1 — Zone 3 — Frontend (React + TypeScript)

_(zone not present yet)_

## Reading guide

- Solid arrows = imports (zone-internal or cross-zone) or a
  detected call-out to an external system.
- Cross-zone arrows only ever point from shell to engine —
  the reverse would violate engine purity (ADR-0005; enforced by
  tests/test_app_db.py::TestEnginePurity).
- Module responsibilities live in each package's MODULE.md (L4);
  this file shows SHAPE, the cards show MEANING.
