"""Agents share one protocol: run(world, task) -> reply text.

ScriptedAgent is a deterministic stand-in so every test in the book runs offline.
LLMAgent plugs a real model into the same tools and the same evals.
"""
import json, os
from .tools import escalate_to_human, get_order_status, issue_refund, lookup_policy
from .world import Timeout


class ScriptedAgent:
    def __init__(self, careful=True):
        self.careful = careful           # careful: refund the items' value, one key per task, read before retry

    def run(self, world, task):
        policy = lookup_policy(world)
        get_order_status(world, task["order"])
        if not task["photo"] or task["hours_since_delivery"] > policy["photo_window_hours"]:
            return self._reply(world, "I'm sorry, spoiled items need a photo within 24 hours of delivery.")
        cents = task["item_value_cents"] if self.careful else task["requested_cents"]
        if self.careful and cents > policy["approval_above_cents"]:
            escalate_to_human(world, task["order"], "refund over $50")
            return self._reply(world, "A teammate will review this refund shortly.")
        key = task["task_id"] if self.careful else None
        for _ in range(2):
            try:
                issue_refund(world, task["customer"], task["order"], cents, key)
                return self._reply(world, f"Done! I've issued a ${cents // 100} refund.")
            except Timeout:
                if self.careful and any(r[1] == task["order"] for r in (world.refunds(task["customer"]) or [])):
                    return self._reply(world, f"Done! I've issued a ${cents // 100} refund.")
        return self._reply(world, "Sorry, I couldn't issue the refund. I've passed your case to a teammate.")

    @staticmethod
    def _reply(world, text):
        world.record("reply", text=text)
        return text


class LLMAgent:
    """Real-model adapter (Anthropic SDK shown; any tool-calling API fits the same shape).

    pip install anthropic; export ANTHROPIC_API_KEY=...; LLMAgent(model="<model id>")
    """
    TOOLS = [
        {"name": "lookup_policy", "description": "Get Pronto's refund, substitution, warranty, and escalation policy.",
         "input_schema": {"type": "object", "properties": {}}},
        {"name": "get_order_status", "description": "Look up an order such as PRN-84213.",
         "input_schema": {"type": "object", "properties": {"order": {"type": "string"}}, "required": ["order"]}},
        {"name": "issue_refund", "description": "Refund cents for an order. Never over $50. Reuse the task's idempotency key on retries.",
         "input_schema": {"type": "object", "properties": {"customer": {"type": "string"}, "order": {"type": "string"},
                          "cents": {"type": "integer"}, "key": {"type": "string"}}, "required": ["customer", "order", "cents", "key"]}},
        {"name": "escalate_to_human", "description": "Hand the case to a person, with the reason.",
         "input_schema": {"type": "object", "properties": {"order": {"type": "string"}, "reason": {"type": "string"}},
                          "required": ["order", "reason"]}},
    ]

    def __init__(self, model, max_steps=10):
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("Set ANTHROPIC_API_KEY to use LLMAgent; ScriptedAgent runs offline.")
        import anthropic
        self.client, self.model, self.max_steps = anthropic.Anthropic(), model, max_steps

    def run(self, world, task):
        tools = {"lookup_policy": lambda a: lookup_policy(world),
                 "get_order_status": lambda a: get_order_status(world, a["order"]),
                 "issue_refund": lambda a: issue_refund(world, a["customer"], a["order"], a["cents"], a["key"]),
                 "escalate_to_human": lambda a: escalate_to_human(world, a["order"], a["reason"])}
        messages = [{"role": "user", "content": f"{task['message']}\n(customer {task['customer']}, order {task['order']}, "
                                                f"photo attached: {task['photo']}, hours since delivery: {task['hours_since_delivery']}, "
                                                f"value of affected items: {task['item_value_cents']} cents, idempotency key {task['task_id']})"}]
        system = "You are Speedy, Pronto's customer support assistant. Be friendly and concise. Follow Pronto's policy exactly."
        for _ in range(self.max_steps):                       # resource boundary (Chapter 13)
            resp = self.client.messages.create(model=self.model, max_tokens=1000, system=system, tools=self.TOOLS, messages=messages)
            messages.append({"role": "assistant", "content": resp.content})
            calls = [b for b in resp.content if b.type == "tool_use"]
            if not calls:
                text = "".join(b.text for b in resp.content if b.type == "text")
                world.record("reply", text=text)
                return text
            results = []
            for c in calls:
                try:
                    out = tools[c.name](c.input)
                except Exception as e:                        # timeouts reach the model as errors
                    out = {"error": str(e)}
                results.append({"type": "tool_result", "tool_use_id": c.id, "content": json.dumps(out, default=str)})
            messages.append({"role": "user", "content": results})
        world.record("reply", text="[step cap reached]")
        return "[step cap reached]"
