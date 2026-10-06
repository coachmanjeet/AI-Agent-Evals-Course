# Failure taxonomy — template

Copy this file to `taxonomy.md` and fill it in. Each code must be a binary
yes/no question answerable from a trace alone.

## Codes

| Code | Binary question | Quality dimension | Count (/30) | Example trace id |
|------|-----------------|-------------------|-------------|------------------|
| `WRONG_TOOL` | Did the agent call the wrong tool for the request? | product behavior | | |
| `NO_TOOL` | Should it have called a tool but answered from nothing? | product behavior | | |
| `HALLUCINATED_FACT` | Did it state a fact (order status, policy) not in any tool output? | model quality | | |
| `BAD_ESCALATION` | Did it escalate when it had what it needed to answer? | product behavior | | |
| `DOC_MISS` | Did a correct doc exist but never get surfaced? | reliability | | |
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

One paragraph: if you had one engineering day, which failure mode you'd attack
and what change you'd try — this becomes Week 2's diagnose-and-fix input.
