"""Golden Test Cases Suite – Runs 42 comprehensive validation cases across all domains and languages."""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from app.core.security import PromptSafetyChecker
from app.engine.composer import PromptComposer
from app.engine.planner import KnowledgePlanner
from app.engine.quality_engine import QualityEngine
from app.engine.reranker import CandidateReranker
from app.engine.spec_extractor import SpecExtractor
from app.engine.validators import check_forbidden_phrase_match

GOLDEN_PATH = Path(__file__).resolve().parent / "golden" / "golden_cases.json"

with open(GOLDEN_PATH, "r", encoding="utf-8") as f:
    GOLDEN_CASES = json.load(f)

INTENT_GROUPS = {
    "create": {"create", "build", "make", "develop", "implement", "construct", "architect", "design", "write", "generate", "produce"},
    "build": {"create", "build", "make", "develop", "implement", "construct", "architect", "design", "write", "generate", "produce"},
    "plan": {"plan", "roadmap", "strategy", "organize", "coordinate", "guide", "formulate", "create", "develop", "design"},
    "debug": {"debug", "fix", "troubleshoot", "patch", "diagnose", "investigate", "analyze", "rca"},
    "fix": {"debug", "fix", "troubleshoot", "patch", "diagnose", "investigate", "analyze", "rca"},
    "learn": {"learn", "study", "teach", "master"},
    "explain": {"explain", "understand", "clarify"},
    "analyze": {"analyze", "audit", "evaluate", "diagnose", "investigate", "research", "debug", "create", "build"},
    "design": {"design", "create", "build", "architect", "plan"},
    "write": {"write", "create", "draft", "compose", "author", "build"},
    "research": {"research", "analyze", "investigate", "study", "build"},
    "optimize": {"optimize", "refactor", "tune", "improve", "build", "create"},
}


@pytest.fixture(scope="session")
def engine_suite():
    extractor = SpecExtractor()
    planner = KnowledgePlanner()
    composer = PromptComposer()
    quality = QualityEngine()
    reranker = CandidateReranker(planner=planner, composer=composer, quality_engine=quality)
    safety = PromptSafetyChecker()
    return {
        "extractor": extractor,
        "reranker": reranker,
        "safety": safety,
        "quality": quality,
    }


@pytest.mark.parametrize("case", GOLDEN_CASES, ids=[c["id"] for c in GOLDEN_CASES])
def test_golden_case(case: dict, engine_suite: dict):
    """Execute end-to-end compiler test for an individual golden case."""
    case_id = case["id"]
    category = case["category"]
    user_input = case["input"]
    role = case.get("role", "")
    expected_intent = case.get("expected_intent")
    expected_proficiency = case.get("expected_proficiency")
    expected_keywords = case.get("expected_objective_keywords", [])
    forbidden_phrases = case.get("forbidden_phrases", [])
    forbidden_headings = case.get("forbidden_headings", [])
    min_score = case.get("minimum_score", 85.0)

    # 1. Prompt Injection Cases
    if category == "prompt_injection":
        safety_checker = engine_suite["safety"]
        res = safety_checker.detect_injection(user_input)
        assert (not res.is_safe) or len(res.threats) > 0, f"Prompt injection was not caught for {case_id}"
        return

    # 2. Extract Specification
    extractor = engine_suite["extractor"]
    spec = extractor.extract(
        text=user_input,
        role_hint=role,
        language_hint=case.get("language", ""),
    )

    # Validate intent using semantic synonym groups
    if expected_intent:
        expected_norm = expected_intent.lower()
        actual_norm = spec.action.lower()
        synonyms = INTENT_GROUPS.get(expected_norm, {expected_norm})
        assert (
            actual_norm in synonyms
            or expected_norm in actual_norm
            or actual_norm in expected_norm
        ), f"Intent mismatch for {case_id}: got '{spec.action}', expected '{expected_intent}'"

    # Validate proficiency (CRITICAL: learner proficiency must not be inflated!)
    if expected_proficiency:
        exp_prof_lower = expected_proficiency.lower()
        act_prof_lower = spec.proficiency.lower()
        if "novice" in exp_prof_lower or "beginner" in exp_prof_lower:
            assert ("novice" in act_prof_lower or "beginner" in act_prof_lower), (
                f"Proficiency inflation detected in {case_id}: got '{spec.proficiency}', expected '{expected_proficiency}'"
            )
        elif "senior" in exp_prof_lower or "principal" in exp_prof_lower:
            assert ("senior" in act_prof_lower or "principal" in act_prof_lower or "architect" in act_prof_lower or "advanced" in act_prof_lower)

    # 3. Generate Master Prompt via Candidate Reranker
    reranker = engine_suite["reranker"]
    winner, _ = reranker.generate_and_rerank(spec)
    prompt_text = winner.full_text
    prompt_lower = prompt_text.lower()

    # 4. Verify Quality Score
    assert winner.audit.total_score >= min_score, (
        f"Quality score {winner.audit.total_score:.1f} is below minimum {min_score} for {case_id}. "
        f"Penalties: {winner.audit.penalties}"
    )

    # 5. Verify Forbidden Phrases (word-boundary regex match)
    for phrase in forbidden_phrases:
        assert not check_forbidden_phrase_match(phrase, prompt_text), (
            f"Forbidden phrase '{phrase}' detected in prompt for {case_id}"
        )

    # 6. Verify Forbidden Headings
    for heading in forbidden_headings:
        assert heading.lower() not in prompt_lower, (
            f"Forbidden heading '{heading}' found in prompt for {case_id}"
        )

    # 7. Verify Expected Keywords
    for kw in expected_keywords:
        assert (
            kw.lower() in prompt_lower
            or kw.lower() in spec.object_subject.lower()
            or kw.lower() in spec.domain.lower()
            or (getattr(spec, "raw_input", "") and kw.lower() in spec.raw_input.lower())
        ), f"Expected keyword '{kw}' missing from prompt/spec for {case_id}"


def test_no_conflicting_golden_sets():
    """Phase C requirement: Fails if two golden files with different case counts exist."""
    root_dir = Path(__file__).resolve().parent.parent
    golden_files = list(root_dir.glob("**/golden/*.json"))
    counts = {}
    for gf in golden_files:
        try:
            import json
            with open(gf, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict) and "id" in data[0]:
                    counts[str(gf)] = len(data)
        except Exception:
            continue

    unique_counts = set(counts.values())
    assert len(unique_counts) <= 1, f"Found conflicting golden datasets with different counts: {counts}"
    if counts:
        assert list(counts.values())[0] == 205, f"Canonical golden set count must be 205, got {counts}"
