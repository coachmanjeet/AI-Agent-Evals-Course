# Agent fleet: operating model (AI-Agent-Evals-Course)

This file is canonical in this repo. It describes how the agent fleet works
here. The fleet ships many small, gated PRs. It never ships on its own
authority.

## Lanes
- Coordinator: owns the backlog (GitHub Issues labeled `fleet`), hands out
  one task per agent, never lets independent tasks wait on each other,
  merges nothing itself.
- Research: verifies facts and sources for a task before build starts.
- Design: shapes the change (outline, structure, examples).
- Engineer: builds on a fleet branch, opens the PR, keeps it under the
  size cap.
- QA: a different lane from the author. Runs the acceptance check from
  the issue and records a `QA PASS` comment on the PR, or sends it back
  with specifics. QA sign-off is a comment, not a review approval: the
  fleet uses one GitHub account, and GitHub does not accept self-approval.

## Branch and PR conventions
Branch: `fleet/<issue-number>-<short-slug>`, cut from main.
One issue, one PR. PR body: issue number, what changed, the acceptance
check and its result, gate status. No PR without an issue number.

## Merge rule
A PR merges only when all three hold: the required PR check is green,
a `QA PASS` comment from a different lane is on the PR, and the change
is not in the never-touch list. The coordinator enables auto-merge on the
PR once those hold. Nothing merges on green checks alone, and nothing
merges on QA alone.

## Counting rule
A merged PR counts only if it is still merged 7 days later with no
revert. Reverted PRs do not count, and a revert counts against the week
it lands in. This keeps the count honest.

## Branch protection (live on main)
Direct pushes are blocked, including for admins. Every change arrives by
PR. Required check: `pr-check` (the eval-gate workflow). No required
review approvals, because the fleet uses one account and self-approval
is blocked by GitHub; QA sign-off by comment is the approval signal.

## Never fleet-touched without Manjeet's approval
Workflows (except the approved fast-check wiring), secrets, publishing
config, deletions, renames of public URLs, and anything that sends,
posts, or charges.

## 24/7 heartbeat
`fleet-pulse` runs daily (13:00 UTC) plus on demand: it compiles the
shipped Python, counts merged PRs and open fleet issues, and writes a
job summary. It changes nothing. It is a heartbeat, not a worker: agent
execution is driven by the coordinator, on demand or on schedule outside
this repo.
