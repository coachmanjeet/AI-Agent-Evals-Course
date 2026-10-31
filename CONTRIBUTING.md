# Contributing (fleet PR rules)

Every change to this repo arrives by PR from a fleet issue. The rules:

1. One purpose per PR. One issue, one PR. A PR mixing a feature, a
   refactor, and a README rewrite gets split, not reviewed.
2. Size cap: under 300 changed lines excluding generated files. Over the
   cap needs a stated reason in the PR body, not silent approval.
3. Green gates before merge. The required `pr-check` must pass. A red
   check blocks merge, no exceptions by the fleet.
4. QA sign-off by a different lane, recorded as a `QA PASS` comment on
   the PR (not a review approval: the fleet uses one GitHub account).
5. Auto-merge only after green checks plus `QA PASS`, enabled by the
   coordinator. Anything touching workflows, secrets, or publishing
   config waits for Manjeet.
6. Counting: a merged PR counts only if it is still merged 7 days later
   with no revert.
7. Branch: `fleet/<issue-number>-<short-slug>`, cut from main.
8. PR body: issue number, what changed, acceptance check and result,
   gate status. No PR without an issue number.

See FLEET.md for the full operating model.
