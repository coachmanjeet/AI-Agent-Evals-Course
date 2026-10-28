"""Week 4 method demo: generate a few synthetic golden-set cases, then check
them by hand.

This is a worked example of the synthetic-generation technique, not an
assignment answer: it generates 5 demo cases from the Pronto policy snippets
below. The assignment's generate_cases() stays yours to fill in.

Run:
    export NEATLOGS_LLM_KEY="sk-..."   (or any OpenAI-compatible key)
    python3 synth_demo.py

Writes:
    synth_cases.jsonl    - one valid JSON case per line (the golden-set file)
    synth_cases_raw.txt  - the model's raw reply, always saved

The base URL defaults to the Neatlogs LLM gateway. With your own OpenAI key,
set NEATLOGS_LLM_BASE_URL="https://api.openai.com/v1" instead.
"""

import json
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

FORMAT = "Output ONLY JSON lines. No intro, no numbered list, no explanation, no markdown fences."

PROMPT = f"""{FORMAT}

Write 5 test questions for a customer-service agent, grounded ONLY in these policies. Do not invent new policy terms.

POLICIES:
{POLICIES}

Each line is one JSON object with exactly these fields: question, contexts (list of {{"title", "text"}} copied from the policies above), ground_truth (what a correct answer must contain), source ("synthetic"), difficulty ("easy", "medium" or "hard"), intent ("policy-lookup"), segment ("policy").
Mix difficulties. Make one edge case: an ambiguous question, or one the policies cannot answer.
Example of ONE line:
{{"question": "My strawberries arrived moldy, can I get a refund?", "contexts": [{{"title": "Perishables policy", "text": "Perishables: full refund if spoiled or damaged on arrival - just send a photo within 24 hours."}}], "ground_truth": "Full refund if spoiled on arrival, photo within 24 hours", "source": "synthetic", "difficulty": "easy", "intent": "policy-lookup", "segment": "policy"}}

{FORMAT}"""


def generate(prompt):
    reply = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[{"role": "user", "content": prompt}],
    )
    return reply.choices[0].message.content


def parse(text):
    """Pull JSON cases out of a reply, tolerating fences, numbering, and a
    single JSON array instead of lines. Returns a list of dicts (maybe empty)."""
    lines = [ln for ln in text.splitlines() if not ln.strip().startswith("```")]
    joined = "\n".join(lines).strip()
    try:
        data = json.loads(joined)
        if isinstance(data, list):
            return [c for c in data if isinstance(c, dict)]
    except json.JSONDecodeError:
        pass
    decoder = json.JSONDecoder()
    cases = []
    for ln in lines:
        idx = ln.find("{")
        if idx < 0:
            continue
        try:
            obj, _ = decoder.raw_decode(ln[idx:])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            cases.append(obj)
    return cases


raw = generate(PROMPT)
cases = parse(raw)
if len(cases) < 5:
    raw = generate(PROMPT + "\n\nReminder: output ONLY 5 JSON lines, nothing else.")
    cases = parse(raw)

with open("synth_cases_raw.txt", "w") as f:
    f.write(raw)
with open("synth_cases.jsonl", "w") as f:
    for c in cases:
        f.write(json.dumps(c) + "\n")

for c in cases:
    print(json.dumps(c))
print(f"\nWrote {len(cases)} cases to synth_cases.jsonl (raw reply in synth_cases_raw.txt).")
if len(cases) < 5:
    print("Fewer than 5 valid cases parsed: copy the good ones by hand from synth_cases_raw.txt.")
