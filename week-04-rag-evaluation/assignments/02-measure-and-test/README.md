# Assignment 2 — Measure and test

## Goal

Score your RAG pipeline component-wise with RAGAS, find a real groundedness failure, and prove a retrieval change with a paired bootstrap test.

## Steps

1. Wire the four RAGAS metrics into your harness (`starter.py` skeleton): **faithfulness**, **answer relevance**, **context precision**, **context recall**. Run them over the pinned golden set v1.
2. Report retrieval metrics and generation metrics **separately**. Which component is weaker?
3. Find **one groundedness failure**: an answer that sounds right but isn't supported by the retrieved context. Dissect it — was it a retrieval miss or a generation hallucination?
4. Change ONE retrieval parameter (e.g. top-k, chunk size) and re-run. Compare with a **paired bootstrap test** on the same inputs; report the delta with a 95% confidence interval.
5. Ship the harness: **one config, one command, one reproducible report** (`report.md`). Someone cloning the repo should reproduce your numbers.

## Acceptance criteria

- [ ] All four RAGAS metrics reported on golden set v1, retrieval vs generation separated
- [ ] One groundedness failure documented with root cause (retrieval vs generation)
- [ ] Paired bootstrap test: delta + 95% CI reported for the retrieval change
- [ ] `report.md` reproducible from one command with one config file

## Starter

`starter.py` — RAGAS wiring, bootstrap test, and the one-command report runner.
