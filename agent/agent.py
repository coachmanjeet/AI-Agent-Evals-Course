"""Customer-service agent skeleton.

Built in Week 1, reused all course long. Run with --demo to verify your
setup without an API key (canned tool outputs). TODO markers show exactly
where Week 1's LangSmith tracing gets wired in.
"""

import argparse
import json

# ---------------------------------------------------------------------------
# Demo data (canned — lets you run without an API key)
# ---------------------------------------------------------------------------
DEMO_ORDERS = {
    "ORD-1001": {"status": "shipped", "eta": "2026-10-09", "items": ["USB-C cable"]},
    "ORD-1002": {"status": "processing", "eta": "2026-10-14", "items": ["Laptop stand"]},
}

DEMO_DOCS = [
    {"title": "Returns policy", "text": "Returns are accepted within 30 days of delivery."},
    {"title": "Shipping times", "text": "Standard shipping takes 3-5 business days."},
]


class CustomerServiceAgent:
    """A tiny tool-using support agent."""

    def __init__(self, demo: bool = False):
        self.demo = demo
        # TODO (Week 1, Assignment 1): wrap this agent with LangSmith tracing.
        # Hint: from langsmith import traceable — decorate run() and each tool.

    # -- tools ------------------------------------------------------------
    def lookup_order(self, order_id: str) -> dict:
        """Look up an order by ID."""
        # TODO (later weeks): replace canned data with a real lookup.
        return DEMO_ORDERS.get(order_id, {"error": f"unknown order {order_id}"})

    def search_docs(self, query: str) -> list:
        """Keyword search over help docs."""
        stopwords = {"what", "is", "the", "a", "an", "your", "my", "how", "do", "does", "i", "me"}
        words = [w.strip("?.,!").lower() for w in query.split() if w.strip("?.,!").lower() not in stopwords]
        hits = []
        for d in DEMO_DOCS:
            text = (d["title"] + " " + d["text"]).lower()
            if any(w in text for w in words):
                hits.append(d)
        return hits

    def escalate(self, reason: str) -> dict:
        """Hand off to a human agent."""
        return {"escalated": True, "reason": reason}

    # -- main loop ---------------------------------------------------------
    def run(self, user_message: str) -> str:
        """Handle one user message. Returns the agent's reply."""
        # TODO (Week 1, Assignment 1): add @traceable here so every run
        # leaves a trace you can inspect in LangSmith.
        msg = user_message.lower()

        if "order" in msg:
            # naive routing: grab something that looks like an order id
            order_id = next(
                (w.strip("?.,!") for w in user_message.split() if w.startswith("ORD-")),
                None,
            )
            if order_id:
                result = self.lookup_order(order_id)
                if "error" in result:
                    self.escalate("unknown order")
                    return "I couldn't find that order. Let me connect you with a human."
                return (
                    f"Order {order_id} is {result['status']}, "
                    f"expected {result['eta']}. Items: {', '.join(result['items'])}."
                )
            return "Which order ID can I look up for you? (e.g. ORD-1001)"

        if "return" in msg or "ship" in msg:
            docs = self.search_docs(user_message)
            if docs:
                return docs[0]["text"] + " Anything else I can help with?"
            return "I don't have documentation on that yet."

        # TODO (Week 2+): route through a real model call here instead of
        # the demo fallback. Keep the tool interface unchanged — the evals
        # in later weeks depend on it.
        if self.demo:
            return "I can help with orders, returns, and shipping questions. What do you need?"
        return self.escalate("demo mode only — no model wired up yet.")["reason"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Customer-service agent skeleton")
    parser.add_argument("--demo", action="store_true", help="canned responses, no API key needed")
    parser.add_argument("--ask", default="Where is my order ORD-1001?",
                        help="single message to handle")
    args = parser.parse_args()

    agent = CustomerServiceAgent(demo=args.demo)
    reply = agent.run(args.ask)
    print(json.dumps({"input": args.ask, "output": reply}, indent=2))


if __name__ == "__main__":
    main()
