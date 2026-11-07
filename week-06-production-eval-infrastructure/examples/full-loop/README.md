# Full loop, Stage 3: offline eval

Worked example for the Week 6 capstone. Stage 3 runs the canonical Pronto
agent over 8 gold-set cases and scores it in Braintrust. Stage 4 (online
evals) stays a walkthrough from the plan; this folder holds Stage 3 only.

## Run it

From the repo root:

```bash
pip install braintrust openai
python3 week-06-production-eval-infrastructure/examples/full-loop/offline_eval.py
```

Keys (`.env` in the repo root, or exported): `BRAINTRUST_API_KEY` and
`NEATLOGS_LLM_KEY`. The agent's generation and the judge calls both go
through the Neatlogs gateway, so the $25 gateway credit pays for the run.
Braintrust still receives the traces (project `pronto`).

The run uploads an experiment to the `pronto-full-loop-stage3` project and
prints a per-case and per-category summary. Open the experiment link it
prints and walk the class through it.

## The 8 cases

Read from `datasets/pronto-eval-gold.csv` by ID at runtime; the CSV is the
single source of truth. They cover the six demo threads from the full-loop
plan:

| Category | Thread | Gold ID (short) |
|---|---|---|
| order_status | normal order lookup | d191fe4e |
| order_status | multi-turn order lookup | 54db9aca |
| refund_request | refund under $50 (spoiled strawberries, $12) | 51fa4434 |
| refund_request | multi-turn delivery-fee refund (75 min late) | e6dabb90 |
| refund_request | $85 refund escalation | b8acf2df |
| adversarial | prompt injection (RefundBot, $150) | 00a2cf49 |
| adversarial | neighbor data-leak probe | 10b52369 |
| adversarial | $90 refund waiver attempt | 84852e5e |

## How it is scored

- **Judge** (Week 2 pattern): one binary PASS/FAIL judge, rubric prompt,
  gpt-4o-mini, grading the agent's reply against the gold `expected`
  behavior. The Week 2 starter's rubrics are assignment TODOs, so the
  rubric lives inline in the script, written from the starter's
  policy_adherence and escalation_correctness descriptions plus the
  Pronto policy bible.
- **Three code scorers** (deterministic, no model): no refund over $50
  approved; escalation correctness (escalate exactly when the expected
  behavior escalates); no other customer's data (the reply must not contain
  an order ID that was not in the input). All three are narrow by design;
  their limits are noted in the code comments.

## Reading the output

Each case prints its judge verdict and reason, its three code scores, and
its Stage 2 `root_span_id`. Find that span in the Braintrust `pronto`
project to show the class the original trace the case was harvested from.
The run itself also re-traces every turn into `pronto`.

## Known limitation: golden-set rot

The gold set's order IDs (`PRN-84xxx`) do not exist in the agent's demo
data (`DEMO_ORDERS` holds only `PRN-10421/22/23`). Lookup cases will
therefore show the agent correctly reporting "not found" while the
expected reply assumes the order exists. That is the eval catching drift
between the dataset and the system under test, and it is a genuine Week 6
teaching point. Do not "fix" it by rewriting the inputs; re-harvest the
gold set or extend `DEMO_ORDERS` instead.

## Out of scope (by design)

No new 40-case harvest, no Neatlogs branch in the agent, no Braintrust
dataset versioning beyond the CSV subset, and no Stage 4. Two demo threads
from the plan are not in the gold set at all (the wife's-order over-block
and the step-limit long chat); teach those two as walkthrough only, or add
2 harvested cases from Week 1 inputs and Week 3 attack material.
