"""Pronto agent, end to end, with Braintrust tracing.

A REAL agent loop — not a scripted demo. The model reasons, picks tools,
reads their results, picks more tools, and answers when it's done:

    user message -> model -> tool call -> result -> model -> ... -> answer

Every step lands in Braintrust as one nested trace. The tracing itself is
still just three moves:

  1. init_logger(project=...)  -- opens the pipe to Braintrust
  2. wrap_openai(OpenAI())     -- every model call becomes a span, automatically
  3. @traced on each tool     -- every tool call becomes a span

Run it, then open the "pronto-demo" project at braintrust.dev -> Logs and
click the trace: one root span per turn, model calls and tool calls nested
inside it, in the order the agent actually ran them.

Needs:  pip install braintrust
        BRAINTRUST_API_KEY and OPENAI_API_KEY in .env (Week 2+ keys)

Usage:
    python agent/pronto_braintrust_demo.py --ask "Where is my order PRN-10421?"
    python agent/pronto_braintrust_demo.py --ask "My $85 order arrived half missing, refund me in full"
"""

import argparse
import json
import os
import sys

try:
    from braintrust import init_logger, traced, wrap_openai
except ImportError:
    sys.exit("pip install braintrust  (Week 4: a per-week install, like promptfoo)")

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
MAX_STEPS = 6  # the agent gets 6 model->tool rounds, then we escalate

SYSTEM = (
    "You are Pronto's customer support agent (\"Groceries in 30 minutes\"). "
    "Use the tools to look things up — never invent order details, policies, or "
    "refund amounts. Acknowledge the customer's problem first, plain language, "
    "one clear next step. Refunds over $50 need human approval: call "
    "escalate_to_human instead of issue_refund. Legal threats, safety issues, "
    "or requests about other customers: escalate_to_human immediately."
)


# Move 3: @traced on each tool. Args in, return value out, nested in the trace.
@traced
def get_order_status(order_id: str) -> dict:
    """Look up a Pronto order by ID, e.g. PRN-10421."""
    order = DEMO_ORDERS.get(order_id)
    if not order:
        return {"found": False, "order_id": order_id}
    return {"found": True, "order_id": order_id, **order}


@traced
def lookup_policy(topic: str) -> dict:
    """Look up the Pronto policy bible for a topic (refunds, warranty, substitution...)."""
    topic = topic.lower()
    hits = [p["text"] for p in DEMO_POLICIES
            if any(k in topic for k in p["topics"])]
    return {"topic": topic, "clauses": hits or ["No exact clause — escalate."]}


@traced
def issue_refund(order_id: str, amount: float, reason: str) -> dict:
    """Refund a customer. Amounts over $50 escalate — the agent can't approve those."""
    if amount > 50:
        return escalate_to_human(
            f"refund of ${amount:.2f} exceeds the $50 approval limit")
    return {"refunded": True, "order_id": order_id,
            "amount": amount, "reason": reason}


@traced
def escalate_to_human(reason: str) -> dict:
    """Hand off to a human agent. Always safe to call; never the wrong move."""
    return {"escalated": True, "reason": reason}


TOOLS = {"get_order_status": get_order_status, "lookup_policy": lookup_policy,
         "issue_refund": issue_refund, "escalate_to_human": escalate_to_human}

TOOL_SCHEMAS = [
    {"type": "function", "function": {
        "name": "get_order_status",
        "description": "Look up a Pronto order by ID (format PRN-#####).",
        "parameters": {"type": "object",
                       "properties": {"order_id": {"type": "string"}},
                       "required": ["order_id"]}}},
    {"type": "function", "function": {
        "name": "lookup_policy",
        "description": "Look up Pronto policy: refunds, warranties, substitutions, delivery fees.",
        "parameters": {"type": "object",
                       "properties": {"topic": {"type": "string"}},
                       "required": ["topic"]}}},
    {"type": "function", "function": {
        "name": "issue_refund",
        "description": "Refund a customer. Over $50 will auto-escalate.",
        "parameters": {"type": "object",
                       "properties": {"order_id": {"type": "string"},
                                      "amount": {"type": "number"},
                                      "reason": {"type": "string"}},
                       "required": ["order_id", "amount", "reason"]}}},
    {"type": "function", "function": {
        "name": "escalate_to_human",
        "description": "Hand off to a human. Use for legal/safety/privacy issues or anything over your authority.",
        "parameters": {"type": "object",
                       "properties": {"reason": {"type": "string"}},
                       "required": ["reason"]}}},
]


@traced
def run_turn(user_message: str) -> str:
    """One customer turn, as a real agent loop. This @traced is the ROOT span."""
    lowered = user_message.lower()
    if any(k in lowered for k in ESCALATION_KEYWORDS):
        return escalate_to_human("legal/safety/privacy keyword matched")["reason"]

    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": user_message}]

    for _ in range(MAX_STEPS):
        # Model thinks (auto-traced by wrap_openai) — may call tools, may answer.
        resp = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOL_SCHEMAS)
        msg = resp.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            return msg.content or "(no answer produced)"

        # Agent acts: each @traced tool becomes a span under this turn.
        for call in msg.tool_calls:
            fn = TOOLS.get(call.function.name, escalate_to_human)
            try:
                result = fn(**json.loads(call.function.arguments or "{}"))
            except Exception as exc:  # tools fail — the agent sees the error
                result = {"error": f"{call.function.name} failed: {exc}"}
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "content": json.dumps(result)})

    return escalate_to_human("too many steps without resolving")["reason"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ask", default="Where is my order PRN-10421?",
                        help="customer message to run through the agent")
    args = parser.parse_args()

    print(f"> {args.ask}\n")
    print(run_turn(args.ask))
    logger.flush()  # make sure spans land before exit
    print("\n— trace sent. Open braintrust.dev → project 'pronto-demo' → Logs.")


if __name__ == "__main__":
    main()
