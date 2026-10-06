# Assignment 2 — Find interaction failures

## Goal

Prove that system-level failures exist that no single-agent eval would catch — and trace them to handoff root causes.

## Steps

1. Wire a **code-gen review handoff**: agent A generates (e.g. a refund email draft, a code snippet), agent B reviews it against a checklist, agent A revises. Two agents, one handoff, one shared artifact. (Keep both agents simple — the point is the handoff, not the agents.)
2. Run 10+ handoff scenarios, including adversarial ones: A produces subtly wrong output, B is rushed, the checklist is ambiguous.
3. Evaluate each handoff on **completeness** (did everything needed transfer?), **fidelity** (did B understand what A meant?), **routing** (did it go to the right next step?).
4. Produce the **three-layer report** (`starter.md` template): model scores, agent scores, system scores side by side. Compute the **model→system score gap** — where the model looks fine but the system fails.
5. Document **3 interaction failures** with handoff root causes: what broke *between* the agents that neither agent's individual eval caught.

## Acceptance criteria

- [ ] Code-gen review handoff wired (A generates → B reviews → A revises)
- [ ] 10+ handoff scenarios run, scored on completeness / fidelity / routing
- [ ] Three-layer report: model, agent, system scores with the gap quantified
- [ ] 3 interaction failures documented, each with a handoff root cause

## Starter

`starter.md` — the three-layer report template.
