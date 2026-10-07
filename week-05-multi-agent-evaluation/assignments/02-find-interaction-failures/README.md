# Assignment 2 — Find interaction failures

## Goal

Prove that system-level failures exist that no single-agent eval would catch — and trace them to handoff root causes.

## Steps

1. Take the Pronto crew (`../pronto_crew.py`): triage → policy → refund, two handoffs, one shared artifact (the customer reply). Read the crew file first — the handoffs are the `context=` chains between tasks.
2. Run 10+ handoff scenarios, including adversarial ones: triage misroutes a legal threat instead of escalating, policy returns the wrong snippet, refund ignores the $50 approval limit, an agent drops context the next one needed.
3. Evaluate each handoff on **completeness** (did everything needed transfer?), **fidelity** (did B understand what A meant?), **routing** (did it go to the right next step?).
4. Produce the **three-layer report** (`starter.md` template): model scores, agent scores, system scores side by side. Compute the **model→system score gap** — where the model looks fine but the system fails.
5. Document **3 interaction failures** with handoff root causes: what broke *between* the agents that neither agent's individual eval caught.

## Acceptance criteria

- [ ] Pronto crew handoffs mapped (triage → policy → refund, two handoffs)
- [ ] 10+ handoff scenarios run, scored on completeness / fidelity / routing
- [ ] Three-layer report: model, agent, system scores with the gap quantified
- [ ] 3 interaction failures documented, each with a handoff root cause

## Starter

`starter.md` — the three-layer report template.
