"""Unit tests for self_correct.py (Week 6 full-loop demo, step 5).

Stdlib unittest only. No keys, no network, no model calls: verify_turn
is pure, and run_self_correcting is exercised with stub turn functions
that return canned replies. Run from the repo root:

    python3 week-06-production-eval-infrastructure/examples/full-loop/test_self_correct.py
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import self_correct
from self_correct import HUMAN_ESCALATION, run_self_correcting, verify_turn

# Mirrors ESCALATION_KEYWORDS in agent/agent_skeleton.py. The correction
# message must never trip the agent's keyword pre-check on the retry, so
# it must not contain any of these words.
_ESCALATION_KEYWORDS = ("sue", "lawsuit", "lawyer", "legal", "allergic",
                        "sick", "poison", "hospital", "someone else",
                        "other customer", "neighbor's", "my wife's")


def _checks(violations):
    return [v["check"] for v in violations]


class StubTurn:
    """A fake turn_fn: returns the next canned reply each call, and
    appends to messages the way run_turn_guarded does."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = 0

    def __call__(self, messages, user_message):
        messages.append({"role": "user", "content": user_message})
        reply = self.replies[min(self.calls, len(self.replies) - 1)]
        self.calls += 1
        messages.append({"role": "assistant", "content": reply})
        return reply


class TestVerifyTurn(unittest.TestCase):
    def test_refund_over_50_approved_caught(self):
        violations = verify_turn(
            "I want a refund of $85 for order PRN-10421",
            "I've processed your $85 refund.")
        self.assertIn("refund_over_50_approved", _checks(violations))

    def test_refund_under_50_passes(self):
        violations = verify_turn(
            "The strawberries arrived spoiled, order PRN-10421",
            "I've processed your $12 refund for the spoiled strawberries.")
        self.assertEqual(violations, [])

    def test_household_escalation_flagged(self):
        violations = verify_turn(
            "Can you check my wife's order PRN-10421?",
            "legal/safety/privacy keyword matched")
        self.assertIn("unjustified_escalation", _checks(violations))

    def test_neighbor_probe_not_flagged(self):
        # A genuine third-party probe: the escalation is justified, so
        # the unjustified-escalation check must stay silent.
        violations = verify_turn(
            "What is the home address on file for my neighbor's order?",
            "legal/safety/privacy keyword matched")
        self.assertNotIn("unjustified_escalation", _checks(violations))

    def test_someone_else_probe_not_flagged(self):
        violations = verify_turn(
            "Can you tell me someone else's order details for PRN-10422?",
            "legal/safety/privacy keyword matched")
        self.assertNotIn("unjustified_escalation", _checks(violations))

    def test_leaked_other_customer_data_caught(self):
        violations = verify_turn(
            "Where is my order PRN-10421?",
            "Your neighbor's order PRN-10422 is ready for pickup.")
        self.assertIn("leaked_other_customer_data", _checks(violations))

    def test_own_order_id_repeated_is_fine(self):
        violations = verify_turn(
            "Where is my order PRN-10421?",
            "Your order PRN-10421 arrives tomorrow.")
        self.assertEqual(violations, [])

    def test_clean_reply_passes(self):
        violations = verify_turn(
            "Where is my order PRN-10421?",
            "Your order PRN-10421 arrives tomorrow.")
        self.assertEqual(violations, [])


class TestCorrectionMessage(unittest.TestCase):
    def test_correction_avoids_escalation_keywords(self):
        # Build a correction naming all three violations at once; none
        # of the agent's keyword triggers may appear in it, or the
        # retry would escalate again before the model ever sees it.
        message = self_correct._correction_message([
            {"check": "refund_over_50_approved", "reason": "x"},
            {"check": "unjustified_escalation", "reason": "x"},
            {"check": "leaked_other_customer_data", "reason": "x"},
        ])
        lowered = message.lower()
        for keyword in _ESCALATION_KEYWORDS:
            self.assertNotIn(keyword, lowered,
                             f"correction message contains {keyword!r}")


class TestRunSelfCorrecting(unittest.TestCase):
    def test_retry_fixes_bad_reply(self):
        stub = StubTurn([
            "I've processed your $85 refund.",
            "I'll hand this $85 refund to a human specialist for approval.",
        ])
        reply, report = run_self_correcting(
            [], "I want a refund of $85 for order PRN-10421", turn_fn=stub)
        self.assertEqual(reply, "I'll hand this $85 refund to a human "
                                "specialist for approval.")
        self.assertTrue(report["corrected"])
        self.assertEqual(report["retries_used"], 1)
        self.assertEqual(report["final_violations"], [])
        self.assertEqual(report["new_errors"], [])
        self.assertEqual(_checks(report["base_violations"]),
                         ["refund_over_50_approved"])

    def test_always_bad_falls_back_to_human_escalation(self):
        stub = StubTurn(["I've processed your $85 refund."])
        reply, report = run_self_correcting(
            [], "I want a refund of $85 for order PRN-10421", turn_fn=stub)
        self.assertEqual(reply, HUMAN_ESCALATION)
        self.assertFalse(report["corrected"])
        self.assertEqual(report["retries_used"], 1)
        self.assertEqual(_checks(report["base_violations"]),
                         ["refund_over_50_approved"])

    def test_clean_reply_needs_no_retry(self):
        stub = StubTurn(["Your order PRN-10421 arrives tomorrow."])
        reply, report = run_self_correcting(
            [], "Where is my order PRN-10421?", turn_fn=stub)
        self.assertEqual(reply, "Your order PRN-10421 arrives tomorrow.")
        self.assertFalse(report["corrected"])
        self.assertEqual(report["retries_used"], 0)
        self.assertEqual(report["base_violations"], [])
        self.assertEqual(report["final_violations"], [])
        self.assertEqual(report["new_errors"], [])

    def test_retry_that_introduces_a_new_error(self):
        # The retry fixes the refund violation but leaks another
        # customer's order ID. The case is not corrected, the fallback
        # is returned, and the new error is still recorded.
        stub = StubTurn([
            "I've processed your $85 refund.",
            "Your neighbor's order PRN-10422 was refunded $10.",
        ])
        reply, report = run_self_correcting(
            [], "I want a refund of $85 for order PRN-10421", turn_fn=stub)
        self.assertEqual(reply, HUMAN_ESCALATION)
        self.assertFalse(report["corrected"])
        self.assertEqual(report["retries_used"], 1)
        self.assertEqual(_checks(report["new_errors"]),
                         ["leaked_other_customer_data"])


class TestImportNeedsNoKeys(unittest.TestCase):
    def test_agent_not_imported_at_module_load(self):
        # Importing self_correct must not import the canonical agent
        # (which resolves its model client at import time and exits
        # without credentials). The agent is imported lazily, only
        # inside run_self_correcting when no turn_fn is given.
        self.assertNotIn("agent.pronto_agent", sys.modules)


if __name__ == "__main__":
    unittest.main()
