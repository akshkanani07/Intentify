"""End-to-end HTTP verification using FastAPI TestClient across all 5 user inputs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / "backend"))
sys.path.insert(0, str(BASE / "ml-engine"))

from fastapi.testclient import TestClient
from app.main import create_app

app = create_app()
client = TestClient(app)

print("\n=======================================================")
print(" 1. HEALTH ENDPOINT VERIFICATION")
print("=======================================================")
resp = client.get("/api/v1/health")
print("GET /api/v1/health -> Status:", resp.status_code, resp.json())
assert resp.status_code == 200

test_inputs = [
    {"detail": "want to learn c++", "language": "Gujarati"},
    {"detail": "મારે Java શીખવું છે", "language": "Gujarati"},
    {"detail": "Build a scheduling website with calendar sync", "language": "Gujarati"},
    {"detail": "fix this NullPointerException", "language": "Gujarati"},
    {"detail": "kuch banao", "language": "Gujarati"},
]

print("\n=======================================================")
print(" 2. POST /api/v1/generate-prompt 5-INPUT VERIFICATION")
print("=======================================================")

for idx, item in enumerate(test_inputs, 1):
    detail = item["detail"]
    lang = item["language"]
    payload = {"detail": detail, "language": lang}
    
    r = client.post("/api/v1/generate-prompt", json=payload)
    assert r.status_code == 200, f"Failed on input '{detail}': {r.text}"
    data = r.json()
    
    print(f"\n[{idx}/5] Input: \"{detail}\"")
    print(f"Status: {r.status_code} | Quality Score: {data.get('quality_score')} | Intent: {data.get('metadata', {}).get('detected_intent')}")
    print(f"Domain: {data.get('metadata', {}).get('detected_domain')} | Role: {data.get('metadata', {}).get('aligned_role')}")
    print("Master Prompt Preview (first 250 chars):")
    prompt_text = data.get("master_prompt", "")
    print(prompt_text[:250].strip())
    print("...")

print("\nAll 5 prompt generation verification calls succeeded with status 200 and enterprise scores!")
