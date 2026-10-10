# Cross-modal consistency

## The problem in one sentence
When an agent produces output in more than one modality — or consumes input in
one modality and answers in another — the two can quietly disagree, and
text-only evals will never catch it.

## Pronto example
A customer uploads a photo of a smashed yogurt container and writes "my yogurt
arrived destroyed, refund me." The agent replies: "I can see the yogurt cup is
dented. Refund approved." But the photo shows the seal is intact and the cup is
fine — the damage is to the *box it shipped in*. The text sounds helpful. It
contradicts the photo. A text-only judge scores it 5/5.

## The method: claim-by-claim comparison
1. Extract the key claims from the primary output (e.g., the agent's text).
2. For each claim, find the corresponding element in the secondary modality
   (e.g., the photo, via a structured visual description).
3. Score each pair: consistent or not — and if not, how bad.

## Severity: central vs peripheral
- **Central** — a primary finding, main conclusion, or headline claim
  contradicts the other modality. Example: "the seal is broken" vs an intact
  seal in the photo.
- **Peripheral** — a supporting detail or example is off. Example: "the blue
  box" vs a white box.
- **n/a** — the topic appears in only one modality. Absence is *not* a
  contradiction.

**The rule that matters:** a central contradiction is a zero-tolerance rollback
trigger. Not "investigate soon." Roll back. Peripheral contradictions get
flagged and investigated within 24 hours.

## Compact judge prompt (adapt freely)
```
You check whether the agent's text claims match what is visible in the
customer's photo. You receive: (1) the agent's claims, (2) a structured
description of the photo.

For each claim, return: the claim, the matching photo element (or "none"),
consistent true/false, severity central/peripheral/na, and one line of
reasoning.

Rules:
- Same claim in different words = consistent.
- "X" vs "not X", or conflicting values for the same item = inconsistent.
- A topic missing from one side is NOT a contradiction.
- If any central contradiction exists, set central_contradiction_present: true.
```

## Before deploying this judge
- Collect 100–150 human-labeled pairs; measure Cohen's kappa on a validation
  split. Ship only at kappa ≥ 0.80.
- Include 10 known central-contradiction cases — the judge must catch 100%.
- Recalibrate monthly; kappa below 0.70 in monitoring means the judge is
  retired until fixed.
