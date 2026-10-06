"""Week 4, Assignment 1 starter: golden-set schema + LangSmith versioning.

Fill in case generation, validate labels by hand, then upload and pin v1.
"""

import json

# ---------------------------------------------------------------------------
# Golden-set schema — one JSON object per line in golden_set.jsonl.
# ---------------------------------------------------------------------------
CASE_SCHEMA = {
    "question": str,        # the user question
    "contexts": list,       # list of {"title": ..., "text": ...} that SHOULD be retrieved
    "ground_truth": str,    # criteria-based: what a correct answer must contain
    "source": str,          # "hand-written" | "synthetic" | "production-log"
    "difficulty": str,      # "easy" | "medium" | "hard"
}

TARGET_CASES = 150


def generate_cases(n: int = TARGET_CASES) -> list:
    """TODO: generate cases — hand-write, synthesize, or mine production logs.

    If synthesizing: generate, then hand-validate 30+ and record the error rate.
    """
    # TODO: implement. Start from your agent's DEMO_DOCS and Week 1 inputs.
    raise NotImplementedError("generate 150+ cases here")


def validate_sample(cases: list, k: int = 30) -> float:
    """TODO: hand-check k cases; return the label error rate."""
    # TODO: print k cases, record your verdicts, return errors / k.
    raise NotImplementedError("hand-validate a sample here")


def upload_and_pin(cases: list, name: str = "agent-golden-set"):
    """TODO: upload to LangSmith and pin v1. Record the version id in dataset.md."""
    # TODO:
    #   from langsmith import Client
    #   client = Client()
    #   ds = client.create_dataset(name)
    #   client.create_examples(inputs=[...], outputs=[...], dataset_id=ds.id)
    #   ... pin / tag as v1 ...
    raise NotImplementedError("upload + pin v1 here")


if __name__ == "__main__":
    cases = generate_cases()
    assert len(cases) >= TARGET_CASES, f"need {TARGET_CASES}+, got {len(cases)}"
    with open("golden_set.jsonl", "w") as f:
        for c in cases:
            f.write(json.dumps(c) + "\n")
    print(f"Wrote {len(cases)} cases. Next: hand-validate 30+, assess the four")
    print("dataset qualities in dataset.md, then upload_and_pin().")
