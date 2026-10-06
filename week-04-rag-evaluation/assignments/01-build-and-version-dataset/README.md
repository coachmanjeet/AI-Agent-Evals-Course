# Assignment 1 — Build and version the dataset

## Goal

Build a golden set worth trusting, then pin it so every future run is comparable.

## Steps

1. Define your golden-set schema (`starter.py` has a starting point): each case needs `question`, `contexts` (the docs that should be retrieved), `ground_truth` (criteria-based — what a correct answer must contain), and metadata (`source`, `difficulty`).
2. Build **150+ cases** covering your agent's doc-lookup surface. Mix difficulties; include edge cases (ambiguous questions, questions with no good doc, multi-doc questions).
3. Generate a first draft synthetically if you like — then **validate a sample by hand**. Synthetic labels are guilty until proven innocent: check at least 30 cases yourself and record the label-error rate.
4. Score the set against the four dataset qualities: representativeness (does it look like real traffic?), diversity, label correctness, versioning.
5. Upload to LangSmith as a dataset and **pin v1**. Every A/B run from here on uses the pinned version.

## Acceptance criteria

- [ ] `golden_set.jsonl` with 150+ cases in the documented schema
- [ ] Label validation: 30+ cases hand-checked, error rate reported
- [ ] Four dataset qualities assessed in writing (one paragraph each)
- [ ] Dataset pinned as v1 in LangSmith; version id recorded in `dataset.md`

## Starter

`starter.py` — golden-set schema, synthetic generation skeleton, and the LangSmith upload/pin calls.
