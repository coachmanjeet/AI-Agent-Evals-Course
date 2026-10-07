"""Week 4, Assignment 1 helper: pilot synthetic scenarios, keep only the ones
that discriminate.

A scenario earns its place in the golden set only if it can tell a good agent
from a bad one: it should PASS on the strong config and FAIL on a deliberately
weakened one (here: policy lookup disabled). Scenarios both configs pass are
dead weight — they inflate your case count without ever catching a regression.
Scenarios the strong config fails are mislabeled or too hard: fix or drop them.

Usage:
    python pilot_scenarios.py my_scenarios.csv [--out kept.csv]

CSV columns: id, question, expected_contains
  (expected_contains: a phrase a correct reply must contain — criteria-based,
  computed from your policy bible, not invented by a model.)
"""

import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "agent"))
from agent import CustomerServiceAgent  # noqa: E402


def make_weakened():
    """Demo agent with policy retrieval disabled — the 'bad' config."""
    agent = CustomerServiceAgent(demo=True)
    agent.lookup_policy = lambda topic: []
    return agent


def pilot(csv_path):
    strong = CustomerServiceAgent(demo=True)
    weak = make_weakened()
    report = []
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            q, expected = row["question"], row["expected_contains"]
            strong_pass = expected.lower() in strong.run(q).lower()
            weak_pass = expected.lower() in weak.run(q).lower()
            if strong_pass and not weak_pass:
                verdict, reason = "KEEP", "discriminates (strong passes, weakened fails)"
            elif not strong_pass:
                verdict, reason = "DISCARD", "strong config fails — mislabeled or too hard"
            else:
                verdict, reason = "DISCARD", "weakened config also passes — no signal"
            report.append((row["id"], verdict, reason))
    return report


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python pilot_scenarios.py scenarios.csv [--out kept.csv]")
    report = pilot(sys.argv[1])
    kept = [r for r in report if r[1] == "KEEP"]
    for sid, verdict, reason in report:
        print(f"{sid:<8} {verdict:<8} {reason}")
    print(f"\n{len(kept)}/{len(report)} scenarios discriminate — keep those, fix or drop the rest.")
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
        with open(sys.argv[1], newline="") as f:
            rows = {r["id"]: r for r in csv.DictReader(f)}
        with open(out, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["id", "question", "expected_contains"])
            w.writeheader()
            for sid, _, _ in kept:
                w.writerow(rows[sid])
        print(f"Wrote {out}")
