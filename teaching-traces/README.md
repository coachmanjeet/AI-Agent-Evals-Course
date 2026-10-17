# Pronto teaching traces — 55 multi-turn conversations, 11 issue types

A synthetic-but-realistic trace set for teaching evals, monitoring, and
observability on the Pronto agent (`agent/pronto_agent.py`). Every trace
mirrors the agent's real span shape: root span `run_turn` per turn, with
`chat.completions` (LLM) and tool spans (`get_order_status`,
`lookup_policy`, `issue_refund`, `escalate_to_human`) underneath.

## What's in the set

55 conversations × 2–4 turns (114 turn-traces), 5 per issue category:

| # | Category | What to teach with it |
|---|----------|----------------------|
| 1 | `high_latency` | Latency SLOs per tool, p99 alerts, critical-path analysis, UX compounding |
| 2 | `excessive_tool_calls` | Loop detection, step budgets, cross-turn redundancy, cost of guessing |
| 3 | `high_cost` | Token/cost budgets per turn, retrieval-size control, output verbosity caps |
| 4 | `high_error_rate` | Retry counting, graceful degradation, error-span grouping for incidents |
| 5 | `pii_leak` | Output guardrails, PII redaction, social-engineering resistance |
| 6 | `policy_violation` | Hard constraints in code (not prompts), commitment eval, eligibility logic |
| 7 | `rag_failure` | Retrieval hit rate, faithfulness eval, conflict resolution, empty-retrieval handling |
| 8 | `prompt_injection` | Direct vs indirect injection, guardrail catch-rate measurement |
| 9 | `hallucination` | No-tool-call detection, tool-result contradiction checks, phantom actions |
| 10 | `escalation_failure` | Tripwire recall, over-escalation cost, handoff quality |
| 11 | `adversarial_safety` | Encoding jailbreaks, harmful-content refusals, exfiltration probes, emotional manipulation |

`traces_manifest.csv` indexes every conversation: id, category, title,
turn count, the issue demonstrated, and a teaching note.

## Files

- `generate_traces.py` — the generator (deterministic, seeded). Edit scenarios
  and re-run: `python3 generate_traces.py`.
- `braintrust_spans.jsonl` — one span event per line; upload via
  `POST /v1/project_logs/{project_id}/insert` with `{"events": [...]}`.
- `langfuse_batch.json` — `{"batch": [...]}` for
  `POST {LANGFUSE_HOST}/api/public/ingestion` (Basic auth: public key / secret key).
- `traces_manifest.csv` — the index.
- `upload_braintrust.py` — uploads the spans to the `pronto-issue-traces`
  Braintrust project (uses the course's `bt_api.py` helper).
- `upload_langfuse.py` — uploads to Langfuse ingestion API; needs
  `LANGFUSE_HOST`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` in env.

## Braintrust

Project: `pronto-issue-traces`. Filter by `metadata.issue_category` or the
`issue:<category>` tag. Every span carries `conversation_id`, `scenario_id`,
`turn`, and `synthetic: true`. Model spans carry token counts and `cost_usd`;
tool spans carry `tool_error` and the `error` tag on failures.

## Langfuse

Each turn is a trace, grouped by `sessionId` = conversation id. Generations
carry `usage` (input/output/total tokens) and `cost_usd` in metadata; failed
tool spans are marked `level: ERROR`.

## Regenerating / extending

Scenarios live in `SCENARIOS` at the bottom of `generate_traces.py`:
`(category, scenario_id, title, builder, issue, teaching)`. Add a builder
function, register it, re-run. Single-turn scenarios automatically get a
follow-up turn from `FOLLOWUPS` so every conversation stays multi-turn.
