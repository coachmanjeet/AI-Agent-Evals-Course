# Assignment 2 — Diagnose and compare

All files below live in
`week-02-designing-reliable-llm-judges/assignments/02-diagnose-and-compare/`
unless noted otherwise.

## Goal

Run a full diagnose-and-fix cycle on the Pronto agent: find what breaks, fix
exactly one thing, and A/B test the fix with per-metric deltas — then make a
ship/no-ship call like you'd defend it in a review.

This builds directly on Assignment 1: you can only A/B test what you can
measure, and your three validated judges are the measuring instruments.
(If a judge never cleared the trust bar — kappa ≥ 0.6 — say so upfront and
note which metric's delta you trust least.)

## Steps

1. **Pick your worst failure mode** from Week 1's taxonomy — the one your
   judges now measure reliably. Not the most interesting one; the one with
   the worst numbers.
2. **Diagnose: pull 10 failing traces** and find the shared root cause. Read
   them together, not one by one — you're looking for the pattern, the way
   you looked for the shared loophole in false passes. Write it down in one
   paragraph: specific enough that someone else could predict the next
   failure from it.
3. **Fix: change ONE thing.** A prompt variant, a tool description, a routing
   rule. Not three things — if you change three things and the numbers move,
   you learned nothing. Document the exact diff between A and B.
4. **A/B test properly:**
   - Same input set through variant A (baseline) and variant B (fix).
     Reuse inputs from Week 1 or Assignment 1 — at least 30, and keep the
     hard ones.
   - Score both variants with your three Week 2 judges, per metric.
   - In Braintrust, run this as two experiments on the same dataset so the
     comparison view shows deltas side by side.
   - Never eyeball a handful of examples. The full suite, both variants.
5. **Report per-metric deltas** — one row per judge
   (e.g. tool-call accuracy +12pp, escalation correctness −2pp). Report the
   deltas separately; do not blend them into one average. A blended +3 can
   hide a −3 regression on the metric your users feel most.
6. **Write the ship/no-ship decision** (`starter.md` → copy to `ab_report.md`):
   verdict, the numbers behind it, the thresholds you set *before* seeing
   results, and what would change your mind.

## What to submit

- `ab_report.md` — the filled-in template: diagnosis, the one change,
  per-metric deltas table, ship/no-ship verdict with thresholds and
  "what would change my mind."
- `diagnosis.md` (or the report's diagnosis section) — the 10 trace IDs you
  read and the one-paragraph root cause.
- Screenshots or exported rows from the two Braintrust experiments showing
  the per-metric comparison (or the equivalent from your tool of choice).

## Acceptance criteria

- [ ] One-paragraph root-cause diagnosis grounded in 10 traces (trace IDs listed)
- [ ] Exactly one change between A and B (documented as a diff)
- [ ] Same input set (n ≥ 30) run through both variants, full suite, no eyeballing
- [ ] Per-metric deltas reported for all 3 judges (pp deltas, not a blended average)
- [ ] Ship/no-ship decision with numeric thresholds stated upfront
      (e.g. "ship if tool-call accuracy ≥ 90% and no metric regresses > 3pp")
- [ ] "What would change my mind" section filled in
- [ ] Any judge below the trust bar is flagged, with which delta you trust least

## Starter

`starter.md` — the A/B report + ship/no-ship template. Copy it to
`ab_report.md` and fill in every section. The table, the thresholds-first
rule, and the "what would change my mind" prompt are all in there.

## Common pitfalls

- **Changing more than one thing.** The classic. One variable per experiment
  or the delta is uninterpretable.
- **Different inputs per variant.** A and B must see the same set, or you're
  measuring the inputs, not the fix.
- **Blended averages.** Report each metric's delta on its own row. The
  decision lives in the trade-off between them.
- **Thresholds after results.** Writing "ship if ≥ 90%" after seeing 91% is
  decorating a decision you already made. Thresholds first, then numbers.
- **Ignoring a regression.** A +12pp win paired with a −5pp loss is not an
  obvious ship. Say which regression you'd accept and why — that's the
  actual judgment call being graded.

## Time estimate

3–4 hours (diagnosis is the bulk of it — reading 10 traces carefully).
