# The shared agent

This is the customer-service agent you build in **Week 1** and reuse for the
rest of the course. Every week's evals run against this same agent, so
improvements compound: Week 2 judges score it, Week 3 attacks it, Week 4
grades its RAG answers, Week 5 scores its tool use, Week 6 gates its deploys.

Two files, two eras:

- `agent_skeleton.py` — the **Week 1 skeleton**. Rule-based keyword
  matching, canned responses — not a real agent loop; the name says so.
  It was the right tool for learning traces and annotations.
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
| 1 | `agent_skeleton.py` skeleton: LangSmith tracing; annotate traces |
| 2 | Judges score the agent's outputs |
| 3+ | `pronto_agent.py` (real loop): guardrails wrap its tools |
| 4 | Its doc answers get scored in Braintrust |
| 5 | Its tool trajectories get evaluated |
| 6 | Its evals gate every change in CI |

## Harvested from the retired Braintrust tracing lab handout

The old handout (`braintrust-tracing-lab-setup.docx`, deleted 2026-10-20)
was a stale parallel of the original real-loop demo
(`pronto_braintrust_demo.py`, removed 2026-10-21 to avoid confusion — the
canonical agent below supersedes it) — it told students to
run `pronto_braintrust_demo` against a project named `pronto-demo` with a
separate OpenAI key, all of which contradicts the canonical contract
above. Its setup/run parts are **not** preserved. The two pieces of
unique, still-valid material it held are preserved here, adapted to the
canonical agent (`python -m agent.pronto_agent`, project `pronto`, model
resolution as above), plus its trace-reading steps and local-model pull
steps, which appear nowhere else.

### Reading a trace in Braintrust

1. Open braintrust.dev → Projects → `pronto` → Logs, and refresh. Your
   run appears at the top (give it ~30 seconds).
2. Click the trace to open it.
3. Expand it: one root span (`run_turn`) with model-call spans and tool
   spans (`get_order_status`, `lookup_policy`, …) nested inside, in the
   exact order the agent ran them.
4. Click any tool span: you'll see its inputs going in and its result
   coming out.

Notice what you did not do: write any logging code. The trace exists
because the program is instrumented, not because anyone printed anything.

### Troubleshooting (Braintrust tracing lab)

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'agent.agent'` | You're not in the repo root, or you forgot `-m`. `cd` to the repo root and run `python3 -m agent.pronto_agent …` |
| "Set `BRAINTRUST_API_KEY` in .env" | The `.env` file must sit in the repo root (next to the `agent/` folder). Check the key names and remove any spaces around `=`. |
| No trace appears in Logs | Wait ~30 seconds and refresh. Confirm the project is named `pronto` and you're in the right organization. |
| Model errors, or everything is very slow | Check the OpenAI key and billing — or switch to the local Ollama path (see "Model resolution" above). |

Local-model note (from the handout's Part 6): install Ollama
(`brew install ollama`, or download it from ollama.com), start it with
`ollama serve`, and pull the model **before class, not on classroom
wifi** — `ollama pull qwen2.5:14b` is about 9 GB. Then use the
`PRONTO_BASE_URL` / `PRONTO_API_KEY=ollama` / `PRONTO_MODEL=qwen2.5:14b`
settings from "Model resolution" above. A 14B local model is a weaker
reasoner than `gpt-4o-mini`, so its answers (and tool choices) may be
rougher — for a tracing lab, that's fine.

### Your turn — predict the tools, then compare

1. Pick a tricky customer message, e.g.: "My $85 order arrived half
   missing, refund me in full".
2. Before running: predict which tools the agent will call, and in what
   order.
3. Run it, open the trace, and compare. Where did it surprise you — and
   can you explain why from the spans?
