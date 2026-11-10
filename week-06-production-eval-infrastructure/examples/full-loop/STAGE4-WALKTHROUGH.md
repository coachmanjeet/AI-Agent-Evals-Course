# Stage 4 walkthrough: closing the loop online

Worked walkthrough for the Week 6 capstone, not a live build. Stages 1-3
are runnable code (the agent, the traces, `offline_eval.py`, and now
`improve_demo.py`). Stage 4 is the part where the loop closes on live
traffic: an online scorer watches production logs, a Detection flags bad
spans as they happen, a human review campaign rates the traces, and every
online failure becomes a new row in the Stage 3 gold set. This document
specifies each piece exactly enough to set up in class, and flags every
step whose UI path was not verified from a live account.

## Prerequisites (read first, they change what is demoable)

- Stage 3 runs: `offline_eval.py` and `improve_demo.py` work, and the
  Braintrust project `pronto-full-loop-stage3` holds the experiments.
- Braintrust project `pronto` holds the live traces (Stage 2). The online
  scorer in (a) attaches to this project.
- The Neatlogs tracing branch in the agent (Stage 2 of the full-loop plan)
  was NOT built, so there are no live Neatlogs traces of Pronto yet. The
  Detection in (b) and the campaign in (c) are specified here, and they go
  live once tracing exists. Do not present them as running until then.

## (a) Braintrust online scorer: the same judge, on live logs

Goal: the Week 2 judge grades a sample of live `pronto` logs as they
arrive, so production quality is a number, not a feeling.

What gets attached: the same binary PASS/FAIL judge from Stage 3. Its
rubric lives in `offline_eval.py` as `JUDGE_RUBRIC` (gpt-4o-mini,
temperature 0, grades the reply against the expected behavior). Reuse
that rubric text verbatim when you create the scorer, so the online
number means the same thing as the offline number. Do not write a second,
slightly different rubric.

Setup path, verified against Braintrust's own docs
(https://docs.braintrust.dev/admin/projects, "Set up online scoring",
read 2026-11-10):

1. Open the `pronto` project, go to Settings, then Online scoring.
2. Click "Online scoring rule".
3. Configure the rule:
   - Name: `pronto-judge-online` (rule identifier).
   - Scorers: select the judge scorer created from `JUDGE_RUBRIC`.
   - Sampling rate: 5-10% of logs. That is the production habit from
     Week 6 (judge a sample to control eval cost). For the class demo,
     100% is also fine: the traffic is tiny, and scoring everything shows
     every verdict live.
   - Filter: leave blank for the demo (score all sampled logs). In
     production, filter to the traffic you care about, for example only
     refund turns.
   - Span type: root spans, so each scored unit is one whole customer
     turn, matching the offline cases.
4. Click "Create automation".

What you see: the rule runs asynchronously in the background. Scores
appear in the Logs page attached to the relevant span or trace, with the
judge's reasoning. A low-scoring log is the starting point for (d).

Verify in class: the exact current UI labels (Braintrust renames menu
items between releases), and the scorer-creation path itself (create the
scorer from the rubric text first, then select it in the rule). The
docs page above is the reference; confirm the clicks live before
presenting them as the path.

Automation alternative, not verified here: the Braintrust agent-evals
workshop documents creating the scorer with `POST /v1/function` and
attaching it with `POST /v1/project_score` (a project score with an
online config). That route was not verified against the live API in this
repo, so treat it as verify in class, not as a given.

## (b) One Neatlogs Detection: refund over $50 approved

Goal: catch the one failure that costs money the moment it happens, with
no model call and no sampling.

Rule spec (the deliverable; the setup clicks are verify in class):

| Field | Spec |
|---|---|
| Name | `refund-over-50-approved` |
| Matches | A tool span for the refund tool whose output approves a refund amount over $50. Same condition as the `no_refund_over_50` code scorer in `offline_eval.py`: a dollar amount over $50 in the same sentence as an approval verb (processed, refunded, issued, credited, approved). |
| Excludes | Spans that escalate instead of approving. A reply that mentions $85 while escalating it is correct behavior, not a detection. |
| Action | Flag the trace, surface it in Detections, and put it at the front of the review queue in (c). |

Why a rule and not the judge: the $50 cap is a hard policy, not a
judgment call. A deterministic rule fires on 100% of traffic for free,
while the judge samples 5-10% and costs a model call per log. The rule
is the guardrail; the judge is the quality signal. They catch different
things.

Verify in class: the exact Detection setup path in Neatlogs. The
full-loop plan describes Detections as rules that flag spans live
(regex, numeric conditions, PII, model classifiers), but no Neatlogs UI
path was verified from a live account for this repo. Do not present a
click path until it is confirmed in the live app. Prerequisite: Neatlogs
traces must exist first (see Prerequisites above).

## (c) One Neatlogs review campaign over the demo traffic

Goal: put human eyes on the traces the machines flagged, and turn the
judgments into labels the evals can reuse.

- Filter: demo traffic traces, that is, the traces from the full-loop
  runs (the 8-case replays), plus any trace flagged by the Detection in
  (b) or scored FAIL by the online scorer in (a). Start narrow: the
  flagged set first, not the whole log.
- Rating form (keep it to three fields; a long form never gets filled):
  1. Verdict (categorical): correct / should-escalate / should-refuse /
     wrong-facts. This is the label the gold set needs.
  2. Policy followed (yes/no): did the agent follow the Pronto policy
     bible, independent of whether the answer happened to be right.
  3. Notes (free-form): one line, what the reviewer would change.
- Who reviews: the instructor reviews the flagged set live in class;
  each student takes 2 traces as homework and brings the verdicts to
  office hours. One named owner triages disagreements (two reviewers
  disagreeing on a verdict is itself a signal: the rubric or the policy
  needs a word changed, not a louder argument).

Verify in class: the exact campaign setup path in Neatlogs. The
full-loop plan describes review campaigns as traces auto-collected by
filter and rated on custom forms; the field names above are this
course's spec, not a verified Neatlogs screen.

## (d) The close-the-loop procedure

This is the point of the whole demo. One online failure becomes an
offline regression test, and the decision gate reads the delta.

1. Spot it. A FAIL from the online scorer, a Detection flag, or a
   review-campaign verdict of should-escalate / should-refuse /
   wrong-facts.
2. Harvest it. Copy the failing input into a new gold-set row: the
   customer input verbatim, the expected behavior (answer, refuse, or
   escalate, in the gold set's words), the category, and the
   `root_span_id` of the live trace it came from. Tag it with what
   found it (online-scorer, detection, review-campaign) so the class
   can see which surface catches what.
3. Add it to the gold set. Append the row to
   `datasets/pronto-eval-gold.csv`, the single source of truth. (Versioning
   the set in Braintrust beyond the CSV is out of scope for this demo.)
4. Re-run the offline eval. `offline_eval.py` first, then
   `improve_demo.py` if the fix under test is the self-correcting agent.
   The new row is now part of the scored set.
5. Read the gate. `gate_reading` in `improve_demo.py` turns the new
   numbers into SHIP, SHIP WITH CONDITIONS, or NO-SHIP using the Week 6
   README targets (refund 95%, escalation 90%, leaks 0%). The delta
   between the run before the new row and the run after it is the
   evidence the fix worked, or did not.
6. Write the decision memo. One page: what the evals said, what shipped,
   what did not, what gets fixed first and why. The memo is the artifact
   stakeholders read; the experiment link is the evidence behind it.

Golden-set rot rule: if the failure is a dataset problem (the gold
order IDs are not in `DEMO_ORDERS`, so lookups report "not found"),
do not silently edit the input to make it pass. Re-harvest the gold set
or extend `DEMO_ORDERS`, and say which one you did. The eval caught
drift between the dataset and the system; hiding it deletes the lesson.

## What was verified, and what was not

Verified:
- Braintrust online scoring setup path and rule fields, from
  https://docs.braintrust.dev/admin/projects (read 2026-11-10).
  Sampling guidance (1-10% typical for high-volume apps, 100% for low
  volume) from Braintrust's own evals guide.
- The Detection rule spec and the campaign form fields: specified here
  from the course's own scorer (`no_refund_over_50`) and the full-loop
  plan, not copied from a vendor screen.
- The close-the-loop procedure: assembled from the full-loop plan and
  the Week 6 README decision gates.

Verify in class (do not present as confirmed):
- Exact current Braintrust UI labels and the scorer-creation clicks.
- The Neatlogs Detection setup path and the review campaign setup path.
- The API route for creating an online scorer (`POST /v1/function`,
  `POST /v1/project_score`).
- That Neatlogs traces exist at all: they depend on the unbuilt Stage 2
  tracing branch.

No screenshots, prices, or links beyond the one Braintrust docs page
above were invented for this walkthrough.
