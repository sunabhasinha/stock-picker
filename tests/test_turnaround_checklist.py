"""
Tests for the Strategy 7 checklist machinery (Section 5.1) and the
Claude-backed research provider.

Price fixture: lifetime high 300, post-peak crash to 60 (an 80% decline,
comfortably past Condition 1's 67%), current price 120 (60% below the
high, comfortably past Condition 7's 50%).
"""

import datetime as dt
import unittest

from sunabha_agent.data.models import Candle, CompanyType, Fundamentals, PriceSeries
from sunabha_agent.research.claude_research import ClaudeResearchProvider
from sunabha_agent.research.turnaround_checklist import (
    ChecklistStatus,
    ResearchAnswer,
    build_checklist,
)

CRASH_AND_PARTIAL_RECOVERY = [200, 250, 300, 250, 180, 120, 80, 60, 70, 90, 110, 120]


def make_candles(closes, start=dt.date(2020, 1, 1)):
    candles, prev = [], closes[0]
    for i, c in enumerate(closes):
        candles.append(
            Candle(date=start + dt.timedelta(days=i), open=prev,
                   high=max(prev, c), low=min(prev, c), close=c)
        )
        prev = c
    return candles


def make_prices(closes=None):
    return PriceSeries(symbol="TESTCO",
                       candles=make_candles(closes or CRASH_AND_PARTIAL_RECOVERY))


def make_fundamentals(**overrides):
    defaults = dict(
        symbol="TESTCO",
        as_of=dt.date(2024, 6, 30),
        company_type=CompanyType.STANDARD,
        market_cap_cr=5000.0,
        revenue_ttm_cr=650.0,
        net_profit_ttm_cr=45.0,
        # Category A shape: revenue grew into a peak then drew down 40%,
        # profit drew down 70% - a genuine business impact.
        revenue_ttm_history_cr=[500, 600, 700, 1000, 700, 600, 650],
        net_profit_ttm_history_cr=[50, 60, 70, 100, 40, 30, 45],
        # Latest quarter 20 vs 13 a year ago (index -5) - a new record.
        quarterly_net_profit_cr=[10, 12, 8, 9, 11, 13, 9, 10, 20],
        listed_on_nse=True,
    )
    defaults.update(overrides)
    return Fundamentals(**defaults)


def item(checklist, n):
    return next(i for i in checklist.items if i.condition_number == n)


class PassingResearcher:
    def research(self, question, context):
        return ResearchAnswer(ChecklistStatus.PASS, "verified (test double)")


class TestQuantitativeConditions(unittest.TestCase):
    def test_condition1_uses_post_peak_trough_not_current_price(self):
        # Current price is only 60% below the high, but the POST-PEAK trough
        # (60) is 80% below - Condition 1 measures the historical fall.
        checklist = build_checklist(make_prices(), make_fundamentals())
        self.assertEqual(item(checklist, 1).status, ChecklistStatus.PASS)

    def test_condition1_fails_on_shallow_decline(self):
        # Trough 150 = only a 50% fall from the 300 high - under 67%.
        shallow = [200, 250, 300, 250, 200, 150, 160, 170, 150, 160, 150, 145]
        checklist = build_checklist(make_prices(shallow), make_fundamentals())
        self.assertEqual(item(checklist, 1).status, ChecklistStatus.FAIL)
        self.assertTrue(checklist.has_hard_failures)

    def test_condition7_fails_when_market_already_rerated(self):
        # Historical crash to 60 (Condition 1 passes) but price recovered to
        # 190 - only ~37% below the high, so the entry window has closed.
        rerated = [200, 250, 300, 250, 180, 120, 80, 60, 120, 160, 180, 190]
        checklist = build_checklist(make_prices(rerated), make_fundamentals())
        self.assertEqual(item(checklist, 1).status, ChecklistStatus.PASS)
        self.assertEqual(item(checklist, 7).status, ChecklistStatus.FAIL)

    def test_condition6_compares_yoy_never_sequential_qoq(self):
        # Section 4.12: latest quarter 20 is DOWN vs the prior quarter (30)
        # but UP vs the same quarter last year (12) - must PASS.
        f = make_fundamentals(quarterly_net_profit_cr=[10, 11, 15, 12, 13, 14, 30, 20])
        checklist = build_checklist(make_prices(), f)
        self.assertEqual(item(checklist, 6).status, ChecklistStatus.PASS)

    def test_condition6_fails_when_latest_quarter_down_yoy(self):
        f = make_fundamentals(quarterly_net_profit_cr=[10, 12, 8, 9, 15, 13, 9, 10, 11])
        # latest 11 vs yoy (index -5) 15 -> declined YoY
        checklist = build_checklist(make_prices(), f)
        self.assertEqual(item(checklist, 6).status, ChecklistStatus.FAIL)


class TestDeclineClassification(unittest.TestCase):
    def test_category_a_when_revenue_fell(self):
        checklist = build_checklist(make_prices(), make_fundamentals())
        self.assertEqual(checklist.decline_category, "A")

    def test_category_b_when_revenue_intact_but_profit_fell(self):
        f = make_fundamentals(
            revenue_ttm_history_cr=[900, 950, 1000, 980, 990, 1000],
            net_profit_ttm_history_cr=[100, 110, 120, 60, 40, 55],
        )
        self.assertEqual(build_checklist(make_prices(), f).decline_category, "B")

    def test_category_c_when_both_intact(self):
        f = make_fundamentals(
            revenue_ttm_history_cr=[900, 950, 1000, 990, 995, 1000],
            net_profit_ttm_history_cr=[100, 105, 110, 108, 112, 115],
        )
        self.assertEqual(build_checklist(make_prices(), f).decline_category, "C")


class TestResearchDelegation(unittest.TestCase):
    def test_without_provider_research_items_carry_their_questions(self):
        checklist = build_checklist(make_prices(), make_fundamentals())
        self.assertEqual(item(checklist, 3).status, ChecklistStatus.NEEDS_RESEARCH)
        self.assertEqual(item(checklist, 5).status, ChecklistStatus.NEEDS_RESEARCH)
        self.assertGreaterEqual(len(checklist.open_research_questions), 2)
        self.assertFalse(checklist.is_fully_confirmed)

    def test_with_passing_provider_checklist_fully_confirms(self):
        checklist = build_checklist(make_prices(), make_fundamentals(),
                                    researcher=PassingResearcher())
        self.assertTrue(checklist.is_fully_confirmed)
        self.assertEqual(checklist.open_research_questions, [])

    def test_info_items_present_but_never_gate(self):
        # Conditions 8/9/10 (exit rules, mindset) are recorded for review
        # completeness but must not affect confirmation.
        checklist = build_checklist(make_prices(), make_fundamentals(),
                                    researcher=PassingResearcher())
        for n in (8, 9, 10):
            self.assertEqual(item(checklist, n).status, ChecklistStatus.INFO)
        self.assertTrue(checklist.is_fully_confirmed)


class TestClaudeResearchProvider(unittest.TestCase):
    @staticmethod
    def reply(text):
        return {"content": [{"text": text}]}

    def test_pass_verdict_parsed(self):
        provider = ClaudeResearchProvider(
            transport=lambda payload: self.reply(
                '{"verdict": "PASS", "reasoning": "The SEBI mandate expired."}'
            )
        )
        answer = provider.research("q", {})
        self.assertEqual(answer.status, ChecklistStatus.PASS)
        self.assertIn("SEBI", answer.detail)

    def test_unclear_maps_to_needs_research_and_tolerates_prose(self):
        provider = ClaudeResearchProvider(
            transport=lambda payload: self.reply(
                'Here is my answer:\n```json\n{"verdict": "UNCLEAR", '
                '"reasoning": "No current data."}\n```'
            )
        )
        self.assertEqual(provider.research("q", {}).status,
                         ChecklistStatus.NEEDS_RESEARCH)

    def test_transport_error_degrades_to_needs_research_not_crash(self):
        def broken(payload):
            raise OSError("network down")

        answer = ClaudeResearchProvider(transport=broken).research("q", {})
        self.assertEqual(answer.status, ChecklistStatus.NEEDS_RESEARCH)
        self.assertIn("manually", answer.detail)

    def test_missing_api_key_degrades_to_needs_research(self):
        import os
        from unittest import mock

        with mock.patch.dict(os.environ, {}, clear=True):
            provider = ClaudeResearchProvider(api_key="")
        answer = provider.research("q", {})
        self.assertEqual(answer.status, ChecklistStatus.NEEDS_RESEARCH)
        self.assertIn("ANTHROPIC_API_KEY", answer.detail)


if __name__ == "__main__":
    unittest.main()
