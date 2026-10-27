"""Tests for SpecExtractor and Pydantic v2 PromptSpec."""

import pytest
from app.engine.spec_extractor import PromptSpec, SpecExtractor


@pytest.fixture
def extractor():
    return SpecExtractor()


def test_learn_java_gujarati_proficiency_not_inflated(extractor):
    spec = extractor.extract("મારે Java શીખવું છે", role_hint="teacher")
    assert isinstance(spec, PromptSpec)
    assert spec.action == "Learn"
    assert "java" in spec.object_subject.lower()
    assert spec.input_language == "Gujarati"
    # CRITICAL: Persona role can be instructor/mentor, but learner proficiency must NOT be Principal!
    assert "novice" in spec.proficiency.lower() or "beginner" in spec.proficiency.lower()
    assert spec.proficiency != "Principal"
    assert spec.proficiency != "Enterprise Architect"


def test_saas_scheduling_website(extractor):
    spec = extractor.extract("Build a scheduling website with calendar sync")
    assert isinstance(spec, PromptSpec)
    assert spec.action.lower() in ["build", "create", "architect"]
    assert "scheduling" in spec.object_subject.lower() or "website" in spec.object_subject.lower()
    assert "saas" in spec.deliverable.lower() or "architecture" in spec.deliverable.lower() or "web" in spec.deliverable.lower()


def test_destination_wedding_udaipur_not_finance(extractor):
    spec = extractor.extract("મારા લગ્ન માટે ઉદયપુરમાં 50 lakh budget")
    assert isinstance(spec, PromptSpec)
    assert spec.domain != "Finance"
    assert "event" in spec.domain.lower() or "hospitality" in spec.domain.lower() or "wedding" in spec.domain.lower()
    assert "wedding" in spec.deliverable.lower() or "event" in spec.deliverable.lower()


def test_debug_error_intent(extractor):
    spec = extractor.extract("fix this error: NullPointerException")
    assert isinstance(spec, PromptSpec)
    assert spec.action.lower() in ["debug", "fix"]
    assert "nullpointerexception" in spec.object_subject.lower() or "error" in spec.object_subject.lower()
    assert "rca" in spec.deliverable.lower() or "patch" in spec.deliverable.lower() or "diagnostic" in spec.deliverable.lower()


def test_unknown_domain_organic_farming(extractor):
    spec = extractor.extract("Develop an organic farming crop rotation and soil sensor monitoring app")
    assert isinstance(spec, PromptSpec)
    assert spec.action.lower() in ["build", "develop", "create"]
    assert len(spec.deliverable) > 0
