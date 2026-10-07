# Operate-and-document templates

## flywheel_cycle.md

Copy the template below into `flywheel_cycle.md`.

```markdown
# Flywheel cycle: <short incident name>

## Incident
What happened, when, how it was detected (canary? user report? red team?).

## Root cause
One paragraph, grounded in traces. Link the trace ids.

## Fix
What changed (one change, like Week 2). Link the PR.

## Regression test
The new test added to the suite: what it checks, where it lives,
which gate runs it (PR check or nightly).

## What this incident taught the evals
One line: what coverage gap this closed.
```

## cost_routing.md

```markdown
# Eval-driven cost routing recommendation

## Current state
Per-task cost (Week 1 metrics): $___ — quality scores: ___ (judges), ___ (Braintrust).

## Proposal
Route <which traffic> to <cheaper model / smaller top-k / fewer retries>.

## The math
- Projected savings: $___/month (show the arithmetic)
- Measured quality delta: ___pp on ___ metric (paired test, n = ___)
- Breach check: quality stays above the blocking thresholds in gating policy? Y/N

## Recommendation
Route / don't route — and what would change the answer.
```

## ownership.md

```markdown
# Eval ownership

## Owner
<name> — owns the eval suite, the gates, and the thresholds.

## Operating cadence
- Weekly: ___ (e.g. review nightly failures, triage new traces)
- Monthly: ___ (e.g. revisit thresholds, refresh golden set sample)
- Quarterly: ___ (e.g. full taxonomy review, judge re-validation)

## 2-AM playbook
When a gate fails overnight: who gets paged, what they check first,
when they're allowed to bypass the gate (and what they must file if they do).

## Threshold review
Thresholds get revisited when: ___ (e.g. 3 consecutive near-misses, model swap,
product surface change). Last reviewed: ___.
```
