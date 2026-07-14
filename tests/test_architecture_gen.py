"""
Tests for the architecture-diagram generator (.github/scripts).

The generator's contract: deterministic (same code -> byte-identical
output, or the CI staleness check would flap) and honest (the edges it
draws reflect real imports).
"""

import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / ".github" / "scripts"))

import generate_architecture as gen  # noqa: E402


class TestGenerator(unittest.TestCase):
    def test_output_is_deterministic(self):
        self.assertEqual(gen.render(), gen.render())

    def test_zones_and_known_edges_present(self):
        output = gen.render()
        self.assertIn("Engine (pure Python", output)
        self.assertIn("shell --> eng", output)  # shell imports engine
        self.assertNotIn("eng --> shell", output)  # NEVER the reverse
        self.assertIn("ext_yahoo", output)  # fetcher's default price source
        self.assertIn("ext_postgres", output)  # the shell's database

    def test_engine_l1_reflects_real_imports(self):
        output = gen.render()
        # The portfolio engine imports strategies/screening/data - the
        # load-bearing internal edges must appear.
        self.assertIn("eng_portfolio --> eng_strategies", output)
        self.assertIn("eng_portfolio --> eng_screening", output)
        self.assertIn("eng_scan --> eng_portfolio", output)


if __name__ == "__main__":
    unittest.main()
