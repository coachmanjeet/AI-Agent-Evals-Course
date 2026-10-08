"""Pronto agent with Braintrust tracing — live demo script.

The whole point in one screen: how an agent's traces get into Braintrust.
Three moves, nothing else:

  1. init_logger(project=...)  — opens the pipe to Braintrust
  2. wrap_openai(OpenAI())     — every LLM call becomes a span, automatically
  3. @traced on each tool      — every tool call becomes a span

Run it, then open the "pronto-demo" project at braintrust.dev -> Logs and
click the trace: one root span per turn, LLM calls and tool calls nested
inside it. That tree IS the trace.

Needs:  pip install braintrust
        BRAINTRUST_API_KEY and OPENAI_API_KEY in .env (Week 2+ keys)

Usage:
    python agent/pronto_braintrust_demo.py --ask "Where is my order PRN-10421?"
    python agent/pronto_braintrust_demo.py --ask "My strawberries arrived moldy, refund me"
"""

import argparse
import json
import os
import sys

try:
    from braintrust import init_logger, traced, wrap_openai
except ImportError:
    sys.exit("pip install braintrust  (Week 4: it's a per-week install, like promptfoo)")

try:
    from openai import OpenAI
except ImportError:
    sys.exit("pip install openai  (already in requirements.txt — did `make setup` finish?)")

from dotenv import load_dotenv

load_dotenv()

# Reuse the canonical Pronto demo data — no duplication.
from agent.agent import DEMO_ORDERS, DEMO_POLICIES, ESCALATION_KEYWORDS

if not os.getenv("BRAINTRUST_API_KEY"):
    sys.exit("Set BRAINTRUST_API_KEY in .env  (free tier at braintrust.dev)")
if not os.getenv("OPENAI_API_KEY"):
    sys.exit("Set OPENAI_API_KEY in .env  (any provider key works from Week 2 on)")

# Move 1: open the pipe. Everything logged from here goes to this project.
logger = init_logger(project="pronto-demo")

# Move 2: wrap the client. Every chat.completions.create() is now a span.
client = wrap_openai(OpenAI())

MODEL = os.getenv("PRONTO_MODEL", "gpt-4o-mini")


# Move 3: @traced on each tool. Args in, return value out, nested in the trace.
@traced
def get_order_status(order_id: str) -> dict:
    order = DEMO_ORDERS.get(order_id)
    if not order:
        return {"found": False, "order_id": order_id}
    return {"found": True, "order_id": order_id, **order}


@traced
def lookup_policy(topic: str) -> dict:
    topic = topic.lower()
    hits = [p["text"] for p in DEMO_POLICIES
            if any(k in topic for k in p["topics"])]
    return {"topic": topic, "clauses": hits or ["No exact clause — escalate."]}


@traced
def issue_refund(order_id: str, amount: float, reason: str) -> dict:
    if amount > 50:
        return escalate_to_human(f"refund ${amount:.2f} exceeds $50 approval limit")
    return {"refunded": True, "order_id": order_id,
            "amount": amount, "reason": reason}


@traced
def escalate_to_human(reason: str) -> dict:
    return {"escalated": True, "reason": reason,
            "summary": f"Human needed: {reason}"}


TOOLS = {"get_order_status": get_order_status, "lookup_policy": lookup_policy,
         "issue_refund": issue_refund, "escalate_to_human": escalate_to_human}


@traced
def run_turn(user_message: str) -> str:
    """One customer turn. This @traced is the ROOT span — everything nests under it."""
    lowered = user_message.lower()
    if any(k in lowered for k in ESCALATION_KEYWORDS):
        return escalate_to_human("legal/safety/privacy keyword matched")["summary"]

    # LLM call 1 (auto-traced by wrap_openai): pick the tool + args.
    plan_resp = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content":
             "You route Pronto grocery support requests. Reply ONLY with JSON: "
             '{"tool": "<one of get_order_status, lookup_policy, issue_refund, escalate_to_human>", '
             '"args": {<the tool arguments>}}. '
             "Extract order IDs like PRN-10421. Refund amounts as numbers."},
            {"role": "user", "content": user_message},
        ],
    )
    plan = json.loads(plan_resp.choices[0].message.content)
    tool = TOOLS.get(plan.get("tool", ""), escalate_to_human)
    result = tool(**plan.get("args", {}))

    # LLM call 2 (auto-traced): draft the customer-facing reply from the tool result.
    reply_resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content":
             "You are Pronto's support agent. Acknowledge the problem first, "
             "plain language, one clear next step. Never invent order details."},
            {"role": "user", "content":
             f"Customer said: {user_message}\nTool result: {json.dumps(result)}\n"
             f"Write the reply."},
        ],
    )
    return reply_resp.choices[0].message.content


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ask", default="Where is my order PRN-10421?",
                        help="customer message to run through the agent")
    args = parser.parse_args()

    print(f"> {args.ask}\n")
    reply = run_turn(args.ask)
    print(reply)
    logger.flush()  # make sure spans land before exit
    print("\n— trace sent. Open braintrust.dev → project 'pronto-demo' → Logs.")


if __name__ == "__main__":
    main()
