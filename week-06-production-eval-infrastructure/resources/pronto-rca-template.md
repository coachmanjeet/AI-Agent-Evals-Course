# RCA Template (Pronto)

A post-incident review template for the Pronto support agent. Use it in Week 6
Assignment 2 when you write up your flywheel cycle — the assignment's
`flywheel_cycle.md` template is the short version; this is the full version for
incidents that deserve one. Adapted for this course from the AgentOps RCA template.

> Blameless. Always. The system that allowed the failure is the problem, not the people.

---

# RCA: <one-line summary>

**Severity:** SEV-<n>
**Date(s):** YYYY-MM-DD
**Duration:** Hh Mm
**Author:** <name>
**Reviewers:** <names>
**Status:** Draft / In review / Approved
**Related:** <links to alerts, dashboards, sample traces, tickets>

## Summary

2–4 sentences. What happened, who was affected, what we did, what's next.

## Impact

| Dimension | Detail |
|---|---|
| Customers affected | <count or scope> |
| Conversations affected | <count or estimate> |
| Quality impact | <e.g., 12pp drop in resolution rate over the window> |
| Money impact | <e.g., $340 in wrongly issued refunds; 6 engineer-hours> |
| Policy impact | <e.g., 3 over-$50 refunds auto-approved — policy breach, yes/no> |

## Timeline

| Time | Event |
|---|---|
| HH:MM | First alert fired (which one? from the [metrics catalog](pronto-metrics-catalog.md)?) |
| HH:MM | On-call acknowledged |
| HH:MM | First mitigation attempted |
| HH:MM | Root cause identified |
| HH:MM | Mitigation in place; customer impact stopped |

Was there a delay between customer impact and the alert firing? That's a finding.

## Root cause

**Trigger:** what specific event or change initiated the failure? (A prompt
deploy? A model swap? A policy-doc edit?)

**Contributing factors:** the conditions that allowed the trigger to cause
customer impact (a missing guardrail, a judge that didn't cover this failure
mode, a canary set that didn't include this input shape).

**Why didn't we catch it earlier?** Missing alert? Missing eval case? Which Week
1–5 artifact should have caught this?

A useful framing: the *5 whys*, stopping at a system property that is genuinely
fixable.

## What went well

- <e.g., the canary caught it within an hour of deploy>
- <e.g., the >$50 escalation path held — no policy breach>

## What didn't go well

- <e.g., the dashboard didn't show per-tool error rates; we found the failing
  tool by hand>
- <e.g., no runbook section existed for this scenario>

## Action items

| # | Action | Owner | Severity | Due |
|---|---|---|---|---|
| 1 | <e.g., add eval case for the failure mode> | <name> | P1 | YYYY-MM-DD |
| 2 | <e.g., add the missing alert> | <name> | P1 | YYYY-MM-DD |
| 3 | <e.g., write the runbook section> | <name> | P2 | YYYY-MM-DD |

Action items need a named owner (not a team) and a due date. A postmortem with
action items but no owners is a fiction.

## Eval suite update

This is the flywheel. What new test cases come out of this incident?

- <new case 1 — which gate runs it: PR check or nightly?>
- <new case 2>

Every incident must leave at least one new regression test, or the flywheel
isn't turning.

## Lessons learned

100–300 words, plain language. What surprised us? What should the team
remember? What pattern should others watch for?

---

## Appendix: trace exemplars

| Trace ID | When | What |
|---|---|---|
| <trace id> | HH:MM | First failure — link the LangSmith run |
| <trace id> | HH:MM | After mitigation, recovered |

## Authoring guidance

- Write so a reader who wasn't in the room understands what happened.
- Specific times, specific numbers, specific component names — no vague language.
- Quote dashboards and traces; embed screenshots where they help.
- No blame language ("X should have known"). Focus on system properties ("the
  system relied on a single human knowing X; make it automatic").
- Keep it short enough to be read. A 30-page RCA is a 0-page RCA.
