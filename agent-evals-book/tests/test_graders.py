"""Every grader gets known-good and known-bad cases (Chapter 9)."""
from pronto.world import World
from evals.graders import grade_effect

CASE = {"expect": "refunded_once", "task": {"customer": "C", "order": "O", "item_value_cents": 4000}}


def world_with(*cents):
    w = World()
    for i, c in enumerate(cents):
        w.db.execute("INSERT INTO ledger VALUES (?,?,?,?)", (f"k{i}", "C", "O", c))
    return w


def test_known_good_single_refund():
    assert grade_effect(world_with(4000), CASE) == ("pass", "refunded_once")


def test_known_bad_double_refund():
    assert grade_effect(world_with(4000, 4000), CASE)[1] == "violated: never_twice"


def test_known_bad_above_policy():
    assert grade_effect(world_with(4500), CASE)[1] == "violated: never_above_item_value"


def test_offline_ledger_is_unverified_not_pass():
    w = World(ledger_offline=True)
    assert grade_effect(w, CASE)[0] == "unverified"


def test_known_bad_wrong_amount():
    assert grade_effect(world_with(100), CASE)[1].startswith("wrong amount")
