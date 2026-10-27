"""Unit tests for Audience and Seniority detection based on explicit signals and invariants.

Rules tested:
  (a) Explicit self-description in user text ALWAYS wins.
  (b) Explicit role in request.
  (c) Action = learn -> default to Beginner unless (a) or (b) contradicts it.
      Hard rule: learn-intent NEVER resolves to Senior or Expert without explicit self-statement.
  (d) Technical vocabulary is weak evidence (cannot raise learn requests to Senior/Expert).
"""

import pytest
from app.engine.spec_extractor import SpecExtractor
from app.nlp.audience_detector import AudienceDetector


@pytest.fixture
def extractor():
    return SpecExtractor()


@pytest.fixture
def detector():
    return AudienceDetector()


def test_learn_distributed_systems_never_senior(extractor):
    """'want to learn distributed systems' -> Beginner or Intermediate, never Senior."""
    spec = extractor.extract("want to learn distributed systems")
    prof = spec.proficiency.lower()
    assert not any(s in prof for s in ["senior", "expert", "principal", "lead", "architect"]), (
        f"Learn intent should never be Senior without explicit statement. Got: {spec.proficiency}"
    )
    assert any(b in prof for b in ["novice", "beginner", "intermediate", "practitioner"])


def test_senior_engineer_learning_retains_senior(extractor):
    """'I am a senior engineer and want to learn distributed systems' -> Senior."""
    spec = extractor.extract("I am a senior engineer and want to learn distributed systems")
    prof = spec.proficiency.lower()
    assert any(s in prof for s in ["senior", "expert", "principal", "lead", "architect"]), (
        f"Explicit senior self-description must produce Senior proficiency. Got: {spec.proficiency}"
    )


def test_production_kafka_cluster_can_be_senior(extractor):
    """'build a production multi-region Kafka cluster' (no learn verb, advanced tech) -> can be Senior."""
    spec = extractor.extract("build a production multi-region Kafka cluster")
    prof = spec.proficiency.lower()
    assert any(s in prof for s in ["senior", "expert", "principal", "lead", "architect", "advanced"]), (
        f"Production advanced distributed systems request should resolve to Senior. Got: {spec.proficiency}"
    )


def test_vague_kuch_banao_is_beginner(extractor):
    """'kuch banao' -> Beginner."""
    spec = extractor.extract("kuch banao")
    prof = spec.proficiency.lower()
    assert any(b in prof for b in ["novice", "beginner"]), (
        f"Vague 'kuch banao' must resolve to Beginner. Got: {spec.proficiency}"
    )


def test_explain_like_i_am_10_is_beginner(extractor):
    """'explain quantum computing like I am 10' -> Beginner."""
    spec = extractor.extract("explain quantum computing like I am 10")
    prof = spec.proficiency.lower()
    assert any(b in prof for b in ["novice", "beginner"]), (
        f"Explicit 'like I am 10' must resolve to Beginner. Got: {spec.proficiency}"
    )


def test_explicit_student_role_hint_is_beginner(extractor):
    """Explicit role='Student' overrides technical terms."""
    spec = extractor.extract("Configure zero-trust Kubernetes mesh", role_hint="Student")
    prof = spec.proficiency.lower()
    assert any(b in prof for b in ["novice", "beginner"]), (
        f"Explicit role hint 'Student' must resolve to Beginner. Got: {spec.proficiency}"
    )


def test_explicit_senior_role_hint_is_senior(extractor):
    """Explicit role='Senior Architect' produces Senior."""
    spec = extractor.extract("How does caching work?", role_hint="Senior Architect")
    prof = spec.proficiency.lower()
    assert any(s in prof for s in ["senior", "architect", "expert", "lead"]), (
        f"Explicit role hint 'Senior Architect' must resolve to Senior. Got: {spec.proficiency}"
    )
