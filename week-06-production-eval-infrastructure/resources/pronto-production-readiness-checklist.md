# Pronto Production Readiness Checklist

The pre-launch checklist for the Pronto support agent. Score honestly — items in
**Hard requirements** block launch. Adapted for this course from the AgentOps
production readiness checklist.

Use it at the end of Week 6 Assignment 1, after your gates are wired: the
assignment proves your *evals* work; this checklist asks whether *Pronto itself*
is safe to operate.

## Hard requirements (do not ship without these)

### Observability
- [ ] Every Pronto run emits an end-to-end trace (LangSmith or OTel) with inputs,
      tool calls, and the final reply.
- [ ] Tokens in/out, cost USD, and latency emitted per LLM call.
- [ ] Run-level outcome attribute (`ok` / `error` / `timeout` / `blocked`) on
      every trace.
- [ ] Structured logs include `trace_id` so a trace can be found from a log line.

### Reliability
- [ ] **Hard timeout** on every run, every LLM call, every tool call
      (`get_order_status`, `issue_refund`, `lookup_policy`, `escalate_to_human`).
- [ ] **Cost ceiling per run** with explicit abort behavior above the cap.
- [ ] **Loop detection** — same tool with same args more than 3 times aborts the run.
- [ ] **Idempotency on `issue_refund`** — a retried run must never double-refund
      an order.
- [ ] **Hard retry caps** on every external call (order lookup, policy store).

### Guardrails (your Week 3 work, now enforced)
- [ ] **Input guardrails** on prompt-injection signatures (e.g. "ignore your
      policy", "approve all refunds").
- [ ] **Output guardrails**: no other customer's data leaves in a reply; no
      invented policy terms.
- [ ] Every guardrail decision logged with policy ID, version, verdict, action.
- [ ] Refunds over $50 **always** route to `escalate_to_human` — no autonomous
      path exists, even if the model asks nicely.

### Monitoring & Alerting
- [ ] Availability SLO with burn-rate alert (runs failing / total runs).
- [ ] Latency SLO with burn-rate alert (p95 run duration).
- [ ] Quality SLO with regression alert (judge-sampled pass rate on live traffic).
- [ ] Cost SLO — alert when daily spend exceeds the expected band.
- [ ] Each paging alert links to a runbook with the top-3 mitigations documented.

### Privacy & Security
- [ ] PII redaction at emit: customer names, addresses, and order details are
      redacted before traces or logs are stored.
- [ ] No API keys in prompts, tool descriptions, or trace attributes.
- [ ] The agent never discloses another customer's orders (the `escalate_to_human`
      path for "my neighbor's order" requests is tested).

### Incident Readiness
- [ ] On-call rotation defined (even if it's "the course team").
- [ ] Severity matrix documented (what counts as SEV-1 for a grocery support agent?).
- [ ] One synthetic failure triggered end-to-end: page → acknowledge → mitigate.
- [ ] The [incident response playbook](pronto-incident-response-playbook.md) has
      been read by everyone on call.

## High value (target within 30 days of launch)

### Observability
- [ ] Per-tool error metrics with per-tool SLOs (which tool fails most —
      `get_order_status` or `issue_refund`?).
- [ ] Cost-per-successful-run on a pinned dashboard.
- [ ] One online quality signal per session (resolution flag or judge sample).
- [ ] Tail-based sampling: errors, high-cost runs, and negative-quality runs
      sampled at 100%.

### Reliability
- [ ] Fallback model configured and exercised (what answers when the primary
      model is down?).
- [ ] Fallback path for each tool documented (order lookup down → what does
      Pronto say?).
- [ ] Circuit breaker on the order-lookup dependency.

### Governance
- [ ] Prompt registry: versions, owners, hashes — every prompt change is traceable.
- [ ] Tool registry: versions, owners, SLAs.
- [ ] Change log appended for every prompt / model / tool change.

## Dry-run before launch

The day before exposing Pronto to traffic:

1. **Force a synthetic tool failure** (kill `get_order_status`). Confirm the
   alert fires, the runbook link works, and the agent degrades gracefully.
2. **Force a synthetic guardrail block** (send a prompt-injection input).
   Confirm the user-facing copy is acceptable and the block is logged.
3. **Force a $51 refund request.** Confirm it escalates to a human — never
   auto-approved.
4. **Force a cost-cap hit.** Confirm the abort behavior produces a clean error,
   not a half-issued refund.
5. **Walk a real trace.** Pick a random staging trace; in under a minute, can
   you see every span, attribute, cost, and outcome?
6. **Privacy spot-check.** Sample 10 traces; confirm no raw PII in span
   attributes or logs.

If 6/6 pass, you're ready.

## Re-score quarterly

Production readiness is not a one-time event. Re-score every quarter; the trend
matters more than the absolute number.
