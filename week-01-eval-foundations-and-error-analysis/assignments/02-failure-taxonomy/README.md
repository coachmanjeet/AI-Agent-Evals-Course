# Assignment 2 — Build a failure taxonomy

This README is the complete Assignment 2 document. It builds directly on
Assignment 1: your `annotations.csv` is the input, and the failure codes you
used in its notes are the starting vocabulary.

## Goal

Turn your 30 annotated traces into a prioritized, countable picture of how the agent fails.

## What to submit

- [ ] `taxonomy.md` — 5+ binary failure codes with definitions, frequency counts,
      quality-dimension mapping, top 3 modes, 1 unexplained anomaly, and a
      "What you'd fix first" paragraph (see Acceptance criteria)

**Explicitly NOT required in Week 1:** LLM judges, automated scorers,
Braintrust, datasets in a formal eval harness. Those start in Week 2. Your
taxonomy is a human, hand-built artifact — that is the point of Week 1.

## Failure-code vocabulary — one set of names

Use **one** SCREAMING_SNAKE vocabulary across `annotations.csv` (Assignment 1)
and `taxonomy.md` (this assignment). The same failure keeps the same name
everywhere:

- Assignment 1 annotation codes (from the decision table in the Assignment 1
  README): `NO_AUTH`, `HALLUCINATED_ORDER`, `OVER_LIMIT_REFUND`,
  `PROMPT_INJECTION`, `CONTEXT_LOSS`.
- Starter example codes for this assignment: `WRONG_TOOL`, `NO_TOOL`,
  `HALLUCINATED_ORDER`, `BAD_ESCALATION`, `DOC_MISS`.

Note the shared name: invented order details are `HALLUCINATED_ORDER` in both
assignments. There is no `HALLUCINATED_FACT` code — that name appeared in an
older starter draft and has been removed; do not use it, so a second reader
(and your Week 2 judge validation) sees one vocabulary.

You may add codes your failures need, and drop example codes that don't match
your failures — but every code you keep must be binary and checkable (Step 2),
and a code that names the same failure as an Assignment 1 code must reuse
that name.

*Trace Viewer / datasets note:* the Trace Viewer's annotation dropdown and
the course datasets (`datasets/README.md`) use a separate machine-readable
snake_case `failure_mode` list (`wrong_order_status`, `over_refund`,
`pii_leak`, …) that labels the shipped datasets and viewer sample. That list
is ground truth for those files — it is not your taxonomy vocabulary. When
you annotate in the Trace Viewer, pick the closest viewer mode and record
your Week 1 code in the note.

## Steps

1. Start from `annotations.csv` (Assignment 1). Read every trace marked **fail**.
2. Cluster the failures into **5 or more binary trace codes** — each code is a yes/no question about a trace, e.g. `WRONG_TOOL` (agent called the wrong tool), `NO_TOOL` (should have called a tool, didn't), `HALLUCINATED_ORDER` (invented order details), `BAD_ESCALATION` (escalated when it could have answered), `DOC_MISS` (correct doc existed, wasn't surfaced).
3. Count: how many of the 30 traces hit each code. A trace can hit multiple codes.
4. Map each code to one of the six quality dimensions (model quality, product behavior, safety, reliability, cost, latency).
5. Write up: the **top 3 failure modes** by frequency, plus **1 unexplained anomaly** — a failure you can't yet explain. Name it honestly.
6. Close with **"What you'd fix first"**: one paragraph — if you had one
   engineering day, which failure mode you'd attack and what change you'd
   try. This becomes Week 2's diagnose-and-fix input. (The starter template
   has this section; it is required, not optional.)

## Acceptance criteria

- [ ] `taxonomy.md` defines 5+ binary codes, each with a one-line definition
- [ ] Every code has a frequency count (sums may exceed 30 — codes aren't exclusive)
- [ ] Every code is mapped to a quality dimension
- [ ] Write-up names the top 3 failure modes and 1 unexplained anomaly
- [ ] Codes are binary and checkable — a second person could apply them to a new trace and agree with you
- [ ] Write-up includes a "What you'd fix first" paragraph (one engineering day: which mode, what change)

## Starter

`starter.md` — the taxonomy table template. Copy it into `taxonomy.md` and fill it in.
