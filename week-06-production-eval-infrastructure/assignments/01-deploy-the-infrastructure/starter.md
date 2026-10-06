# Deploy-the-infrastructure checklist

Copy to `deploy.md` and work through it.

## 1. PR check (fast subset)

- [ ] Workflow file: `.github/workflows/eval-gate.yml` (start from the repo skeleton)
- [ ] Fast suite defined: (list the evals — e.g. 3 judges on 20 inputs + guardrail spot-check)
- [ ] Runs in under 10 minutes (measure it)
- [ ] Secrets configured: `OPENAI_API_KEY`, `LANGSMITH_API_KEY` (repo Settings → Secrets)
- [ ] Test: open a PR that breaks a known eval — the gate blocks it (`gate_demo.md`)

## 2. Nightly regression (full suite)

- [ ] Cron schedule set (e.g. `0 6 * * *` UTC)
- [ ] Full suite: golden set v1 + RAGAS + trajectory evals + guardrail suite
- [ ] Results written to `reports/` (or LangSmith) with date stamps
- [ ] Failure alert configured (where does the alert go?)

## 3. Gating policy

| Metric | Blocking or logged? | Threshold | Why this choice |
|--------|---------------------|-----------|-----------------|
| safety (guardrail catch rate) | blocking | | |
| correctness (judge pass rate) | blocking | | |
| latency p95 | logged | | |
| cost per task | logged | | |

Rule of thumb: block on safety and correctness; log the rest. Every blocking
metric needs an owner who gets paged when it fails.

## 4. Production monitoring

- **Online signals:** (e.g. sampled judge scores, tool-error rate, p95 latency)
- **Traffic sampling:** ___% of traffic judged (and what it costs — Week 1 cost metrics)
- **Alerting policy:** pages on ___; waits for morning on ___

## 5. Drift canary

- **Canary set:** (fixed inputs, pinned — reuse golden set v1 subset)
- **Schedule:** (e.g. hourly, daily)
- **Baseline:** (scores recorded on ___)
- **Alert threshold:** (e.g. faithfulness drops > 5pp vs baseline)
- **Drift type watched:** data / concept / prompt-model (pick, and say why)
