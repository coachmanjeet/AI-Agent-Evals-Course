# Ingestion fidelity

## The problem in one sentence
Before your agent can reason about a photo, a PDF, or an audio clip, your
pipeline has to *ingest* it — and ingestion fails silently more often than
you'd think.

## Pronto example
A customer uploads a photo of a receipt for a missing-item claim. The OCR
reads the total as $84.50 instead of $34.50. Every downstream check —
refund amount, policy lookup, the agent's apology — is now wrong, and every
downstream evaluator scores the agent on corrupted input. You debug the agent
for a week before realizing the parser was the culprit.

## The method
Evaluate the ingestion step *separately*, against the source — not against
extracted text.

- **What you grade:** did the pipeline faithfully extract content from the
  uploaded source? Items, quantities, prices, dates, damage visible.
- **What you compare against:** the source images/audio themselves, via human
  labels. Never grade ingestion by comparing extracted text to extracted text.
- **Why it gets the strictest bar:** ingestion failures cascade. One bad parse
  poisons every downstream evaluator at once, so this judge needs kappa ≥ 0.85
  before it gates anything (vs 0.80 for other evaluators).

## What to measure
- **Extraction accuracy** — key fields correct (item, quantity, price).
- **Omission rate** — content present in the source but missing from extraction.
- **Hallucination rate** — content in the extraction with no source support.
- **Canary** — a small fixed set of tricky sources (crumpled receipts, blurry
  photos, accented audio) run on every parser change.

## The rule that matters
Recalibrate this evaluator quarterly **and after every parser/OCR/ASR update**.
A parser upgrade is an ingestion behavior change — treat it like a model swap.
