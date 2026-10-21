# Assignment 3 — Jev guardrail judge

## Goal

Replace the free-text LLM-judge guardrail from Assignment 2 with the real
thing: TypeSafe Jev, a decision model that never generates text — it picks
from choices you define and returns calibrated probabilities. Measure it on
the same three numbers (catch rate, over-block rate, cost/latency), then add
the fourth: a confidence threshold that routes uncertain cases to a human.
This is the Jev pattern from the IBM video made runnable: constrained
output → measured calibration → thresholds as code → human routing.

## Setup (one-time, ~5 min)

Braintrust ships built-in Jev — no TypeSafe account needed:

1. In Braintrust, go to **Settings → AI providers** and click **Enable Jev**
   (requires the Owners permission group, and built-in models must be
   allowed for your org). Usage draws down your org's model credits like
   any built-in model.
2. Go to **Scorers → Scorer → LLM judge** and pick **Jev** in the model
   picker. (Jev appears for scorers/classifiers only — not for prompts or
   playgrounds — because it takes no sampling parameters.)
3. Prefer your own key? Add TypeSafe as an AI provider at org or project
   scope instead, and `pip install typesafe-sdk`.

For the code parts below you will call Jev directly. If you use the
Braintrust built-in path for scoring, do the threshold-routing analysis
against the confidence/probabilities metadata Braintrust returns.

## Steps

1. **Define the safety question as choices.** In the Braintrust scorer
   editor, write the prompt (context + what each choice means) and set
   **Output type → Score**: e.g. `attack` → `1`, `benign` → `0`. Keep it
   to ONE focused question — Jev is built for "frequent, focused checks
   with a clear answer" (their docs' words). For broad or nuanced criteria
   like tone, a general LLM remains the better judge; say which of your
   guardrail questions qualify and which don't.
   - Side is a design decision (same as Assignment 2): an injection/jailbreak
     check goes INPUT-side; a leakage/PII check goes OUTPUT-side.
2. **Test 5 known cases in the UI** (the scorer's Run/Test panel): 3 attacks
   from Assignment 1, 2 legitimate edge cases. Refine the prompt until all
   5 decide correctly. Note Jev gives no chain-of-thought — the decision
   arrives directly, so prompt accordingly.
3. **Score the full 40-input set** with `starter.py`: for each input capture
   Jev's decision, its confidence, and the per-choice probabilities. Report
   **catch rate**, **over-block rate**, **review rate** (fraction you would
   route to a human — see step 5), and **latency** per check. Print a
   side-by-side table vs your Assignment 2 LLM-judge guardrail.
4. **Calibration check — don't assume, measure.** Bin Jev's confidence
   (e.g. 0.5–0.7, 0.7–0.9, 0.9–1.0) and plot predicted vs empirical accuracy
   on your 40 labels (a 3-bin reliability diagram). Is Jev calibrated on
   YOUR data? Report where it is over/under-confident. The video's claim —
   "when it says 80%, it's right 80% of the time" — is a hypothesis until
   your plot confirms it.
5. **Thresholds as code.** Implement the bands on Jev's attack
   probability: P(attack) ≥ 0.9 → auto-block; P(attack) ≤ 0.1 →
   auto-allow; between the two → human review queue. (Route on the
   per-choice probability, not on the confidence of whichever label won —
   for a binary choice that confidence never drops below 0.5, so a
   "low-confidence" band would never fire.) Compute the expected error
   rate on each auto band from your calibration data: false passes on the
   allow band, false blocks on the block band. Then the cost question: a
   false pass ships an attack, a false block annoys a customer — make
   false passes 10× costlier and move the bars. Where do they land, and
   what happens to your review rate?
6. **Ship/no-ship verdict** with upfront numeric thresholds (e.g. "ship if
   catch ≥ 90% AND over-block ≤ 5% AND review rate ≤ 20%"), plus the HITL
   flow for the review band: what the reviewer sees (input text, Jev's
   probabilities per choice, the agent's planned action) and the SLA.

## Acceptance criteria

- [ ] Jev scorer created in Braintrust (built-in Jev enabled) and passing 5/5 UI test cases
- [ ] 40-input test set scored through Jev: catch rate, over-block rate, review rate, latency reported
- [ ] Side-by-side comparison vs the Assignment 2 LLM-judge guardrail (same test set)
- [ ] 3-bin reliability diagram: Jev's confidence vs empirical accuracy, with a written read ("calibrated / overconfident / underconfident, and where")
- [ ] Thresholds implemented in code with the review band routed to a documented HITL flow
- [ ] Ship/no-ship verdict with upfront numeric thresholds

## Stretch: the honest gaps

1. **Who guards the guard?** Jev is still prompt-injectable (the video says
   so). An attacker input could try to flip the safety question itself.
   Sketch one defense that doesn't just move the problem one layer up.
2. **Cost at scale.** Jev is priced per decision, not per token. Estimate:
   10k agent turns/day × your guardrail's call pattern — what does Jev cost
   vs your Assignment 2 LLM judge? When does the hybrid (regex pre-filter +
   Jev only on suspicious) win?
3. **Where Jev doesn't belong.** Pick one of your Week 2 quality judges
   (e.g. tone/helpfulness) and argue in 3 sentences why Jev would be the
   wrong judge for it. This is the docs' caveat turned into judgment.

## Starter

`starter.py` — Jev guardrail skeleton, threshold routing, and the scoring
harness (extends Assignment 2's three numbers with review rate).
