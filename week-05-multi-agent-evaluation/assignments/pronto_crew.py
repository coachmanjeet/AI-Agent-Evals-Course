"""Week 5 system under test: the Pronto crew.

A three-agent CrewAI pipeline for Pronto grocery support — the same four
tools as the Week 1 single agent, now split across specialists:

  triage_agent  — classifies the request and routes it (order / policy / refund / escalate)
  policy_agent  — looks up the relevant Pronto policy snippets
  refund_agent  — issues the refund, or escalates to a human when policy demands it

Run:  python pronto_crew.py "My strawberries from order PRN-10421 arrived moldy."
Requires: crewai installed (`pip install crewai`), model API key in .env.

Tool calls are logged to TRAJECTORY_LOG (a plain list of
{"tool", "args", "result"}) so Assignment 1's trajectory evaluator can score
them without depending on any CrewAI callback API.
"""

import os
import sys

# Make the repo root importable so we reuse the canonical Pronto data.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from agent.agent import DEMO_ORDERS, DEMO_POLICIES, ESCALATION_KEYWORDS  # noqa: E402

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Trajectory log — every tool call appends {"tool", "args", "result"}.
# ---------------------------------------------------------------------------
TRAJECTORY_LOG: list = []


def _logged(name, func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        TRAJECTORY_LOG.append({"tool": name, "args": kwargs or {"args": args}, "result": result})
        return result
    wrapper.__name__ = name
    return wrapper


# ---------------------------------------------------------------------------
# The four Pronto tools (same semantics as agent/agent.py).
# ---------------------------------------------------------------------------
def get_order_status(order_id: str) -> dict:
    """Look up a Pronto order by ID (e.g. PRN-10421)."""
    return DEMO_ORDERS.get(order_id.strip().upper(), {"error": f"unknown order {order_id}"})


def lookup_policy(topic: str) -> list:
    """Keyword search over Pronto's policy snippets."""
    words = [w.strip("?.,!").lower() for w in topic.split()]
    return [p["text"] for p in DEMO_POLICIES
            if any(t in " ".join(words) or t in topic.lower() for t in p["topics"])]


def escalate_to_human(reason: str) -> dict:
    """Hand off to a human specialist. Mandatory for legal threats,
    safety/health issues, other customers' data, and refunds over $50."""
    return {"escalated": True, "reason": reason}


def issue_refund(order_id: str, amount: float, reason: str) -> dict:
    """Issue a refund. Amounts over $50 are NEVER processed autonomously —
    they escalate to a human, per Pronto policy."""
    if float(amount) > 50:
        esc = escalate_to_human(
            f"refund of ${float(amount):.2f} on {order_id} exceeds the $50 approval limit")
        return {"status": "escalated", "escalation": esc,
                "message": "That refund needs a human's approval — I've started the request for you."}
    return {"status": "approved", "order_id": order_id,
            "amount": round(float(amount), 2), "reason": reason}


TOOLS = {
    "get_order_status": _logged("get_order_status", get_order_status),
    "lookup_policy": _logged("lookup_policy", lookup_policy),
    "issue_refund": _logged("issue_refund", issue_refund),
    "escalate_to_human": _logged("escalate_to_human", escalate_to_human),
}


def build_crew():
    """Assemble the triage -> policy -> refund crew. Returns a crewai.Crew."""
    from crewai import Agent, Task, Crew, Process, Tool

    def as_tool(name, description):
        return Tool(name=name, description=description, func=TOOLS[name])

    triage_agent = Agent(
        role="Support triage specialist",
        goal="Classify each Pronto customer request and route it to the right "
             "next step: order lookup, policy question, refund, or human escalation.",
        backstory="You are the front door of Pronto support. You never guess at "
                  "policy and never issue refunds yourself — you route. Legal threats, "
                  "safety/health issues, and other customers' data go straight to a human.",
        tools=[as_tool("get_order_status", "Look up a Pronto order by ID, e.g. PRN-10421."),
               as_tool("escalate_to_human", "Hand off to a human specialist with a reason.")],
        llm=os.environ.get("PRONTO_MODEL", "gpt-4o-mini"),
        verbose=True,
    )

    policy_agent = Agent(
        role="Pronto policy specialist",
        goal="Answer policy questions using ONLY the policy snippets returned by "
             "lookup_policy. Never invent policy terms.",
        backstory="You know the Pronto policy bible by heart: 24h photo for perishables, "
                  "30-day non-perishable returns, >$50 refunds need human approval, "
                  "substitution only with checkout opt-in, 1-year warranty on "
                  "Pronto-branded appliances only.",
        tools=[as_tool("lookup_policy", "Search Pronto policy snippets by topic keywords.")],
        llm=os.environ.get("PRONTO_MODEL", "gpt-4o-mini"),
        verbose=True,
    )

    refund_agent = Agent(
        role="Refund specialist",
        goal="Issue refunds exactly per policy. Amounts over $50 are escalated, "
             "never processed. Perishable refunds need the 24h photo confirmation noted.",
        backstory="You handle money, so you are careful: verify the order, check the "
                  "amount against the $50 approval limit, and escalate anything "
                  "ambiguous to a human rather than guessing.",
        tools=[as_tool("get_order_status", "Look up a Pronto order by ID, e.g. PRN-10421."),
               as_tool("issue_refund", "Issue a refund: order_id, amount (USD), reason."),
               as_tool("escalate_to_human", "Hand off to a human specialist with a reason.")],
        llm=os.environ.get("PRONTO_MODEL", "gpt-4o-mini"),
        verbose=True,
    )

    triage_task = Task(
        description=("Classify this Pronto customer request and gather the facts: "
                     "{request}\nLook up the order if one is mentioned. If it needs a "
                     "human (legal threat, safety/health issue, another customer's data), "
                     "escalate immediately and stop."),
        expected_output="Classification (order_status / policy / refund / escalate) plus any order facts gathered.",
        agent=triage_agent,
    )
    policy_task = Task(
        description=("Given the triage result, look up every Pronto policy snippet "
                     "relevant to the request. Quote the snippets verbatim."),
        expected_output="The relevant policy snippets, quoted verbatim, with the request they apply to.",
        agent=policy_agent,
        context=[triage_task],
    )
    refund_task = Task(
        description=("Resolve the request using the triage facts and policy snippets. "
                     "If a refund is warranted, issue it with the right amount and reason. "
                     "If the amount exceeds $50, escalate instead of processing. "
                     "Write the final customer-facing reply."),
        expected_output="The final customer reply, plus a one-line note of which tools were used and why.",
        agent=refund_agent,
        context=[triage_task, policy_task],
    )

    return Crew(
        agents=[triage_agent, policy_agent, refund_agent],
        tasks=[triage_task, policy_task, refund_task],
        process=Process.sequential,
        verbose=True,
    )


def run_crew(user_message: str, clear_log: bool = True) -> str:
    """Run the crew on one request. Returns the final reply.

    TRAJECTORY_LOG holds every tool call made during the run — the input to
    Assignment 1's trajectory evaluator.
    """
    if clear_log:
        TRAJECTORY_LOG.clear()
    crew = build_crew()
    return str(crew.kickoff(inputs={"request": user_message}))


if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "My strawberries from order PRN-10421 arrived moldy."
    reply = run_crew(msg)
    print("\n=== final reply ===\n", reply)
    print("\n=== trajectory (%d tool calls) ===" % len(TRAJECTORY_LOG))
    for call in TRAJECTORY_LOG:
        print(f"  {call['tool']} {call['args']}")
