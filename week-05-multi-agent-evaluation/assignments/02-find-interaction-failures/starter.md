# Three-layer report — template

Copy to `three_layer_report.md` and fill in. The point of this report: show
where the system fails even though the parts look fine.

## Setup

**Handoff under test:** (e.g. code-gen review: agent A drafts, agent B reviews against checklist, agent A revises)

**Scenarios run:** n = ___ (10+ required, including adversarial ones)

## Layer 1 — Model scores

(Score the underlying model on the task in isolation, e.g. with your Week 2 judges.)

| Metric | Score |
|--------|-------|
| | |

## Layer 2 — Agent scores

(Score each agent's individual behavior: tool use from Assignment 1, judge scores.)

| Agent | Metric | Score |
|-------|--------|-------|
| A (generator) | | |
| B (reviewer) | | |

## Layer 3 — System scores

(Score the end-to-end outcome: was the final artifact correct?)

| Metric | Score |
|--------|-------|
| final artifact correct | |
| handoff completeness | |
| handoff fidelity | |
| handoff routing | |

## The model→system gap

**Gap:** (model score minus system score, in percentage points)

**What it means:** (one paragraph — what breaks *between* the agents)

## 3 interaction failures

### Failure 1
**What happened:**
**Handoff root cause:** (completeness / fidelity / routing — be specific about what didn't transfer)
**Why neither agent's eval caught it:**

### Failure 2
...

### Failure 3
...
