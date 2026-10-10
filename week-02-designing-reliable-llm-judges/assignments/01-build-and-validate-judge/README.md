# Assignment 1 — Build and validate a judge

All files below live in
`week-02-designing-reliable-llm-judges/assignments/01-build-and-validate-judge/`
unless noted otherwise.

## Goal

Build three binary LLM judges for the Pronto agent and prove each one agrees
with human judgment before you trust it to gate anything.

> **Warm up first (15 min, done in class).** Play the
> [Judge Calibration Game](https://coachmanjeet.github.io/AI-Agent-Evals-Course/judge-calibration-game/)
> before you start: label 24 Pronto responses, write one judge prompt, and
> watch your agreement scored live. It teaches the whole loop — labels,
> rubric, agreement matrix, kappa — before you touch code. Paste your
> Braintrust API key in the game's Setup step (free course credit), or run it
> in `?mock=1` mode with no key.

## Setup

1. `pip install braintrust openai` (both are in the course `requirements.txt` —
   skip if you ran `make setup`).
2. Put `BRAINTRUST_API_KEY=...` in your `.env` (free course access at
   braintrust.dev — no separate model key needed; judge calls run on the
   course credit through Braintrust's proxy).
3. Sanity-check with `python ../../braintrust_smoke_test.py` — all three
   checks should print OK. If they don't, fix that before writing a single
   rubric.

## Steps

1. **Write 3 binary rubrics** as judge prompts — one criterion each:
   - **policy adherence** — did the agent follow the Pronto policy bible?
     (24h photo for perishables, 30-day non-perishable returns, >$50 refunds
     need human approval, substitution only with checkout opt-in, 1-year
     warranty on Pronto-branded appliances only.)
   - **escalation correctness** — did it escalate exactly when required
     (legal threats, safety/health issues, another customer's data, refunds
     over $50) and *not* escalate routine requests it could handle itself?
   - **tool-call accuracy** — right tool, right arguments?
     (`get_order_status` / `issue_refund` / `lookup_policy` / `escalate_to_human`).
   
   Each rubric needs the five elements from class: auditor role, one binary
   question, concrete PASS/FAIL standard, a boundary example, strict output
   format (`PASS`/`FAIL` + one-line reason). `starter.py` has templates —
   the prompts are yours to write.
2. **Implement them as Braintrust scorers** (`starter.py` has the skeleton):
   one scorer function per rubric, each returning 0/1, run over your labeled
   cases with `braintrust.Eval`. Judge calls go through Braintrust's proxy,
   so they draw from the free course credit.
   
   > Prefer LangSmith or another tool? Fine — implement the same three
   > rubrics there instead. The rubrics and the validation below are what get
   > graded, not the platform.
3. **Label 40 agent outputs by hand** — your ground truth. Reuse your Week 1
   traces or generate 40 fresh Pronto outputs. Label *each output against all
   three rubrics* (40 outputs × 3 rubrics = 120 individual labels). Aim for a
   hard set: if everything passes, your cases are too easy and the agreement
   number will flatter you.
4. **Run the judges over the 40-label set.** For each judge, build the
   agreement matrix (judge-pass/human-pass, judge-pass/human-fail,
   judge-fail/human-pass, judge-fail/human-fail) — 4 cells with counts.
   In Braintrust, open the Eval run and compare each scorer's verdicts
   against your hand labels row by row.
5. **Compute Cohen's kappa per judge** (`cohens_kappa()` is in the starter).
   Then investigate *every* disagreement and decide: is the judge wrong, or
   is your label wrong? Labels are allowed to be wrong — that's why you
   adjudicate. Write down each call you made.
6. **Name your worst judge's failure mode.** False passes (judge waved
   through a real failure) or false fails? What's the shared pattern?

## What to submit

- `rubrics.md` — your 3 judge prompts, verbatim.
- `labels.jsonl` — 40 rows: `{"input", "output", "human": {rubric: PASS/FAIL}}`.
- `results.md` — per judge: agreement matrix (4 cells), agreement %, Cohen's κ,
  and the false-pass / false-fail counts.
- `diagnosis.md` — for your worst judge: dominant failure mode, the shared
  loophole behind its false passes, and whether any labels changed on
  adjudication (and why).

## Acceptance criteria

- [ ] 3 judge prompts, one criterion each, strict `PASS`/`FAIL` + reason output format
- [ ] 40 outputs labeled by hand against all 3 rubrics (120 labels)
- [ ] Agreement matrix per judge (4 cells with counts)
- [ ] Cohen's kappa reported per judge; kappa ≥ 0.6 before the judge is "trusted"
- [ ] Written note on the worst judge: its dominant failure mode (false-pass or false-fail?)
- [ ] At least one label changed on adjudication, with the reason written down
      (if none did, say so and why — perfect first-pass labels are suspicious)

## Starter

`starter.py` — rubric prompt templates, Braintrust scorer skeleton
(`run_judge` + `make_scorer` + `run_braintrust_eval` wiring), judge calls via
Braintrust's proxy (free course credit, no separate model key), and
`cohens_kappa()` + `agreement_matrix()` implementations. Fill in the three
prompts and the judge wiring, then run the `__main__` flow.

## Common pitfalls

- **Tuning on the test set.** If you edit the rubric to fix misses on these
  same 40 labels, the agreement number is no longer honest. Keep a held-out
  slice if you iterate.
- **Easy cases inflating agreement.** 40 trivial passes will give you 95%+
  agreement and teach you nothing. Include adversarial and edge cases.
- **Multi-criteria prompts.** "Rate helpfulness, accuracy, and tone" is three
  judges wearing a trench coat. One judge, one question.
- **Trusting the first kappa.** A lucky 0.62 on 40 labels is not a validated
  judge. Read the false passes — that's where the real signal is.

## Time estimate

4–6 hours (labeling is the bulk of it — about 5 minutes per output × 40).

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
