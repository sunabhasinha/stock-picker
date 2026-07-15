"""
Doc-drift gate (L5): a PR that changes a module's source must update that
module's MODULE.md in the same PR, or explicitly opt out.

Rule (from AGENTS.md / ADR-0001): context files are only trustworthy if
code changes update the context they invalidate atomically. This check
makes that mechanical instead of a discipline heroic.

Escape hatch: include "[no-doc-update]" in any commit message in the PR
range (use it WITH a stated reason - reviewers can see it).

Usage: python3 .github/scripts/check_doc_drift.py <base_ref>
"""

from __future__ import annotations

import subprocess
import sys

PACKAGE = "sunabha_agent"
SUBMODULES = ("data", "screening", "strategies", "research", "portfolio")


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], check=True, capture_output=True, text=True
    ).stdout


FRONTEND_SOURCE = (".ts", ".tsx", ".css", ".html")
FRONTEND_EXEMPT = (
    "frontend/src/api/schema.d.ts",  # generated from openapi.json
    "frontend/package-lock.json",
)


def module_card_for(path: str) -> str | None:
    """Map a changed source file to the MODULE.md that must accompany it."""
    if path.startswith("app/") and path.endswith(".py"):
        return "app/MODULE.md"  # the application shell (ADR-0005 zone 2)
    if (
        path.startswith("frontend/")
        and path.endswith(FRONTEND_SOURCE)
        and path not in FRONTEND_EXEMPT
    ):
        return "frontend/MODULE.md"  # zone 3 (ADR-0007)
    if not path.startswith(f"{PACKAGE}/") or not (
        path.endswith(".py") or path.startswith(f"{PACKAGE}/static/")
    ):
        return None
    parts = path.split("/")
    if len(parts) >= 3 and parts[1] in SUBMODULES:
        return f"{PACKAGE}/{parts[1]}/MODULE.md"
    return f"{PACKAGE}/MODULE.md"  # engine app layer (scan.py, web.py, static/)


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    changed = set(git("diff", "--name-only", f"{base}...HEAD").splitlines())
    messages = git("log", "--format=%B", f"{base}..HEAD")

    if "[no-doc-update]" in messages:
        print("doc-drift: opt-out marker found in commit messages - skipping.")
        return 0

    missing: dict[str, list[str]] = {}
    for path in sorted(changed):
        card = module_card_for(path)
        if card and card not in changed:
            missing.setdefault(card, []).append(path)

    if not missing:
        print("doc-drift: OK - every touched module's MODULE.md is current "
              "or untouched modules only.")
        return 0

    print("doc-drift: FAIL - source changed without its module card:\n")
    for card, paths in missing.items():
        print(f"  {card} not updated, but these changed:")
        for p in paths:
            print(f"    - {p}")
    print(
        "\nEither update the MODULE.md(s) in this PR (interface, deps, or "
        "blast radius may have moved), or add '[no-doc-update]' to a commit "
        "message with a reason."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
