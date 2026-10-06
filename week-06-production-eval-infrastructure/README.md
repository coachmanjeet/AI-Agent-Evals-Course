# Week 6 — Production Eval Infrastructure

Everything so far was practice. This week the evals move into production:
gates in CI, monitoring online, and an operating cadence with a named owner.

## What we covered

- Eval checkpoints: PR check, nightly regression, pre-launch gate
- Eval gates in GitHub Actions (this repo has a starter: `.github/workflows/eval-gate.yml`)
- Gating policy: blocking vs. logged metrics
- Fast PR subsets vs. full regression suites
- Online evaluation signals; traffic sampling for eval cost control
- Alerting policy: what pages, what waits for morning
- The drift taxonomy: data drift, concept drift, prompt/model drift
- Scheduled canary evaluation
- Compounding eval: the eval flywheel, from production failures to regression tests
- Eval-driven model routing and cost optimization
- Ownership and operating cadence

## Key takeaways

1. **Gate the merge, not just the deploy.** A PR check that runs the fast eval subset catches regressions when they're cheapest to fix.
2. **Blocking vs. logged is a policy decision.** Block on safety and correctness; log (don't block) on exploratory metrics — or every team learns to bypass the gate.
3. **Production is a new eval surface.** Drift, canaries, and traffic sampling are evals too — they just run on live data.
4. **Evals compound.** Every incident becomes a regression test; every regression test makes the next incident cheaper. That flywheel needs an owner and a cadence, or it stops.

## Links

- GitHub Actions docs — workflows, schedules: https://docs.github.com/actions
- LangSmith docs — monitoring and automations: https://docs.langchain.com/langsmith

## In this folder

- `examples/` — worked examples from the live session (added after the session)
- `assignments/01-deploy-the-infrastructure/` — GitHub Actions gates + monitoring + canary
- `assignments/02-operate-and-document/` — flywheel cycle doc, cost-routing recommendation, ownership doc
