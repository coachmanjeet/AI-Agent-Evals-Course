# Assignment 1 — Instrument and trace

All files below live in
`week-01-eval-foundations-and-error-analysis/assignments/01-instrument-and-trace/`
unless noted otherwise.

## Goal

Get every agent run leaving a trace you can inspect, then build your first annotated evaluation set.

> **Two paths — pick one.** **Path A (below):** LangSmith, recommended for
> engineers. **Path B (no keys, no LangSmith):** run `python export_otel.py`
> in the assignment folder — it replays all 30 inputs through the demo agent
> (no API key needed) and writes `pronto-traces.json`. Upload that file to the
> [Trace Viewer](https://coachmanjeet.github.io/AI-Agent-Evals-Course/trace-viewer/),
> annotate all 30 traces there, and export annotations as JSON/CSV — the export
> counts as your annotations deliverable. Same learning, zero setup.

## Steps

1. Wire LangSmith tracing into `agent/agent.py`: decorate `run()` and each tool
   (`get_order_status`, `lookup_policy`, `issue_refund`, `escalate_to_human`)
   with `@traceable`. (Markers are already in the code — fill them in.)
   Keys: put **one model key (OpenAI OR Anthropic OR Gemini)** in `.env`,
   plus `LANGSMITH_API_KEY` for Path A. (Path B needs no keys at all.)
2. Confirm traces appear in your LangSmith project (`ai-evals-course`) —
   open smith.langchain.com, pick the project, and you should see your runs.
3. Review the provided `inputs.json`: 30 Pronto inputs, 10 per category —
   - 10 **order/refund requests** (edge cases: a refund over $50, a late-delivery fee request, spoiled perishables, an unknown order ID),
   - 10 **policy / warranty / substitution questions** (perishable vs non-perishable rules, the $50 approval limit, substitution opt-in, Pronto vs manufacturer warranty),
   - 10 **multi-turn conversations** (2–3 turns each), including adversarial ones: a prompt-injection attempt, a request for another customer's data, a legal threat.
4. Run all 30 through the agent using `starter.py` (it replays multi-turn
   inputs turn by turn, so context is preserved). Every run must produce a trace.
5. Annotate each trace end-to-end: **pass/fail** plus a one-line note on what happened.
   (Path B: annotate in the Trace Viewer instead of LangSmith.)
6. Export the annotations to `annotations.csv` (the starter writes this for you).
   (Path B: your Trace Viewer JSON/CSV export is accepted instead.)

## Acceptance criteria

- [ ] All 30 runs produce traces you can inspect (LangSmith project for Path A, Trace Viewer for Path B)
- [ ] `inputs.json` has exactly 30 inputs, 10 per category
- [ ] `annotations.csv` (or Trace Viewer export) has 30 rows, each with pass/fail and a note
- [ ] At least 5 of the 30 are annotated **fail** (if everything passes, your inputs are too easy)

## Starter

`starter.py` — run it with `python starter.py`. It loads your 30 inputs,
runs the agent (multi-turn inputs replayed turn by turn), and writes
`annotations.csv` with empty pass/fail columns for you to fill in (or fill
them programmatically after reviewing traces).

`export_otel.py` — Path B helper. Run it with `python export_otel.py` (no keys
needed): it replays the same 30 inputs through the demo agent and writes
`pronto-traces.json`, an OTel file you upload to the Trace Viewer to annotate.
