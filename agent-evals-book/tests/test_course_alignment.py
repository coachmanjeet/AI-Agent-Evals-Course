from evals.rag_metrics import context_precision, context_recall, faithfulness
from evals.stats import paired_bootstrap, psi


def test_rag_metrics_match_chapter_15():
    retrieved = ["policy_v3", "faq_payments", "policy_v2", "delivery_log"]
    relevant = {"policy_v3", "delivery_log", "warranty_terms"}
    assert context_precision(retrieved, relevant) == 0.5
    assert round(context_recall(retrieved, relevant), 2) == 0.67
    assert round(faithfulness({"a": True, "b": True, "c": False}), 2) == 0.67


def test_psi_flags_the_chapter_19_shift():
    assert round(psi({"refund": .7, "warranty": .2, "delivery": .1},
                     {"refund": .48, "warranty": .22, "delivery": .3}), 2) == 0.30


def test_paired_bootstrap_covers_zero_for_a_coin_flip_gain():
    v8 = [1] * 84 + [0] * 16
    v9 = [1] * 77 + [0] * 7 + [1] * 9 + [0] * 7
    lo, hi = paired_bootstrap(v8, v9)
    assert lo < 0 < hi
