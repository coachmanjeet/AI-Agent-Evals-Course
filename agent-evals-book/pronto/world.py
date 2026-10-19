"""A fresh, isolated copy of Pronto's systems for one trial (Chapter 11)."""
import sqlite3


class Timeout(Exception):
    """The response never came back. That says nothing about the write."""


class KeyConflict(Exception):
    """A reused idempotency key arrived with different arguments (Chapter 1)."""


DEFAULT_POLICY = {"approval_above_cents": 5000,     # the $50 rule
                  "photo_window_hours": 24,          # perishables
                  "return_window_days": 30}          # non-perishables


class World:
    def __init__(self, faults=None, policy=None, ledger_offline=False):
        self.db = sqlite3.connect(":memory:")                 # system of record
        self.db.execute("CREATE TABLE ledger (key TEXT PRIMARY KEY, customer TEXT, order_id TEXT, cents INTEGER)")
        self.db.execute("CREATE TABLE escalations (order_id TEXT PRIMARY KEY, reason TEXT)")
        self.faults = dict(faults or {})                      # e.g. {"timeout_after_commit": 1}
        self.policy = {**DEFAULT_POLICY, **(policy or {})}
        self.ledger_offline = ledger_offline
        self.trace = []                                       # execution record

    def record(self, kind, **fields):
        self.trace.append({"step": len(self.trace) + 1, "kind": kind, **fields})

    def refunds(self, customer):
        if self.ledger_offline:
            return None                                       # evidence unavailable
        return self.db.execute("SELECT key, order_id, cents FROM ledger WHERE customer=?", (customer,)).fetchall()
