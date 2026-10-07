# Assignment 2 — Diagnose and compare

## Goal

Run a full diagnose-and-fix cycle: find what breaks, try a fix, and A/B test it with per-metric deltas before deciding to ship.

## Steps

1. Pick your worst failure mode from Week 1's taxonomy (the one your judges now measure reliably).
2. Diagnose: pull 10 failing traces, find the shared root cause, write it down in one paragraph.
3. Fix: change ONE thing — a prompt variant, a tool description, a routing rule. Not three things.
4. A/B test: run the same input set through variant A (baseline) and variant B (fix). Score both with your Week 2 judges, per metric.
5. Report per-metric deltas (e.g. tool-call accuracy +12pp, escalation correctness −2pp).
6. Write the ship/no-ship decision (`starter.md` template): verdict, the numbers behind it, and what would change your mind.

## Acceptance criteria

- [ ] One-paragraph root-cause diagnosis grounded in 10 traces
- [ ] Exactly one change between A and B (documented)
- [ ] Per-metric deltas reported for all 3 judges
- [ ] Ship/no-ship decision with numeric thresholds stated upfront (e.g. "ship if tool-call accuracy ≥ 90% and no metric regresses > 3pp")
- [ ] "What would change my mind" section filled in

## Starter

`starter.md` — the A/B report + ship/no-ship template.
