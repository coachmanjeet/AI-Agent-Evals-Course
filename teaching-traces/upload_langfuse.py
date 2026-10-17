"""Upload generated observations to Langfuse via the ingestion API.

Needs env vars (export them first — never commit keys):
  LANGFUSE_HOST        e.g. https://cloud.langfuse.com
  LANGFUSE_PUBLIC_KEY
  LANGFUSE_SECRET_KEY

Run: python3 upload_langfuse.py   (from this folder, after generate_traces.py)
Uses curl (this VM's egress proxy hangs urllib tunnels).
"""

import base64
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone

BATCH = 100


def main():
    host = os.environ.get("LANGFUSE_HOST", "").rstrip("/")
    pk = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
    sk = os.environ.get("LANGFUSE_SECRET_KEY", "")
    if not (host and pk and sk):
        sys.exit("Set LANGFUSE_HOST, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY first.")
    token = base64.b64encode(f"{pk}:{sk}".encode()).decode()
    items = json.load(open("langfuse_batch.json"))["batch"]
    # Ingestion API requires a per-event envelope: id / type / timestamp / body.
    # The batch file stores {type, body}; add the envelope here at upload time.
    now = datetime.now(timezone.utc).isoformat()
    events = []
    for e in items:
        body = e["body"]
        events.append({
            "id": str(uuid.uuid4()),
            "type": e["type"],
            "timestamp": body.get("timestamp") or body.get("startTime") or now,
            "body": body,
        })
    items = events
    print(f"{len(items)} items to upload in batches of {BATCH}")
    for i in range(0, len(items), BATCH):
        chunk = items[i:i + BATCH]
        with open("/tmp/lf_chunk.json", "w") as f:
            json.dump({"batch": chunk}, f)
        r = subprocess.run(
            ["curl", "-sS", "-X", "POST", f"{host}/api/public/ingestion",
             "-H", "Content-Type: application/json",
             "-H", f"Authorization: Basic {token}",
             "--data-binary", "@/tmp/lf_chunk.json",
             "-w", "\n%{http_code}"],
            capture_output=True, text=True, timeout=120)
        body, _, code = r.stdout.rpartition("\n")
        if r.returncode != 0 or code.strip() != "200":
            print(f"batch {i // BATCH + 1} FAILED (http {code}):\n{body}\n{r.stderr}")
            sys.exit(1)
        print(f"batch {i // BATCH + 1}: ok")
    print("done")


if __name__ == "__main__":
    main()
