"""
Tests for the local web UI backend.

A real ThreadingHTTPServer on an ephemeral port with a FAKE scanner
factory injected - exercises the actual HTTP surface (routes, JSON
shapes, job lifecycle) with zero network and instant "scans".
"""

import datetime as dt
import json
import threading
import time
import unittest
import urllib.request

from sunabha_agent.data.models import Signal, Universe
from sunabha_agent.scan import ScanReport
from sunabha_agent.web import WebApp, serve


def fake_report():
    return ScanReport(
        category_key="category_2",
        as_of=dt.date(2026, 7, 2),
        ranked_candidates=[(
            Signal(
                symbol="ALPHA", strategy_name="SMA Strategy",
                universe_at_signal_time=Universe.V40, action="BUY",
                trigger_date=dt.date(2026, 7, 2), signal_price=100.0,
                rationale="test rationale",
            ),
            None,
        )],
        errors=["BROKEN: boom"],
        scanned_symbols=["ALPHA", "BROKEN"],
    )


class FakeScanner:
    def __init__(self, category_key):
        self.category_key = category_key

    def scan(self, symbols=None, positions=None, progress=None):
        if progress:
            progress(0, 2, "ALPHA")
        return fake_report()


class TestWebApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = WebApp(scanner_factory=FakeScanner)
        cls.server = serve(port=0, app=cls.app)
        cls.port = cls.server.server_address[1]
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def _get(self, path):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{self.port}{path}") as r:
                return r.status, r.headers.get("Content-Type", ""), r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.headers.get("Content-Type", ""), e.read()

    def _post(self, path, body):
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def test_index_page_served(self):
        status, ctype, body = self._get("/")
        self.assertEqual(status, 200)
        self.assertIn("text/html", ctype)
        self.assertIn(b"Daily Scan", body)

    def test_categories_endpoint_lists_the_four_presets(self):
        status, _, body = self._get("/api/categories")
        self.assertEqual(status, 200)
        cats = json.loads(body)
        self.assertEqual({c["key"] for c in cats},
                         {"category_1", "category_2", "category_3", "category_4"})
        cat2 = next(c for c in cats if c["key"] == "category_2")
        self.assertEqual(len(cat2["strategies"]), 8)
        self.assertEqual(cat2["universes"], ["V40"])

    def test_scan_job_lifecycle(self):
        status, body = self._post("/api/scan",
                                  {"category": "category_2", "symbols": "alpha, broken"})
        self.assertEqual(status, 202)
        job_id = body["job_id"]

        deadline = time.time() + 5
        job = None
        while time.time() < deadline:
            _, _, raw = self._get(f"/api/scan/{job_id}")
            job = json.loads(raw)
            if job["status"] == "done":
                break
            time.sleep(0.02)
        self.assertEqual(job["status"], "done")
        report = job["report"]
        self.assertEqual(report["category"], "category_2")
        self.assertEqual(report["ranked_candidates"][0]["signal"]["symbol"], "ALPHA")
        self.assertEqual(report["errors"], ["BROKEN: boom"])

    def test_unknown_category_is_a_400(self):
        status, body = self._post("/api/scan", {"category": "category_99"})
        self.assertEqual(status, 400)
        self.assertIn("category_99", body["error"])

    def test_unknown_job_is_a_404(self):
        status, _, body = self._get("/api/scan/nope")
        self.assertEqual(status, 404)

    def test_unknown_path_is_a_404(self):
        status, _, _ = self._get("/definitely/not/here")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
