# The shared agent

This is the customer-service agent you build in **Week 1** and reuse for the
rest of the course. Every week's evals run against this same agent, so
improvements compound: Week 2 judges score it, Week 3 attacks it, Week 4
grades its RAG answers, Week 5 scores its tool use, Week 6 gates its deploys.

## Run it

```bash
make agent                    # --demo mode: canned responses, no API key needed
python agent/agent.py --demo  # same thing, without make
python agent/agent.py --demo --ask "Where is my order PRN-10421?"
```

`--demo` uses canned tool outputs so you can verify your setup before adding
an API key. Try the policy paths too: refunds over $50 get escalated to a
human (per the Pronto bible), legal/safety/privacy issues always escalate.
With a key in `.env`, the `run()` loop is ready for you to wire
up a real model call.

## What's inside

- `CustomerServiceAgent` — the agent. Four stub tools, one `run()` loop.
- `get_order_status`, `lookup_policy`, `issue_refund`, `escalate_to_human` —
  tools with canned demo data (Pronto grocery orders, policy snippets).
  Replace the bodies with real implementations (or model-driven tool calls)
  as the course progresses.
- `TODO (Week 1)` markers — exactly where LangSmith tracing gets wired in
  during Assignment 1. Don't wire them early; the assignment walks you through it.

## How it evolves

| Week | What changes in `agent/` |
|------|--------------------------|
| 1 | Add LangSmith tracing; annotate traces |
| 2 | Judges score its outputs |
| 3 | Guardrails wrap its tools |
| 4 | Its doc answers get scored in Braintrust |
| 5 | Its tool trajectories get evaluated |
| 6 | Its evals gate every change in CI |

## Braintrust tracing demo

`pronto_braintrust_demo.py` — the Pronto agent as a real end-to-end loop
(model reasons → calls tools → reads results → answers), sending its traces
to Braintrust instead of LangSmith. Three moves: `init_logger(project=...)`,
`wrap_openai(OpenAI())`, `@traced` on each tool. Run it, then open the
`pronto-demo` project at braintrust.dev → Logs to see the full trace tree —
each turn's model calls and tool calls nested in the order the agent ran them.

```bash
pip install braintrust   # per-week install, like promptfoo
python agent/pronto_braintrust_demo.py --ask "Where is my order PRN-10421?"
```

Needs `BRAINTRUST_API_KEY` and `OPENAI_API_KEY` in `.env`. Good for a live
"where do traces go?" demo — the trace you watch being built is the trace
you then open in the dashboard.
