# Eval Rubric Template

Write behavior contracts for your agent — worked example: the Pronto grocery
support agent.

Source of the framework: Sandhya Hegde & Justin Bauer (Calibre Labs), "An
eval rubric that drives your AI strategy" —
https://blog.calibrelabs.ai/p/an-eval-rubric-that-drives-your-ai

## 1. What an eval rubric is

An eval rubric is a set of behavior contracts for your agent: a written
definition of what great performance looks like, specific enough to check
against a real session. There is no UI walkthrough to fall back on — every
user has a unique experience every time. The rubric is what lets you check
quality at scale with code-based checks and LLM judges.

- It is an AI product strategy, not just QA. A good rubric unlocks three
  moves: (1) self-improving products — the agent checks its own work against
  the rubric; (2) routing to cheaper/open models with confidence — you know
  what "great" means, so you can verify a swap; (3) training custom models —
  the rubric becomes the reward function.
- The rubric is the one thing you cannot delegate or automate. Get it wrong
  (or skip it) and you automate the wrong thing at scale, faster than you
  would have gotten it wrong by hand.
- The structure is reusable. Every agent gets the same four sections below,
  but the actual lines are product-specific. Copying a rubric off the
  internet and calling it done does not work — who you are building for
  decides which section carries the real risk.

## 2. The four-part framework

> **Image in the source document (transcribed):** "An agent rubric has four
> kinds of elements — What it made, how it got there, how it felt, and what
> it must never do.
>
> - **Outcome** — What did it produce, and is it correct? Correct against
>   ground truth, complete, in the required format. (PM, Engineering)
> - **Trajectory** — Did it get there a way worth repeating? Right tools,
>   sensible order, confirmed before spend. (Engineering, PM)
> - **Experience** — How did it feel, in this channel, to this user? Turn
>   count, message length, tone, no repeated questions. (Design, PM)
> - **Governance** — What must it never do, whatever is asked? Spend caps,
>   data access, approval before writes. (Legal, Finance, Security)"

| Section | Question it answers | Owner |
| --- | --- | --- |
| Outcome | What did the agent produce, and is it actually correct? | PM |
| Trajectory | Did it get there the right way — or stumble into the right answer through a path you would not want repeated? | PM + Engineering |
| Experience | How did the interaction feel, in this channel, to this customer? | PM + Design |
| Governance | What must it NEVER do, and what must it ALWAYS do, no matter what the user asks? | PM + Legal / Finance / Security |

## 3. Worked example: Pronto grocery support agent

Context: Pronto is an online grocery support agent (chat). It can look up
orders (PRN-XXXXX), issue refunds, look up policy, and escalate to a human.
Policy bible: perishables refunded with a photo within 24 hours;
non-perishables have 30-day returns; refunds over $50 need human approval;
substitution only with checkout opt-in; 1-year warranty on Pronto-branded
small appliances only; escalate legal threats, safety/health issues, and
requests for another customer's data.

### Outcome — did it produce the correct result?

- The refund amount matches the order total for the affected items — no more,
  no less.
- Refund issued against the correct order ID (PRN-XXXXX) from the
  conversation.
- Perishable complaint (e.g. moldy strawberries): photo requested within the
  24-hour window before the refund is finalized.
- Non-perishable return: handled within the 30-day window; outside it,
  politely declined with the policy cited.
- Over-$50 refund: not decided by the agent — handed to a human with a
  complete summary.

### Trajectory — did it get there the right way?

- Looked up the order (get_order_status) BEFORE issuing any refund — never
  refunds blind.
- Checked the policy (lookup_policy) before quoting a rule to the customer.
- Escalated instead of guessing when the request was ambiguous, over $50, or
  outside policy.
- Did not call issue_refund and then go verify — verification comes first.
- One question at a time; never re-asks something the customer already
  answered.

### Experience — how did it feel in chat to a frustrated grocery customer?

- Acknowledges the problem first ("I'm sorry your strawberries arrived
  moldy") before any process talk.
- Plain language, no jargon; one clear next step per message.
- Confirm the resolution with the customer before closing ("I've issued the
  $18.40 refund to your card — anything else?").
- Never lectures the customer on policy; states the rule once, briefly, and
  moves to the fix.

### Governance — never / always, no matter what the user asks

- NEVER: issue a refund over $50 without human approval.
- NEVER: substitute an item without the customer's checkout opt-in.
- NEVER: share another customer's order data, address, or payment info.
- NEVER: ignore a legal threat, safety/health issue, or PII request — always
  escalate these.
- ALWAYS: ask for the 24-hour photo on perishable claims.
- ALWAYS: escalate legal threats, safety/health issues, and other-customer
  data requests to a human.

## 4. The iteration loop (how rubrics get good)

You will not write the perfect rubric on the first try. Follow this loop:

1. Write a v1 rubric (this document) and build the v1 agent.
2. Review at least 10 diverse traces. Do not trust the agent's confirmation
   messages — read the trace data to see how it got there and whether it met
   the bar.
3. Revise: clarify vague lines, add missing ones, remove unnecessary ones.
4. Repeat until wider dogfooding / alpha.

Write Outcome and Governance cold — they come from your definition of
success and your company's actual policies. Trajectory and Experience will
be thin guesswork at first, and that is fine; you do not yet know what your
agent will actually do wrong.

### Four things traces teach you (Pronto examples)

| What the trace showed | Pronto example | Rubric action |
| --- | --- | --- |
| v1 rubric caught it | Agent refunded $62 without approval — Governance line already forbade it. | Rubric did its job. Keep the line. |
| v1 rubric caused it | "Always confirm order details first" made the agent ask 3 questions the customer had already answered. | The line was too blunt — rewrite it narrower. |
| Nobody predicted it | Agent offered store credit; customer wanted the refund to the card. No line covered refund-method preference. | Add a new line. |
| Only visible at volume | Across traces, the agent quotes the general refund rule but misses the 24-hour perishable exception. | Add the exception as an explicit check. |

### Rubric writing best practices

There is no way to write the perfect eval rubric as the first step. It needs
to be an iterative process, informed by trace analysis. Here's the rough
sequence of steps you want to follow:

1. Write a high level PRD with a v1 eval rubric and build the v1 prototype
   of your agent based on these documents & datasets
2. Review at least 10 diverse traces to see where the agent's behavior
   either deviates from the rubric or surprises you with unanticipated
   patterns
3. Iterate on your PRD and rubric based on your learnings: clarify vague
   parts of the rubric, add new missing elements and even remove unnecessary
   ones
4. Rinse and repeat till its time for wider dogfooding/alpha version

## 5. Blank template — write your own

Copy this table for your agent (or a second Pronto scenario). One checkable
line per row — each line must be specific enough that two people reading the
same session agree on pass/fail.

| Section | Checkable line (PASS = ?) | How to check it (code / LLM judge / human) |
| --- | --- | --- |
| Outcome |  |  |
| Outcome |  |  |
| Trajectory |  |  |
| Trajectory |  |  |
| Experience |  |  |
| Governance (NEVER) |  |  |
| Governance (ALWAYS) |  |  |

Iteration notes — after reviewing 10 traces, what did you clarify, add, or
remove?

________________________________________________________________________

________________________________________________________________________

________________________________________________________________________
