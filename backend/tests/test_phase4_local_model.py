"""Unit tests for Phase 4: Local Model Generator (Stage C2) and clean fallback behavior."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from app.core.config import get_settings
from app.engine.planner import KnowledgePlanner
from app.engine.spec_extractor import PromptSpec
from app.services.orchestrator import PromptOrchestrator
from app.api.v1.schemas.prompt import PromptGenerationRequest


def test_stage_c2_flag_disabled_by_default():
    """Verify ENABLE_LOCAL_INSTRUCTION_MODEL is False by default."""
    settings = get_settings()
    assert settings.ENABLE_LOCAL_INSTRUCTION_MODEL is False


def test_stage_c2_fallback_when_disabled():
    """When ENABLE_LOCAL_INSTRUCTION_MODEL is False, planner falls back to C3 derived structure for novel subject."""
    planner = KnowledgePlanner()
    spec = PromptSpec(
        canonical_intent="Create",
        action="learn",
        object_subject="Novel Astrobiology Exploration",
        domain="Science",
        audience="Students",
        proficiency="Novice / Beginner",
        persona_role="Astrobiology Educator",
        format="Markdown",
        deliverable="Step-by-Step Curriculum",
    )
    plan = planner.plan(spec)
    assert plan.content_source == "derived"
    assert len(plan.topics) >= 5
    assert all("objective" in t and "exercise" in t for t in plan.topics)


def test_stage_c2_with_mock_generator():
    """When ENABLE_LOCAL_INSTRUCTION_MODEL is True and model generates output, topics are extracted as 'generated'."""
    planner = KnowledgePlanner()
    spec = PromptSpec(
        canonical_intent="Create",
        action="learn",
        object_subject="Quantum Circuitry",
        domain="Physics",
        audience="Students",
        proficiency="Novice / Beginner",
        persona_role="Quantum Physics Instructor",
        format="Markdown",
        deliverable="Step-by-Step Curriculum",
    )

    mock_topics = (
        "Topic 1: Qubit States & Superposition\n"
        "Topic 2: Quantum Logic Gates\n"
        "Topic 3: Entanglement & Bell States\n"
        "Topic 4: Circuit Simulation\n"
        "Topic 5: Quantum Algorithms"
    )

    mock_tf = MagicMock()
    generator_mock = MagicMock()
    generator_mock.return_value = [{"generated_text": mock_topics}]
    mock_tf.pipeline.return_value = generator_mock

    with patch("app.engine.planner.get_settings") as mock_settings:
        settings_obj = MagicMock()
        settings_obj.ENABLE_LOCAL_INSTRUCTION_MODEL = True
        settings_obj.LOCAL_INSTRUCTION_MODEL_NAME = "google/flan-t5-small"
        mock_settings.return_value = settings_obj

        with patch.dict("sys.modules", {"transformers": mock_tf}):
            topics = planner._generate_topics_with_model(spec)
            assert topics is not None
            assert len(topics) == 5
            assert topics[0]["title"] == "Topic 1: Qubit States & Superposition"
            assert "objective" in topics[0]
            assert "exercise" in topics[0]


def test_stage_c2_graceful_fallback_on_exception():
    """When ENABLE_LOCAL_INSTRUCTION_MODEL is True but model raises error, falls back cleanly to C3."""
    planner = KnowledgePlanner()
    spec = PromptSpec(
        canonical_intent="Create",
        action="learn",
        object_subject="Exoplanet Spectroscopy",
        domain="Science",
        audience="Students",
        proficiency="Novice / Beginner",
        persona_role="Astronomy Instructor",
        format="Markdown",
        deliverable="Step-by-Step Curriculum",
    )

    with patch("app.engine.planner.get_settings") as mock_settings:
        settings_obj = MagicMock()
        settings_obj.ENABLE_LOCAL_INSTRUCTION_MODEL = True
        mock_settings.return_value = settings_obj

        # No transformers installed in sys.modules
        with patch.dict("sys.modules", {"transformers": None}):
            plan = planner.plan(spec)
            assert plan.content_source == "derived"
            assert len(plan.topics) >= 5
