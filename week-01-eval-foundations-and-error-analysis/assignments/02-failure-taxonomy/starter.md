# Failure taxonomy — template

Copy this file to `taxonomy.md` and fill it in. Each code must be a binary
yes/no question answerable from a trace alone.

## Codes

Starter example codes — the worked definitions live in the README (Step 2);
don't copy them here. Write each code's binary question in your own words.

| Code | Binary question | Quality dimension | Count (/30) | Example trace id |
|------|-----------------|-------------------|-------------|------------------|
| `WRONG_TOOL` | | product behavior | | |
| `NO_TOOL` | | product behavior | | |
| `HALLUCINATED_ORDER` | | model quality | | |
| `BAD_ESCALATION` | | product behavior | | |
| `DOC_MISS` | | reliability | | |
| `YOUR_CODE_HERE` | | | | |

(Add rows — you need 5+. Delete the examples above if they don't match your failures.)

## Top 3 failure modes

1. **CODE** (n/30) — what it looks like, and your hypothesis for why it happens.
2. **CODE** (n/30) — ...
3. **CODE** (n/30) — ...

## Unexplained anomaly

**What happened:** (one trace that failed in a way none of your codes capture)

**Why it's unexplained:** (what you checked, what didn't explain it)

## What you'd fix first

One paragraph: which failure mode you'd attack with one engineering day, and
what change you'd try. (Requirement and context: README, acceptance criteria.
This becomes Week 2's diagnose-and-fix input.)
