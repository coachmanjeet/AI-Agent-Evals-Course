"""Week 6, Assignment 2 helper: accuracy-vs-cost Pareto analysis for Pronto configs.

The demo agent makes no real model calls, so each tool call is priced with a
token estimate x a per-1K-token price. When you wire a real model, replace
TOKENS_PER_TOOL_CALL with measured means from your traces — the frontier math
below doesn't change.

Three Pronto configurations that trade quality for cost:
  standard — the demo agent as shipped.
  verbose  — retrieves policy twice per policy question (extra retrieval +
             extra model context, billed twice). Same answers, higher cost.
  cheap    — skips policy lookup entirely and answers from a canned fallback.
             Cheaper per run, wrong on every policy question.

Run:  python cost_model.py
"""

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "agent"))
from agent import CustomerServiceAgent  # noqa: E402

# ---------------------------------------------------------------------------
# Cost model — replace with your measured numbers when you have traces.
# ---------------------------------------------------------------------------
PRICE_PER_1K_TOKENS_USD = 0.003  # blended input/output price; make it yours

TOKENS_PER_TOOL_CALL = {
    "get_order_status": 400,
    "lookup_policy": 900,
    "issue_refund": 600,
    "escalate_to_human": 300,
}
BASE_TOKENS_PER_RUN = 800  # system prompt + user message + reply framing

# (question, phrase a correct reply must contain) — criteria-based checks.
SCENARIOS = [
    ("Where is my order PRN-10421?", "out_for_delivery"),
    ("Where is my order PRN-10422?", "delivered"),
    ("I was charged a delivery fee but my order was 90 minutes late.", "60 minutes"),
    ("What is the warranty on the Pronto air fryer?", "1-year"),
    ("Can you substitute items that are out of stock?", "opted in"),
    ("My strawberries from order PRN-10421 arrived moldy.", "PRN-10421"),
    ("I need a refund for PRN-10422, total $85.40, half the items never arrived",
     "human's approval"),
    ("Do you price-match other grocery stores?", "Pronto policies"),
]


def _counting_agent(mode):
    """Fresh demo agent whose tool calls are counted (and priced)."""
    agent = CustomerServiceAgent(demo=True)
    calls = Counter()

    def wrap(name, fn):
        def wrapper(*args, **kwargs):
            if name == "lookup_policy" and mode == "verbose":
                calls[name] += 2  # billed twice; second call discarded
                fn(*args, **kwargs)
            elif name == "lookup_policy" and mode == "cheap":
                return []  # skipped: canned fallback, no retrieval cost
            else:
                calls[name] += 1
            return fn(*args, **kwargs)
        return wrapper

    for tool in TOKENS_PER_TOOL_CALL:
        setattr(agent, tool, wrap(tool, getattr(agent, tool)))
    return agent, calls


def evaluate_config(mode):
    """Run all scenarios; return (quality, cost_usd_per_1k_requests)."""
    agent, calls = _counting_agent(mode)
    passed = 0
    for question, expected in SCENARIOS:
        if expected.lower() in agent.run(question).lower():
            passed += 1
    quality = passed / len(SCENARIOS)
    tokens = BASE_TOKENS_PER_RUN * len(SCENARIOS)
    tokens += sum(TOKENS_PER_TOOL_CALL[t] * c for t, c in calls.items())
    cost_per_run = tokens / len(SCENARIOS) * PRICE_PER_1K_TOKENS_USD / 1000
    return quality, cost_per_run * 1000


def pareto_frontier(results):
    """Configs no other config beats on BOTH cost (lower) and quality (higher)."""
    frontier = []
    for name, (q, c) in results.items():
        dominated = any(
            other != name and oq >= q and oc <= c and (oq > q or oc < c)
            for other, (oq, oc) in results.items()
        )
        if not dominated:
            frontier.append(name)
    return sorted(frontier, key=lambda n: results[n][1])


if __name__ == "__main__":
    results = {m: evaluate_config(m) for m in ("standard", "verbose", "cheap")}
    print(f"{'config':<10} {'quality':>8} {'$/1K req':>9}  verdict")
    for name in sorted(results, key=lambda n: results[n][1]):
        q, c = results[name]
        print(f"{name:<10} {q:>7.0%}  ${c:>7.3f}", end="   ")
        if name == "verbose":
            print("DOMINATED — same answers as standard, higher cost. Drop it.")
        elif name == "cheap":
            print("cheapest, but quality collapsed on policy questions.")
        else:
            print("baseline.")
    print(f"\nPareto frontier: {pareto_frontier(results)}")
    print("Ship rule: cheapest frontier config whose quality holds your bar "
          "(e.g. within 2pp of baseline).")
