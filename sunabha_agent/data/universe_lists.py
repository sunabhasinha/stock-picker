"""
Loads the curated V40 / V40 Next universe lists from config/v40_v40next.yaml.

This is deliberately a thin, dumb loader. The list itself is a qualitative
human judgment (Section 1.2) - this module's only job is to make that list
queryable, not to second-guess it.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from vivek_agent.data.models import CompanyType, Universe

_DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "v40_v40next.yaml"


@dataclass(frozen=True)
class UniverseEntry:
    symbol: str
    universe: Universe
    sector: str
    company_type: CompanyType
    note: str | None = None


class UniverseRegistry:
    """In-memory lookup of which curated universe (if any) a symbol belongs to."""

    def __init__(self, entries: list[UniverseEntry]):
        self._by_symbol: dict[str, UniverseEntry] = {e.symbol: e for e in entries}

    @classmethod
    def from_yaml(cls, path: Path = _DEFAULT_CONFIG_PATH) -> "UniverseRegistry":
        with open(path, "r") as f:
            raw = yaml.safe_load(f)

        entries: list[UniverseEntry] = []
        for row in raw.get("v40", []):
            entries.append(
                UniverseEntry(
                    symbol=row["symbol"],
                    universe=Universe.V40,
                    sector=row.get("sector", "Unknown"),
                    company_type=CompanyType(row.get("company_type", "STANDARD")),
                    note=row.get("note"),
                )
            )
        for row in raw.get("v40_next", []):
            entries.append(
                UniverseEntry(
                    symbol=row["symbol"],
                    universe=Universe.V40_NEXT,
                    sector=row.get("sector", "Unknown"),
                    company_type=CompanyType(row.get("company_type", "STANDARD")),
                    note=row.get("note"),
                )
            )
        return cls(entries)

    def lookup(self, symbol: str) -> UniverseEntry | None:
        return self._by_symbol.get(symbol.upper())

    def universe_of(self, symbol: str) -> Universe:
        """Returns V40 / V40_NEXT / UNCLASSIFIED. Does NOT check V200 - that's
        a live quantitative screen done separately against Fundamentals
        (see vivek_agent.screening.fundamental_gate), not a static lookup."""
        entry = self.lookup(symbol)
        return entry.universe if entry else Universe.UNCLASSIFIED

    def all_symbols(self, universe: Universe | None = None) -> list[str]:
        if universe is None:
            return list(self._by_symbol.keys())
        return [s for s, e in self._by_symbol.items() if e.universe == universe]

    def flagged_entries(self) -> list[UniverseEntry]:
        """Entries with an unresolved note (e.g. the JOFIN/JIOFIN typo flag) -
        surface these in any onboarding/setup UI so they don't get missed."""
        return [e for e in self._by_symbol.values() if e.note]
