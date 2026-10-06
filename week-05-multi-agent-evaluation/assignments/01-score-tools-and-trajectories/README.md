# Assignment 1 — Score tools and trajectories

## Goal

Move from scoring answers to scoring behavior: did the agent use the right tools, in the right order, with valid arguments?

## Steps

1. Build **15+ expected-action records** (`starter.py` has the schema): each record is a test input plus the expected tool sequence — required tools in order, optional tools, and an **extra-call policy** (which unexpected calls are harmless vs. which fail the case, e.g. an extra `lookup_policy` is fine, an extra `escalate_to_human` is not).
2. Run the agent over all 15+ records, capturing the full tool trajectory per run (LangSmith traces from Week 1 make this easy).
3. Score tool use **per dimension**: right tool? right arguments? (validate arguments as structured output — types, formats, required fields) right order? policy violations?
4. Build a **trajectory evaluator**: property-based checks over the trajectory (e.g. "`get_order_status` called before answering about an order", "no tool called twice with identical args", "`escalate_to_human` only as the last step").
5. Flag **one fragile pass**: a case that passed but succeeded for the wrong reason (right answer, wrong trajectory). Write up why it's fragile.

## Acceptance criteria

- [ ] 15+ expected-action records with order and extra-call policies
- [ ] Per-dimension tool-use scores reported (tool choice, arguments, order, policy)
- [ ] Trajectory evaluator implemented with 3+ property checks
- [ ] One fragile pass documented: what passed, why the trajectory was wrong

## Starter

`starter.py` — expected-action schema, trajectory capture, and the evaluator skeleton.
