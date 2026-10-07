# Pronto Metrics Catalog

The named metrics worth emitting for the Pronto support agent. Names follow
OTel-style dot conventions. The 10-metric **starter set** is bolded — start
there, add the rest only when a question needs them. Adapted for this course
from the AgentOps metrics catalog.

## Throughput & Errors

| Metric | Type | Unit | Labels | Definition |
|---|---|---|---|---|
| **`agent.runs.total`** | counter | runs | `version`, `env`, `outcome` | Every Pronto run completed (success or failure) |
| **`agent.runs.failed`** | counter | runs | `version`, `error.class` | Runs ending in unrecovered error or timeout |
| `agent.runs.timeout` | counter | runs | `version` | Runs that hit the hard timeout |
| `agent.runs.blocked` | counter | runs | `policy.id` | Runs blocked by a guardrail (e.g. prompt injection) |

## Latency

| Metric | Type | Unit | Labels | Definition |
|---|---|---|---|---|
| **`agent.run.duration`** | histogram | ms | `version`, `outcome` | End-to-end run duration |
| `agent.llm.duration` | histogram | ms | `model` | Time per LLM call |
| `agent.tool.duration` | histogram | ms | `tool.name` | Time per tool call (`get_order_status`, `issue_refund`, `lookup_policy`, `escalate_to_human`) |

## LLM / Tokens / Cost

| Metric | Type | Unit | Labels | Definition |
|---|---|---|---|---|
| **`agent.llm.calls.total`** | counter | calls | `model` | LLM calls made |
| **`agent.llm.tokens.input`** | counter | tokens | `model` | Input tokens consumed |
| **`agent.llm.tokens.output`** | counter | tokens | `model` | Output tokens generated |
| **`agent.llm.cost.usd`** | counter | USD | `model` | Computed cost per call |

## Tools (Pronto's four)

| Metric | Type | Unit | Labels | Definition |
|---|---|---|---|---|
| **`agent.tool.calls.total`** | counter | calls | `tool.name` | Invocations of each Pronto tool |
| **`agent.tool.errors.total`** | counter | errors | `tool.name`, `error.class` | Tool errors and timeouts |
| `agent.tool.retry.total` | counter | retries | `tool.name` | Retries attempted |

## Refunds & Escalations (Pronto-specific)

| Metric | Type | Unit | Labels | Definition |
|---|---|---|---|---|
| **`pronto.refund.issued.total`** | counter | refunds | `outcome` (`approved`/`escalated`) | Refunds issued vs. escalated |
| `pronto.refund.amount.usd` | histogram | USD | `outcome` | Refund amounts — watch the $50 boundary |
| `pronto.escalation.total` | counter | escalations | `reason` (`over_50`/`legal`/`safety`/`privacy`/`other`) | Human handoffs by reason |

## Quality (online)

| Metric | Type | Unit | Labels | Definition |
|---|---|---|---|---|
| **`agent.quality.signal`** | counter | events | `version`, `signal`, `source` | `resolved` / `escalated` / `abandoned`; `source` ∈ `user`, `llm_judge` |
| `agent.quality.score` | histogram | score (0–1) | `version`, `judge` | Numeric quality score from your Week 2 judges |
| `agent.eval.production_pass_rate` | gauge | ratio (0–1) | `version`, `suite` | Pass rate of production traces re-run through the eval suite |

## Guardrails / Safety

| Metric | Type | Unit | Labels | Definition |
|---|---|---|---|---|
| `agent.guardrail.checks.total` | counter | checks | `policy.id`, `stage` | Guardrail evaluations (your Week 3 guardrails) |
| `agent.guardrail.blocked.total` | counter | events | `policy.id` | Blocks — prompt injections stopped, PII leaks stopped |

## Drift indicators (computed; surface in dashboards and the canary)

| Indicator | Source metrics | Why it matters for Pronto |
|---|---|---|
| Tokens-per-run trend | `tokens.input + tokens.output` ÷ `runs.total` | Rising = prompt drift or history bloat |
| Tool-calls-per-run trend | `tool.calls.total` ÷ `runs.total` | Rising = planner inefficiency, looping on order lookup |
| Escalation-rate trend | `pronto.escalation.total` ÷ `runs.total` | Rising = the agent is getting less autonomous — or attacks are rising |
| Over-$50 auto-approval rate | `pronto.refund.issued.total{outcome=approved}` over $50 | Must stay at **zero** — any non-zero value is a policy breach |
| Cost-per-success | `cost.usd` ÷ (`runs.total - runs.failed`) | Unit economics of a support conversation |
| Quality-by-version delta | `quality.signal{resolved}` per `version` | Regression detector across deploys |

## Naming and unit rules

- **All durations** in milliseconds, suffix `.duration`.
- **All money** in `USD`.
- **All ratios** as a 0–1 gauge, not a percentage.
- **All counters** monotonic with `.total` suffix.
- **All histograms** suffix `.duration`, `.count`, or `.score`.

## When to add a new metric

1. **Is there a question this answers that no existing metric does?** If no, don't add it.
2. **Is the cardinality bounded?** `tool.name` has 4 values — fine. A label with
   unbounded values (raw order IDs) is not.
3. **Will somebody alert or chart on it?** If neither, skip — it's noise.

A small, used catalog beats a big, ignored one. Start with the bolded ten.
