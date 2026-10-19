"""Runs cases in fresh worlds, grades them, and writes run records (Chapters 1, 8, 11, 18)."""
import hashlib, json, time
from pathlib import Path
from pronto.world import World
from .graders import CONTRACT, grade_effect, grade_path
from .stats import pass_hat_k

CASES = Path(__file__).parent / "cases" / "refund_cases.jsonl"


def load_cases(tier="full"):
    cases = [json.loads(l) for l in CASES.read_text().splitlines() if l.strip()]
    return [c for c in cases if tier == "full" or c["tier"] == tier]


def dataset_version():
    return hashlib.sha256(CASES.read_bytes()).hexdigest()[:12]


def run_case(agent, case, trials=1):
    records = []
    for trial in range(trials):
        world = World(faults=case.get("faults"), policy=case.get("policy"), ledger_offline=case.get("ledger_offline", False))
        started = time.perf_counter()
        reply = agent.run(world, case["task"])
        effect, reason = grade_effect(world, case)
        path, path_reason = grade_path(world)
        verdict = "fail" if "fail" in (effect, path) else effect
        records.append({"case": case["id"], "trial": trial, "dataset": dataset_version(), "contract": CONTRACT["version"],
                        "agent": type(agent).__name__ + (":careful" if getattr(agent, "careful", False) else ""),
                        "verdict": verdict, "reason": reason if effect != "pass" else path_reason, "reply": reply,
                        "steps": len(world.trace), "ms": round((time.perf_counter() - started) * 1000, 2),
                        "trace": world.trace, "unresolved": "concurrent retries not simulated"})
    return records


def scorecard(records, k=4):
    n = len(records)
    gates = sum(1 for r in records if r["reason"].startswith("violated"))
    passed = sum(r["verdict"] == "pass" for r in records)
    unverified = sum(r["verdict"] == "unverified" for r in records)
    by_case = {}
    for r in records:
        by_case.setdefault(r["case"], []).append(r["verdict"] == "pass")
    reliability = {c: round(pass_hat_k(len(v), sum(v), k), 2) for c, v in by_case.items() if len(v) >= k}
    return {"runs": n, "gate_violations": gates, "verified_success": round(passed / n, 3),
            "unverified": round(unverified / n, 3), "pass_hat_k": reliability,
            "mean_steps": round(sum(r["steps"] for r in records) / n, 1)}
