"""Braintrust RAG eval demo (class demo, NOT the assignment).

One command runs a tiny RAG pipeline over 5 questions and scores it with
four standard RAG scorers in Braintrust. Open the experiment link it prints
and walk the class through it.

Setup:
    pip install braintrust autoevals openai
    export BRAINTRUST_API_KEY="..."   (your Braintrust key)
    export NEATLOGS_LLM_KEY="sk-..."  (gateway key, pays for all model calls)

Run:
    python3 braintrust_rag_demo.py

What it does:
    1. Retrieves contexts by keyword overlap over 6 Pronto policy snippets.
    2. Generates an answer with the gateway model, grounded in those contexts.
    3. Scores every case with Faithfulness, AnswerRelevancy, ContextPrecision
       and ContextRecall, and uploads the run to Braintrust as an experiment
       in the "pronto-rag-demo" project.

Two things worth knowing before you run it:
    - Braintrust's Eval hands scorers only input/output/expected, so the four
      RAG scorers (which also need the retrieved context) are wrapped in small
      functions that pull the answer and context out of the task output.
    - The scorers default to a model the gateway does not carry, so each one
      is pinned to gpt-4o-mini, which the gateway does carry.
"""

import os
import re
import sys

MISSING = [v for v in ("BRAINTRUST_API_KEY", "NEATLOGS_LLM_KEY") if not os.environ.get(v)]
if MISSING:
    print("Missing environment variables:", ", ".join(MISSING))
    print("Set them first, then re-run. No keys are stored in this file.")
    sys.exit(1)

try:
    from openai import OpenAI
except ModuleNotFoundError:
    print("Missing package: openai")
    print("Run: pip install braintrust autoevals openai")
    sys.exit(1)

GATEWAY_URL = "https://llm.neatlogs.ai/v1"
GATEWAY_KEY = os.environ["NEATLOGS_LLM_KEY"]

# autoevals builds its scorer LLM client from these env vars, so point them
# at the gateway too: every model call in this demo then uses the $25 credit.
os.environ["OPENAI_API_KEY"] = GATEWAY_KEY
os.environ["OPENAI_BASE_URL"] = GATEWAY_URL

try:
    from autoevals import AnswerRelevancy, ContextPrecision, ContextRecall, Faithfulness
    from braintrust import Eval
except ModuleNotFoundError as e:
    print("Missing package:", e.name)
    print("Run: pip install braintrust autoevals openai")
    sys.exit(1)

MODEL = "gpt-4o-mini"
gen_client = OpenAI(api_key=GATEWAY_KEY, base_url=GATEWAY_URL)

DOCS = [
    "Perishables: full refund if spoiled or damaged on arrival - just send a photo within 24 hours.",
    "Non-perishables: 30-day returns (unopened preferred).",
    "Delivery fee is refunded only if your order is over 60 minutes late, or if Pronto cancels it.",
    "Refunds over $50 need a human's approval - I can't process those myself, but I can start the request for you.",
    "We only substitute items if you opted in at checkout - otherwise we never swap without asking.",
    "Pronto-branded small appliances (like the Pronto air fryer) carry a 1-year limited warranty. Everything else is covered by the manufacturer's warranty.",
]

CASES = [
    ("My strawberries arrived moldy, can I get a refund?",
     "Full refund if spoiled on arrival, photo within 24 hours"),
    ("Can I return a non-perishable item after 20 days?",
     "30-day returns, unopened preferred"),
    ("My order was 90 minutes late, do I get the delivery fee back?",
     "Delivery fee refunded if over 60 minutes late"),
    ("My refund is $75, can you process it now?",
     "Refunds over $50 need a human's approval; the agent can start the request but cannot process it"),
    ("Do you deliver to San Francisco?",
     "Not covered by the policies"),
]

STOPWORDS = {"what", "is", "the", "a", "an", "do", "you", "my", "can", "i", "it", "to", "if", "me"}


def retrieve(question, k=2):
    words = set(re.findall(r"[a-z0-9]+", question.lower())) - STOPWORDS
    scored = sorted(
        DOCS,
        key=lambda d: len(words & set(re.findall(r"[a-z0-9]+", d.lower()))),
        reverse=True,
    )
    return scored[:k]


def task(question):
    contexts = retrieve(question)
    prompt = (
        "Answer the question using ONLY the policies below. "
        "If the policies do not cover it, say exactly: Not covered by the policies.\n\n"
        "POLICIES:\n" + "\n".join(contexts) + "\n\nQUESTION: " + question
    )
    reply = gen_client.chat.completions.create(
        model=MODEL, messages=[{"role": "user", "content": prompt}]
    )
    return {"answer": reply.choices[0].message.content.strip(), "context": "\n".join(contexts)}


def faithfulness(input, output, expected):
    return Faithfulness(model=MODEL).eval(
        input=input, output=output["answer"], expected=expected, context=output["context"]
    )


def answer_relevancy(input, output, expected):
    return AnswerRelevancy(model=MODEL).eval(
        input=input, output=output["answer"], expected=expected, context=output["context"]
    )


def context_precision(input, output, expected):
    return ContextPrecision(model=MODEL).eval(
        input=input, output=output["answer"], expected=expected, context=output["context"]
    )


def context_recall(input, output, expected):
    return ContextRecall(model=MODEL).eval(
        input=input, output=output["answer"], expected=expected, context=output["context"]
    )


Eval(
    "pronto-rag-demo",
    data=[{"input": q, "expected": e} for q, e in CASES],
    task=task,
    scores=[faithfulness, answer_relevancy, context_precision, context_recall],
)
print("\nDone. Open the experiment link printed above and walk through it.")
