# Assignment 1 — Build and validate a judge

## Goal

Build three binary LLM judges for your agent and prove they agree with humans before trusting them.

## Steps

1. Write 3 binary rubrics as judge prompts: **code correctness** (is the generated code right?), **doc relevance** (does the cited doc answer the question?), **tool-call accuracy** (right tool, right arguments?). One criterion each; strict output format (`PASS`/`FAIL` + one-line reason).
2. Implement them as LLM judges in DeepEval (`starter.py` has the skeleton).
3. Label 40 agent outputs by hand (reuse Week 1 traces or generate fresh ones): your ground-truth pass/fail per rubric.
4. Run the judges over the 40-label set. Build the agreement matrix per judge (judge-pass/human-pass, judge-pass/human-fail, …).
5. Compute Cohen's kappa per judge (function provided in the starter). Investigate every disagreement: is the judge wrong, or is your label wrong?

## Acceptance criteria

- [ ] 3 judge prompts, one criterion each, strict `PASS`/`FAIL` + reason output format
- [ ] 40 hand labels, one per output per rubric
- [ ] Agreement matrix per judge (4 cells with counts)
- [ ] Cohen's kappa reported per judge; kappa ≥ 0.6 before the judge is "trusted"
- [ ] Written note on the worst judge: its dominant failure mode (false-pass or false-fail?)

## Starter

`starter.py` — rubric prompt templates, DeepEval judge skeleton, and a
`cohens_kappa()` implementation. Fill in the three prompts and the judge wiring.
