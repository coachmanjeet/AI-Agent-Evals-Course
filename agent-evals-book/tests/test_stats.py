from evals.stats import cohens_kappa, paired_cases_needed, rogan_gladen, sign_test_p, wilson


def test_book_numbers():
    lo, hi = wilson(84, 100)
    assert (round(lo, 2), round(hi, 2)) == (0.76, 0.90)
    assert round(sign_test_p(9, 7), 2) == 0.80
    assert round(rogan_gladen(0.90, 27 / 28, 4 / 12), 2) == 0.78
    assert round(cohens_kappa(["p"] * 18 + ["f", "p"], ["p"] * 18 + ["p", "f"]), 2) == -0.05
    assert 2800 <= paired_cases_needed(0.02, 0.16) <= 3400
