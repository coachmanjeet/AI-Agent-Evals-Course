# In-Class Exercise: Design Your First Eval Spec

**This is an in-class exercise, not an assignment.** It is the exercise
titled "Assignment 1: Design your first Eval spec" in the original class
document — that title is *not* this repo's Week 1 Assignment 1. The repo's
Assignment 1 is
[`assignments/01-instrument-and-trace/`](assignments/01-instrument-and-trace/README.md)
(instrument the agent and annotate traces). Do that assignment from its own
README; use this file only for the in-class exercise.

*Created by: Manjeet Singh*

What you'll practice: turning a vague quality worry into test cases, a
failure label, an eval method, and a ship/no-ship threshold.

> **Your scenario (use this one — don't invent your own):** A Customer
> Service Agent handles refund requests. It can look up an order, issue a
> refund up to $200, file a carrier claim, or escalate to a human. It
> answers policy questions from a retrieved knowledge article.
>
> *(In Tab 6 of the source document the scenario is worded "A Customer Proto
> Service Agent handles refund requests…" — same scenario.)*

Rows marked **Example** below are pre-filled example answers from the class
document — they show the shape of a good answer; they are not yours to
submit as-is.

---

## Box 1. Test set — write cases that would actually catch a bug

Think of it as: Given a scenario, did the Agent… follow policy? use the
right tools? resolve the issue?

At least one of your cases must be one the agent should refuse.

Two rules: one behaviour per case, and an expected outcome you could check
without re-reading the transcript. Cover a happy path, a policy edge, and a
hostile input.

| # | Scenarios | First user message | Expected outcome |
| --- | --- | --- | --- |
| e.g. *(Example)* | Refund above the $50 limit | "I need a refund for order #4501. It was $450 and never arrived." | Does not issue refund; escalates or files claim; states the limit |
| 1 *(Example answer, pre-filled in the source)* | Asking for order status | Where is my order / Where is my order xyz / I did not my receive / My order is lost | Order is verified against \<source\> and then the order tracking is provided to the: / Output format: Text, JSON / Voice - Text to Voice conversion |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |

## Box 2. Error analysis / Failure modes — name the failure, not the vibe (3 min)

> **Image in the source document (transcribed):** "How to analyze traces:
> the three-step process — Repeat it whenever your agent changes
> meaningfully.
>
> 1. **source inputs** — 20–30 traces — real runs or synthetic stress tests
> 2. **annotate traces** — read end to end. free-form notes: what worked,
>    what failed, bad UX
> 3. **cluster & code** — group notes into short, binary failure categories
>    — your taxonomy"

Assume you ran your cases and some failed. Write what you saw, then give it
a label you could sort 200 traces by. "Bad answer" is not a label.

| What you observed in the trace | Failure mode (your label) | How often |
| --- | --- | --- |
| Agent quoted a 30-day return window; the article says 45 days in 5 traces *(Example)* | Ungrounded policy claim | ~1 in 10 |
| Can you tell me the status of my order #12345? *(pre-filled start in the source)* |  |  |
|  |  |  |
|  |  |  |

---

## Box 3. Eval method — pick the right method that works

*(Week 2 continuation in the source document: "Evals Method (Judges) and
Gates".)*

> **Image in the source document (transcribed):** "How to pick the right
> method — Match the evaluator to the question you're actually asking.
>
> - can a rule express it? → **code-based check** — valid JSON, latency,
>   exact ID match
> - does it need judgment on open text? → **LLM-as-judge** — faithfulness,
>   tone, task completion
> - setting ground truth or calibrating? → **human review** — labeling a
>   golden set, judging the judge
> - measuring real-world outcomes? → **user feedback** — satisfaction,
>   escalation, retention"

Code for anything checkable (IDs, limits, tool calls, allowlists). LLM
judges only when correctness is a judgement call. Human for taste and for
calibrating the judge. Default to code; justify every judge.

| Failure mode (from box 2) | Code / LLM / Human | What exactly it checks | Metric name |
| --- | --- | --- | --- |
| Ungrounded policy claim *(Example)* | LLM-as-judge | Each factual claim traced to the retrieved article | Unsupported-claim rate |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

## Box 4. Eval gate — the number that blocks the launch

**Go/No Decision Framework:** A gate is only real if someone would actually
hold the release for it. Pick one metric from box 3 and finish these three
lines.

|  |  |
| --- | --- |
| Metric | which one, on which slice of cases |
| Threshold | number — and where the number came from |
| If it fails | who is paged, what ships anyway, what gets cut |

## Debrief — be ready to answer one of these

- Which of your four test cases would still pass if the agent were
  completely rewritten? Those are the ones worth keeping.
- Did you reach for an LLM judge where a five-line assertion would have
  been made? What would the assertion be?
- Your threshold — would you hold a release for it on a Friday afternoon? If
  not, it is a dashboard, not a gate.
