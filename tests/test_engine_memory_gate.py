"""Tests for MemoryGate: validation, purge, and deduplication."""

import json
from pathlib import Path
import pytest
from app.engine.memory_gate import MemoryGate


def test_memory_gate_purge():
    mg = MemoryGate()
    result = mg.purge_corrupted_memories()
    assert result["scanned"] >= 0
    assert result["retained"] >= 0

    # Read back store to verify no wedding + finance contamination remains
    with open(mg.store_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for m in data.get("memories", []):
        goal = m.get("goal", "").lower()
        domain = m.get("domain", "").lower()
        assumptions = " ".join(m.get("smart_assumptions", [])).lower()

        # No wedding in Finance
        if "wedding" in goal:
            assert domain != "finance"
            assert "sec" not in assumptions
            assert "finra" not in assumptions

        # No goal echoing
        assert "a want to" not in goal
        assert "build a mare" not in goal


def test_memory_gate_admission():
    mg = MemoryGate()
    # Bad memory should fail
    assert not mg.validate_admission(
        goal="Build a mare wedding planner in Udaipur",
        domain="Finance",
        quality_score=95.0,
        assumptions=["Comply with SEC and FINRA rules"],
    )

    # Low score should fail
    assert not mg.validate_admission(
        goal="Build a scheduling website",
        domain="SaaS",
        quality_score=70.0,
    )

    # Valid memory should pass
    assert mg.validate_admission(
        goal="Build a production-grade scheduling website with automated calendar synchronization",
        domain="Scheduling SaaS Platform",
        quality_score=95.0,
        assumptions=["PostgreSQL with UTC timezone"],
    )
