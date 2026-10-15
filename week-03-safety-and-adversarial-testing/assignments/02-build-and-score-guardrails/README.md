# Assignment 2 — Build and score guardrails

## Goal

Build layered defenses for your agent and measure both sides of the trade-off: what they catch vs. what they wrongly block.

## Steps

1. Build **3 guardrails**, one of each kind (starter skeleton provided):
   - **Regex guardrail** — pattern-based (e.g. block outputs containing SSNs, API keys, or known injection phrases).
   - **LLM-judge guardrail** — a judge prompt that scores whether a tool call or output is safe.
     This IS a Week-2-style judge with a block threshold: reuse your Week 2
     judge prompt/scorer, pointed at safety instead of quality.
   - **Hybrid guardrail** — regex pre-filter + LLM judge only on the suspicious subset (cheaper, faster).
2. Wire each guardrail around the agent: check inputs before tool calls and outputs before responding.
3. Build a test set: 20 adversarial inputs (from Assignment 1) + 20 legitimate edge-case inputs (tricky but benign — e.g. "my order number looks like PRN-10421 but with a typo").
4. Score each guardrail: **catch rate** (% of the 20 attacks blocked) and **over-block rate** (% of the 20 legitimate inputs wrongly blocked).
5. Write the ship/no-ship verdict with numeric thresholds set upfront (e.g. "ship if catch rate ≥ 90% AND over-block rate ≤ 5%").
6. Design the HITL approval flow: which actions always require human approval, and what the approver sees.

> The agent already escalates two things: refunds over $50 and the
> `ESCALATION_KEYWORDS` pre-check (legal/safety/privacy). Document those
> as your baseline, then extend. A good HITL entry looks like this:
>
> | Trigger condition | What the approver sees | Rule |
> |---|---|---|
> | `issue_refund` with amount > $50 | order id, amount, reason, customer history | approve / edit / deny in one click |
> | Output contains `\b\d{3}-\d{2}-\d{4}\b` (SSN-shaped) | the flagged output + which guardrail fired | block + log, never auto-send |
> | Customer mentions lawyer / lawsuit | full turn transcript | route to specialist queue, SLA 1h |

## Acceptance criteria

- [ ] 3 guardrails implemented and wired around the agent
- [ ] 40-input test set (20 adversarial + 20 legitimate edge cases), documented
- [ ] Catch rate and over-block rate reported per guardrail
- [ ] Ship/no-ship verdict with upfront numeric thresholds
- [ ] HITL flow documented: trigger conditions + approver view

## Starter

`starter.py` — guardrail skeletons and the scoring harness.
