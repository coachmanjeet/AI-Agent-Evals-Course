# Assignment 1 — Deploy the infrastructure

## Goal

Turn your Weeks 1–5 harness into production infrastructure: gates in CI, monitoring online, a canary watching for drift.

## Steps

1. Start from `.github/workflows/eval-gate.yml` at the repo root (a commented skeleton). Replace the placeholder commands with your real harness:
   - **PR check**: fast subset (your Week 2 judges + Week 3 guardrail spot-checks), gated on safety and correctness. Must finish in under 10 minutes.
   - **Nightly cron**: full regression suite (golden set v1, RAGAS metrics, trajectory evals). Results logged; failures alert.
2. Decide the **gating policy** and write it down: which metrics block a merge, which are logged-only, and why.
3. Deploy **production monitoring**: pick your online eval signals (e.g. judge-sampled outputs, tool-error rates, latency percentiles), set **traffic sampling** to control eval cost (e.g. judge 5% of traffic), and define the **alerting policy** (what pages vs. what waits).
4. Schedule a **drift canary**: a fixed input set re-run on a schedule, compared against baseline, alerting on drift (data, concept, or prompt/model).
5. Open a test PR that intentionally breaks something your evals catch. Watch the gate block it. (This is the most satisfying step of the course.)

## Acceptance criteria

- [ ] `eval-gate.yml` runs a real PR check (fast subset, < 10 min) and a nightly full regression
- [ ] Gating policy documented: blocking vs. logged metrics, with reasons
- [ ] Production monitoring defined: signals, sampling rate, alerting policy
- [ ] Drift canary scheduled with a documented alert threshold
- [ ] A deliberately-broken test PR is blocked by the gate (screenshot or log in `gate_demo.md`)

## Starter

`starter.md` — the deployment checklist and policy template.
