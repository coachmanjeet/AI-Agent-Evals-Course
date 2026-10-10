# Eval contracts

## The idea in one sentence
Stop thinking "we have some evals." Start thinking "this feature has five
contracts, each with a pass bar" — and nothing ships until every contract
passes.

## What a contract is
A contract names one quality promise, the evaluator that checks it, and the
number that gates deployment. Example contracts for a photo-refund feature:

| Contract | Promise | Evaluator | CI gate | Monitoring floor |
|---|---|---|---|---|
| Ingestion fidelity | The photo was read correctly | Ingestion judge | kappa ≥ 0.85 | kappa ≥ 0.75 |
| Faithfulness | The reply sticks to the photo + policy | Faithfulness judge | kappa ≥ 0.80 | kappa ≥ 0.70 |
| Factuality | Refund math and policy cites are right | Factuality checks | kappa ≥ 0.80 | kappa ≥ 0.70 |
| Cross-modal consistency | Text reply matches the photo | Consistency judge | kappa ≥ 0.80 | kappa ≥ 0.70 |
| Output quality | (Audio/video: natural, glitch-free) | Modality judge | kappa ≥ 0.80 | kappa ≥ 0.70 |

Kappa here is Cohen's kappa: agreement between your judge and human labels,
corrected for chance. It answers "does this judge grade like my team does?"

## The rules that make contracts work
1. **Two bars, not one.** The CI gate bar (ship/no-ship) is higher than the
   monitoring bar (healthy/degraded). A judge between the two stays live but
   gets recalibrated.
2. **Recalibrate on a schedule** — monthly for most judges, quarterly for
   ingestion — plus after any upstream change (new parser, new TTS voice, new
   model version).
3. **Freeze judge versions.** Tag the prompt version; never pin "latest." A
   silently-updated judge is a silently-moved goalpost.
4. **Validate before deploying the judge itself:** 60/20/20 build/validate/
   holdout split on human labels, slice analysis per modality, and a
   sensitivity test with known failures the judge must catch at 100%.

## Why this upgrades Week 2 and Week 6
Week 2 teaches you to build a judge and calibrate it. Contracts answer the next
question: *when is the judge good enough to block a deploy?* Week 6 (production)
is where contracts live — they're the quality bars your CI gates and monitors
enforce.
