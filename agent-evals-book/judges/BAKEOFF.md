# Judge bake-off results

Model names and prices change quickly, so this file holds dated, measured results instead of recommendations (Chapter 10). Rerun the bake-off every quarter and whenever a candidate releases a new version.

## How to run it

1. Shortlist three candidates: large, mid-size, and small, from a different family than your agent's where you can.
2. Run each on the same expert-labeled calibration set (Chapter 7), one criterion at a time.
3. Compute TPR and TNR per criterion (`evals/stats.py`), and cost per 1,000 verdicts.
4. Call `judges.bakeoff.choose_judge` with the targets for the criterion's risk tier (Appendix F).

## Results

| Date | Criterion | Risk tier | Candidate (exact model version) | TPR | TNR | $ / 1,000 verdicts | p95 latency | Chosen |
|---|---|---|---|---|---|---|---|---|
| YYYY-MM-DD | | | | | | | | |
