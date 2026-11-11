"""Unit tests for improve_demo.py pure helpers. Stdlib unittest only.

No keys, no network, no model calls: every test runs on canned rows and
canned env dicts. Run from this folder or from the repo root:

    python3 test_improve_demo.py
    python3 week-06-production-eval-infrastructure/examples/full-loop/test_improve_demo.py
"""

import unittest

from improve_demo import delta_table, gate_reading, model_route, scores_from_rows


def _row(case_id, category, judge, code=(1.0, 1.0, 1.0), corrections=0,
          corrected=False):
    return {
        "id": case_id, "category": category, "thread": case_id,
        "judge": judge,
        "no_refund_over_50": code[0],
        "escalation_correctness": code[1],
        "no_other_customer_data": code[2],
        "corrections": corrections,
        "corrected": corrected,
    }


class TestModelRoute(unittest.TestCase):
    def test_gateway_wins_when_its_key_is_set(self):
        url, key = model_route({"NEATLOGS_LLM_KEY": "sk-test",
                                "BRAINTRUST_API_KEY": "sk-test"})
        self.assertEqual(url, "https://llm.neatlogs.ai/v1")
        self.assertEqual(key, "NEATLOGS_LLM_KEY")

    def test_proxy_fallback_when_gateway_key_absent(self):
        url, key = model_route({"BRAINTRUST_API_KEY": "sk-test"})
        self.assertEqual(url, "https://api.braintrust.dev/v1/proxy")
        self.assertEqual(key, "BRAINTRUST_API_KEY")

    def test_empty_env_falls_back_to_proxy(self):
        url, key = model_route({})
        self.assertEqual(url, "https://api.braintrust.dev/v1/proxy")
        self.assertEqual(key, "BRAINTRUST_API_KEY")


class TestDeltaTable(unittest.TestCase):
    def test_improves_regresses_unchanged(self):
        before = [
            _row("a", "refund_request", 0.0),
            _row("b", "refund_request", 1.0),
            _row("c", "adversarial", 1.0),
        ]
        after = [
            _row("a", "refund_request", 1.0, corrections=1, corrected=True),
            _row("b", "refund_request", 0.0, corrections=1),
            _row("c", "adversarial", 1.0),
        ]
        delta = delta_table(before, after)
        by_id = {r["id"]: r for r in delta["rows"]}
        self.assertEqual(by_id["a"]["label"], "improved")
        self.assertEqual(by_id["a"]["judge_delta"], 1.0)
        self.assertEqual(by_id["a"]["corrections"], 1)
        self.assertTrue(by_id["a"]["corrected"])
        self.assertEqual(delta["summary"]["corrected_after"], 1)
        self.assertEqual(by_id["b"]["label"], "regressed")
        self.assertEqual(by_id["b"]["judge_delta"], -1.0)
        self.assertEqual(by_id["c"]["label"], "unchanged")
        self.assertEqual(by_id["c"]["judge_delta"], 0.0)
        self.assertEqual(delta["summary"]["improved"], 1)
        self.assertEqual(delta["summary"]["regressed"], 1)
        self.assertEqual(delta["summary"]["unchanged"], 1)
        self.assertEqual(delta["summary"]["n"], 3)

    def test_code_only_improvement_counts(self):
        # Judge holds, but the code mean rises: still an improvement.
        before = [_row("a", "refund_request", 1.0, code=(1.0, 0.0, 1.0))]
        after = [_row("a", "refund_request", 1.0, code=(1.0, 1.0, 1.0),
                      corrections=1)]
        delta = delta_table(before, after)
        self.assertEqual(delta["rows"][0]["label"], "improved")
        self.assertAlmostEqual(delta["rows"][0]["code_delta"], 1.0 / 3.0)

    def test_code_only_regression_counts(self):
        before = [_row("a", "refund_request", 0.0, code=(1.0, 1.0, 1.0))]
        after = [_row("a", "refund_request", 0.0, code=(0.0, 1.0, 1.0))]
        delta = delta_table(before, after)
        self.assertEqual(delta["rows"][0]["label"], "regressed")

    def test_summary_rates(self):
        before = [_row("a", "refund_request", 0.0),
                  _row("b", "refund_request", 1.0)]
        after = [_row("a", "refund_request", 1.0),
                 _row("b", "refund_request", 1.0)]
        delta = delta_table(before, after)
        self.assertAlmostEqual(delta["summary"]["judge_before"], 0.5)
        self.assertAlmostEqual(delta["summary"]["judge_after"], 1.0)

    def test_id_mismatch_raises(self):
        before = [_row("a", "refund_request", 1.0)]
        after = [_row("b", "refund_request", 1.0)]
        with self.assertRaises(ValueError):
            delta_table(before, after)


class TestScoresFromRows(unittest.TestCase):
    def test_refund_uses_refund_subset_only(self):
        rows = [
            _row("a", "refund_request", 1.0, code=(0.0, 1.0, 1.0)),
            _row("b", "refund_request", 1.0, code=(1.0, 1.0, 1.0)),
            _row("c", "adversarial", 0.0, code=(1.0, 0.0, 0.0)),
        ]
        scores = scores_from_rows(rows)
        self.assertAlmostEqual(scores["refund_correctness"], 0.5)
        self.assertAlmostEqual(scores["escalation_correctness"], 2.0 / 3.0)
        self.assertAlmostEqual(scores["leak_rate"], 1.0 / 3.0)
        self.assertAlmostEqual(scores["judge_pass_rate"], 2.0 / 3.0)

    def test_no_refund_cases_reads_clean(self):
        rows = [_row("c", "adversarial", 1.0, code=(1.0, 1.0, 1.0))]
        self.assertEqual(scores_from_rows(rows)["refund_correctness"], 1.0)


class TestGateReading(unittest.TestCase):
    def test_above_bar_ships(self):
        reading = gate_reading({
            "refund_correctness": 0.96, "escalation_correctness": 0.95,
            "leak_rate": 0.0})
        self.assertTrue(reading.startswith("SHIP -"), reading)

    def test_exactly_at_bar_ships(self):
        reading = gate_reading({
            "refund_correctness": 0.95, "escalation_correctness": 0.90,
            "leak_rate": 0.0})
        self.assertTrue(reading.startswith("SHIP -"), reading)

    def test_escalation_below_bar_ships_with_conditions(self):
        reading = gate_reading({
            "refund_correctness": 0.96, "escalation_correctness": 0.84,
            "leak_rate": 0.0})
        self.assertTrue(reading.startswith("SHIP WITH CONDITIONS -"), reading)

    def test_refund_below_bar_ships_with_conditions(self):
        reading = gate_reading({
            "refund_correctness": 0.90, "escalation_correctness": 0.95,
            "leak_rate": 0.0})
        self.assertTrue(reading.startswith("SHIP WITH CONDITIONS -"), reading)

    def test_any_leak_is_no_ship(self):
        reading = gate_reading({
            "refund_correctness": 1.0, "escalation_correctness": 1.0,
            "leak_rate": 0.125})
        self.assertTrue(reading.startswith("NO-SHIP -"), reading)

    def test_leak_beats_good_scores(self):
        # Even with refund and escalation above bar, a leak blocks the ship.
        reading = gate_reading({
            "refund_correctness": 1.0, "escalation_correctness": 1.0,
            "leak_rate": 0.05})
        self.assertTrue(reading.startswith("NO-SHIP -"), reading)


if __name__ == "__main__":
    unittest.main()
