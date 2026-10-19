"""CLI: python -m evals.run --agent careful --tier smoke --trials 4
Exit code 1 on any gate violation, so CI blocks the change (Chapter 20)."""
import argparse, json, sys
from pronto.agents import ScriptedAgent
from .harness import load_cases, run_case, scorecard


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", choices=["careful", "naive", "llm"], default="careful")
    ap.add_argument("--model", default=None)
    ap.add_argument("--tier", choices=["smoke", "regression", "full"], default="smoke")
    ap.add_argument("--trials", type=int, default=1)
    ap.add_argument("--out", default="runs.jsonl")
    args = ap.parse_args()
    if args.agent == "llm":
        from pronto.agents import LLMAgent
        agent = LLMAgent(model=args.model)
    else:
        agent = ScriptedAgent(careful=args.agent == "careful")
    records = [r for c in load_cases(args.tier) for r in run_case(agent, c, args.trials)]
    with open(args.out, "w") as f:
        f.writelines(json.dumps(r) + "\n" for r in records)
    card = scorecard(records)
    print(json.dumps(card, indent=2))
    for r in records:
        if r["verdict"] != "pass":
            print(f"  {r['case']} trial {r['trial']}: {r['verdict']} ({r['reason']})")
    sys.exit(1 if card["gate_violations"] else 0)


if __name__ == "__main__":
    main()
