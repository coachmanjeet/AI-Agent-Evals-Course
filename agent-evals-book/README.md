# agent-evals-book

Companion code for *AI Agent Evals: Evaluate and Improve Single- and Multi-Agent Systems* (First Edition). It lives in the course repository, https://github.com/coachmanjeet/AI-Agent-Evals-Course, next to the AI Evals in Practice course materials.

Runnable code for *AI Agent Evals: Evaluate and Improve Single- and Multi-Agent Systems*. Every idea in the book runs here against one agent, Pronto's customer support agent (an online grocery store), backed by a real SQLite system of record.

## Quick start

```bash
git clone https://github.com/coachmanjeet/AI-Agent-Evals-Course.git
cd AI-Agent-Evals-Course/agent-evals-book
pip install -r requirements.txt
pytest -q                                                   # grader tests, smoke tier, statistics
python -m evals.run --agent careful --tier full --trials 4  # scorecard + run records (runs.jsonl)
python -m evals.run --agent naive --tier full               # reproduces the book's failures; exits 1
```

## Plug in a real model

`ScriptedAgent` is a deterministic stand-in so everything runs offline. `LLMAgent` connects a real model to the same tools, graders, and harness:

```bash
pip install anthropic && export ANTHROPIC_API_KEY=...
python -m evals.run --agent llm --model <model-id> --tier smoke --trials 4
```

Any tool-calling model works if it implements `run(world, task) -> reply`.

## Map to the book

| Path | Chapters |
|---|---|
| `pronto/world.py`: SQLite ledger, injected clock, fault injector, trace | 1, 11, 18 |
| `pronto/tools.py`: idempotency keys, key-conflict rejection | 1 |
| `evals/contracts/refund.json`: the task contract | 2 |
| `evals/cases/refund_cases.jsonl`: cases with tier, source, dimensions | 5, 6, 8 |
| `evals/graders.py`: effect grader, path rules, three verdicts | 1, 2, 9, 12 |
| `evals/stats.py`: pass^k, Wilson, sign test, kappa, Rogan-Gladen, sizing | 4, 7, 10, 20, App. F |
| `evals/harness.py`: fresh world per trial, run records, scorecard | 4, 8, 11 |
| `evals/judge.py`: judge prompt, output schema, grader errors | 10 |
| `evals/rag_metrics.py`: context precision and recall, faithfulness | 15 |
| `TOOLS.md`: dated map of harness parts to tools | 22 |
| `evals/redact.py`: redaction before traces become cases | 19 |
| `judges/`: judge bake-off script and dated results template | 10 |
| `evals/reconcile.py`: duplicates, wrong amounts, missing and unexpected writes | 19 |
| `../.github/workflows/agent-evals-book.yml`: smoke on every PR, full suite nightly | 22 |

## Extend it

Add a case: append a line to `evals/cases/refund_cases.jsonl`. Add a failure: add a fault to `World` and a case that triggers it. Add a grader: write it in `evals/graders.py` with a known-good and known-bad test in `tests/`.
