"""Week 4, Assignment 2 starter: RAGAS metrics + paired bootstrap test.

Requires: ragas installed, golden_set.jsonl (Assignment 1), model API key.
"""

import json
import random

# ---------------------------------------------------------------------------
# 1. RAGAS wiring — TODO: implement run_ragas().
# ---------------------------------------------------------------------------
def run_ragas(cases: list) -> dict:
    """Score cases with the four RAGAS metrics. Return {metric: mean_score}."""
    # TODO:
    #   from ragas import evaluate
    #   from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
    #   Build a Dataset with question / contexts / answer / ground_truth per case,
    #   call evaluate(), and split results into retrieval vs generation metrics:
    #     retrieval:  context_precision, context_recall
    #     generation: faithfulness, answer_relevancy
    raise NotImplementedError("wire up RAGAS here")


# ---------------------------------------------------------------------------
# 2. Paired bootstrap test — same inputs, two variants, delta with 95% CI.
# ---------------------------------------------------------------------------
def paired_bootstrap(a_scores: list, b_scores: list, n_boot: int = 10000, seed: int = 7):
    """Return (mean_delta, lo, hi) — 95% CI for mean(b - a) via bootstrap."""
    assert len(a_scores) == len(b_scores) and len(a_scores) > 0
    rng = random.Random(seed)
    diffs = [b - a for a, b in zip(a_scores, b_scores)]
    n = len(diffs)
    boot_means = [sum(rng.choice(diffs) for _ in range(n)) / n for _ in range(n_boot)]
    boot_means.sort()
    lo = boot_means[int(0.025 * n_boot)]
    hi = boot_means[int(0.975 * n_boot)]
    return sum(diffs) / n, lo, hi


def load_cases(path: str = "../01-build-and-version-dataset/golden_set.jsonl") -> list:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


if __name__ == "__main__":
    cases = load_cases()
    print(f"Loaded {len(cases)} golden cases.")
    # TODO:
    #   1. scores = run_ragas(cases) -> report the four metrics, retrieval vs generation.
    #   2. Find ONE groundedness failure; write it up in groundedness_failure.md
    #      (was it retrieval or generation at fault?).
    #   3. Change one retrieval param, re-run, collect per-case faithfulness for
    #      both variants, then:
    #        delta, lo, hi = paired_bootstrap(a_scores, b_scores)
    #        print(f"delta={delta:.3f} 95% CI=[{lo:.3f}, {hi:.3f}]")
    #   4. Write report.md so `python starter.py --config config.yaml` reproduces it.
    print("TODO: wire RAGAS, find the groundedness failure, run the bootstrap test.")
