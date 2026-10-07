"""Week 2, Assignment 1 starter: three binary LLM judges + agreement math.

Fill in the three rubric prompts, wire the LangSmith evaluators, then run
against your 40 hand labels. Requires: LANGSMITH_API_KEY + a model API key
in .env (both set up in Week 1).
"""

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
# 2. LangSmith evaluators — one per rubric. Each returns {"key", "score"}.
# ---------------------------------------------------------------------------
def run_judge(rubric_name: str, agent_output: str) -> str:
    """Call the judge LLM with the rubric prompt. Returns 'PASS' or 'FAIL'."""
    # TODO: pick your provider client (openai is already a course dep).
    #   from openai import OpenAI
    #   client = OpenAI()  # reads OPENAI_API_KEY from .env
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


def make_evaluator(rubric_name: str):
    """Build a LangSmith evaluator for one rubric.

    LangSmith evaluators take (run, example) and return a dict with
    "key" (the metric name) and "score" (0 or 1 for our binary judges).
    """
    def evaluator(run, example) -> dict:
        output = run.outputs.get("output", "") if run.outputs else ""
        verdict = run_judge(rubric_name, output)
        return {"key": rubric_name, "score": 1 if verdict == "PASS" else 0}

    evaluator.__name__ = f"{rubric_name}_evaluator"
    return evaluator


EVALUATORS = [make_evaluator(name) for name in RUBRICS]


def run_langsmith_eval(dataset_name: str = "pronto-judge-labels-40"):
    """Run all three judges over a LangSmith dataset via evaluate()."""
    # TODO:
    #   from langsmith import Client
    #   from langsmith.evaluation import evaluate
    #
    #   client = Client()  # reads LANGSMITH_API_KEY from .env
    #   # Upload your 40 hand-labeled outputs as a dataset first (Week 1 Path A
    #   # traces, or rows you build by hand):
    #   #   dataset = client.create_dataset(dataset_name)
    #   #   for row in labels:  # {"input": ..., "output": ..., "human": "PASS"/"FAIL"}
    #   #       client.create_example(
    #   #           inputs={"input": row["input"]},
    #   #           outputs={"output": row["output"], "human": row["human"]},
    #   #           dataset_id=dataset.id)
    #
    #   def target(inputs):  # the "system" under eval: identity over the outputs
    #       return {"output": inputs["output"]}
    #
    #   results = evaluate(
    #       target,
    #       data=dataset_name,
    #       evaluators=EVALUATORS,
    #       experiment_prefix="pronto-judges-v1",
    #   )
    #   # In the LangSmith UI, open the experiment and compare each evaluator's
    #   # score against example.outputs["human"] — that's your agreement data
    #   # for the math in section 3.
    raise NotImplementedError("wire up the LangSmith evaluate() call here")


# ---------------------------------------------------------------------------
# 3. Agreement math — judge vs human labels.
# ---------------------------------------------------------------------------
def cohens_kappa(judge_labels: list, human_labels: list) -> float:
    """Cohen's kappa for two binary label lists (values 'PASS'/'FAIL')."""
    assert len(judge_labels) == len(human_labels) and len(judge_labels) > 0
    n = len(judge_labels)
    agree = sum(j == h for j, h in zip(judge_labels, human_labels))
    p_o = agree / n
    for label in ("PASS", "FAIL"):
        p_j = sum(j == label for j in judge_labels) / n
        p_h = sum(h == label for h in human_labels) / n
        if label == "PASS":
            p_e = p_j * p_h
        else:
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
    #   {"input": "...", "output": "...", "rubric": "policy_adherence", "human": "PASS"}
    # Run each judge via run_judge(), collect judge_labels, then:
    #   print(agreement_matrix(judge_labels, human_labels))
    #   print("kappa:", cohens_kappa(judge_labels, human_labels))
    # Then scale up: upload the 40 as a LangSmith dataset and run
    # run_langsmith_eval() to see all three judges scored in the UI.
    print("TODO: load labels, run judges, report agreement + kappa per rubric.")
