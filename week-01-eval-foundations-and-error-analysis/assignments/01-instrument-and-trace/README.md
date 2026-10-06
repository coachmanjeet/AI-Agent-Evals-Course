# Assignment 1 — Instrument and trace

## Goal

Get every agent run leaving a trace you can inspect, then build your first annotated evaluation set.

> **Two paths — pick one.** **Path A (below):** LangSmith, recommended for
> engineers. **Path B:** skip the LangSmith steps and do this whole assignment
> in the [Trace Viewer](https://coachmanjeet.github.io/AI-Agent-Evals-Course/trace-viewer/):
> load the Pronto sample, annotate 30 traces (re-run the samples or upload your
> own OTel JSON), export annotations as JSON/CSV. Same learning, zero setup.

## Steps

1. Wire LangSmith tracing into `agent/agent.py`: decorate `run()` and each tool
   (`get_order_status`, `lookup_policy`, `issue_refund`, `escalate_to_human`)
   with `@traceable`. (Markers are already in the code — fill them in.)
2. Confirm traces appear in your LangSmith project (`ai-evals-course`).
3. Build `inputs.json`: 30 inputs total —
   - 10 **order/refund requests** (include edge cases: a refund over $50, a late-delivery fee request, spoiled perishables, an unknown order ID),
   - 10 **policy / warranty / substitution questions** (perishable vs non-perishable rules, the $50 approval limit, substitution opt-in, Pronto vs manufacturer warranty),
   - 10 **multi-turn conversations** (2–3 turns each), including 2–3 adversarial ones: a prompt-injection attempt, a request for another customer's data, a legal threat.
4. Run all 30 through the agent using `starter.py`. Every run must produce a trace.
5. Annotate each trace end-to-end in LangSmith: **pass/fail** plus a one-line note on what happened.
6. Export the annotations to `annotations.csv` (the starter writes this for you).

## Acceptance criteria

- [ ] All 30 runs produce traces visible in LangSmith under one project
- [ ] `inputs.json` has exactly 30 inputs, 10 per category
- [ ] `annotations.csv` has 30 rows, each with pass/fail and a note
- [ ] At least 5 of the 30 are annotated **fail** (if everything passes, your inputs are too easy)

## Starter

`starter.py` — run it with `python starter.py`. It loads your 30 inputs,
runs the agent, and writes `annotations.csv` with empty pass/fail columns
for you to fill in (or fill them programmatically after reviewing traces).
