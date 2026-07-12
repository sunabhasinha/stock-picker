"""
Tests for the application shell's data layer (M1 spec:
docs/specs/user-data-layer.md).

Judgment call, recorded: the automated suite runs the ORM against
IN-MEMORY SQLITE (JSON variant of JSONB), which exercises the repository
logic and the lossless positions round-trip with zero infrastructure.
What SQLite cannot exercise - JSONB itself, RLS policies, server-side
UUID defaults - lives in the hand-written migration, which is validated
here by generating its full SQL offline (alembic --sql) and asserted
against a real Postgres as a live-verification step at deploy time
(the same unit-vs-live layering the journal reviews established).

The shell's dependencies are optional for the rest of the suite: these
tests skip cleanly when SQLAlchemy isn't installed, so the engine's
zero-dependency test experience is preserved (ADR-0002/0005).
"""

import datetime as dt
import pathlib
import subprocess
import sys
import unittest

try:
    import sqlalchemy  # noqa: F401
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


class TestEnginePurity(unittest.TestCase):
    """ADR-0005 clause 1, enforced mechanically: the engine never imports
    the shell. Runs regardless of whether shell deps are installed."""

    def test_sunabha_agent_never_imports_app(self):
        offenders = []
        for path in (REPO_ROOT / "sunabha_agent").rglob("*.py"):
            text = path.read_text()
            if "import app" in text or "from app" in text:
                offenders.append(str(path.relative_to(REPO_ROOT)))
        self.assertEqual(offenders, [], "engine must stay pure (ADR-0005)")


@unittest.skipUnless(HAS_SQLALCHEMY, "shell deps not installed (app/requirements.txt)")
class RepositoryTestCase(unittest.TestCase):
    def setUp(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import Session

        from app.db.models import Base
        from app.db.repository import Repository

        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        self.repo = Repository(self.session)
        user = self.repo.get_or_create_local_user()
        self.portfolio = self.repo.create_portfolio(
            user.id, "main", "category_2", dt.date(2026, 7, 1)
        )

    def tearDown(self):
        self.session.close()
        self.engine.dispose()


class TestHoldingsRoundTrip(RepositoryTestCase):
    RAW_POSITIONS = {
        "TCS": {
            "average_cost": 3200.5,
            "open_trades": [{
                "strategy_name": "Lifetime High Strategy",
                "action": "BUY",
                "entry_price": 3100.0,
                "entry_date": "2026-02-01",
                "target_price": 4100.0,
                "metadata": {"lifetime_high_at_entry": 4100.0},
            }],
        },
        "TITAN": {"average_cost": 3400.0, "open_trades": []},
    }

    def test_lossless_round_trip_with_positions_json_contract(self):
        # Spec acceptance: positions_from_dict <-> DB is lossless.
        from sunabha_agent.scan import positions_from_dict

        original = positions_from_dict(self.RAW_POSITIONS)
        self.repo.replace_holdings_from_positions(self.portfolio.id, original)
        restored = self.repo.positions_for(self.portfolio.id)

        self.assertEqual(set(restored), {"TCS", "TITAN"})
        self.assertEqual(restored["TCS"].average_cost, 3200.5)
        trade_out, trade_in = restored["TCS"].open_trades[0], original["TCS"].open_trades[0]
        for field in ("strategy_name", "action", "signal_price",
                      "trigger_date", "target_price", "metadata"):
            self.assertEqual(getattr(trade_out, field), getattr(trade_in, field))

    def test_replace_is_a_full_sync(self):
        from sunabha_agent.scan import positions_from_dict

        self.repo.replace_holdings_from_positions(
            self.portfolio.id, positions_from_dict(self.RAW_POSITIONS)
        )
        # TITAN sold, TCS cost updated:
        self.repo.replace_holdings_from_positions(
            self.portfolio.id,
            positions_from_dict({"TCS": {"average_cost": 3250.0}}),
        )
        restored = self.repo.positions_for(self.portfolio.id)
        self.assertEqual(set(restored), {"TCS"})
        self.assertEqual(restored["TCS"].average_cost, 3250.0)


class TestSignalEvents(RepositoryTestCase):
    def _fake_report(self):
        from sunabha_agent.data.models import Signal, Universe
        from sunabha_agent.scan import ScanReport

        buy = Signal(symbol="RELIANCE", strategy_name="SMA Strategy",
                     universe_at_signal_time=Universe.V40, action="BUY",
                     trigger_date=dt.date(2026, 7, 10), signal_price=1293.9,
                     rationale="test")
        sell = Signal(symbol="TCS", strategy_name="V20 Strategy",
                      universe_at_signal_time=Universe.V40, action="SELL",
                      trigger_date=dt.date(2026, 7, 10), signal_price=2100.0)
        return ScanReport(category_key="category_2", as_of=dt.date(2026, 7, 10),
                          ranked_candidates=[(buy, None)], exit_signals=[sell],
                          scanned_symbols=["RELIANCE", "TCS"])

    def test_record_scan_persists_run_and_pending_events(self):
        run = self.repo.record_scan(self.portfolio.id, self._fake_report())
        events = self.repo.pending_signals(self.portfolio.id)
        self.assertEqual(len(events), 2)
        self.assertEqual({e.action for e in events}, {"BUY", "SELL"})
        self.assertTrue(all(e.response == "pending" for e in events))
        self.assertTrue(all(e.scan_run_id == run.id for e in events))
        # The snapshot carries the full serialized signal, rationale included
        buy = next(e for e in events if e.action == "BUY")
        self.assertEqual(buy.signal["rationale"], "test")

    def test_respond_mutates_only_the_response(self):
        # ADR-0003 made structural: snapshot immutable, response tracked.
        self.repo.record_scan(self.portfolio.id, self._fake_report())
        event = self.repo.pending_signals(self.portfolio.id)[0]
        snapshot_before = dict(event.signal)

        updated = self.repo.respond_to_signal(event.id, "confirmed")
        self.assertEqual(updated.response, "confirmed")
        self.assertIsNotNone(updated.responded_at)
        self.assertEqual(updated.signal, snapshot_before)
        self.assertEqual(len(self.repo.pending_signals(self.portfolio.id)), 1)

    def test_invalid_response_rejected(self):
        self.repo.record_scan(self.portfolio.id, self._fake_report())
        event = self.repo.pending_signals(self.portfolio.id)[0]
        with self.assertRaises(ValueError):
            self.repo.respond_to_signal(event.id, "executed")  # no such thing -
            # nothing in this system executes (ADR-0003/0005)


class TestShadowSignals(RepositoryTestCase):
    def test_shadow_signals_recorded_per_category(self):
        from sqlalchemy import select

        from app.db.models import ShadowSignal
        from sunabha_agent.data.models import Signal, Universe

        s = Signal(symbol="TITAN", strategy_name="V20 Strategy",
                   universe_at_signal_time=Universe.V40, action="BUY",
                   trigger_date=dt.date(2026, 7, 10), signal_price=3400.0)
        self.repo.record_shadow_signals(
            self.portfolio.id, dt.date(2026, 7, 10),
            {"category_1": [], "category_4": [s]},
        )
        rows = list(self.session.scalars(select(ShadowSignal)))
        self.assertEqual({r.category_key for r in rows}, {"category_1", "category_4"})
        cat4 = next(r for r in rows if r.category_key == "category_4")
        self.assertEqual(cat4.signals[0]["symbol"], "TITAN")


@unittest.skipUnless(HAS_SQLALCHEMY, "shell deps not installed")
class TestMigrationSQL(unittest.TestCase):
    def test_initial_migration_generates_valid_postgres_sql_offline(self):
        """The migration is Postgres-only (JSONB, RLS) and can't run on
        SQLite - validate it by generating its full SQL offline instead."""
        try:
            import alembic  # noqa: F401
        except ImportError:
            self.skipTest("alembic not installed")
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "-c", "app/alembic.ini",
             "-x", "dry=1", "upgrade", "head", "--sql"],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        sql = result.stdout
        for expected in (
            "CREATE TABLE users", "CREATE TABLE portfolios",
            "CREATE TABLE holdings", "CREATE TABLE signal_events",
            "CREATE TABLE scan_runs", "CREATE TABLE shadow_signals",
            "ENABLE ROW LEVEL SECURITY", "CREATE POLICY",
            "INSERT INTO users",
        ):
            self.assertIn(expected, sql)


if __name__ == "__main__":
    unittest.main()
