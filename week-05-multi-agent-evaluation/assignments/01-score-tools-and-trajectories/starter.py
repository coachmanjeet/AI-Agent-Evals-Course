"""Week 5, Assignment 1 starter: expected-action records + trajectory evaluator.

Capture tool trajectories (Week 1 tracing already records these), then score
them against expected-action records with property-based checks.
"""

import json

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


def capture_trajectory(agent, user_message: str) -> list:
    """Run the agent and return the tool-call trajectory.

    Returns e.g. [{"tool": "get_order_status", "args": {"order_id": "PRN-10421"}}].
    TODO: implement by wrapping agent tools (or reading the LangSmith trace).
    """
    # TODO: simplest path — monkeypatch agent.get_order_status / lookup_policy /
    # escalate_to_human to append to a list, call agent.run(), return the list.
    raise NotImplementedError("capture the tool trajectory here")


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
    #   1. Add 14+ records.
    #   2. Implement capture_trajectory + score_arguments.
    #   3. Run all records; report per-dimension scores.
    #   4. Find ONE fragile pass — passed overall, wrong trajectory — and write
    #      it up in fragile_pass.md.
    print("TODO: implement capture + scoring, run the suite, find the fragile pass.")
