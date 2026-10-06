# Week 5 — Multi-Agent Evaluation

Single-agent evals stop being enough the moment agents use tools, keep memory,
and hand work to each other. This week: score the trajectory, not just the answer.

## What we covered

- Agent eval foundations: model vs. agent vs. system (three different things to score)
- Agent failure modes: tool misuse, reasoning loops, memory drift, permission escalation, coordination conflict
- Turn-level vs. conversation-level metrics
- Tool-call scoring; expected-action sets
- Argument validation as structured-output evaluation
- Trajectory evaluation: the path matters, not just the destination
- Property-based trajectory judging vs. exact-match diffs
- Multi-agent coordination: handoff evaluation (completeness, fidelity, routing)
- Cascading failures in agent pipelines
- Model→system score gaps as interaction-failure signals

## Key takeaways

1. **Score at three layers.** A great model can still produce a failing system — the gap between model score and system score is where the bugs live.
2. **Judge properties, not exact paths.** There are many good trajectories; check invariants (right tools, right order, no extra calls) instead of exact matching.
3. **Handoffs are where multi-agent systems die.** Completeness, fidelity, routing — evaluate each handoff like a contract.
4. **Flag fragile passes.** A pass that succeeded for the wrong reason is a future incident with a timestamp.

## Links

- LangSmith docs — tracing multi-step trajectories: https://docs.langchain.com/langsmith
- DeepEval docs — conversational metrics: https://deepeval.com

## In this folder

- `examples/` — worked examples from the live session (added after the session)
- `assignments/01-score-tools-and-trajectories/` — expected-action records + trajectory evaluator
- `assignments/02-find-interaction-failures/` — three-layer report + handoff root causes
