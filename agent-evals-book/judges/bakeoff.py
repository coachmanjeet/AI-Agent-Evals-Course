"""Pick the cheapest judge that meets the TPR/TNR targets (Chapter 10)."""


def choose_judge(candidates, target_tpr, target_tnr):
    """candidates: {name: (tpr, tnr, cost_per_1000_verdicts)}.
    Returns (choice or None, {name: status})."""
    status = {}
    for name, (tpr, tnr, _) in candidates.items():
        misses = [m for m, v, t in (("TPR", tpr, target_tpr),
                                    ("TNR", tnr, target_tnr)) if v < t]
        status[name] = "qualifies" if not misses else "fails " + ", ".join(misses)
    qualified = [n for n, s in status.items() if s == "qualifies"]
    choice = min(qualified, key=lambda n: candidates[n][2]) if qualified else None
    return choice, status
