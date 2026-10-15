# The shared agent

This is the customer-service agent you build in **Week 1** and reuse for the
rest of the course. Every week's evals run against this same agent, so
improvements compound: Week 2 judges score it, Week 3 attacks it, Week 4
grades its RAG answers, Week 5 scores its tool use, Week 6 gates its deploys.

Two files, two eras:

- `agent.py` — the **Week 1 skeleton**. Rule-based keyword matching, canned
  responses. It was the right tool for learning traces and annotations.
  From Week 3 on, it is retired as the agent under test.
- **`pronto_agent.py` — the canonical agent from Week 3 on.** A REAL loop:
  model reasons -> calls tools -> reads results -> answers. Shared-history
  multi-turn (`--chat`), real multi-turn traces, no canned responses.

## Run the canonical agent

Always from the repo root, as a module (the `python agent/...py` form
breaks on imports):

```bash
python -m agent.pronto_agent --ask "Where is my order PRN-10421?"
python -m agent.pronto_agent --ask "refund $85 on PRN-10421" --model gpt-4o
python -m agent.pronto_agent --chat     # multi-turn: history carries across turns
```

`--ask` (or a positional prompt — the form promptfoo's exec provider uses)
prints ONLY clean JSON `{"input": ..., "output": ...}` to stdout —
safe as a promptfoo exec provider (banners go to stderr):

```yaml
# promptfooconfig.yaml (Week 3) — run `promptfoo eval` from the repo root.
# NOTE: promptfoo >= 0.122 uses the `exec: <command>` string form
# (the old `id: exec` + `config.command` form was removed).
providers:
  - id: 'exec: python -m agent.pronto_agent'
```

## Model resolution (first match wins)

1. `PRONTO_BASE_URL` set -> local model, e.g. Ollama at
   `http://localhost:11434/v1` with `PRONTO_API_KEY=ollama`,
   `PRONTO_MODEL=qwen2.5:14b`.
2. `BRAINTRUST_API_KEY` set -> Braintrust's AI proxy. **You already have
   this key from Week 2 — zero new setup.**
3. `OPENAI_API_KEY` set -> plain OpenAI.

Model name: `PRONTO_MODEL`, default `gpt-4o-mini` (`--model` overrides).
With nothing set, the agent exits naming exactly which env var to set.

## Tracing (first match wins; never crashes on missing deps)

1. `braintrust` installed + `BRAINTRUST_API_KEY` -> Braintrust traces
   (project `pronto`), one trace per turn.
2. `langsmith` installed + `LANGSMITH_API_KEY` (or `LANGCHAIN_API_KEY`) ->
   LangSmith traces.
3. Otherwise -> untraced. The agent still runs.

## The one built-in guardrail

Every turn starts with an `ESCALATION_KEYWORDS` pre-check (legal threats,
safety issues, other customers' data) that escalates to a human. It is
deliberately crude — Week 3 measures it (catch rate vs over-block rate)
and then you build better ones.

## Guardrail hook (Week 3)

`run_turn_guarded(messages, user_message, model=MODEL,
input_guardrails=(), output_guardrails=())` wires your guardrails around
the loop without touching `run_turn` itself. A guardrail is any callable
`(text) -> (blocked, reason)`:

- `input_guardrails` see the user text before the model is called — a
  block returns a refusal with no model call.
- `output_guardrails` see the final reply before it is returned — a block
  swaps in a safe refusal. This side catches data leakage, whose *input*
  looks benign.

Runs at temperature 0 (`PRONTO_TEMPERATURE` to override) so scans are
reproducible across runs.

## How it evolves

| Week | What changes in `agent/` |
|------|--------------------------|
| 1 | `agent.py` skeleton: LangSmith tracing; annotate traces |
| 2 | Judges score the agent's outputs |
| 3+ | `pronto_agent.py` (real loop): guardrails wrap its tools |
| 4 | Its doc answers get scored in Braintrust |
| 5 | Its tool trajectories get evaluated |
| 6 | Its evals gate every change in CI |

## Reference: the old tracing demo

`pronto_braintrust_demo.py` — the original real-loop demo this file was
promoted from. Deprecated; kept for reference. Use `pronto_agent.py`.
