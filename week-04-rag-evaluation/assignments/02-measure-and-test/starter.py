"""Week 4, Assignment 2 starter: Braintrust scorers + paired bootstrap test.

Requires: braintrust installed (`pip install braintrust`), BRAINTRUST_API_KEY
in .env (free tier at braintrust.dev), golden_set.jsonl (Assignment 1).
"""

import json
import random

# ---------------------------------------------------------------------------
# 1. Braintrust scorers — TODO: implement the four scorer functions.
#
# Braintrust scorers are plain functions returning 0..1, with the signature
# (output, expected, metadata) — the same convention as Week 2's judges.
# Write four, mirroring the retrieval/generation split:
#   retrieval:  context_precision, context_recall
#   generation: faithfulness, answer_relevancy
#
# Where each input comes from (this split is the week's whole point):
#   output    — what your task returned at eval time: a dict with "answer"
#               and "retrieved_contexts" (the chunks retrieval ACTUALLY
#               returned for this case — never the gold contexts).
#   expected  — the case's ground_truth text (criteria for a correct answer).
#   metadata  — fields you attach per data row: "question" and
#               "ground_truth_contexts" (the GOLD contexts from Assignment
#               1 — the denominator context_recall is measured against).
# ---------------------------------------------------------------------------
def faithfulness(output, expected, metadata, **kwargs) -> float:
    """Is every claim in the answer supported by the retrieved context?

    output["retrieved_contexts"] holds the snippets retrieved for this case.
    TODO: LLM call — split output["answer"] into claims, check each against
    the retrieved contexts, return supported_claims / total_claims.
    """
    raise NotImplementedError("implement the faithfulness scorer here")


def answer_relevancy(output, expected, metadata, **kwargs) -> float:
    """Does the answer actually address the question asked?"""
    # TODO: LLM call or rubric check of output["answer"] against the
    # question in metadata["question"].
    raise NotImplementedError("implement the answer_relevancy scorer here")


def context_precision(output, expected, metadata, **kwargs) -> float:
    """Of the retrieved chunks, how many were relevant? (signal vs. noise)"""
    # TODO: for each snippet in output["retrieved_contexts"], judge
    # relevant/not; return relevant / total.
    raise NotImplementedError("implement the context_precision scorer here")


def context_recall(output, expected, metadata, **kwargs) -> float:
    """Of the relevant chunks that exist, how many were retrieved? (coverage)"""
    # TODO: compare output["retrieved_contexts"] (what retrieval returned)
    # against metadata["ground_truth_contexts"] (the gold set);
    # return retrieved_relevant / total_relevant.
    raise NotImplementedError("implement the context_recall scorer here")


SCORERS = [faithfulness, answer_relevancy, context_precision, context_recall]


def run_braintrust(cases: list) -> dict:
    """Score cases in Braintrust. Return {scorer_name: mean_score}."""
    # TODO:
    #   from braintrust import Eval
    #
    #   def rag_pipeline(input: str) -> dict:
    #       # TODO: your retrieval + generation pipeline over the Pronto docs.
    #       # It must return BOTH the answer and the contexts retrieval
    #       # actually returned for this input:
    #       #   return {"answer": <generated answer>,
    #       #           "retrieved_contexts": [<chunks retrieval returned>]}
    #       ...
    #
    #   Eval(
    #       "pronto-rag",
    #       data=lambda: (
    #           {
    #               "input": c["question"],
    #               "expected": c["ground_truth"],
    #               "metadata": {
    #                   "question": c["question"],
    #                   # GOLD contexts from Assignment 1. These are the
    #                   # denominator for context_recall — and nothing else.
    #                   # Do NOT also feed them to the task or the scorers
    #                   # as "retrieved": recall would then compare gold
    #                   # against itself and score a meaningless 1.0.
    #                   "ground_truth_contexts": c["contexts"],
    #               },
    #           }
    #           for c in cases
    #       ),
    #       task=rag_pipeline,
    #       scores=SCORERS,
    #   )
    #   Read the per-scorer means from the Braintrust UI (or the Eval summary),
    #   split retrieval vs generation, and report them separately.
    raise NotImplementedError("wire up the Braintrust Eval() call here")


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
    #   1. scores = run_braintrust(cases) -> report the four scorers,
    #      retrieval vs generation.
    #   2. Find ONE groundedness failure; write it up in groundedness_failure.md
    #      (was it retrieval or generation at fault?).
    #   3. Change one retrieval param, re-run, collect per-case faithfulness for
    #      both variants, then:
    #        delta, lo, hi = paired_bootstrap(a_scores, b_scores)
    #        print(f"delta={delta:.3f} 95% CI=[{lo:.3f}, {hi:.3f}]")
    #   4. Write report.md so `python starter.py --config config.yaml` reproduces it.
    print("TODO: wire Braintrust scorers, find the groundedness failure, run the bootstrap test.")
