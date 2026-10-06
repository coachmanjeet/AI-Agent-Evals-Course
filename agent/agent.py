"""Pronto customer-service agent skeleton.

Built in Week 1, reused all course long. Pronto is a fictitious online
grocery store ("Groceries in 30 minutes"). Run with --demo to verify your
setup without an API key (canned tool outputs). TODO markers show exactly
where Week 1's LangSmith tracing gets wired in.
"""

import argparse
import json
import re

# ---------------------------------------------------------------------------
# Demo data (canned — lets you run without an API key)
# ---------------------------------------------------------------------------
DEMO_ORDERS = {
    "PRN-10421": {"status": "out_for_delivery", "eta": "about 25 minutes",
                  "items": ["organic strawberries", "sourdough loaf"]},
    "PRN-10422": {"status": "delivered", "eta": "delivered at 9:42 AM",
                  "items": ["oat milk", "free-range eggs"]},
    "PRN-10423": {"status": "delayed", "eta": "running about 40 minutes late",
                  "items": ["Pronto air fryer"]},
}

DEMO_POLICIES = [
    {"topics": ["perishable", "spoiled", "moldy", "rotten", "strawberr", "milk", "egg"],
     "text": "Perishables: full refund if spoiled or damaged on arrival — just send a photo within 24 hours."},
    {"topics": ["non-perishable", "nonperishable", "return", "30-day"],
     "text": "Non-perishables: 30-day returns (unopened preferred)."},
    {"topics": ["delivery fee", "fee", "late"],
     "text": "Delivery fee is refunded only if your order is over 60 minutes late, or if Pronto cancels it."},
    {"topics": ["approval", "approve", "over $50", "$50", "50 dollar"],
     "text": "Refunds over $50 need a human's approval — I can't process those myself, but I can start the request for you."},
    {"topics": ["substitut"],
     "text": "We only substitute items if you opted in at checkout — otherwise we never swap without asking."},
    {"topics": ["warranty", "air fryer", "appliance"],
     "text": "Pronto-branded small appliances (like the Pronto air fryer) carry a 1-year limited warranty. Everything else is covered by the manufacturer's warranty — I can't invent terms beyond that."},
]

# Always escalate these — the agent must never handle them alone.
ESCALATION_KEYWORDS = ["sue", "lawsuit", "lawyer", "legal",
                       "allergic", "sick", "poison", "hospital",
                       "someone else", "other customer", "neighbor's", "my wife's"]


class CustomerServiceAgent:
    """A tiny tool-using support agent for Pronto groceries."""

    def __init__(self, demo: bool = False):
        self.demo = demo
        # TODO (Week 1, Assignment 1): wrap this agent with LangSmith tracing.
        # Hint: from langsmith import traceable — decorate run() and each tool
        # (get_order_status, lookup_policy, issue_refund, escalate_to_human).

    # -- tools ------------------------------------------------------------
    def get_order_status(self, order_id: str) -> dict:
        """Look up a Pronto order by ID (e.g. PRN-10421)."""
        # TODO (later weeks): replace canned data with a real lookup.
        return DEMO_ORDERS.get(order_id, {"error": f"unknown order {order_id}"})

    def lookup_policy(self, topic: str) -> list:
        """Keyword search over Pronto's policy snippets."""
        words = [w.strip("?.,!").lower() for w in topic.split()]
        hits = []
        for p in DEMO_POLICIES:
            if any(t in " ".join(words) or t in topic.lower() for t in p["topics"]):
                hits.append(p["text"])
        return hits

    def issue_refund(self, order_id: str, amount: float, reason: str) -> dict:
        """Issue a refund. Amounts over $50 are NEVER processed autonomously —
        they are escalated to a human, per Pronto policy."""
        if amount > 50:
            esc = self.escalate_to_human(
                f"refund of ${amount:.2f} on {order_id} exceeds the $50 approval limit")
            return {"status": "escalated", "escalation": esc,
                    "message": "That refund needs a human's approval — I've started the request for you."}
        return {"status": "approved", "order_id": order_id,
                "amount": round(amount, 2), "reason": reason}

    def escalate_to_human(self, reason: str) -> dict:
        """Hand off to a human specialist. Mandatory for legal threats,
        safety/health issues, and other customers' data."""
        return {"escalated": True, "reason": reason}

    # -- main loop ---------------------------------------------------------
    def run(self, user_message: str) -> str:
        """Handle one user message. Returns the agent's reply."""
        # TODO (Week 1, Assignment 1): add @traceable here so every run
        # leaves a trace you can inspect in LangSmith.
        msg = user_message.lower()

        def order_id():
            m = re.search(r"PRN-\d+", user_message.upper())
            return m.group(0) if m else None

        # Safety first: legal / health / other-customer data always escalate.
        if any(k in msg for k in ESCALATION_KEYWORDS):
            self.escalate_to_human("safety/legal/privacy: " + user_message[:80])
            return ("That needs a human specialist — I'm connecting you now. "
                    "They'll pick this up right away.")

        if "refund" in msg:
            oid = order_id()
            if not oid:
                return "I can help with that — which order ID? (e.g. PRN-10421)"
            m = re.search(r"\$?\s*(\d+(?:\.\d{1,2})?)", msg)
            amount = float(m.group(1)) if m else 0.0
            result = self.issue_refund(oid, amount, user_message[:120])
            if result["status"] == "escalated":
                return result["message"]
            return (f"Refund of ${result['amount']:.2f} on {oid} approved. "
                    f"It'll land back in 3–5 business days.")

        if ("order" in msg or "PRN-" in user_message.upper() or "where is" in msg
                or "arrived" in msg) and "fee" not in msg:
            oid = order_id()
            if oid:
                result = self.get_order_status(oid)
                if "error" in result:
                    self.escalate_to_human("unknown order " + oid)
                    return "I couldn't find that order. Let me connect you with a human."
                return (f"Order {oid} is {result['status']}, "
                        f"{result['eta']}. Items: {', '.join(result['items'])}.")
            return "Which order ID can I look up for you? (e.g. PRN-10421)"

        if any(k in msg for k in ["policy", "policies", "warranty", "substitut",
                                  "return", "fee", "late", "guarantee"]):
            hits = self.lookup_policy(user_message)
            if hits:
                return hits[0] + " Anything else I can help with?"
            return "I don't have a policy note on that yet — want me to connect you with a human?"

        # TODO (Week 2+): route through a real model call here instead of
        # the demo fallback. Keep the tool interface unchanged — the evals
        # in later weeks depend on it.
        if self.demo:
            return ("I can help with orders, refunds, and Pronto policies. "
                    "What do you need? (Try: 'Where is my order PRN-10421?')")
        return self.escalate_to_human("demo mode only — no model wired up yet.")["reason"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Pronto customer-service agent skeleton")
    parser.add_argument("--demo", action="store_true", help="canned responses, no API key needed")
    parser.add_argument("--ask", default="Where is my order PRN-10421?",
                        help="single message to handle")
    args = parser.parse_args()

    agent = CustomerServiceAgent(demo=args.demo)
    reply = agent.run(args.ask)
    print(json.dumps({"input": args.ask, "output": reply}, indent=2))


if __name__ == "__main__":
    main()
