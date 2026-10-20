# Eval Plan Template

*Created by: Manjeet Singh*

Order of operations. You cannot name failure modes, write rubric anchors, or
set thresholds honestly until you have read real agent traces. Build the
prototype, run 50 cases, read every one, then fill this in.

## What it should have

- **Test Set/Scenario:** Representative examples: [brief description, e.g.
  "50 real support tickets across top 5 categories"]
- **Failure Scenario:** Edge cases / adversarial cases: [brief description]
- **Error Analysis:** linked spreadsheet (see note below)
- **Eval Methods:** Code, LLM, Code, Feedback
- **Rubric:** [e.g. 1–5 on accuracy, helpfulness, tone; binary safety check]
- **LLM-as-judge** for [dimensions]
- **Human Eval:** Who evaluates: [e.g. 2 PMs + 1 domain expert + 1 support
  lead]
- **Rule-based checks** for [policy, toxicity, PII leakage, etc.]
- **Eval Metrics:** AI Metrics and Business Metrics
- **Eval Gates:** Launch decision
- **Success thresholds** to move beyond prototype
  - e.g. "≥ 4.2/5 average human score on accuracy + helpfulness
- **Online Eval:** Post launch perf tracking via prod eval and monitoring.

> **Linked sheet (by reference):** the Error Analysis item above links to a
> Google Sheet, "Error Analysis":
> https://docs.google.com/spreadsheets/d/12R9UsqGgWUj4NfcZuZWHEAQW8BAAsxSblgrAYR9aITI/edit?gid=1986635191#gid=1986635191
> The sheet itself is not copied into the repo.

---

## 1. Dataset

Test Case Scenarios:

| Field | Agentforce Service Agent example |
| --- | --- |
| Sources | 50 anonymized production case transcripts across the top 3 Tier-1 types, plus 20 synthetic edge cases and 10 adversarial prompts |
| Synthetic generation | Metadata-seeded from Knowledge coverage gaps; Q&A pairs generated from policy docs; a few hand-written "provide sample, create more" variants |
| Frozen eval set | 40 cases locked at v1. Never tuned against. Re-cut only when the case mix genuinely changes |
| Dev set | The remaining 40. Iterate against these freely |
| Metadata per case | Case type, channel, customer tier, expected action, expected escalation (Y/N), ground-truth Knowledge article ID |
| PII handling | Names, emails, and order numbers tokenized before the set leaves production |

## 2. Failure modes — from error analysis

- Failure Scenario: Edge cases / adversarial cases: [brief description]
- Error Analysis: [linked Google Sheet — see the note at the top of this
  file]

This is the only block that is real work. Open 50 traces, read them end to
end, write down what actually went wrong in your own words, then group what
repeats. Do not start from a generic checklist of AI failures — you will
find the failures you expected and miss the ones that matter.

Read each trace through four layers:

- **Topic / routing** — did it pick the right topic? Did it escalate when it
  shouldn't have, or fail to when it should?
- **Retrieval** — was the right Knowledge article pulled? Is the answer
  actually grounded in it?
- **Action** — did it invoke the right action, with the right parameters, on
  the right record?
- **Response** — is the answer correct, complete, and on-brand for how this
  customer is feeling?

Frequency is what earns a row a gate. Severity is what decides whether that
gate is hard or soft.

**Worked example (Agentforce):**

| Failure mode | Layer | What it looked like | Freq | Sev |
| --- | --- | --- | --- | --- |
| States a return window not present in Knowledge | Retrieval | "You have 90 days" when policy says 30 | 4 / 50 | P0 |
| Initiates return on most recent order, not the one discussed | Action | Customer asks about a March order; agent returns the April item | 2 / 50 | P0 |
| Answers from a deprecated Knowledge article | Retrieval | Cites the 2023 policy article, still active in the data set | 6 / 50 | P1 |
| Fails to escalate a billing dispute | Topic | Attempts to resolve an explicitly out-of-scope case | 5 / 50 | P2 |
| Reads as scripted with frustrated customers | Response | Repeats policy verbatim right after the customer expresses anger | 9 / 50 | P3 |

## 3. How each failure mode gets measured

Pick the cheapest evaluator that reliably catches the failure. Code first.
LLM-as-judge second. Human last — humans are for things that need judgment,
not for things a regex catches for free.

**Worked example (Agentforce):**

| Failure mode | Evaluator | Metric |
| --- | --- | --- |
| Ungrounded policy claim | LLM-as-judge — groundedness against the retrieved article | % of responses with ≥ 1 unsupported claim |
| Wrong-order action | Code — assert action parameters match the expected order ID | Wrong-action rate |
| Deprecated article retrieved | Code — article ID checked against the active-version allowlist | Stale-retrieval rate |
| Missed escalation | Code — expected-escalation label vs. actual behavior | Escalation recall |
| Tone with frustrated customers | Human eval (see `human-evals-guide.md`), 0–3 rubric | Mean tone score on the 15-case frustration slice |

## 4. Gates

One table. Severity from block 2 sets the gate type. Hard = the pipeline
blocks the release. Soft = PM signs off in writing with a stated rationale.
Advisory = logged for the next iteration, no block.

**Worked example (Agentforce):**

| Metric | Threshold | Gate | Evaluator | Owner |
| --- | --- | --- | --- | --- |
| Ungrounded claim rate | 0% on frozen set | Hard | LLM-judge + human spot-check | PM |
| Wrong-action rate | 0% on frozen set | Hard | Code | Eng |
| Stale-retrieval rate | < 2% | Hard | Code | Eng |
| Escalation recall | ≥ 0.95 | Soft | Code | PM |
| p95 first token | < 3.0s | Soft | Performance logging | Eng |
| Mean tone score | ≥ 2.4 / 3 | Advisory | Human | PM |

## 5. After launch

- **Online sampling.** 2% of live sessions run daily through the
  groundedness judge. Alert if the ungrounded rate crosses 0.5%.
- **Regression cadence.** Re-run the frozen set monthly, and after every
  model, prompt, or Knowledge change. A drop greater than 2% on any
  hard-gate metric triggers a rollback review.
- **Feedback loop.** Every thumbs-down and every escalation-after-agent-
  attempt gets read weekly and coded. New failure modes earn a row in
  block 2; recurring ones earn a case in the dev set.
