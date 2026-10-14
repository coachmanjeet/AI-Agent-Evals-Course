# Assignment 1 — Step-by-step walkthrough

Follow top to bottom. Each step tells you exactly what to do, what you
should see, and how to know you're done before moving on. Budget 4–6 hours;
labeling (Step 5) is the bulk of it.

---

## Step 0 — Prereqs (5 min)

**Do this:**
- Clone the course repo (if you haven't): `git clone https://github.com/coachmanjeet/AI-Agent-Evals-Course.git`
- `cd AI-Agent-Evals-Course`
- Create `.env` in the repo root with one line: `BRAINTRUST_API_KEY=...`
  (get the key at braintrust.dev → your account → API keys — free course access)
- Add a provider key for judge calls: in Braintrust, Settings → AI Providers →
  add your OpenAI key once (see the note in Step 0's checkpoint for why).

**Checkpoint:** `.env` exists with your Braintrust key, **and** a provider key
is saved in Braintrust under Settings → AI Providers. Both are needed:
your Braintrust API key authenticates you but does not pay for inference —
judge calls (gpt-4o-mini, ~$0.01 for the week) route through the provider key.
The smoke test in Step 1 fails without it.

**If it breaks:** "Set BRAINTRUST_API_KEY" errors trace back to the `.env`
line (check for extra spaces or quotes). Proxy/auth errors in Step 1 trace
back to the missing provider key.

---

## Step 1 — Install and smoke-test (10 min)

**Do this:**
```
pip install braintrust openai
python week-02-designing-reliable-llm-judges/braintrust_smoke_test.py
```

**You should see:**
```
Check 1+2: API key + proxy judge call…
  [OK] proxy answered via gpt-4o-mini: {"verdict": ...
Check 3: Eval + scorer…
  [OK] Eval ran — open braintrust.dev -> project 'smoke-test' to see 3 scored rows

All green. The course Week 2 tooling will work with this key.
```

**Checkpoint:** all three checks print `[OK]`. Then open braintrust.dev,
click the `smoke-test` project, and confirm you see 3 rows with scores.
This is the exact UI you'll use for the assignment — get comfortable here.

**If it breaks:** paste the full error into your course channel. Common one:
`401` means the key is wrong or from the wrong Braintrust account.

---

## Step 2 — Warm up with the game (15 min, done in class)

**Do this:** open https://coachmanjeet.github.io/AI-Agent-Evals-Course/judge-calibration-game/
- Setup step: pick **OpenAI**, paste your OpenAI key (the same one you added
  under Braintrust's Settings → AI Providers), hit **Test key**. (The game
  can't use your Braintrust key directly — browsers are blocked from calling
  Braintrust's proxy. The assignment's Python code uses Braintrust normally.)
- Label all 24 responses pass/fail. Don't overthink — go with your gut, the
  way a support lead would.
- Write one judge prompt, run it, and read your agreement numbers.
- Gold check: compare your labels against the answer key.

**Checkpoint:** you can explain, in one sentence each, what accuracy,
precision/recall, and Cohen's κ told you about your judge.

**Why this matters:** everything after this is the same loop with your own
rubrics instead of the game's. If the loop feels obvious now, the assignment
is just execution.

---

## Step 3 — Get your 40 outputs (20 min)

**Do this:** collect 40 Pronto agent outputs to judge. Two good sources:
- **Reuse:** your 30 annotated traces from Week 1, plus 10 fresh ones.
- **Fresh:** run the demo agent over tricky inputs (adversarial ones from
  Week 1's taxonomy are ideal). Copy-paste runner — save as
  `collect_outputs.py` in the repo root, edit the `INPUTS` list, run it:

```python
import json, sys
sys.path.insert(0, "agent")
from agent import CustomerServiceAgent

INPUTS = [
    "Refund $49.99 on PRN-10421, the milk arrived spoiled",
    "Refund $50.01 on PRN-10421, the milk arrived spoiled",
    # add yours — aim for edge cases and likely failures
]

agent = CustomerServiceAgent(demo=True)  # demo=False once a model is wired
with open("outputs.jsonl", "w") as f:
    for text in INPUTS:
        f.write(json.dumps({"input": text, "output": agent.run(text)}) + "\n")
print(f"wrote {len(INPUTS)} outputs to outputs.jsonl")
```

**Rules for the set:**
- Include failures. If all 40 pass, your agreement numbers will flatter you
  and you'll learn nothing. Aim for roughly a third that you suspect are fails.
- Include edge cases: the $50 boundary, substitution opt-in wording,
  warranty claims on non-Pronto appliances, multi-turn context.

**Checkpoint:** you have 40 agent outputs saved somewhere you can read them
one by one (a file, a spreadsheet, printed — your choice).

---

## Step 4 — Write rubric 1: policy adherence (30 min)

Open `assignments/01-build-and-validate-judge/starter.py`. The
`policy_adherence` template is waiting. Replace the TODO with a real prompt
built from the five elements:

1. **Auditor role** — "You audit Pronto grocery-support agents against the policy bible below."
2. **One binary question** — "Did the agent follow every applicable policy?"
3. **Concrete standard** — spell out the actual rules (24h photo for
   perishables, 30-day non-perishable returns, >$50 refunds need human
   approval, substitution only with checkout opt-in, 1-year warranty on
   Pronto-branded appliances only). The judge can only apply what you wrote down.
4. **Boundary example** — "A $50.00 refund processed alone is a FAIL
   (over $50 needs approval); a $49.99 refund processed alone is a PASS."
5. **Strict output format** — `PASS` or `FAIL` on the first line, then
   `Reason: ...` in under 20 words. (The starter's parser keys off the
   first line — keep it clean.)

**Checkpoint:** read your prompt back and ask: "Could a careful human apply
this without asking me a clarifying question?" If not, it's not done.

**Trap to avoid:** adding a second criterion ("…and was polite"). One judge,
one question. Politeness is a different rubric.

---

## Step 5 — Write rubrics 2 and 3 (30 min)

Same five elements, new questions:
- **escalation_correctness** — "Did the agent escalate exactly when required
  (legal threats, safety/health, another customer's data, refunds over $50)
  and NOT escalate routine requests?" Boundary example: "A legal threat
  answered with a refund offer instead of escalation is a FAIL."
- **tool_call_accuracy** — "Did the agent call the right tool with the right
  arguments?" Boundary example: "Calling `issue_refund` for an $85 order
  instead of `escalate_to_human` is a FAIL even if the amount math is right."

**Checkpoint:** three prompts in `RUBRICS`, each one criterion, each with a
boundary example. Save the file.

---

## Step 6 — Label all 40 outputs (2–3 hours)

**Do this:** for each of the 40 outputs, record a PASS/FAIL against **each
of the three rubrics** — 120 labels total. Write them as `labels.jsonl`,
one JSON object per line:

```json
{"input": "<customer message>", "output": "<agent response>",
 "human": {"policy_adherence": "PASS", "escalation_correctness": "FAIL", "tool_call_accuracy": "PASS"}}
```

**Labeling discipline (this is the skill being graded):**
- Label against the rubric as written, not as you wish you'd written it.
  If the rubric is ambiguous on a case, note it — that's a rubric bug to
  fix later, not a label to fudge now.
- Work in batches of 10 with breaks. Label fatigue is real and it shows
  up as sloppy FAILs in the last batch.
- If you're unsure on a case, mark it and move on; adjudicate at Step 10.

**Checkpoint:** `labels.jsonl` has exactly 40 lines, each with all three
human labels. Count the FAILs — if fewer than ~10 across the set, go back
to Step 3 and toughen the inputs.

---

## Step 7 — Wire up the judge (30 min)

**Do this:** in `starter.py`, fill in `_judge_client()` and `run_judge()`
(the commented code shows the shape — uncomment and complete it):

```python
from openai import OpenAI
def _judge_client():
    return OpenAI(base_url="https://api.braintrust.dev/v1/proxy",
                  api_key=os.environ["BRAINTRUST_API_KEY"])
```

`run_judge()` sends the rubric as the system prompt and the agent output as
the user message, then returns `"PASS"` if the reply starts with PASS.

**Test it immediately** on 3 cases you already know the answer to:
```
python -c "
from starter import run_judge
print(run_judge('policy_adherence', 'Processed your \$85 refund in full, no approval needed.'))
"
```
**You should see:** `FAIL` (over $50 without human approval).

**Checkpoint:** the judge returns PASS/FAIL (not an essay, not JSON) on your
3 known cases, and all 3 match what you'd label by hand.

**If it breaks:** the reply doesn't start with PASS/FAIL → your rubric's
output-format instruction is too weak; strengthen step 5 of the rubric
("Output EXACTLY: ..."). `401` → back to Step 0, the key.

---

## Step 8 — Run the judges, build the matrices (30 min)

**Do this:** loop your 40 labels through `run_judge()` once per rubric and
collect judge verdicts. Then, per rubric:

```
print(agreement_matrix(judge_labels, human_labels))
print("kappa:", cohens_kappa(judge_labels, human_labels))
```

**You should see** something like:
```
{'JP_HP': 22, 'JP_HF': 3, 'JF_HP': 5, 'JF_HF': 10}
kappa: 0.58
```
Translation: 22 both-pass, 10 both-fail, 3 judge-pass/human-fail
(false passes — the dangerous ones), 5 judge-fail/human-pass (false fails).

**Checkpoint:** three matrices (4 cells each), three kappas, written down.
Don't interpret yet — just record.

---

## Step 9 — Investigate every disagreement (45 min)

This is the heart of the assignment. For **each** of the 8 disagreements
above (3 false passes + 5 false fails), open the agent output, your label,
and the judge's reason side by side, and decide:

- **Judge wrong?** The rubric has a loophole or the judge misread. Note the
  pattern — e.g. "judge passes any response containing the word 'escalated'
  even when no escalation happened."
- **Label wrong?** You mislabeled. Change the label and write down why —
  this is adjudication, and it's expected. (Acceptance criteria require at
  least one changed label with a reason, or an explicit note saying none
  changed and why.)

**Checkpoint:** for your worst judge, you can name its dominant failure
mode in one sentence: "It false-passes when ___." That's the shared loophole
from class — write it in `diagnosis.md`.

**Trap to avoid:** editing the rubric now to fix these 40 cases and
re-running. That's tuning on the test set — the agreement number becomes
dishonest. Note the fix; don't apply it to these numbers.

---

## Step 10 — Run it in Braintrust (20 min)

**Do this:** fill in `run_braintrust_eval()` in the starter (commented
shape provided) and run it over your 40 cases. Then open braintrust.dev →
your project.

**You should see:** one experiment per rubric, per-row verdicts next to
your hand labels, and average scores — those averages ARE your agreement
rates. Click into disagreeing rows and read the judge's reasoning.

**Checkpoint:** 3 experiments visible in the UI, per-rubric agreement rates
matching your Step 8 numbers. Screenshot the comparison view for your
submission.

---

## Step 11 — Package your deliverables (20 min)

Create these four files in the assignment folder:
- `rubrics.md` — your 3 judge prompts, verbatim.
- `labels.jsonl` — the 40 rows from Step 6 (final, post-adjudication).
- `results.md` — per judge: agreement matrix, agreement %, Cohen's κ,
  false-pass and false-fail counts.
- `diagnosis.md` — worst judge's failure mode, its shared loophole, and
  every label you changed on adjudication with reasons.

**Final checkpoint** (the acceptance criteria):
- [ ] 3 prompts, one criterion each, strict PASS/FAIL + reason
- [ ] 40 outputs × 3 rubrics = 120 hand labels
- [ ] Agreement matrix + κ per judge; κ ≥ 0.6 to call a judge "trusted"
- [ ] Worst judge's failure mode named (false-pass or false-fail?)
- [ ] Adjudication notes: labels changed + why (or why none changed)

**Stretch (optional):** `python judge_stats.py` — bias-corrected pass rate
with 95% CI for one judge, plus a one-line read on which way it was biased.
