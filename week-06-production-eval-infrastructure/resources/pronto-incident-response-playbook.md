# Pronto Incident Response Playbook

The on-call runbook for the Pronto support agent. Each scenario has documented
steps. Adapted for this course from the AgentOps incident response playbook.

> The on-call who reads this at 3 AM hasn't seen this incident before. Write
> for that reader.

## Universal first 5 minutes

For any incident, regardless of severity:

1. **Acknowledge the alert** immediately so it stops paging.
2. **Open a channel** — `#incident-<id>` — and post the alert summary.
3. **Determine severity** from the severity matrix (Week 6 Assignment 2's
   ownership doc) and the customer impact.
4. **Identify recent changes** — last 24h prompt deploys, model swaps, policy
   doc edits, tool changes.
5. **Decide: investigate or mitigate first?** If customers are actively impacted
   (SEV-1/2), mitigate first; investigate after.

## Scenario A — Refund runaway

**Symptom:** `pronto.refund.issued.total` or `pronto.refund.amount.usd` spiked;
a single customer (or many) received repeated or oversized refunds.

**Mitigate:**
1. Identify the affected orders from the dashboard.
2. Pause autonomous refunds: force all refunds through `escalate_to_human`
   until the cause is found.
3. If a single cause (one prompt version, one model): roll back.

**Investigate:**
- Traces: is the agent looping on `issue_refund` (same order, same args)?
- Did the >$50 escalation path get bypassed? Check
  `pronto.refund.issued.total{outcome=approved}` over $50 — must be zero.
- Was idempotency on `issue_refund` actually working, or did retries
  double-refund?

**RCA must answer:** what caused the refund shape change, and why didn't the
$50 policy or the cost ceiling catch it?

## Scenario B — Quality regression (wrong refunds / wrong answers)

**Symptom:** `agent.quality.signal{resolved}` dropped > 5pp vs trailing 7d baseline.

**Mitigate:**
1. Confirm it's not noise — absolute counts, not rate, on small populations.
2. If a recent deploy: roll back the prompt or model version.
3. If no recent deploy: check upstream — model behavior change, policy doc edit.

**Investigate:**
- Cluster recent failed traces by your Week 1 failure taxonomy — which code
  is dominant?
- Does the eval suite reproduce it? If not, why not? Add the case.

**RCA must answer:** which failure mode is dominant, what introduced it, and
how does the eval suite catch it next time?

## Scenario C — Model provider outage / degradation

**Symptom:** rising `agent.llm.calls.failed` rate; customers getting errors or
timeouts.

**Mitigate:**
1. Confirm via the provider's status page.
2. Engage the fallback model; verify it answers Pronto-style (policy-bible
   compliant).
3. If no fallback: throttle traffic; queue complex cases for humans.

**Investigate (post-incident):**
- Did the fallback engage as fast as designed?
- Did any downstream cascade — tool errors caused by LLM-side timeouts?

**RCA must answer:** how did the fallback perform on quality, not just
availability? Do we need a second fallback?

## Scenario D — Order-lookup failure

**Symptom:** `agent.tool.errors.total{tool.name=get_order_status}` spiking;
Pronto can't answer "where is my order?".

**Mitigate:**
1. Check the order system's status; engage its owning team.
2. Agent degrades gracefully: "I can't reach order tracking right now" beats a
   hallucinated status. Verify it isn't inventing ETAs.

**Investigate:**
- Was retry / circuit-breaker behavior correct?
- Did the agent abandon promptly, or loop on the failing tool?

**RCA must answer:** what's the order system's reliability story, and does
Pronto need a cached-status fallback?

## Scenario E — Prompt-injection wave

**Symptom:** `agent.guardrail.blocked.total` spiked; or customers report the
agent doing something odd ("it approved my $200 refund!").

**Mitigate:**
1. Determine: real attack wave or false-positive regression from a guardrail
   change?
2. If attack: tighten input guardrails on the observed signature (your Week 3
   work); sample 20 blocks for the legitimate-vs-malicious breakdown.
3. If false-positive: roll back the guardrail or prompt change.

**Investigate:**
- Is the bypass signature in your Week 3 red-team set? If not, add it.
- Was any customer data exposed in the affected runs? Audit them.

**RCA must answer:** how do we systematically prevent this attack class — not
just this signature?

## Scenario F — Latency regression

**Symptom:** p95 `agent.run.duration` exceeded SLO; customers waiting.

**Mitigate:**
1. Which step grew — LLM, tool, or overall? Check `agent.tool.duration` per
   tool and `agent.llm.duration`.
2. If a tool: see Scenario D. If LLM: provider status, or route to a faster
   model.

**Investigate:**
- Histogram vs prior week; split by prompt version.

**RCA must answer:** what change introduced the latency, and what pre-production
check catches it next time?

## Scenario G — Trace silence

**Symptom:** `agent.runs.total` dropped sharply with no matching traffic drop.

**Mitigate:**
1. Is the trace pipeline broken (collector, sampling config) or is Pronto
   actually down? Cross-check with raw provider billing.
2. If pipeline: fix ingestion. If runtime: crash loop? Auth failure?

**RCA must answer:** observability noise or real outage — and build the missing
alarm either way.

## Comms templates

### Internal — incident open
```
SEV-<n> :: pronto :: <one-line summary>
Impact: <customers / orders / scope>
Sample failing trace: <link>
Channel: #incident-<id>
```

### Status page — investigating
```
We're investigating an issue affecting Pronto support responses.
Engineering is engaged; next update within 30 minutes.
```

### Status page — resolved
```
The issue affecting Pronto is resolved. <Brief root cause>.
```

## After the incident

1. Within 48 hours: timeline drafted.
2. Within 1 week: postmortem using the [RCA template](pronto-rca-template.md).
3. Within 2 weeks: review; action items have owners and deadlines.
4. 30 days later: action-item completion check.
5. Eval suite: at least one new test case from the incident (the flywheel).
6. Runbook: this playbook gets a new scenario section if this one was novel.

## Anti-patterns

- **Mitigating without acknowledging the alert.** Pages everyone again.
- **Mitigating without a channel.** No timeline, no scribe, no postmortem.
- **Skipping the RCA.** Same incident next month.
- **Action items without owners.** Same outcome.
