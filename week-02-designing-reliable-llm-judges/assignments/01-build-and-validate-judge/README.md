# Assignment 1 — Build and validate a judge

## Goal

Build three binary LLM judges for your agent and prove they agree with humans before trusting them.

## Steps

1. Write 3 binary rubrics as judge prompts: **policy adherence** (did the agent follow the Pronto policy bible?), **escalation correctness** (escalated exactly when required — legal, safety, PII, over-$50 — and not otherwise?), **tool-call accuracy** (right tool, right arguments?). One criterion each; strict output format (`PASS`/`FAIL` + one-line reason).
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

## Stretch — put error bars on your judge

Your agreement matrix says how the judge did on 40 labels. But the number you
actually ship — the pass rate on thousands of unlabeled traces — inherits the
judge's bias (judges that over-pass inflate it; judges that over-fail deflate
it). `judge_stats.py` (stdlib only, no new dependencies) fixes that:

- `bias_corrected_rate(...)`: your 40 hand-labels measure the judge's
  true-positive / true-negative rates; the correction applies them to the
  judge's verdicts on unlabeled data to estimate the TRUE pass rate.
- `bootstrap_ci(...)`: resamples your 40 labels 2000 times to put a 95%
  confidence interval around that estimate.

Run it on one judge: your 40 hand labels + its verdicts on those 40 + its
verdicts on 200+ unlabeled traces (`python judge_stats.py` shows a worked
Pronto example with illustrative synthetic numbers).

- [ ] Bias-corrected pass rate reported with 95% CI for at least one judge
- [ ] One-line interpretation: which direction was your judge biased, and by how much?
