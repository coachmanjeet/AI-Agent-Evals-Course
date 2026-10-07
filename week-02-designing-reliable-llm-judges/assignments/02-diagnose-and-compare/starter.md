# Diagnose-and-fix report — template

Copy to `ab_report.md` and fill in.

## Root-cause diagnosis

**Failure mode:** (from Week 1 taxonomy)

**Evidence (10 traces):** (what the failing traces have in common — be specific)

**Root cause (one paragraph):**

## The fix

**Variant A (baseline):** (current behavior)

**Variant B (fix):** (exactly one change — describe it precisely)

## A/B results

Same input set, both variants, scored by the Week 2 judges.

| Metric | A (baseline) | B (fix) | Delta (pp) |
|--------|--------------|---------|------------|
| policy adherence | | | |
| escalation correctness | | | |
| tool-call accuracy | | | |

Sample size: n = ___ per variant.

## Ship / no-ship decision

**Thresholds (written before seeing results):**

**Verdict:** SHIP / NO-SHIP

**Why:** (the numbers behind the verdict, in two sentences)

**What would change my mind:** (what evidence would flip this decision)
