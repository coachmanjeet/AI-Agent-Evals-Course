# Assignment 2 — Operate and document

## Goal

Prove the eval flywheel turns: take one real incident through root cause → fix → regression test, then write the docs that keep the system healthy after the course ends.

## Steps

1. **Document one flywheel cycle** (`starter.md` template): pick a real incident — a production failure, a canary alert, or a red-team find from Week 3. Write it up end-to-end: incident → root cause → fix → new regression test added to the suite. The regression test is the deliverable; the write-up is the proof.
2. **Produce an eval-driven cost-routing recommendation**: using your cost metrics (Week 1) and quality scores (Weeks 2/4), recommend where a cheaper model (or smaller retrieval top-k, or fewer retries) can be routed without breaching quality thresholds. Show the math: projected savings vs. measured quality delta.
3. **Write the ownership doc**: who owns the evals, what the operating cadence is (weekly review? on-call rotation?), what happens when a gate fails at 2 AM, and when thresholds get revisited.

## Acceptance criteria

- [ ] `flywheel_cycle.md`: incident → root cause → fix → regression test, all four present
- [ ] The regression test actually exists in the suite and runs in CI
- [ ] `cost_routing.md`: recommendation with projected savings and measured quality delta
- [ ] `ownership.md`: named owner, cadence, 2-AM playbook, threshold review schedule

## Starter

`starter.md` — templates for all three docs.
