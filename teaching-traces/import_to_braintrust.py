"""Import the teaching traces into YOUR OWN Braintrust account.

Prerequisites:
  pip install requests
  export BRAINTRUST_API_KEY=...   # from braintrust.dev -> Settings -> API keys

Run:
  python3 import_to_braintrust.py                  # creates project "pronto-issue-traces"
  python3 import_to_braintrust.py --project my-proj # or reuse an existing project name

What it does:
  1. Creates the project if it doesn't exist (POST /v1/project).
  2. Reads braintrust_spans.jsonl (one span event per line).
  3. Inserts spans in batches of 50 via POST /v1/project_logs/{project_id}/insert.
  4. Prints the project URL when done.

Span shape (each line of the JSONL):
  span_id / root_span_id / span_parents  -> the trace hierarchy
  span_attributes: {name, type}          -> e.g. run_turn/function, chat.completions/llm
  input / output / metadata / tags       -> metadata.issue_category, issue:<category> tag
  metrics: {start, end}                  -> epoch seconds; model spans also carry tokens
"""

import argparse
import json
import os
import sys

import requests

API = "https://api.braintrust.dev"
BATCH = 50


def headers():
    key = os.environ.get("BRAINTRUST_API_KEY")
    if not key:
        sys.exit("Set BRAINTRUST_API_KEY first (braintrust.dev -> Settings -> API keys).")
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def get_or_create_project(name):
    h = headers()
    r = requests.get(f"{API}/v1/project", params={"project_name": name}, headers=h)
    r.raise_for_status()
    for p in r.json().get("objects", r.json() if isinstance(r.json(), list) else []):
        if p.get("name") == name:
            print(f"using existing project '{name}' ({p['id']})")
            return p["id"]
    r = requests.post(f"{API}/v1/project", json={"name": name}, headers=h)
    r.raise_for_status()
    pid = r.json()["id"]
    print(f"created project '{name}' ({pid})")
    return pid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="pronto-issue-traces")
    ap.add_argument("--file", default="braintrust_spans.jsonl")
    args = ap.parse_args()

    pid = get_or_create_project(args.project)
    events = [json.loads(l) for l in open(args.file) if l.strip()]
    print(f"{len(events)} spans -> project {pid}")

    h = headers()
    total = 0
    for i in range(0, len(events), BATCH):
        chunk = events[i:i + BATCH]
        r = requests.post(f"{API}/v1/project_logs/{pid}/insert",
                          json={"events": chunk}, headers=h)
        r.raise_for_status()
        n = len(r.json().get("row_ids", []))
        total += n
        print(f"  batch {i // BATCH + 1}: {n} rows")
    print(f"done: {total} rows. View at https://www.braintrust.dev/app -> {args.project}")


if __name__ == "__main__":
    main()
