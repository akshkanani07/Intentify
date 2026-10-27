"""End-to-end verification script: boots FastAPI server, tests health and all 5 prompt inputs, terminates server."""

from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

# Add pythonpath
root = Path(__file__).resolve().parent

proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8000", "--app-dir", "backend"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
print("Launched FastAPI server on port 8000. Waiting 3 seconds...")
time.sleep(3)

try:
    with urllib.request.urlopen("http://127.0.0.1:8000/api/v1/health") as resp:
        print("HEALTH CHECK:", resp.status, resp.read().decode())

    test_inputs = [
        {"detail": "want to learn c++", "language": "Gujarati"},
        {"detail": "મારે Java શીખવું છે", "language": "Gujarati"},
        {"detail": "Build a scheduling website with calendar sync", "language": "Gujarati"},
        {"detail": "fix this NullPointerException", "language": "Gujarati"},
        {"detail": "kuch banao", "language": "Gujarati"},
    ]

    print("\n=======================================================")
    print(" ENDPOINT POST /api/v1/generate-prompt 5-INPUT VERIFICATION")
    print("=======================================================")
    for payload in test_inputs:
        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:8000/api/v1/generate-prompt",
            data=req_data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            detail_val = payload["detail"]
            print(f"\n[Test Input]: {detail_val}")
            print(f"HTTP Status: {resp.status} | Quality Score: {data['quality_score']}")
            print("Master Prompt Preview:")
            print(data["master_prompt"][:250].strip())
            print("...")

    print("\nAll 5 prompt generation verification calls succeeded with status 200!")
finally:
    proc.terminate()
    proc.wait()
    print("Backend server cleanly terminated.")
