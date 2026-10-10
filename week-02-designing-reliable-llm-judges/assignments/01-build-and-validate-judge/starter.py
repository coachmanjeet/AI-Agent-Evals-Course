"""Week 2, Assignment 1 starter: three binary LLM judges + agreement math.

Braintrust is the default platform for this course (free credit for the
duration of the course). Prefer LangSmith or another tool? Fine — the rubrics
and the validation method below transfer unchanged.

Fill in the three rubric prompts, wire the Braintrust scorers, then run
against your 40 hand labels. Requires: BRAINTRUST_API_KEY in .env
(free course access at braintrust.dev — no separate model key needed,
the course credit covers judge calls too).
"""

import os

# ---------------------------------------------------------------------------
# 1. Rubric prompts — one criterion each, strict output format.
# ---------------------------------------------------------------------------
RUBRICS = {
    "policy_adherence": """TODO: write the judge prompt.
Task: decide if the agent followed the Pronto policy bible (24h photo for
perishables, 30-day non-perishable returns, >$50 refunds need human approval,
substitution only with checkout opt-in, 1-year warranty on Pronto-branded
appliances only).
Output EXACTLY: PASS or FAIL on the first line, then one line starting with
"Reason: " explaining the verdict in under 20 words.""",
    "escalation_correctness": """TODO: write the judge prompt.
Task: decide if the agent escalated exactly when required (legal threats,
safety/health issues, another customer's data, refunds over $50) and did NOT
escalate routine requests it could handle itself.
Output EXACTLY: PASS or FAIL on the first line, then one line starting with
"Reason: " explaining the verdict in under 20 words.""",
    "tool_call_accuracy": """TODO: write the judge prompt.
Task: decide if the agent called the right tool with the right arguments
(get_order_status / issue_refund / lookup_policy / escalate_to_human).
Output EXACTLY: PASS or FAIL on the first line, then one line starting with
"Reason: " explaining the verdict in under 20 words.""",
}


# ---------------------------------------------------------------------------
# 2. Judge LLM call — via Braintrust's proxy (free course credit).
# ---------------------------------------------------------------------------
def _judge_client():
    """OpenAI-compatible client pointed at Braintrust's AI proxy.

    Your BRAINTRUST_API_KEY doubles as the model credential here, so judge
    calls draw from the free course credit. Prefer your own provider key?
    Point the client at api.openai.com (or Anthropic's API) instead — the
    rest of this file doesn't care.
    """
    # TODO: pip install openai braintrust   (both in requirements.txt)
    #   from openai import OpenAI
    #   return OpenAI(
    #       base_url="https://api.braintrust.dev/v1",
    #       api_key=os.environ["BRAINTRUST_API_KEY"],
    #   )
    raise NotImplementedError("wire up your judge LLM client here")


def run_judge(rubric_name: str, agent_output: str) -> str:
    """Call the judge LLM with the rubric prompt. Returns 'PASS' or 'FAIL'."""
    # TODO:
    #   client = _judge_client()
    #   resp = client.chat.completions.create(
    #       model="gpt-4o-mini",
    #       messages=[
    #           {"role": "system", "content": RUBRICS[rubric_name]},
    #           {"role": "user", "content": f"Agent output:\n{agent_output}"},
    #       ],
    #   )
    #   text = resp.choices[0].message.content.strip()
    #   return "PASS" if text.startswith("PASS") else "FAIL"
    raise NotImplementedError("wire up your judge LLM call here")


# ---------------------------------------------------------------------------
# 3. Braintrust scorers — one per rubric. Each returns 0 or 1.
#
#    A Braintrust scorer takes (output, expected) and returns a number.
#    Here output is the agent's stored response and expected is YOUR hand
#    label, so the score IS the agreement signal: 1 = judge agrees with you.
# ---------------------------------------------------------------------------
def make_scorer(rubric_name: str):
    def scorer(output, expected) -> float:
        agent_output = output["output"] if isinstance(output, dict) else output
        verdict = run_judge(rubric_name, agent_output)
        human = expected["human"] if isinstance(expected, dict) else expected
        return 1.0 if verdict == human else 0.0

    scorer.__name__ = f"{rubric_name}_scorer"
    return scorer


SCORERS = {name: make_scorer(name) for name in RUBRICS}


async def run_braintrust_eval(cases: list, project: str = "pronto-judges-w2"):
    """Score all three judges over your labeled cases in Braintrust.

    cases: list of {"input": <user msg>, "output": <agent response>,
                    "human": {"policy_adherence": "PASS", ...}} — one human
           label per rubric per case (your 40 hand labels).
    Open the run in Braintrust afterwards: per-scorer averages ARE your
    agreement rates; drill into individual rows to read disagreements.
    """
    # TODO:
    #   import braintrust
    #
    #   async def main():
    #       for rubric_name, scorer in SCORERS.items():
    #           data = [
    #               braintrust.EvalCase(
    #                   input={"input": c["input"], "output": c["output"]},
    #                   expected={"human": c["human"][rubric_name]},
    #               )
    #               for c in cases
    #           ]
    #           await braintrust.Eval(
    #               project,
    #               data=data,
    #               task=lambda input: {"output": input["output"]},  # judge stored outputs
    #               scores=[scorer],
    #           )
    #
    #   import asyncio; asyncio.run(main())
    raise NotImplementedError("wire up the braintrust.Eval call here")


# ---------------------------------------------------------------------------
# 4. Agreement math — judge vs human labels (runs locally, no API needed).
# ---------------------------------------------------------------------------
def cohens_kappa(judge_labels: list, human_labels: list) -> float:
    """Cohen's kappa for two binary label lists (values 'PASS'/'FAIL')."""
    assert len(judge_labels) == len(human_labels) and len(judge_labels) > 0
    n = len(judge_labels)
    agree = sum(j == h for j, h in zip(judge_labels, human_labels))
    p_o = agree / n
    p_e = 0.0
    for label in ("PASS", "FAIL"):
        p_j = sum(j == label for j in judge_labels) / n
        p_h = sum(h == label for h in human_labels) / n
        p_e += p_j * p_h
    return (p_o - p_e) / (1 - p_e) if p_e != 1 else 1.0


def agreement_matrix(judge_labels: list, human_labels: list) -> dict:
    """Return the 2x2 counts: JP_HP, JP_HF, JF_HP, JF_HF."""
    cells = {"JP_HP": 0, "JP_HF": 0, "JF_HP": 0, "JF_HF": 0}
    for j, h in zip(judge_labels, human_labels):
        key = f"J{'P' if j == 'PASS' else 'F'}_H{'P' if h == 'PASS' else 'F'}"
        cells[key] += 1
    return cells


if __name__ == "__main__":
    # TODO: load your 40 labels, e.g. labels.jsonl rows:
    #   {"input": "...", "output": "...",
    #    "human": {"policy_adherence": "PASS", "escalation_correctness": "FAIL",
    #              "tool_call_accuracy": "PASS"}}
    # Run each judge via run_judge() per rubric, collect judge_labels, then:
    #   print(agreement_matrix(judge_labels, human_labels))
    #   print("kappa:", cohens_kappa(judge_labels, human_labels))
    # Then scale up: await run_braintrust_eval(cases) to see all three
    # judges scored per-row in the Braintrust UI.
    if not os.getenv("BRAINTRUST_API_KEY"):
        print("Set BRAINTRUST_API_KEY in .env (free course access at braintrust.dev).")
    else:
        print("TODO: load labels, run judges, report agreement + kappa per rubric.")
