"""
Architecture diagram generator: derives Mermaid block diagrams from the
ACTUAL code (import analysis + known-external detection) and writes
docs/architecture.md. Stdlib-only, deterministic (sorted everywhere) so
diffs are stable.

Why generated: a hand-maintained diagram rots (ADR-0001's wiki problem).
This one is recomputed from source; the architecture workflow fails any
PR whose committed diagram is stale. Regenerate with:

    python3 .github/scripts/generate_architecture.py

Growth plan (documented in the output header too):
- L0 zone diagram: one node per zone + externals - stays small forever.
- L1 per-zone diagrams: one node per PACKAGE (never per file). A new
  package = one new node; files never appear individually.
- If a zone ever exceeds ~12 packages, split its L1 into per-package L2
  sections here - the structure below already isolates each zone's
  rendering.
"""

from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "docs" / "architecture.md"

#: zone dir -> (mermaid id prefix, human label)
ZONES = {
    "sunabha_agent": ("eng", "Zone 1 — Engine (pure Python, KB-traceable)"),
    "app": ("shell", "Zone 2 — Shell (FastAPI, auth, DB)"),
    "frontend": ("fe", "Zone 3 — Frontend (React + TypeScript)"),
}

#: substring found in source -> (external id, label). Detection is
#: derived from the code, not hand-listed per module.
EXTERNAL_PATTERNS = {
    "yfinance": ("yahoo", "Yahoo Finance"),
    "screener.in": ("screener", "Screener.in"),
    "nseindia.com": ("nse", "NSE"),
    "api.anthropic.com": ("claude", "Claude API"),
    "DATABASE_URL": ("postgres", "Supabase Postgres"),
}

#: substring -> entry-point kind (drawn as User-facing)
ENTRY_PATTERNS = {
    "FastAPI(": "HTTP API",
    "ThreadingHTTPServer": "local web UI",
    "ArgumentParser(": "CLI",
}


def module_node(zone: str, path: Path) -> str | None:
    """Collapse a file to its zone-level package node (growth rule: one
    node per package, top-level files keep their stem)."""
    rel = path.relative_to(REPO / zone)
    if "__pycache__" in rel.parts:
        return None
    if len(rel.parts) == 1:
        stem = rel.stem
        return None if stem == "__init__" else stem
    return rel.parts[0]


def scan_zone(zone: str):
    """Returns (nodes, internal_edges, cross_edges, external_edges,
    entry_points) for one zone - all sets of tuples, later sorted."""
    root = REPO / zone
    nodes: set[str] = set()
    internal: set[tuple[str, str]] = set()
    cross: set[tuple[str, str, str]] = set()  # (node, other_zone, other_node)
    external: set[tuple[str, str]] = set()  # (node, external_id)
    entries: dict[str, str] = {}

    if not root.exists():
        return nodes, internal, cross, external, entries

    for path in sorted(root.rglob("*.py")):
        node = module_node(zone, path)
        if node is None:
            continue
        nodes.add(node)
        text = path.read_text(errors="replace")

        for needle, (ext_id, _) in EXTERNAL_PATTERNS.items():
            if needle in text:
                external.add((node, ext_id))
        for needle, kind in ENTRY_PATTERNS.items():
            if needle in text:
                entries.setdefault(node, kind)

        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for imported in _imported_modules(tree):
            parts = imported.split(".")
            if parts[0] not in ZONES:
                continue
            target_zone = parts[0]
            target_node = parts[1] if len(parts) > 1 else parts[0]
            if target_zone == zone:
                if target_node != node:
                    internal.add((node, target_node))
            else:
                cross.add((node, target_zone, target_node))
    return nodes, internal, cross, external, entries


def _imported_modules(tree: ast.AST):
    for stmt in ast.walk(tree):
        if isinstance(stmt, ast.Import):
            for alias in stmt.names:
                yield alias.name
        elif isinstance(stmt, ast.ImportFrom) and stmt.module:
            yield stmt.module


def render() -> str:
    per_zone = {zone: scan_zone(zone) for zone in ZONES}
    used_externals = sorted({
        ext for _, _, _, external, _ in per_zone.values() for _, ext in external
    })
    ext_labels = {eid: label for eid, label in EXTERNAL_PATTERNS.values()}

    lines = [
        "# Architecture — block diagrams",
        "",
        "**AUTO-GENERATED — do not edit by hand.** Derived from import",
        "analysis of the actual code. Regenerate after structural changes:",
        "",
        "```bash",
        "python3 .github/scripts/generate_architecture.py",
        "```",
        "",
        "CI (architecture workflow) fails any PR where this file is stale.",
        "",
        "Growth plan: the L0 diagram stays zone-level forever; L1 diagrams",
        "are one-node-per-package (files never appear); a zone exceeding",
        "~12 packages gets split into per-package L2 sections.",
        "",
        "## L0 — zones and external systems",
        "",
        "```mermaid",
        "flowchart LR",
        '    user(["User / Browser"])',
    ]

    # L0: zone boxes, user edges to zones with entry points, zone->zone,
    # zone->external (aggregated).
    for zone, (prefix, label) in ZONES.items():
        nodes, _, _, _, _ = per_zone[zone]
        if nodes:
            lines.append(f'    {prefix}["{label.split(" — ")[1]}"]')
    for ext in used_externals:
        lines.append(f'    ext_{ext}(("{ext_labels[ext]}"))')

    l0_edges: set[tuple[str, str]] = set()
    for zone, (prefix, _) in ZONES.items():
        nodes, _, cross, external, entries = per_zone[zone]
        if not nodes:
            continue
        if entries:
            l0_edges.add(("user", prefix))
        for _, other_zone, _ in cross:
            l0_edges.add((prefix, ZONES[other_zone][0]))
        for _, ext in external:
            l0_edges.add((prefix, f"ext_{ext}"))
    for a, b in sorted(l0_edges):
        lines.append(f"    {a} --> {b}")
    lines += ["```", ""]

    # L1 per zone
    for zone, (prefix, label) in ZONES.items():
        nodes, internal, cross, external, entries = per_zone[zone]
        if not nodes:
            lines += [f"## L1 — {label}", "", "_(zone not present yet)_", ""]
            continue
        lines += [f"## L1 — {label}", "", "```mermaid", "flowchart TD"]
        lines.append(f'    subgraph {prefix}_zone["{label}"]')
        for node in sorted(nodes):
            suffix = f"<br/><i>{entries[node]}</i>" if node in entries else ""
            lines.append(f'        {prefix}_{node}["{node}{suffix}"]')
        lines.append("    end")
        for ext in sorted({e for _, e in external}):
            lines.append(f'    ext_{ext}(("{ext_labels[ext]}"))')
        for a, b in sorted(internal):
            lines.append(f"    {prefix}_{a} --> {prefix}_{b}")
        for a, other_zone, other_node in sorted(cross):
            other_prefix = ZONES[other_zone][0]
            lines.append(
                f'    {prefix}_{a} --> {other_prefix}_x_{other_node}'
                f'["{other_zone}/{other_node}"]'
            )
        for a, ext in sorted(external):
            lines.append(f"    {prefix}_{a} --> ext_{ext}")
        lines += ["```", ""]

    lines += [
        "## Reading guide",
        "",
        "- Solid arrows = imports (zone-internal or cross-zone) or a",
        "  detected call-out to an external system.",
        "- Cross-zone arrows only ever point from shell to engine —",
        "  the reverse would violate engine purity (ADR-0005; enforced by",
        "  tests/test_app_db.py::TestEnginePurity).",
        "- Module responsibilities live in each package's MODULE.md (L4);",
        "  this file shows SHAPE, the cards show MEANING.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    OUTPUT.write_text(render())
    print(f"wrote {OUTPUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
