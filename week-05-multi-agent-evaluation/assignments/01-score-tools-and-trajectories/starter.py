"""Week 5, Assignment 1 starter: expected-action records + trajectory evaluator.

The system under test is the Pronto crew (pronto_crew.py): triage -> policy ->
refund agents on CrewAI. Capture its tool trajectories, then score them
against expected-action records with property-based checks.
"""

import json
import os
import sys

# pronto_crew.py lives one folder up (shared by both Week 5 assignments).
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from pronto_crew import run_crew, TRAJECTORY_LOG

# ---------------------------------------------------------------------------
# Expected-action record schema.
# extra_call_policy: "allow" (harmless extras ok) | "deny" (any extra call fails)
# ---------------------------------------------------------------------------
EXPECTED_ACTIONS = [
    {
        "input": "Where is my order PRN-10421?",
        "required_tools": ["get_order_status"],
        "order_matters": True,
        "extra_call_policy": "allow",   # an extra lookup_policy is harmless here
        "forbidden_tools": ["escalate_to_human"],
        # TODO: add 14+ more records covering your agent's surface.
    },
]


def capture_trajectory(user_message: str) -> list:
    """Run the Pronto crew and return the tool-call trajectory.

    Returns e.g. [{"tool": "get_order_status", "args": {"order_id": "PRN-10421"}}].
    pronto_crew logs every tool call into TRAJECTORY_LOG — just run the crew
    and read it. (Week 1 LangSmith tracing records these runs too.)
    """
    run_crew(user_message, clear_log=True)
    return list(TRAJECTORY_LOG)


def check_properties(trajectory: list, record: dict) -> dict:
    """Property-based checks. Returns {check_name: pass_bool}."""
    tools = [t["tool"] for t in trajectory]
    required = record["required_tools"]
    results = {}

    # P1: all required tools called, in order
    idx = 0
    for tool in tools:
        if idx < len(required) and tool == required[idx]:
            idx += 1
    results["required_in_order"] = idx == len(required)

    # P2: no forbidden tools
    results["no_forbidden"] = not any(t in record.get("forbidden_tools", []) for t in tools)

    # P3: extra-call policy
    if record.get("extra_call_policy") == "deny":
        results["no_extra_calls"] = tools == required
    else:
        results["no_extra_calls"] = True  # policy allows extras

    # TODO: add your own — e.g. "no duplicate identical calls",
    # "escalate only as final step", "args match expected schema".
    return results


def score_arguments(trajectory: list) -> dict:
    """TODO: validate tool args as structured output (types, formats, required fields)."""
    # TODO: e.g. order_id must match r"ORD-\d+"; escalate requires non-empty reason.
    raise NotImplementedError("validate tool arguments here")


if __name__ == "__main__":
    print(f"{len(EXPECTED_ACTIONS)} expected-action records (need 15+).")
    # TODO:
    #   1. Add 14+ records covering the crew's surface (triage routing,
    #      policy lookup, refunds, escalations).
    #   2. Implement score_arguments (capture_trajectory is wired already).
    #   3. Run all records; report per-dimension scores.
    #   4. Find ONE fragile pass — passed overall, wrong trajectory — and write
    #      it up in fragile_pass.md.
    print("TODO: add records, implement scoring, run the suite, find the fragile pass.")
