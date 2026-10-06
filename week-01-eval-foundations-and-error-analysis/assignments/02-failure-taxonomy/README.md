# Assignment 2 — Build a failure taxonomy

## Goal

Turn your 30 annotated traces into a prioritized, countable picture of how the agent fails.

## Steps

1. Start from `annotations.csv` (Assignment 1). Read every trace marked **fail**.
2. Cluster the failures into **5 or more binary trace codes** — each code is a yes/no question about a trace, e.g. `WRONG_TOOL` (agent called the wrong tool), `NO_TOOL` (should have called a tool, didn't), `HALLUCINATED_ORDER` (invented order details), `BAD_ESCALATION` (escalated when it could have answered), `DOC_MISS` (correct doc existed, wasn't surfaced).
3. Count: how many of the 30 traces hit each code. A trace can hit multiple codes.
4. Map each code to one of the six quality dimensions (model quality, product behavior, safety, reliability, cost, latency).
5. Write up: the **top 3 failure modes** by frequency, plus **1 unexplained anomaly** — a failure you can't yet explain. Name it honestly.

## Acceptance criteria

- [ ] `taxonomy.md` defines 5+ binary codes, each with a one-line definition
- [ ] Every code has a frequency count (sums may exceed 30 — codes aren't exclusive)
- [ ] Every code is mapped to a quality dimension
- [ ] Write-up names the top 3 failure modes and 1 unexplained anomaly
- [ ] Codes are binary and checkable — a second person could apply them to a new trace and agree with you

## Starter

`starter.md` — the taxonomy table template. Copy it into `taxonomy.md` and fill it in.
