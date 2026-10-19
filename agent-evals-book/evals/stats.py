"""The statistics used in the book, in one place (Chapters 4, 7, 10, 20)."""
import random
from math import comb, log, sqrt


def pass_at_k(n, c, k):
    return 1 - comb(n - c, k) / comb(n, k)


def pass_hat_k(n, c, k):
    return comb(c, k) / comb(n, k)


def wilson(passes, n, z=1.96):
    p = passes / n
    center = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return center - half, center + half


def sign_test_p(wins, losses):
    n = wins + losses
    return min(1.0, 2 * sum(comb(n, i) for i in range(min(wins, losses) + 1)) / 2 ** n)


def cohens_kappa(a, b):
    n = len(a)
    observed = sum(x == y for x, y in zip(a, b)) / n
    expected = sum((a.count(l) / n) * (b.count(l) / n) for l in set(a) | set(b))
    return (observed - expected) / (1 - expected)


def rogan_gladen(observed, tpr, tnr):
    return (observed + tnr - 1) / (tpr + tnr - 1)


def paired_cases_needed(true_gain, disagreement_rate, z_alpha=1.96, z_power=0.84):
    """Cases needed for a sign test to detect `true_gain` (e.g. 0.02) with 80% power (Chapter 20)."""
    p = 0.5 + true_gain / (2 * disagreement_rate)             # share of disagreements the better version wins
    discordant = ((z_alpha * 0.5 + z_power * sqrt(p * (1 - p))) / (p - 0.5)) ** 2
    return round(discordant / disagreement_rate)


def paired_bootstrap(a, b, rounds=5000, seed=1):
    """95% interval for mean(b) - mean(a) over the same cases (Chapter 20)."""
    rng, n, diffs = random.Random(seed), len(a), []
    for _ in range(rounds):
        idx = [rng.randrange(n) for _ in range(n)]
        diffs.append(sum(b[i] - a[i] for i in idx) / n)
    diffs.sort()
    return diffs[int(0.025 * rounds)], diffs[int(0.975 * rounds)]


def psi(expected, actual):
    """Population stability index between two category shares (Chapter 19)."""
    return sum((actual[k] - expected[k]) * log(actual[k] / expected[k]) for k in expected)
