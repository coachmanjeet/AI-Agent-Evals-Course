"""Week 4 method demo: generate a few synthetic golden-set cases, then check
them by hand.

This is a worked example of the synthetic-generation technique, not an
assignment answer: it generates 5 demo cases from the Pronto policy snippets
below. The assignment's generate_cases() stays yours to fill in.

Run:
    export NEATLOGS_LLM_KEY="sk-..."   (or any OpenAI-compatible key)
    python3 synth_demo.py

The base URL defaults to the Neatlogs LLM gateway. With your own OpenAI key,
set NEATLOGS_LLM_BASE_URL="https://api.openai.com/v1" instead.

Prints 5 cases as JSON lines. The teacher curates them by hand on screen.
No case is trusted until it is hand-checked: that is the lesson.
"""

import os

from openai import OpenAI

client = OpenAI(
    api_key=os.environ["NEATLOGS_LLM_KEY"],
    base_url=os.environ.get(
        "NEATLOGS_LLM_BASE_URL", "https://llm.neatlogs.ai/v1"
    ),
)

POLICIES = """1. Perishables: full refund if spoiled or damaged on arrival - just send a photo within 24 hours.
2. Non-perishables: 30-day returns (unopened preferred).
3. Delivery fee is refunded only if your order is over 60 minutes late, or if Pronto cancels it.
4. Refunds over $50 need a human's approval - I can't process those myself, but I can start the request for you.
5. We only substitute items if you opted in at checkout - otherwise we never swap without asking.
6. Pronto-branded small appliances (like the Pronto air fryer) carry a 1-year limited warranty. Everything else is covered by the manufacturer's warranty."""

PROMPT = f"""Write 5 test questions for a customer-service agent, grounded ONLY in
these policies. Do not invent new policy terms.

POLICIES:
{POLICIES}

Rules:
- Output exactly 5 lines, one JSON object per line, no other text.
- Each object has: question, contexts (list of {{"title", "text"}} copied from
  the policies above), ground_truth (what a correct answer must contain),
  source ("synthetic"), difficulty ("easy", "medium" or "hard"),
  intent ("policy-lookup"), segment ("policy").
- Mix difficulties. Make one edge case: an ambiguous question, or one the
  policies cannot answer.
- Example line:
{{"question": "My strawberries arrived moldy, can I get a refund?", "contexts": [{{"title": "Perishables policy", "text": "Perishables: full refund if spoiled or damaged on arrival - just send a photo within 24 hours."}}], "ground_truth": "Full refund if spoiled on arrival, photo within 24 hours", "source": "synthetic", "difficulty": "easy", "intent": "policy-lookup", "segment": "policy"}}
"""

reply = client.chat.completions.create(
    model="gpt-5-nano",
    messages=[{"role": "user", "content": PROMPT}],
)
print(reply.choices[0].message.content)
