"""Week 2, Assignment 1 starter: three binary LLM judges + agreement math.

Fill in the three rubric prompts, wire the DeepEval judges, then run against
your 40 hand labels. Requires: deepeval installed, model API key in .env.
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
# 2. DeepEval wiring — TODO: implement one judge per rubric.
# ---------------------------------------------------------------------------
def build_judges():
    """Return {rubric_name: deepeval_judge}. See DeepEval docs for GEval/CustomMetric."""
    # TODO: from deepeval.metrics import GEval
    # TODO: from deepeval.test_case import LLMTestCase
    # Each judge: GEval(name=..., criteria=<RUBRICS[k]>, evaluation_params=[...])
    raise NotImplementedError("wire up your three judges here")


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
    #   {"output": "...", "rubric": "doc_relevance", "human": "PASS"}
    # Run each judge, collect judge_labels, then:
    #   print(agreement_matrix(judge_labels, human_labels))
    #   print("kappa:", cohens_kappa(judge_labels, human_labels))
    print("TODO: load labels, run judges, report agreement + kappa per rubric.")
