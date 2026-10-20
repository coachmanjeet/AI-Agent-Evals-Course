# Human Evals Guide

**Human Eval Plan:** [AI Evals: Human Evaluation Template](https://docs.google.com/spreadsheets/d/1rTxaQwMee4sP-0Y2IbpcGUup__4StiqXryJ6SzB6VVQ/edit?usp=sharing) (linked Google Sheet)

## 1. What you're looking at

You'll see a customer service conversation handled by an AI agent, alongside
the Knowledge article the agent had access to. Score the agent's final
response.

Good looks like:

- Every factual claim about policy traces back to the provided Knowledge
  article
- The customer's actual question is answered — not a nearby one
- If an action was taken (return, plan change), it matches what the customer
  asked for
- Tone matches how the customer is feeling — brief and warm when they're
  frustrated, not a policy recital
- If it's out of scope, the agent says so and hands off rather than guessing

## 2. Rubric

Score each dimension 0–3.

| Dimension | 0 — Low | 1–2 — Mid | 3 — High | Weight | Hard gate |
| --- | --- | --- | --- | --- | --- |
| Groundedness | Claims contradict the article, or aren't in it at all | Mostly supported; one soft or unverifiable claim | Every claim traceable to the article | 0.40 | Yes |
| Task completion | Doesn't address what was asked | Answers partly; leaves a real gap | Fully resolves, or correctly escalates | 0.35 | No |
| Tone | Cold, scripted, or dismissive | Polite but generic | Warm and matched to the customer's state | 0.25 | No |

Weighted score = Σ (weight × score). A 0 on Groundedness fails the item
outright, whatever the total says.

## 3. Worked examples

Read these before you score anything. They will teach you more than the
anchors will.

| Case | Agent response (abridged) | Score | Why |
| --- | --- | --- | --- |
| PASS / Return window, March order | "Orders placed in March fall inside the 30-day window, which closed April 12. I can look at a store-credit exception if you'd like." | G3 · TC3 · T3 / = 3.00 | Grounded, complete, and offers a real next step |
| PASS / Billing dispute, out of scope | "That's a billing question I'm not able to resolve here — let me connect you to a specialist now." | G3 · TC3 · T3 / = 3.00 | Correct escalation counts as full task completion, not a failure |
| FAIL / Return window | "You have 90 days to return any item." | G0 · TC2 · T2 / = 1.20 | The article says 30 days. Groundedness 0 means an automatic fail |
| FAIL / Frustrated customer, order delayed twice | "Per our shipping policy, delivery estimates are not guaranteed." | G3 · TC1 · T0 / = 1.55 | Factually fine, but it doesn't help and it reads as dismissive |
| EDGE / Article is silent on the question | "I don't have that in my policy information — let me get someone who can confirm." | G3 · TC3 · T3 / = 3.00 | Saying "I don't know" and escalating is correct. Score it as a pass |

## 4. When you're not sure

- The article is silent on the question → the agent saying "I don't know"
  and escalating is a pass, not a failure.
- Response is correct but answers a different question → Task completion 1,
  not 3.
- The agent took an action the customer didn't ask for → Task completion 0,
  and flag the item.
- The agent is right but the Knowledge article itself is wrong → score
  against the article, add a bad source flag, and don't penalize the agent.
- Still unsure after 60 seconds → tag Needs adjudication and move on. Don't
  guess. Escalate to: [name].

## 5. Quality check

- Two raters on 20% of the set; single rater on the rest
- Target agreement: Cohen's κ ≥ 0.6 on Groundedness. Below that, we rewrite
  the anchors — we don't retrain the raters
- 1 in 10 items is a gold item with a known score. Raters below 80% on
  golds get re-onboarded
- Items with a disagreement of 2 points or more go to [name] for weekly
  adjudication

Comparing two agent versions rather than grading one? Skip the rubric. Show
both responses side by side and pick A / B / Tie, with an optional reason tag
(groundedness · completion · tone).

Owner: [name] | Version: v[ ] | Last updated: [YYYY-MM-DD] | Change log:
[link]
