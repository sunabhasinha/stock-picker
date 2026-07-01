"""
Tests for the fundamental screening gate.

These are written directly against the thresholds stated in
master_strategy_kb.md - not against "reasonable-sounding" numbers. Every
test case traces back to a specific section so a reviewer can check the
test against the source doc, not just against the code.
"""

import datetime as dt
import unittest

from vivek_agent.data.models import CompanyType, Fundamentals, Universe
from vivek_agent.screening.fundamental_gate import (
    PLEDGING_DISQUALIFIER_THRESHOLD_PCT,
    debt_equity_tier,
    fails_pledging_disqualifier,
    qualifies_for_v200,
    roce_tier,
    screen,
)


def make_fundamentals(**overrides) -> Fundamentals:
    """A baseline 'clearly qualifies' fundamentals object, overridden per test."""
    base = dict(
        symbol="TEST",
        as_of=dt.date(2024, 1, 1),
        company_type=CompanyType.STANDARD,
        market_cap_cr=10000.0,
        revenue_ttm_cr=2000.0,
        net_profit_ttm_cr=300.0,  # > 200cr floor
        roce_pct=25.0,  # > 20% floor
        roe_pct=None,
        debt_to_equity=0.10,  # < 0.25 ceiling
        promoter_holding_pct=50.0,
        promoter_pledging_pct_of_holding=0.0,
        public_pct=20.0,
        hni_pct=5.0,
        fii_pct=15.0,
        dii_pct=15.0,
    )
    base.update(overrides)
    return Fundamentals(**base)


class TestV200Qualification(unittest.TestCase):
    """Section 1.3: net profit > 200cr TTM AND ROCE > 20% AND D/E < 0.25
    (non-BFSI); net profit > 200cr TTM AND ROE > 10% (BFSI/functionally-lending)."""

    def test_standard_company_qualifies_when_all_three_conditions_met(self):
        f = make_fundamentals()
        qualifies, reasons = qualifies_for_v200(f)
        self.assertTrue(qualifies, reasons)

    def test_standard_company_fails_on_net_profit_floor(self):
        f = make_fundamentals(net_profit_ttm_cr=199.9)
        qualifies, reasons = qualifies_for_v200(f)
        self.assertFalse(qualifies)
        self.assertTrue(any("net profit" in r for r in reasons))

    def test_standard_company_fails_on_roce_floor(self):
        f = make_fundamentals(roce_pct=20.0)  # must be STRICTLY > 20, not >=
        qualifies, reasons = qualifies_for_v200(f)
        self.assertFalse(qualifies)

    def test_standard_company_fails_on_debt_equity_ceiling(self):
        f = make_fundamentals(debt_to_equity=0.25)  # must be STRICTLY < 0.25
        qualifies, reasons = qualifies_for_v200(f)
        self.assertFalse(qualifies)

    def test_bank_uses_roe_not_roce_and_ignores_debt_equity(self):
        # Section 1.3 exception: banks/NBFCs skip ROCE+D/E entirely, use ROE>10% instead.
        f = make_fundamentals(
            company_type=CompanyType.BANK,
            roce_pct=None,
            debt_to_equity=5.0,  # would fail standard test, but BFSI is exempt
            roe_pct=12.0,
        )
        qualifies, reasons = qualifies_for_v200(f)
        self.assertTrue(qualifies, reasons)

    def test_bank_fails_v200_if_roe_at_or_below_10(self):
        f = make_fundamentals(company_type=CompanyType.BANK, roe_pct=10.0, roce_pct=None)
        qualifies, reasons = qualifies_for_v200(f)
        self.assertFalse(qualifies)

    def test_functionally_lending_broker_uses_bfsi_rule(self):
        # Section 4.8: Angel-One-style margin-lending brokers, even without
        # formal NBFC registration, get the BFSI exemption.
        f = make_fundamentals(
            company_type=CompanyType.FUNCTIONALLY_LENDING,
            roce_pct=None,
            debt_to_equity=1.61,  # Angel One's real cited figure in the source video
            roe_pct=46.0,  # Angel One's real cited figure
            net_profit_ttm_cr=685.0,  # Angel One's real cited figure
        )
        qualifies, reasons = qualifies_for_v200(f)
        self.assertTrue(qualifies, reasons)


class TestPledgingDisqualifier(unittest.TestCase):
    """Section 4.10: promoter_holding% * pledging%-of-that-holding >= 10% => reject.
    NOTE: this is promoter_holding times pledging-of-that-holding, NOT just
    the raw pledging percentage - a very easy formula to get wrong."""

    def test_below_threshold_does_not_disqualify(self):
        # 30% holding, 20% of that pledged => 6% of total company. Below 10%.
        f = make_fundamentals(promoter_holding_pct=30.0, promoter_pledging_pct_of_holding=20.0)
        fails, reason = fails_pledging_disqualifier(f)
        self.assertFalse(fails, reason)

    def test_at_or_above_threshold_disqualifies(self):
        # 40% holding, 25% of that pledged => 10% of total company. At threshold => reject.
        f = make_fundamentals(promoter_holding_pct=40.0, promoter_pledging_pct_of_holding=25.0)
        fails, reason = fails_pledging_disqualifier(f)
        self.assertTrue(fails)
        self.assertIsNotNone(reason)

    def test_formula_is_not_pledging_percent_alone(self):
        # A naive ("just check pledging % > 10") implementation would wrongly
        # reject this: pledging is 50% of holding, but holding itself is only
        # 5%, so total-company pledged = 2.5%, well under the 10% threshold.
        f = make_fundamentals(promoter_holding_pct=5.0, promoter_pledging_pct_of_holding=50.0)
        fails, reason = fails_pledging_disqualifier(f)
        self.assertFalse(fails, reason)

    def test_pledging_overrides_an_otherwise_perfect_v200_candidate(self):
        # Confirms the gate's screen() entry point actually rejects on pledging
        # even when every other quantitative threshold is comfortably passed.
        f = make_fundamentals(promoter_holding_pct=50.0, promoter_pledging_pct_of_holding=25.0)  # 12.5% of co.
        report = screen(f, Universe.V200)
        self.assertEqual(report.gate_result.value, "FAIL")
        self.assertTrue(any("pledging" in r.lower() for r in report.fail_reasons))


class TestTiering(unittest.TestCase):
    """Section 4.6 / 4.8: tiering is for RANKING among already-qualifying
    candidates, never for disqualifying."""

    def test_roce_best_tier(self):
        f = make_fundamentals(roce_pct=31.0)
        self.assertEqual(roce_tier(f), "best")

    def test_roce_very_good_tier(self):
        f = make_fundamentals(roce_pct=25.0)
        self.assertEqual(roce_tier(f), "very_good")

    def test_roce_fails_gate_tier(self):
        f = make_fundamentals(roce_pct=15.0)
        self.assertEqual(roce_tier(f), "fails_gate")

    def test_debt_equity_best_tier(self):
        f = make_fundamentals(debt_to_equity=0.05)
        self.assertEqual(debt_equity_tier(f), "best")

    def test_debt_equity_very_good_tier(self):
        f = make_fundamentals(debt_to_equity=0.20)
        self.assertEqual(debt_equity_tier(f), "very_good")

    def test_bfsi_company_tiering_is_not_applicable(self):
        f = make_fundamentals(company_type=CompanyType.BANK)
        self.assertIn("n/a", roce_tier(f))
        self.assertIn("n/a", debt_equity_tier(f))


class TestSoftFlags(unittest.TestCase):
    """Section 4.9: weak-hands > 30% is a soft caution, never a hard reject."""

    def test_weak_hands_above_30_pct_flagged_but_not_rejected(self):
        f = make_fundamentals(public_pct=40.0, hni_pct=2.0)  # weak_hands = 38%
        report = screen(f, Universe.V200)
        self.assertEqual(report.gate_result.value, "PASS")
        self.assertTrue(any("weak-hands" in flag.lower() for flag in report.soft_flags))


if __name__ == "__main__":
    unittest.main()
