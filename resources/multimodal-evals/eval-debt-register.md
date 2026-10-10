# Eval debt register

## The idea in one sentence
Evals rot. Rubrics go stale, judges drift, datasets stop matching production —
and nobody notices until an incident. A debt register makes the rot visible on
a schedule.

## How it works
First week of every quarter, 3 hours, led by whoever owns eval quality, with
the people who label data in the room. Walk the checklist below. **Every
flagged item leaves the room with a named owner and a target date** — a debt
register with no owners is a complaint list, not a governance artifact.

## The checklist
- [ ] **Rubrics** — any rubric not reviewed in 6 months? Any "definition of
      good" the team would now disagree with?
- [ ] **Judges** — any judge whose monitoring kappa slipped below its floor?
      Any judge never validated against humans in the first place?
- [ ] **Datasets** — what fraction of eval cases still resemble last month's
      production traffic? Any failure mode from a real incident missing from
      the regression set?
- [ ] **Coverage** — run the UIG skill (`resources/skills/uig-skill.md`):
      which user inputs have zero eval coverage?
- [ ] **Cadence** — any recalibration or review that was scheduled but skipped?
- [ ] **Incidents** — every production failure since last quarter: is there a
      regression case for it now? If not, why not?

## Ownership (adapt to your team)
| Role | Owns |
|---|---|
| Eval quality lead | Pipeline integrity, judge calibration, dataset lifecycle |
| Data labelers / judge panel | Golden labels, rubric review — the definition of "good" |
| Product manager | Ship/hold decisions, quality bars, decision memos |
| Safety / policy | Safety gates, PII handling — zero-tolerance events |

## Pronto example
Q3 review finds: the refund-policy rubric still says "$50 needs approval" but
the policy changed to $75 in August — 40 eval cases now grade against the wrong
rule. Owner: eval lead. Target: fix rubric + regenerate cases by Friday.
