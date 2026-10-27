"""Unit tests verifying Area 2: Generation Engine pluggable architectures."""

from app.engine.generator import (
    GeneratedPromptArtifact,
    LocalGGUFEngine,
    RulesGenerationEngine,
    get_generation_engine,
)
from app.engine.spec_extractor import SpecExtractor


def test_rules_generation_engine():
    """Verify RulesGenerationEngine creates valid artifact."""
    extractor = SpecExtractor()
    spec = extractor.extract("want to learn python")
    engine = RulesGenerationEngine()
    artifact, plan = engine.generate(spec)
    assert isinstance(artifact, GeneratedPromptArtifact)
    assert artifact.contract == "learn"
    assert "python" in artifact.subject.lower()
    assert len(artifact.sections) >= 5
    assert artifact.content_source in ["kb", "rules_fallback", "drafted", "concept_graph"]


def test_local_gguf_engine_graceful_fallback():
    """Verify LocalGGUFEngine falls back cleanly when model path is None or missing."""
    extractor = SpecExtractor()
    spec = extractor.extract("build a fast shopping app with checkout")
    engine = LocalGGUFEngine(model_path="non_existent_model.gguf")
    assert not engine.is_active

    artifact, plan = engine.generate(spec)
    assert isinstance(artifact, GeneratedPromptArtifact)
    assert artifact.contract == "build_app"
    assert artifact.content_source == "rules_fallback"


def test_get_generation_engine_factory():
    """Verify engine factory returns correct instances."""
    rules_engine = get_generation_engine("rules_fallback")
    assert isinstance(rules_engine, RulesGenerationEngine)

    gguf_engine = get_generation_engine("local_gguf", model_path=None)
    assert isinstance(gguf_engine, LocalGGUFEngine)
