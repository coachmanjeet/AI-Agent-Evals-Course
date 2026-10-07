"""Week 1, Assignment 1 starter: run 30 inputs through the traced agent.

Prereqs: agent/agent.py has @traceable wired in (Assignment step 1),
inputs.json exists (Assignment step 3), .env has LANGSMITH_API_KEY.
Writes annotations.csv with empty pass/fail + note columns for you to fill.

Multi-turn inputs are replayed turn by turn in order (agent.run per
message); the CSV row keeps the full conversation as input and the last
turn's reply as output.
"""

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "agent"))
from agent import CustomerServiceAgent  # noqa: E402


def load_inputs(path: str = "inputs.json") -> list:
    with open(path) as f:
        inputs = json.load(f)
    assert len(inputs) == 30, f"expected 30 inputs, got {len(inputs)}"
    return inputs


def main() -> None:
    agent = CustomerServiceAgent(demo=True)  # flip to demo=False once a model is wired
    inputs = load_inputs()

    rows = []
    for i, item in enumerate(inputs):
        # item shape: {"category": "order-refund|policy-warranty|multi-turn", "messages": ["..."]}
        messages = item["messages"] if isinstance(item, dict) else [item]
        category = item.get("category", "?") if isinstance(item, dict) else "?"
        reply = ""
        for m in messages:  # run every turn in order; multi-turn inputs keep their context
            reply = agent.run(m)
        rows.append({
            "id": i,
            "category": category,
            "input": " / ".join(messages)[:160],
            "output": reply[:160],
            "pass_fail": "",   # TODO: fill after reviewing the trace in LangSmith
            "note": "",        # TODO: one line on what happened
        })
        print(f"[{i+1}/30] {rows[-1]['category']}: {reply[:80]}")

    with open("annotations.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "category", "input", "output", "pass_fail", "note"])
        writer.writeheader()
        writer.writerows(rows)
    print("Wrote annotations.csv — now review each trace in LangSmith and fill pass_fail + note.")


if __name__ == "__main__":
    main()
