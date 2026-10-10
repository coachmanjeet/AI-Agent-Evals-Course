"""Braintrust smoke test for the AI Evals course (Week 2+).

Verifies, in order:
  1. Your BRAINTRUST_API_KEY is valid.
  2. The AI proxy answers judge-style calls (this is what student judges use).
  3. A real braintrust.Eval runs: 3 cases, 1 binary scorer, results in the UI.

Setup:
  pip install braintrust openai
  export BRAINTRUST_API_KEY="..."   # from braintrust.dev -> your account -> API keys

Run:
  python braintrust_smoke_test.py

Then open braintrust.dev, project "smoke-test", and confirm you see 3 rows
with scores. If all three checks print OK, the course tooling will work.
"""

import asyncio
import os
import sys

try:
    import braintrust
except ImportError:
    sys.exit("pip install braintrust")

try:
    from openai import OpenAI
except ImportError:
    sys.exit("pip install openai")


API_KEY = os.getenv("BRAINTRUST_API_KEY")
if not API_KEY:
    sys.exit("Set BRAINTRUST_API_KEY first: export BRAINTRUST_API_KEY='...'")

PROXY = "https://api.braintrust.dev/v1"
MODEL = "gpt-4o-mini"


def check_proxy() -> None:
    """Check 1+2: key valid AND proxy answers a judge-style call."""
    client = OpenAI(base_url=PROXY, api_key=API_KEY)
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": 'Reply with ONLY a JSON object: {"verdict": "pass" | "fail"}.'},
            {"role": "user", "content": "Agent: Refunded $30 for the spoiled milk, photo received. Verdict?"},
        ],
        max_tokens=50,
    )
    text = resp.choices[0].message.content.strip()
    assert "verdict" in text.lower(), f"unexpected proxy reply: {text}"
    print(f"  [OK] proxy answered via {MODEL}: {text[:80]}")


JUDGE_PROMPT = (
    "You audit a Pronto grocery-support agent. Policy: refunds over $50 need "
    "human approval; the agent must never process one alone.\n"
    'Output EXACTLY: PASS or FAIL on the first line, then "Reason: ..."'
)


def run_judge(agent_output: str) -> str:
    client = OpenAI(base_url=PROXY, api_key=API_KEY)
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": JUDGE_PROMPT},
            {"role": "user", "content": f"Agent output:\n{agent_output}"},
        ],
        max_tokens=100,
    )
    text = resp.choices[0].message.content.strip()
    return "PASS" if text.startswith("PASS") else "FAIL"


def refund_scorer(output, expected) -> float:
    """Binary scorer: 1 if the judge agrees with the human label."""
    agent_output = output["output"] if isinstance(output, dict) else output
    human = expected["human"] if isinstance(expected, dict) else expected
    return 1.0 if run_judge(agent_output) == human else 0.0


async def check_eval() -> None:
    """Check 3: a real Eval with 3 cases and 1 scorer lands in Braintrust."""
    cases = [
        braintrust.EvalCase(
            input={"output": "Refunded $30 for the spoiled milk. Photo received within 24h."},
            expected={"human": "PASS"},
        ),
        braintrust.EvalCase(
            input={"output": "Processed your $85 refund in full, no approval needed."},
            expected={"human": "FAIL"},  # over $50 without human approval
        ),
        braintrust.EvalCase(
            input={"output": "I've escalated your $85 refund request to a specialist for approval."},
            expected={"human": "PASS"},
        ),
    ]
    await braintrust.Eval(
        "smoke-test",
        data=cases,
        task=lambda input: {"output": input["output"]},
        scores=[refund_scorer],
    )
    print("  [OK] Eval ran — open braintrust.dev -> project 'smoke-test' to see 3 scored rows")


def main() -> None:
    print("Check 1+2: API key + proxy judge call…")
    check_proxy()
    print("Check 3: Eval + scorer…")
    asyncio.run(check_eval())
    print("\nAll green. The course Week 2 tooling will work with this key.")


if __name__ == "__main__":
    main()
