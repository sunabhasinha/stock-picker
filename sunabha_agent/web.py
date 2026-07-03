"""
Local web UI for the daily scan.

A single-user, localhost tool (matching the course's explicit
single-user philosophy, Section 3.5 - no sharing/community layer):
pick your ONE category, optionally narrow the symbols, paste holdings,
run the scan, review the ranked signals with their full rationales.
Nothing here executes trades - like everything else in this project, the
output is candidates for a human to act on.

Stdlib-only (http.server + threading), consistent with the rest of the
project. Live scans take minutes (one price-history + one fundamentals
pull per symbol), so a scan runs as a background job the page polls:

    POST /api/scan {category, symbols?, positions?} -> {job_id}
    GET  /api/scan/<job_id> -> {status, progress, report?}
    GET  /api/categories -> the four presets, for the picker
    GET  /       -> the single-page UI (sunabha_agent/static/index.html)

Run:  python3 -m sunabha_agent.web [--port 8788]
"""

from __future__ import annotations

import argparse
import json
import threading
import uuid
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable, Optional

from sunabha_agent.data.models import Fundamentals, Signal
from sunabha_agent.portfolio.category_engine import PRESET_CATEGORIES
from sunabha_agent.scan import DailyScanner, ScanReport, positions_from_dict

STATIC_DIR = Path(__file__).resolve().parent / "static"


# --------------------------------------------------------------------------
# JSON serialization (dataclass -> plain dicts the frontend renders)
# --------------------------------------------------------------------------


def signal_to_dict(s: Signal) -> dict:
    return {
        "symbol": s.symbol,
        "strategy": s.strategy_name,
        "action": s.action,
        "signal_price": s.signal_price,
        "target_price": s.target_price,
        "suggested_position_pct": s.suggested_position_pct,
        "requires_human_confirmation": s.requires_human_confirmation,
        "rationale": s.rationale,
        "universe": s.universe_at_signal_time.value,
        "trigger_date": s.trigger_date.isoformat(),
        "metadata": s.metadata,
    }


def fundamentals_to_dict(f: Optional[Fundamentals]) -> Optional[dict]:
    if f is None:
        return None
    return {
        "roce_pct": f.roce_pct,
        "roe_pct": f.roe_pct,
        "debt_to_equity": f.debt_to_equity,
        "market_cap_cr": f.market_cap_cr,
        "promoter_holding_pct": f.promoter_holding_pct,
    }


def report_to_dict(report: ScanReport) -> dict:
    return {
        "category": report.category_key,
        "as_of": report.as_of.isoformat(),
        "scanned_symbols": report.scanned_symbols,
        "exit_signals": [signal_to_dict(s) for s in report.exit_signals],
        "ranked_candidates": [
            {"signal": signal_to_dict(s), "fundamentals": fundamentals_to_dict(f)}
            for s, f in report.ranked_candidates
        ],
        "reconciliations": [
            {"symbol": r.symbol, "action": r.action.value, "rationale": r.rationale}
            for r in report.reconciliations
        ],
        "errors": report.errors,
    }


def categories_payload() -> list[dict]:
    return [
        {
            "key": c.key,
            "name": c.name,
            "universes": [u.value for u in c.universes],
            "strategies": [cls().name for cls in c.strategy_classes],
            "max_allocation_pct_per_stock": c.max_allocation_pct_per_stock,
            "idle_capital_note": c.idle_capital_note,
        }
        for c in PRESET_CATEGORIES.values()
    ]


# --------------------------------------------------------------------------
# Background scan jobs
# --------------------------------------------------------------------------


@dataclass
class ScanJob:
    job_id: str
    status: str = "running"  # running | done | error
    done: int = 0
    total: int = 0
    current_symbol: str = ""
    report: Optional[dict] = None
    error: Optional[str] = None
    lock: threading.Lock = field(default_factory=threading.Lock)

    def snapshot(self) -> dict:
        with self.lock:
            body = {
                "job_id": self.job_id,
                "status": self.status,
                "progress": {
                    "done": self.done,
                    "total": self.total,
                    "current_symbol": self.current_symbol,
                },
            }
            if self.report is not None:
                body["report"] = self.report
            if self.error is not None:
                body["error"] = self.error
            return body


class WebApp:
    """Holds the jobs and the scanner factory. `scanner_factory` is
    injectable so tests run with fakes and no network."""

    def __init__(
        self, scanner_factory: Optional[Callable[[str], DailyScanner]] = None
    ):
        self._scanner_factory = scanner_factory or (
            lambda key: DailyScanner(PRESET_CATEGORIES[key])
        )
        self._jobs: dict[str, ScanJob] = {}

    def start_scan(
        self,
        category_key: str,
        symbols: Optional[list[str]],
        positions_raw: Optional[dict],
    ) -> str:
        if category_key not in PRESET_CATEGORIES:
            raise KeyError(f"unknown category: {category_key}")
        positions = positions_from_dict(positions_raw) if positions_raw else None
        job = ScanJob(job_id=uuid.uuid4().hex[:12])
        self._jobs[job.job_id] = job

        def on_progress(done: int, total: int, symbol: str) -> None:
            with job.lock:
                job.done, job.total, job.current_symbol = done, total, symbol

        def run() -> None:
            try:
                scanner = self._scanner_factory(category_key)
                report = scanner.scan(
                    symbols=symbols, positions=positions, progress=on_progress
                )
                with job.lock:
                    job.report = report_to_dict(report)
                    job.status = "done"
            except Exception as exc:  # surfaced to the UI, never a dead job
                with job.lock:
                    job.error = f"{type(exc).__name__}: {exc}"
                    job.status = "error"

        threading.Thread(target=run, daemon=True).start()
        return job.job_id

    def job(self, job_id: str) -> Optional[ScanJob]:
        return self._jobs.get(job_id)


# --------------------------------------------------------------------------
# HTTP layer
# --------------------------------------------------------------------------


def make_handler(app: WebApp):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # quiet by default
            pass

        def _send_json(self, body: dict | list, status: int = 200) -> None:
            payload = json.dumps(body).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                page = (STATIC_DIR / "index.html").read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(page)))
                self.end_headers()
                self.wfile.write(page)
            elif self.path == "/api/categories":
                self._send_json(categories_payload())
            elif self.path.startswith("/api/scan/"):
                job = app.job(self.path.rsplit("/", 1)[-1])
                if job is None:
                    self._send_json({"error": "no such job"}, status=404)
                else:
                    self._send_json(job.snapshot())
            else:
                self._send_json({"error": "not found"}, status=404)

        def do_POST(self):
            if self.path != "/api/scan":
                self._send_json({"error": "not found"}, status=404)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                body = json.loads(self.rfile.read(length) or b"{}")
                symbols = body.get("symbols") or None
                if isinstance(symbols, str):
                    symbols = [s.strip().upper() for s in symbols.split(",") if s.strip()]
                job_id = app.start_scan(
                    category_key=body.get("category", ""),
                    symbols=symbols,
                    positions_raw=body.get("positions") or None,
                )
                self._send_json({"job_id": job_id}, status=202)
            except (KeyError, ValueError, json.JSONDecodeError) as exc:
                self._send_json({"error": str(exc)}, status=400)

    return Handler


def serve(port: int = 8788, app: Optional[WebApp] = None) -> ThreadingHTTPServer:
    """Build the server (bound to localhost only - this is a single-user
    local tool, never expose it). Caller decides serve_forever vs thread."""
    return ThreadingHTTPServer(("127.0.0.1", port), make_handler(app or WebApp()))


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Local web UI for the daily scan.")
    parser.add_argument("--port", type=int, default=8788)
    args = parser.parse_args(argv)
    server = serve(port=args.port)
    print(f"Sunabha Agent UI: http://127.0.0.1:{args.port}/  (Ctrl-C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
