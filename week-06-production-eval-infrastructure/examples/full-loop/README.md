# Full loop, Stage 3: offline eval

Worked example for the Week 6 capstone. Stage 3 runs the canonical Pronto
agent over 10 gold-set cases and scores it in Braintrust. The same folder
also holds the step-5 self-correction wrapper, the before/after improvement
runner, and the Stage 4 walkthrough (see below).

## Run it

From the repo root:

```bash
pip install braintrust openai
python3 week-06-production-eval-infrastructure/examples/full-loop/offline_eval.py
```

Keys (`.env` in the repo root, or exported): `BRAINTRUST_API_KEY` and
`NEATLOGS_LLM_KEY` (or `OPENAI_API_KEY` when the gateway key is absent).
Model calls go through the Neatlogs gateway when its key is set, so the
$25 gateway credit pays for the run; otherwise they go to OpenAI directly
on `OPENAI_API_KEY`. Braintrust still receives the traces (project
`pronto`).

The run uploads an experiment to the `pronto-full-loop-stage3` project and
prints a per-case and per-category summary. Open the experiment link it
prints and walk the class through it.

## The 10 cases

Read from `datasets/pronto-eval-gold.csv` by ID at runtime; the CSV is the
single source of truth. They cover all eight demo threads from the full-loop
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
| order_status | wife's-order over-block | fe1b9486 |
| warranty_claim | step-limit long chat | cedb52c4 |

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
dataset versioning beyond the CSV subset, and no Stage 4. The two demo
threads added here (the wife's-order over-block and the step-limit long
chat) are now in the gold set as rows 49 and 50: the wife's-order input is
harvested verbatim from the Week 3 guardrail material, and the step-limit
input is built from teaching trace conv-tool-04 with constructed middle
turns. The step-limit case is a probe, not a guaranteed fail: the judge is
the discriminating scorer for it, since the narrow escalation scorer counts
any escalation as a match and both the correct behavior and the failure
mode escalate, for different reasons.

## The rest of the loop (same folder)

- **Step 5, self-correction:** `self_correct.py` wraps the agent in a
  verify-before-act loop. After a turn, three deterministic checks run
  (refund over $50 approved, unjustified escalation, leaked order ID). On
  a violation the agent re-drafts once with the violation named; still
  failing means escalate to a human. It prints the correction rate and the
  new-error rate. Unit tests in `test_self_correct.py` run key-free.
- **Step 4, improve and optimize:** `improve_demo.py` runs the same 10
  cases twice, base agent vs self-correcting agent, and prints the
  before/after table, the delta, and the decision-gate reading (SHIP, SHIP
  WITH CONDITIONS, NO-SHIP) against the Week 6 README targets. Unit tests
  in `test_improve_demo.py` run key-free.
- **Stage 4, online evals:** `STAGE4-WALKTHROUGH.md` is a walkthrough, not
  a live build. It covers the Braintrust online scorer, one Neatlogs
  Detection, one Neatlogs review campaign, and the close-the-loop procedure
  (online failure becomes a new gold row, re-run the offline eval, the
  decision gate reads the delta). Paths that could not be verified from a
  live account are marked "verify in class".

All three mains take keys the same way as Stage 3: `BRAINTRUST_API_KEY`
required, `NEATLOGS_LLM_KEY` optional. When the gateway key is set, model
calls go through the Neatlogs gateway; when it is not, they go to OpenAI
directly on `OPENAI_API_KEY`; only when neither is set do they fall back
to the Braintrust proxy.
