"""Pronto's four agent tools. Every call is recorded with its arguments and result (Chapter 18)."""
import uuid
from .world import KeyConflict, Timeout


def lookup_policy(world):
    world.record("tool", name="lookup_policy", result=world.policy)
    return world.policy


def get_order_status(world, order):
    world.record("tool", name="get_order_status", args={"order": order}, result={"status": "delivered"})
    return {"status": "delivered"}


def escalate_to_human(world, order, reason):
    world.db.execute("INSERT OR IGNORE INTO escalations VALUES (?,?)", (order, reason))
    world.record("tool", name="escalate_to_human", args={"order": order, "reason": reason}, result="queued")


def issue_refund(world, customer, order, cents, key=None):
    key = key or str(uuid.uuid4())                            # no key: every retry looks new
    row = world.db.execute("SELECT customer, order_id, cents FROM ledger WHERE key=?", (key,)).fetchone()
    if row and row != (customer, order, cents):
        raise KeyConflict(key)
    result = "duplicate_ignored" if row else "committed"
    if not row:
        world.db.execute("INSERT INTO ledger VALUES (?,?,?,?)", (key, customer, order, cents))
    world.record("tool", name="issue_refund", args={"customer": customer, "order": order, "cents": cents},
                 idempotency_key=key, result=result, record_id=key)
    if world.faults.get("timeout_after_commit", 0) > 0:      # fault injector
        world.faults["timeout_after_commit"] -= 1
        world.record("error", name="issue_refund", error="timeout")
        raise Timeout("payments API timed out")
    return {"status": result, "record_id": key}
