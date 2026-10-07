"""Week 2 helper: bias-corrected pass rates and confidence intervals for LLM judges.

Intuition in three lines:
- A judge's raw pass rate is biased: judges systematically over-pass or over-fail.
- Your hand-labeled subset measures that bias (the judge's true-positive and
  true-negative rates) — the direction and size of the error.
- The correction below applies those rates to the judge's verdicts on unlabeled
  data to estimate the TRUE pass rate, and bootstrap resampling turns that one
  estimate into a 95% confidence interval.

Stdlib only. Inputs are 0/1 lists: 1 = PASS, 0 = FAIL.
"""

import random


def confusion_counts(human_labels, judge_preds):
    """(tp, tn, fp, fp) of judge predictions against human ground truth."""
    tp = sum(1 for h, j in zip(human_labels, judge_preds) if h == 1 and j == 1)
    tn = sum(1 for h, j in zip(human_labels, judge_preds) if h == 0 and j == 0)
    fp = sum(1 for h, j in zip(human_labels, judge_preds) if h == 0 and j == 1)
    fn = sum(1 for h, j in zip(human_labels, judge_preds) if h == 1 and j == 0)
    return tp, tn, fp, fn


def judge_rates(human_labels, judge_preds):
    """(tpr, tnr): P(judge says PASS | human PASS), P(judge says FAIL | human FAIL)."""
    tp, tn, fp, fn = confusion_counts(human_labels, judge_preds)
    tpr = tp / (tp + fn) if (tp + fn) else 0.0
    tnr = tn / (tn + fp) if (tn + fp) else 0.0
    return tpr, tnr


def bias_corrected_rate(human_labels, judge_preds_on_labeled, judge_preds_on_unlabeled):
    """Estimate the TRUE pass rate on unlabeled data, correcting for judge bias.

    Apparent pass rate = tpr * true + (1 - tnr) * (1 - true); solve for true.
    Raises ValueError if the judge is uninformative on the labeled set.
    """
    if not judge_preds_on_unlabeled:
        raise ValueError("need at least one unlabeled judge prediction")
    tpr, tnr = judge_rates(human_labels, judge_preds_on_labeled)
    denom = tpr + tnr - 1.0
    if abs(denom) < 1e-9:
        raise ValueError(
            "judge is uninformative on the labeled set (TPR + TNR ≈ 1): "
            "label more data or fix the judge before correcting."
        )
    apparent = sum(judge_preds_on_unlabeled) / len(judge_preds_on_unlabeled)
    return (apparent + tnr - 1.0) / denom


def bootstrap_ci(human_labels, judge_preds_on_labeled, judge_preds_on_unlabeled,
                 n_boot=2000, seed=7):
    """(estimate, lower, upper): 95% percentile-bootstrap CI for the corrected rate.

    Resamples the labeled pairs with replacement; each replicate re-estimates
    the judge's error rates and re-applies the correction. The spread across
    replicates is the uncertainty from having only N hand labels.
    """
    rng = random.Random(seed)
    n = len(human_labels)
    estimate = bias_corrected_rate(human_labels, judge_preds_on_labeled,
                                  judge_preds_on_unlabeled)
    replicates = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        try:
            replicates.append(bias_corrected_rate(
                [human_labels[i] for i in idx],
                [judge_preds_on_labeled[i] for i in idx],
                judge_preds_on_unlabeled))
        except ValueError:
            continue  # degenerate resample; skip it
    replicates.sort()
    lower = replicates[int(0.025 * len(replicates))]
    upper = replicates[int(0.975 * len(replicates)) - 1]
    return estimate, lower, upper


if __name__ == "__main__":
    # Illustrative synthetic Pronto example — NOT real student data.
    # A judge that over-passes: PASS on 90% of true passes, but also
    # 50% of true fails (e.g. it rarely catches policy misquotes).
    rng = random.Random(42)
    human = [1] * 26 + [0] * 14          # 40 hand-labeled traces
    rng.shuffle(human)
    judge_labeled = [
        1 if (h == 1 and rng.random() < 0.90) or (h == 0 and rng.random() < 0.50) else 0
        for h in human
    ]
    judge_unlabeled = [1 if rng.random() < 0.72 else 0 for _ in range(200)]

    raw = sum(judge_unlabeled) / len(judge_unlabeled)
    est, lo, hi = bootstrap_ci(human, judge_labeled, judge_unlabeled)
    tpr, tnr = judge_rates(human, judge_labeled)
    print(f"Judge error rates on 40 hand labels: TPR={tpr:.2f} TNR={tnr:.2f} "
          f"(over-passes: fails called PASS too often)")
    print(f"Judge raw pass rate on 200 unlabeled traces: {raw:.1%}")
    print(f"Bias-corrected pass rate: {est:.1%}  (95% CI [{max(0, lo):.1%}, {min(1, hi):.1%}])")
    print("The corrected rate sits below the raw rate — the judge's "
          "over-passing inflated it.")
