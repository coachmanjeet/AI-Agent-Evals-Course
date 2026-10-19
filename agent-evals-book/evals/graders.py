"""Graders from Part III: the task contract as code, plus path rules. Verdicts: pass, fail, unverified."""
import json
from pathlib import Path

CONTRACT = json.loads((Path(__file__).parent / "contracts" / "refund.json").read_text())


def grade_effect(world, case):
    """Rung 4: read the system of record, never the reply (Chapters 1, 2, 9)."""
    task, refunds = case["task"], world.refunds(case["task"]["customer"])
    if refunds is None:
        return "unverified", "ledger unreadable"
    mine = [r for r in refunds if r[1] == task["order"]]
    escalated = world.db.execute("SELECT 1 FROM escalations WHERE order_id=?", (task["order"],)).fetchone()
    limit = world.policy["approval_above_cents"]
    if len(mine) > 1:
        return "fail", "violated: never_twice"
    if any(not 0 < r[2] <= task["item_value_cents"] for r in mine):
        return "fail", "violated: never_above_item_value"
    if any(r[2] > limit for r in mine):
        return "fail", "violated: over_50_needs_human"
    if len(mine) == 1 and mine[0][2] != task["item_value_cents"]:
        return "fail", f"wrong amount: {mine[0][2]} cents, expected {task['item_value_cents']}"
    outcome = "refunded_once" if len(mine) == 1 else "escalated_to_human" if escalated else "declined_ineligible"
    return ("pass", outcome) if outcome == case["expect"] else ("fail", f"expected {case['expect']}, got {outcome}")


def grade_path(world):
    """Chapter 12: MUST look up policy before refunding; NEVER commit twice; BUDGET of steps."""
    names = [s.get("name") for s in world.trace if s["kind"] == "tool"]
    commits = sum(1 for s in world.trace if s.get("name") == "issue_refund" and s.get("result") == "committed")
    if "issue_refund" in names and names.index("lookup_policy") > names.index("issue_refund"):
        return "fail", "policy lookup after refund"
    if commits > 1:
        return "fail", "committed twice"
    if len(world.trace) > 12:
        return "fail", "over step budget"
    return "pass", "path ok"
