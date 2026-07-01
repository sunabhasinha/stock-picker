"""
The daily scan: the first end-to-end "what should I look at today".

Wires the layers together in the order the course demands:
curated universe list -> live data (fetcher) -> fundamental gate ->
the user's ONE selected Category (engine) -> ranked candidates
(Section 4.20 hierarchy) -> a human-readable report.

Every signal that reaches the report still carries its own
requires_human_confirmation flag and rationale - this runner finds and
orders candidates; it never executes anything.

Scan scope: by default we scan the curated V40/V40Next symbols that fall
inside the selected category's universe. Two universes cannot be
enumerated from the curated file and need explicit symbol lists from the
caller: V200 (a live quantitative screen, not a static list) and
Strategy 7's NSE-wide universe (~1,600 symbols). Pass `symbols=`
explicitly to scan those.

Held positions go in a positions dict/JSON file (see
positions_from_dict); the scan then also runs Section 6.3's
reconciliation on each holding - the output the course says answers
nearly every "I hold X, what do I do?" question.

CLI:  python3 -m sunabha_agent.scan --category category_2
      [--symbols TCS,TITAN] [--positions positions.json]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from dataclasses import dataclass, field
from typing import Optional

from sunabha_agent.data.fetcher import NSEFetcher, ScreenerFetcher
from sunabha_agent.data.models import CompanyType, Fundamentals, Signal, Universe
from sunabha_agent.data.universe_lists import UniverseRegistry
from sunabha_agent.portfolio.category_engine import (
    PRESET_CATEGORIES,
    Category,
    CategoryEngine,
    HoldingReconciliation,
)
from sunabha_agent.research.turnaround_checklist import ResearchProvider


@dataclass
class Position:
    """One held stock, as the user records it. open_trades are the entries
    still open under this framework's strategies (empty for legacy holdings
    acquired before/outside the framework)."""

    average_cost: float
    open_trades: list[Signal] = field(default_factory=list)


@dataclass
class ScanReport:
    category_key: str
    as_of: dt.date
    #: BUY/AVERAGE candidates, best-first per the Section 4.20 hierarchy,
    #: paired with the fundamentals used to rank them.
    ranked_candidates: list[tuple[Signal, Optional[Fundamentals]]] = field(default_factory=list)
    #: SELL signals for open trades - surfaced first, exits are never queued
    #: behind new ideas.
    exit_signals: list[Signal] = field(default_factory=list)
    #: Section 6.3 reconciliation verdicts for each held position.
    reconciliations: list[HoldingReconciliation] = field(default_factory=list)
    #: Per-symbol fetch/parse failures. A bad symbol must never kill the
    #: scan - same no-crash posture as the strategy layer.
    errors: list[str] = field(default_factory=list)
    scanned_symbols: list[str] = field(default_factory=list)


def positions_from_dict(raw: dict) -> dict[str, Position]:
    """
    Parse the positions file format:
      { "SYMBOL": { "average_cost": 123.0,
                    "open_trades": [ { "strategy_name": "...", "action": "BUY",
                                       "entry_price": 100.0,
                                       "entry_date": "2024-01-05",
                                       "target_price": 140.0,     # optional
                                       "metadata": {...} } ] } }  # optional
    """
    positions: dict[str, Position] = {}
    for symbol, body in raw.items():
        trades = [
            Signal(
                symbol=symbol.upper(),
                strategy_name=t["strategy_name"],
                universe_at_signal_time=Universe.UNCLASSIFIED,  # rebuilt at scan time
                action=t.get("action", "BUY"),
                trigger_date=dt.date.fromisoformat(t["entry_date"]),
                signal_price=float(t["entry_price"]),
                target_price=(
                    float(t["target_price"]) if t.get("target_price") is not None else None
                ),
                metadata=dict(t.get("metadata", {})),
            )
            for t in body.get("open_trades", [])
        ]
        positions[symbol.upper()] = Position(
            average_cost=float(body["average_cost"]), open_trades=trades
        )
    return positions


class DailyScanner:
    """One configured scanner = one selected Category (Section 6.3's
    pick-exactly-one rule) + the data sources. Fetchers are injectable for
    tests and for callers who add caching."""

    def __init__(
        self,
        category: Category,
        registry: Optional[UniverseRegistry] = None,
        price_fetcher: Optional[NSEFetcher] = None,
        fundamentals_fetcher: Optional[ScreenerFetcher] = None,
        researcher: Optional[ResearchProvider] = None,
    ):
        self.engine = CategoryEngine(category, researcher)
        self.registry = registry or UniverseRegistry.from_yaml()
        self.price_fetcher = price_fetcher or NSEFetcher()
        self.fundamentals_fetcher = fundamentals_fetcher or ScreenerFetcher()

    def default_symbols(self) -> list[str]:
        """Curated symbols inside the selected category's universe."""
        return [
            s
            for s in self.registry.all_symbols()
            if self.registry.universe_of(s) in self.engine.category.universes
        ]

    def scan(
        self,
        symbols: Optional[list[str]] = None,
        positions: Optional[dict[str, Position]] = None,
    ) -> ScanReport:
        positions = positions or {}
        symbols = symbols if symbols is not None else self.default_symbols()
        # Held stocks always get looked at, even if outside today's scan list.
        symbols = list(dict.fromkeys([*symbols, *positions.keys()]))

        report = ScanReport(
            category_key=self.engine.category.key,
            as_of=dt.date.today(),
            scanned_symbols=symbols,
        )
        buy_candidates: list[tuple[Signal, Optional[Fundamentals]]] = []

        for symbol in symbols:
            position = positions.get(symbol)
            open_trades = position.open_trades if position else []
            try:
                prices = self.price_fetcher.fetch_full_history(symbol)
                if not prices.candles:
                    raise ValueError("no price history returned")
                entry = self.registry.lookup(symbol)
                fundamentals = self.fundamentals_fetcher.fetch(
                    symbol,
                    company_type=entry.company_type if entry else CompanyType.STANDARD,
                    # The NSE price pull just succeeded - that IS the evidence
                    # for Strategy 7's NSE-listing gate (Section 5.0).
                    listed_on_nse=True,
                )
                universe = self.registry.universe_of(symbol)

                signals = self.engine.evaluate_stock(
                    prices, fundamentals, universe, open_trades
                )
                for signal in signals:
                    if signal.action == "SELL":
                        report.exit_signals.append(signal)
                    else:
                        buy_candidates.append((signal, fundamentals))

                if position is not None:
                    report.reconciliations.append(
                        self.engine.reconcile_holding(
                            prices, fundamentals, universe, open_trades,
                            average_cost=position.average_cost,
                        )
                    )
            except Exception as exc:  # noqa: BLE001 - one bad symbol must
                # never kill the whole scan; the error is surfaced instead
                report.errors.append(f"{symbol}: {exc}")

        report.ranked_candidates = CategoryEngine.rank_candidates(buy_candidates)
        return report


def format_report(report: ScanReport) -> str:
    lines = [
        f"Daily scan — category: {report.category_key} — {report.as_of.isoformat()}",
        f"Scanned {len(report.scanned_symbols)} symbol(s).",
        "",
    ]

    if report.exit_signals:
        lines.append("== EXITS (act on these first) ==")
        for s in report.exit_signals:
            lines.append(f"  SELL {s.symbol} @ {s.signal_price:.2f} [{s.strategy_name}]")
            lines.append(f"       {s.rationale}")
        lines.append("")

    lines.append("== BUY CANDIDATES (ranked per Section 4.20) ==")
    if report.ranked_candidates:
        for i, (s, _) in enumerate(report.ranked_candidates, start=1):
            confirm = " [NEEDS HUMAN CONFIRMATION]" if s.requires_human_confirmation else ""
            target = f" -> target {s.target_price:.2f}" if s.target_price else ""
            lines.append(
                f"  {i}. {s.action} {s.symbol} @ {s.signal_price:.2f}{target} "
                f"({s.suggested_position_pct:.0f}%) [{s.strategy_name}]"
                f"{confirm}"
            )
            lines.append(f"     {s.rationale}")
    else:
        lines.append("  None today. Per the category's idle-capital rule, hold cash —")
        lines.append("  never substitute an out-of-category strategy to stay invested.")
    lines.append("")

    if report.reconciliations:
        lines.append("== HELD POSITIONS (Section 6.3 reconciliation) ==")
        for r in report.reconciliations:
            lines.append(f"  {r.symbol}: {r.action.value}")
            lines.append(f"     {r.rationale}")
        lines.append("")

    if report.errors:
        lines.append("== ERRORS (symbols skipped, fix and re-run) ==")
        for e in report.errors:
            lines.append(f"  {e}")
        lines.append("")

    return "\n".join(lines)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the daily scan for ONE selected category."
    )
    parser.add_argument(
        "--category", required=True, choices=sorted(PRESET_CATEGORIES),
        help="The user's single committed category (Section 6.3).",
    )
    parser.add_argument(
        "--symbols", default=None,
        help="Comma-separated symbols to scan (default: curated list within "
        "the category's universe).",
    )
    parser.add_argument(
        "--positions", default=None,
        help="Path to a positions JSON file (see positions_from_dict).",
    )
    args = parser.parse_args(argv)

    positions = None
    if args.positions:
        with open(args.positions) as f:
            positions = positions_from_dict(json.load(f))

    scanner = DailyScanner(PRESET_CATEGORIES[args.category])
    report = scanner.scan(
        symbols=[s.strip().upper() for s in args.symbols.split(",")] if args.symbols else None,
        positions=positions,
    )
    print(format_report(report))
    return 1 if report.errors and not report.scanned_symbols else 0


if __name__ == "__main__":
    sys.exit(main())
