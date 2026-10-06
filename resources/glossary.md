# Eval glossary

Plain-English definitions for the terms used across the course.

- **Golden set** — a curated, labeled set of test cases you trust; the ground truth your evals run against.
- **Trace** — the full record of one agent run: inputs, tool calls, model outputs, timing.
- **Span** — one timed unit inside a trace (a single tool call, a single model call).
- **Judge** — an evaluator, often an LLM, that scores an output against a rubric.
- **Rubric** — the written criteria a judge scores against.
- **Likert scale** — a rating scale (e.g. 1–5); useful for exploration, weak for gating.
- **Cohen's kappa** — a statistic measuring agreement between two labelers, corrected for chance agreement. Above 0.6 is decent; above 0.8 is strong.
- **Red teaming** — deliberately attacking your own system to find weaknesses before someone else does.
- **Guardrail** — a check that blocks or flags unsafe inputs, tool calls, or outputs.
- **Prompt injection (direct)** — malicious instructions in the user's own input ("ignore your instructions…").
- **Prompt injection (indirect)** — malicious instructions smuggled in via content the agent reads (a doc, a webpage, a tool result).
- **Jailbreak** — a technique that gets a model to bypass its safety training (role-play, hypotheticals, encoding, emotional framing).
- **Groundedness** — whether an answer is actually supported by the retrieved context, as opposed to hallucinated.
- **Faithfulness** — a RAGAS metric: is the generated answer consistent with the retrieved context?
- **Answer relevance** — a RAGAS metric: does the answer actually address the question asked?
- **Context precision** — a RAGAS metric: of the retrieved chunks, how many were relevant? (signal vs. noise)
- **Context recall** — a RAGAS metric: of the relevant chunks that exist, how many were retrieved? (coverage)
- **Data drift** — the incoming data distribution shifts (users start asking new kinds of questions).
- **Concept drift** — the right answer changes even though the inputs look the same (policies update, the world moves).
- **Prompt/model drift** — behavior changes because the prompt or the underlying model changed.
- **Canary eval** — a fixed input set re-run on a schedule and compared against baseline to detect drift early.
- **Eval gate** — an automated checkpoint (usually in CI) that blocks a merge or deploy when eval scores drop below thresholds.
- **Flywheel** — the compounding loop: deploy → analyze failures → build dataset → improve → monitor → repeat.
- **Catch rate** — of the attacks in your test set, the share a guardrail blocks.
- **Over-block rate** — of the legitimate inputs in your test set, the share a guardrail wrongly blocks.
- **Trajectory** — the sequence of steps (tool calls, reasoning) an agent took, not just its final answer.
- **Handoff** — a transfer of work between agents (or agent and human); evaluated on completeness, fidelity, and routing.
- **Ship / no-ship** — the release decision, made against numeric thresholds written down *before* seeing results.
