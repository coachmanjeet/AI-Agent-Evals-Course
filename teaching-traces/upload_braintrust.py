"""Upload generated spans to the pronto-issue-traces Braintrust project.

Run: python3 upload_braintrust.py   (from this folder, after generate_traces.py)
Uses the course bt_api.py helper (curl transport, authd credential).
"""

import json
import subprocess
import sys

PROJECT_ID = "f0d8b02e-434e-4de1-b9cf-1ecdfa92e9f3"
BT_API = "/home/hatch/workspace/custom-connectors/custom.braintrust/bin/bt_api.py"
BATCH = 50


def main():
    events = [json.loads(line) for line in
              open("braintrust_spans.jsonl") if line.strip()]
    print(f"{len(events)} spans to upload in batches of {BATCH}")
    total_rows = 0
    for i in range(0, len(events), BATCH):
        chunk = events[i:i + BATCH]
        with open("/tmp/bt_upload_chunk.json", "w") as f:
            json.dump({"events": chunk}, f)
        r = subprocess.run(
            [sys.executable, BT_API, "POST",
             f"/v1/project_logs/{PROJECT_ID}/insert",
             "/tmp/bt_upload_chunk.json"],
            capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            print(f"batch {i // BATCH + 1} FAILED:\n{r.stdout}\n{r.stderr}")
            sys.exit(1)
        try:
            n = len(json.loads(r.stdout).get("row_ids", []))
        except Exception:
            print(f"batch {i // BATCH + 1} bad response:\n{r.stdout}")
            sys.exit(1)
        total_rows += n
        print(f"batch {i // BATCH + 1}: {n} rows")
    print(f"done: {total_rows} rows inserted")


if __name__ == "__main__":
    main()
