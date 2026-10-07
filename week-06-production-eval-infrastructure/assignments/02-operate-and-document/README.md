# Assignment 2 — Operate and document

## Goal

Prove the eval flywheel turns: take one real incident through root cause → fix → regression test, then write the docs that keep the system healthy after the course ends.

## Steps

1. **Document one flywheel cycle** (`starter.md` template): pick a real incident — a production failure, a canary alert, or a red-team find from Week 3. Write it up end-to-end: incident → root cause → fix → new regression test added to the suite. The regression test is the deliverable; the write-up is the proof.
2. **Produce an eval-driven cost-routing recommendation**: using your cost metrics (Week 1) and quality scores (Weeks 2/4), recommend where a cheaper model (or smaller retrieval top-k, or fewer retries) can be routed without breaching quality thresholds. Do it as a Pareto analysis with `cost_model.py` (stdlib only — the demo agent makes no real model calls, so tool calls are priced with token estimates × a per-1K-token price; swap in your measured token counts when you have them):
   - Score 3 Pronto configurations on quality (criteria checks, or your Week 2 judge) vs. cost per 1K requests: `standard` (as shipped), `verbose` (extra retrieval — same answers, higher cost), `cheap` (no policy lookup — cheaper, wrong on policy questions). Adapt them to your real variants.
   - Read the Pareto frontier from the printed table: drop any config another beats on both cost and quality.
   - Ship the cheapest frontier config that holds your quality bar (e.g. within 2pp of baseline). Write it up in `cost_routing.md`: the frontier table, the dropped configs and why, projected savings vs. measured quality delta.
3. **Write the ownership doc**: who owns the evals, what the operating cadence is (weekly review? on-call rotation?), what happens when a gate fails at 2 AM, and when thresholds get revisited.

## Acceptance criteria

- [ ] `flywheel_cycle.md`: incident → root cause → fix → regression test, all four present
- [ ] The regression test actually exists in the suite and runs in CI
- [ ] `cost_routing.md`: Pareto table for 3+ configs; dominated configs named and dropped with reasons
- [ ] Ship recommendation: cheapest frontier config holding the quality bar, with projected savings and measured quality delta
- [ ] `ownership.md`: named owner, cadence, 2-AM playbook, threshold review schedule

## Starter

`starter.md` — templates for all three docs.
