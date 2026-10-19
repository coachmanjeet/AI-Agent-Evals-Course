from evals.redact import redact
from judges.bakeoff import choose_judge


def test_redaction_keeps_entities_distinct():
    out = redact("Card 4111 1111 1111 1111 hit C-1007 twice and C-1009 once; mail jo@example.com")
    assert "4111" not in out and "jo@example.com" not in out
    assert "<CUSTOMER_1>" in out and "<CUSTOMER_2>" in out and "<CARD_1> hit" in out


def test_bakeoff_picks_cheapest_qualified_judge():
    c = {"large": (0.97, 0.92, 9.0), "medium": (0.95, 0.88, 2.1), "small": (0.93, 0.71, 0.4)}
    choice, status = choose_judge(c, 0.90, 0.80)
    assert choice == "medium" and status["small"] == "fails TNR"
    assert choose_judge({"x": (0.5, 0.5, 1.0)}, 0.9, 0.8)[0] is None
