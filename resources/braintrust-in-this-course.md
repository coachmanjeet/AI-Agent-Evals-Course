# Braintrust in This Course

Braintrust plays two roles: (1) where agent traces land so you can see what
the agent did, and (2) the eval harness — datasets, scorers, and the results
table. The key detail for students: two keys, two jobs.
`BRAINTRUST_API_KEY` is your Braintrust login — traces, datasets, evals.
Judge calls go through Braintrust's OpenAI-compatible proxy
(api.braintrust.dev/v1/proxy), and the proxy calls the model through a
provider key you add once in Braintrust under Settings → AI Providers
(your own OpenAI key; gpt-4o-mini judge calls cost ~$0.01 for the week).
Without that provider key, the proxy has no model to call and judge
calls fail.

## Week 1 — tracing

Week 1's assignments officially offer two paths: Path A (LangSmith, needs a
key) and Path B (the keyless Trace Viewer in the browser). Braintrust is
the third, upgrade option: the canonical agent — `python -m agent.pronto_agent`,
run from the repo root — sends its traces to Braintrust automatically when
`BRAINTRUST_API_KEY` is set, no extra wiring. Students open braintrust.dev →
project `pronto` → Logs → click a trace and see the full
nested run: model → tool → model → answer.

Point to land: traces are the raw material. Everything in Week 2 (labels,
judges, agreement) starts from looking at real traces.

## Week 2 — judges, Braintrust-first

This is where Braintrust becomes the default:

- **Assignment 1 (starter.py):** students write three binary rubric prompts
  (policy adherence, escalation correctness, tool-call accuracy), wire each
  as a Braintrust scorer returning 0/1, then run `braintrust.Eval` over
  their 40 hand-labeled cases. The payoff moment is the results table in the
  Braintrust UI — per-case scores, side by side with their own labels.
  That's where judge-vs-human agreement stops being abstract.
- **Judge calibration game:** in the Setup step they pick Braintrust, paste
  the key, and play — the game calls the same proxy.
- **Smoke test (braintrust_smoke_test.py):** verifies key → proxy answers a
  judge-style call → a real 3-case Eval lands in the UI. This is the "is my
  setup working" check.

Point to land: a judge is just a scorer with a rubric prompt, and
Braintrust is where you see whether your judge agrees with you.

## Quick start

```sh
pip install braintrust openai
export BRAINTRUST_API_KEY=<your-key>

# 1. Prove the plumbing (30s)
python week-02-designing-reliable-llm-judges/braintrust_smoke_test.py
# → open braintrust.dev, project "smoke-test": 3 scored rows

# 2. Traces (2 min)
python -m agent.pronto_agent --ask "My $85 order arrived half missing, refund me in full"
# → braintrust.dev → Logs → click the trace, expand the spans

# 3. The eval loop (2 min) — after students wire starter.py
# → Eval results table: judge scores vs. their 40 hand labels
```
