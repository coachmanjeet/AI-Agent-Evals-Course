"""Week 6 full-loop demo: before/after improvement runner (worked example).

Runs the same 10 gold cases twice and shows whether the self-correcting
agent actually improved anything:

    BEFORE = the canonical agent (agent/pronto_agent.py, run_turn_guarded)
    AFTER  = the self-correcting agent (self_correct.py, run_self_correcting)

Both arms are scored with the same judge (Week 2 pattern, from
offline_eval.py) and the same three code scorers (no refund over $50,
escalation correctness, no other customer's data), then the script prints
a per-case before/after table, per-category judge pass rates, the delta,
and the Week 6 decision-gate reading for each arm.

Model route: the Neatlogs gateway when NEATLOGS_LLM_KEY is set, OpenAI
direct when the gateway key is absent but OPENAI_API_KEY is set, else the
Braintrust proxy (BRAINTRUST_API_KEY). The agent picks the proxy natively
when PRONTO_BASE_URL is unset; the judge client below gets the same
fallback explicitly. This script never stores a key; keys live in the
repo-root .env or the environment, like the other course scripts.

Setup:
    pip install braintrust openai
    export BRAINTRUST_API_KEY="..."   (required; also enables tracing)
    export NEATLOGS_LLM_KEY="sk-..."  (optional; gateway route when set)

Run (from the repo root):
    python3 week-06-production-eval-infrastructure/examples/full-loop/improve_demo.py

What it prints:
    1. The model route in use (gateway or proxy).
    2. A per-case table: judge and code-mean before, after, and delta.
    3. Per-category judge pass rates, before and after.
    4. The decision-gate reading for BEFORE and for AFTER, using the
       Week 6 README rules: refund correctness target 95%, escalation
       correctness target 90%, other-customer-data leak target 0%.
       SHIP when all three are at or above bar; SHIP WITH CONDITIONS when
       refund or escalation is below bar; NO-SHIP when any leak is found.

Known limitations (same as Stage 3): gold order IDs (PRN-84xxx) are not
in DEMO_ORDERS, so lookup cases show the agent reporting "not found";
that is golden-set rot, a teaching point, not a bug to hide. The
self-correcting arm needs self_correct.py in this folder (built by a
parallel lane); if it is missing, this script exits with a clear message
instead of running half the demo.
"""

import os
import sys
from pathlib import Path

GATEWAY_URL = "https://llm.neatlogs.ai/v1"
PROXY_URL = "https://api.braintrust.dev/v1/proxy"
OPENAI_URL = "https://api.openai.com/v1"

# ---------------------------------------------------------------------------
# Pure helpers (no keys, no network): unit-tested in test_improve_demo.py.
#
# Row shape (one dict per case per arm):
#   {"id", "category", "thread",
#    "judge": 1.0 or 0.0,
#    "no_refund_over_50": 1.0 or 0.0,
#    "escalation_correctness": 1.0 or 0.0,
#    "no_other_customer_data": 1.0 or 0.0,
#    "corrections": int, self-correction rounds run (0 for the BEFORE arm),
#    "corrected": bool, a retry ran and its reply passes all checks
#        (False for the BEFORE arm; read from the self_correct report)}
# ---------------------------------------------------------------------------

CODE_SCORERS = ("no_refund_over_50", "escalation_correctness",
                "no_other_customer_data")


def model_route(env=None):
    """Pick the model route from the environment. Returns (base_url, key_name).

    Neatlogs gateway wins when NEATLOGS_LLM_KEY is set; OpenAI direct
    when the gateway key is absent but OPENAI_API_KEY is set; otherwise
    the Braintrust proxy on BRAINTRUST_API_KEY. Only the key NAME is
    returned, never a key value, so this stays safe to test with canned
    env dicts.
    """
    env = os.environ if env is None else env
    if env.get("NEATLOGS_LLM_KEY"):
        return GATEWAY_URL, "NEATLOGS_LLM_KEY"
    if env.get("OPENAI_API_KEY"):
        return OPENAI_URL, "OPENAI_API_KEY"
    return PROXY_URL, "BRAINTRUST_API_KEY"


def _mean(values):
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def _code_mean(row):
    return _mean(row.get(name, 0.0) for name in CODE_SCORERS)


def scores_from_rows(rows):
    """Collapse per-case rows into the gate inputs.

    refund_correctness: mean no_refund_over_50 over refund_request cases
        (1.0 when the run has no refund cases: nothing to violate).
    escalation_correctness: mean over all cases.
    leak_rate: fraction of cases whose reply disclosed another customer's
        data, i.e. 1 minus the mean of no_other_customer_data.
    judge_pass_rate: mean judge score over all cases.
    """
    rows = list(rows)
    refund_rows = [r for r in rows if r.get("category") == "refund_request"]
    refund = (_mean(r.get("no_refund_over_50", 0.0) for r in refund_rows)
              if refund_rows else 1.0)
    return {
        "refund_correctness": refund,
        "escalation_correctness": _mean(
            r.get("escalation_correctness", 0.0) for r in rows),
        "leak_rate": 1.0 - _mean(
            r.get("no_other_customer_data", 0.0) for r in rows),
        "judge_pass_rate": _mean(r.get("judge", 0.0) for r in rows),
    }


def delta_table(before_rows, after_rows):
    """Per-case before/after comparison. Returns {"rows", "summary"}.

    Rows are matched by case "id"; a mismatch in the id sets raises
    ValueError rather than silently comparing different cases. Label per
    case: "improved" when the judge flips to PASS, or the judge holds and
    the code mean rises; "regressed" for the mirror image; "unchanged"
    when neither the judge nor the code mean moves.
    """
    before = {r["id"]: r for r in before_rows}
    after = {r["id"]: r for r in after_rows}
    if set(before) != set(after):
        raise ValueError(
            f"before/after case ids differ: "
            f"only-before={sorted(set(before) - set(after))}, "
            f"only-after={sorted(set(after) - set(before))}")
    rows = []
    for case_id, b in before.items():
        a = after[case_id]
        judge_before, judge_after = b.get("judge", 0.0), a.get("judge", 0.0)
        code_before, code_after = _code_mean(b), _code_mean(a)
        if judge_after > judge_before or (
                judge_after == judge_before and code_after > code_before):
            label = "improved"
        elif judge_after < judge_before or (
                judge_after == judge_before and code_after < code_before):
            label = "regressed"
        else:
            label = "unchanged"
        rows.append({
            "id": case_id, "category": b.get("category", ""),
            "thread": b.get("thread", ""),
            "judge_before": judge_before, "judge_after": judge_after,
            "judge_delta": judge_after - judge_before,
            "code_before": code_before, "code_after": code_after,
            "code_delta": code_after - code_before,
            "corrections": a.get("corrections", 0),
            "corrected": bool(a.get("corrected", False)),
            "label": label,
        })
    summary = {
        "n": len(rows),
        "improved": sum(1 for r in rows if r["label"] == "improved"),
        "regressed": sum(1 for r in rows if r["label"] == "regressed"),
        "unchanged": sum(1 for r in rows if r["label"] == "unchanged"),
        "corrected_after": sum(1 for r in rows if r.get("corrected")),
        "judge_before": _mean(r["judge_before"] for r in rows),
        "judge_after": _mean(r["judge_after"] for r in rows),
        "code_before": _mean(r["code_before"] for r in rows),
        "code_after": _mean(r["code_after"] for r in rows),
    }
    return {"rows": rows, "summary": summary}


def gate_reading(scores_dict):
    """Week 6 decision gate. Returns "VERDICT - one-line reason".

    Targets from week-06-production-eval-infrastructure/README.md
    ("Decision gates"): refund correctness 95%, escalation correctness
    90%, other-customer-data leak 0%. Missing scores fail closed: a gate
    cannot pass on evidence it does not have.
    """
    refund = scores_dict.get("refund_correctness", 0.0)
    escalation = scores_dict.get("escalation_correctness", 0.0)
    leak = scores_dict.get("leak_rate", 1.0)
    if leak > 0:
        return (f"NO-SHIP - leak rate {leak:.0%} is above the 0% bar: "
                "any leaked order ID is a wrong-customer refund; "
                "the gate stays red until 0% on the regression set.")
    if escalation < 0.90:
        return (f"SHIP WITH CONDITIONS - escalation {escalation:.0%} is "
                "below the 90% bar: the $50-cap misses become P0 fixes "
                "this sprint, each miss is unapproved revenue leaving.")
    if refund < 0.95:
        return (f"SHIP WITH CONDITIONS - refund correctness {refund:.0%} "
                "is below the 95% bar: ship, but log the misses into the "
                "gold set and fix them first.")
    return (f"SHIP - refund {refund:.0%}, escalation {escalation:.0%}, "
            "leaks 0%: all at or above bar; log the misses into the gold set.")


# ---------------------------------------------------------------------------
# Main: env, clients, agent imports, two Eval arms, printed comparison.
# ---------------------------------------------------------------------------

def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path.insert(0, str(repo_root))
    try:
        from dotenv import load_dotenv
        load_dotenv(repo_root / ".env")
    except ImportError:
        pass

    if not os.environ.get("BRAINTRUST_API_KEY"):
        print("Missing environment variable: BRAINTRUST_API_KEY")
        print("Set it in .env or export it first, then re-run.")
        print("No keys are stored in this file.")
        sys.exit(1)

    base_url, key_name = model_route()
    route = {"NEATLOGS_LLM_KEY": "Neatlogs gateway",
             "OPENAI_API_KEY": "OpenAI direct (NEATLOGS_LLM_KEY not set)",
             "BRAINTRUST_API_KEY": "Braintrust proxy (no gateway or OpenAI key)"}[key_name]
    print(f"Model route: {route} (base_url {base_url})")
    if key_name in ("NEATLOGS_LLM_KEY", "OPENAI_API_KEY"):
        # Route the agent's generation through the chosen base URL BEFORE
        # importing it: the agent resolves its client at import time, and
        # PRONTO_BASE_URL wins over the Braintrust proxy.
        os.environ["PRONTO_BASE_URL"] = base_url
        os.environ["PRONTO_API_KEY"] = os.environ[key_name]
    else:
        # Deterministic fallback: drop any stray gateway setting so the
        # agent takes its native Braintrust proxy branch.
        os.environ.pop("PRONTO_BASE_URL", None)
        os.environ.pop("PRONTO_API_KEY", None)

    try:
        from openai import OpenAI
    except ModuleNotFoundError:
        print("Missing package: openai")
        print("Run: pip install braintrust openai")
        sys.exit(1)
    try:
        from braintrust import Eval
    except ModuleNotFoundError:
        print("Missing package: braintrust")
        print("Run: pip install braintrust openai")
        sys.exit(1)
    try:
        from offline_eval import (
            load_cases, parse_transcript,
            run_judge, no_refund_over_50, escalation_correctness,
            no_other_customer_data)
    except ModuleNotFoundError as e:
        print("Could not import the Stage 3 helpers:", e)
        print("Run from the repo root.")
        sys.exit(1)
    try:
        from self_correct import run_self_correcting
    except ModuleNotFoundError:
        print("self_correct.py is not in this folder yet.")
        print("It is built by a parallel lane; re-run once it lands.")
        print("Nothing was run: the demo needs both arms to compare.")
        sys.exit(1)
    try:
        from agent.pronto_agent import run_turn_guarded
    except ModuleNotFoundError as e:
        print("Could not import the canonical agent:", e)
        print("Run from the repo root.")
        sys.exit(1)

    judge_client = OpenAI(api_key=os.environ[key_name], base_url=base_url)
    cases = load_cases(repo_root)
    by_input = {c["input"]: c for c in cases}
    scorers = {"no_refund_over_50": no_refund_over_50,
               "escalation_correctness": escalation_correctness,
               "no_other_customer_data": no_other_customer_data}

    def run_arm(label, turn_fn):
        """One Eval arm over the 10 cases. Returns per-case row dicts."""
        results = {}

        def task(case_input):
            case = by_input[case_input]
            history, user_message = parse_transcript(case_input)
            reply, corrections, corrected = turn_fn(list(history), user_message)
            if isinstance(reply, dict):
                reply = reply.get("reply", str(reply))
            results[case["id"]] = {
                "reply": reply, "case": case, "corrections": corrections,
                "corrected": corrected}
            return {"reply": reply, "root_span_id": case["root_span_id"]}

        def judge_scorer(input, output, expected):
            case = by_input[input]
            reply = output["reply"] if isinstance(output, dict) else str(output)
            verdict, reason = run_judge(judge_client, input, reply, expected)
            results[case["id"]].update(
                {"judge": 1.0 if verdict == "PASS" else 0.0,
                 "judge_verdict": verdict, "judge_reason": reason})
            return 1.0 if verdict == "PASS" else 0.0

        def record(name):
            fn = scorers[name]

            def scorer(input, output, expected):
                case = by_input[input]
                score = fn(input, output, expected)
                results[case["id"]][name] = score
                return score
            scorer.__name__ = name
            return scorer

        Eval(
            "pronto-full-loop-stage3",
            experiment_name=f"improve-{label}",
            data=[{"input": c["input"], "expected": c["expected"],
                   "metadata": {"case_id": c["id"], "category": c["category"],
                                "thread": c["thread"],
                                "root_span_id": c["root_span_id"]}}
                  for c in cases],
            task=task,
            scores=[judge_scorer,
                    record("no_refund_over_50"),
                    record("escalation_correctness"),
                    record("no_other_customer_data")],
        )
        rows = []
        for c in cases:
            r = results[c["id"]]
            rows.append({
                "id": c["id"], "category": c["category"],
                "thread": c["thread"], "judge": r.get("judge", 0.0),
                "no_refund_over_50": r.get("no_refund_over_50", 0.0),
                "escalation_correctness": r.get("escalation_correctness", 0.0),
                "no_other_customer_data": r.get("no_other_customer_data", 0.0),
                "corrections": r.get("corrections", 0),
                "corrected": r.get("corrected", False),
                "judge_verdict": r.get("judge_verdict", "?"),
                "judge_reason": r.get("judge_reason", ""),
                "reply": r["reply"],
            })
        return rows

    def before_turn(messages, user_message):
        return run_turn_guarded(messages, user_message), 0, False

    def after_turn(messages, user_message):
        reply, report = run_self_correcting(
            messages, user_message, turn_fn=run_turn_guarded, max_retries=1)
        # Report shape is the self_correct lane's: "retries_used" counts
        # the correction rounds, "corrected" is True only when a retry ran
        # and its reply passes all checks. Fall back gracefully if the
        # shape ever changes.
        if isinstance(report, dict):
            corrections = report.get(
                "retries_used", report.get("corrections", 0))
            corrected = bool(report.get("corrected", False))
        else:
            corrections, corrected = 0, False
        return reply, corrections, corrected

    print("\nBEFORE arm: canonical agent (run_turn_guarded) ...")
    before_rows = run_arm("before", before_turn)
    print("\nAFTER arm: self-correcting agent (run_self_correcting) ...")
    after_rows = run_arm("after", after_turn)

    delta = delta_table(before_rows, after_rows)
    print("\nBefore/after per-case table "
          "(judge 1 = PASS; code = mean of the 3 code scorers)")
    for r in delta["rows"]:
        print(f"  [{r['category']}] {r['thread']}")
        print(f"    judge: {r['judge_before']:.0f} -> {r['judge_after']:.0f} "
              f"({r['judge_delta']:+.0f}); "
              f"code: {r['code_before']:.2f} -> {r['code_after']:.2f} "
              f"({r['code_delta']:+.2f}); "
              f"corrections: {r['corrections']}; {r['label']}")
    s = delta["summary"]
    print(f"\nSummary: {s['improved']} improved, {s['regressed']} regressed, "
          f"{s['unchanged']} unchanged (of {s['n']})")
    print(f"  judge pass rate: {s['judge_before']:.0%} -> {s['judge_after']:.0%}")
    print(f"  code mean:       {s['code_before']:.2f} -> {s['code_after']:.2f}")
    print(f"  self-correction: {s['corrected_after']} cases corrected by retry "
          "(AFTER arm)")

    print("\nPer-category judge pass rate:")
    for category in ("order_status", "refund_request", "adversarial"):
        b = [r for r in before_rows if r["category"] == category]
        a = [r for r in after_rows if r["category"] == category]
        bp = _mean(r["judge"] for r in b)
        ap = _mean(r["judge"] for r in a)
        print(f"  {category}: {bp:.0%} -> {ap:.0%} "
              f"({len(b)} cases)")

    print("\nDecision-gate reading (Week 6 README targets: refund 95%, "
          "escalation 90%, leaks 0%):")
    print(f"  BEFORE: {gate_reading(scores_from_rows(before_rows))}")
    print(f"  AFTER:  {gate_reading(scores_from_rows(after_rows))}")
    print("\nDone. In Braintrust, open project 'pronto-full-loop-stage3' and")
    print("compare experiments 'improve-before' vs 'improve-after' "
          "(comparison key: input).")
    print("Known limitation: gold order IDs (PRN-84xxx) are not in "
          "DEMO_ORDERS, so lookup cases show 'not found'. See Stage 3.")


if __name__ == "__main__":
    main()
