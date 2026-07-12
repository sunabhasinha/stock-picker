"""
The application SHELL (ADR-0005).

This package is the dependency-bearing zone: database, and later auth and
hosted serving. It IMPORTS the pure engine (`sunabha_agent`) and never the
reverse - `sunabha_agent/` must contain no `app` imports, ever. The drift
gate and app/MODULE.md police that boundary.
"""
