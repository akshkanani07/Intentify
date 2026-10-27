"""Tests for Step 5: Role Extraction & Persona Resolution Engine."""

import pytest
from app.knowledge.knowledge_manager import KnowledgeManager
from app.knowledge.role_resolver import RoleResolver, RoleResult
from app.nlp.entity_extractor import Entity
from app.nlp.role_extractor import RoleExtractor


@pytest.fixture
def km():
    return KnowledgeManager()


@pytest.fixture
def extractor():
    return RoleExtractor()


@pytest.fixture
def resolver(km):
    return RoleResolver(knowledge_manager=km)


class TestRoleExtractor:
    """Tests for RoleExtractor pattern matching and noun phrase parsing."""

    def test_extract_english_patterns(self, extractor):
        samples = [
            ("Act as a Senior DevOps Engineer to configure Kubernetes cluster", "Senior DevOps Engineer"),
            ("You are a Product Manager responsible for B2B SaaS onboarding", "Product Manager"),
            ("I need a Financial Analyst to review this quarterly balance sheet", "Financial Analyst"),
            ("Prompt for a Creative Copywriter to draft ad headlines", "Creative Copywriter"),
        ]
        for text, expected in samples:
            role = extractor.extract_primary_role(text)
            assert role is not None, f"Failed to extract from: {text}"
            assert expected.lower() in role.lower(), f"Expected '{expected}' in '{role}'"

    def test_extract_gujarati_romanized(self, extractor):
        text = "mare wedding planner mate prompt joiye"
        role = extractor.extract_primary_role(text)
        assert role is not None
        assert "wedding planner" in role.lower()
        # Pronoun filler "mare" must be removed
        assert "mare" not in role.lower()

    def test_extract_gujarati_romanized_variation(self, extractor):
        text = "amare ek full stack developer joiye che project mate"
        role = extractor.extract_primary_role(text)
        assert role is not None
        assert "developer" in role.lower() or "stack" in role.lower()

    def test_extract_hindi_romanized(self, extractor):
        text = "mujhe data scientist ke liye prompt chahiye machine learning model banana hai"
        role = extractor.extract_primary_role(text)
        assert role is not None
        assert "data scientist" in role.lower()
        # Pronoun filler "mujhe" must be stripped
        assert "mujhe" not in role.lower()

    def test_extract_native_gujarati(self, extractor):
        text = "મને લગ્ન માટે વેડિંગ પ્લાનર જોઈએ"
        candidates = extractor.extract_candidates(text)
        assert len(candidates) > 0
        assert candidates[0].clean_role != ""

    def test_extract_native_devanagari(self, extractor):
        text = "मुझे वित्तीय सलाहकार चाहिए"
        candidates = extractor.extract_candidates(text)
        assert len(candidates) > 0
        assert candidates[0].clean_role != ""

    def test_seniority_detection(self, extractor):
        assert extractor._detect_seniority("Principal System Architect") == "Principal"
        assert extractor._detect_seniority("Senior Frontend Developer") == "Senior"
        assert extractor._detect_seniority("Head of Growth Marketing") == "Head of"
        assert extractor._detect_seniority("Junior Data Analyst") == "Junior"
        assert extractor._detect_seniority("Python Programmer") is None

    def test_empty_or_whitespace_input(self, extractor):
        assert extractor.extract_primary_role("") is None
        assert extractor.extract_primary_role("   \n\t  ") is None
        assert extractor.extract_candidates("") == []


class TestRoleResolver:
    """Tests for RoleResolver multi-tier resolution and dynamic persona synthesis."""

    def test_exact_role_match(self, resolver):
        result = resolver.resolve(role_input="Backend Developer")
        assert isinstance(result, RoleResult)
        assert "Backend Developer" in result.role_title
        assert result.confidence >= 0.90
        assert not result.is_dynamic
        assert len(result.expertise_areas) > 0

    def test_alias_role_match(self, resolver):
        # "coder" or "dev" should map or match a software engineering role
        result = resolver.resolve(role_input="wedding planner")
        assert "Wedding" in result.role_title
        assert result.category == "Hospitality & Events"
        assert not result.is_dynamic

    def test_extraction_from_detail_when_role_empty_gujarati(self, resolver):
        """Core scenario: user provides empty role and raw Gujarati text."""
        result = resolver.resolve(
            role_input="",
            detail_text="mare wedding planner mate prompt joiye gujarati traditional wedding che",
        )
        assert isinstance(result, RoleResult)
        assert "Wedding" in result.role_title
        assert not result.is_dynamic
        assert result.category == "Hospitality & Events"

    def test_extraction_from_detail_when_role_empty_hindi(self, resolver):
        """User provides empty role and raw Hindi Romanized text."""
        result = resolver.resolve(
            role_input="",
            detail_text="mujhe data scientist ke liye prompt chahiye churn prediction model ke liye",
        )
        assert isinstance(result, RoleResult)
        assert "Data Scientist" in result.role_title or "Machine Learning" in result.role_title

    def test_seniority_preservation(self, resolver):
        result = resolver.resolve(role_input="Senior DevOps Engineer")
        assert "Senior" in result.role_title
        assert result.seniority == "Senior"

    def test_dynamic_role_synthesis_for_unknown_role(self, resolver):
        """Completely novel, unknown role should generate a custom dynamic expert persona."""
        novel_role = "Intergalactic Subspace Communications Officer"
        result = resolver.resolve(role_input=novel_role)

        assert isinstance(result, RoleResult)
        assert result.is_dynamic is True
        assert novel_role in result.role_title
        assert result.category == "Custom / Emerging Industry"
        assert len(result.expertise_areas) >= 4
        # Expertise areas must be synthesized contextually
        assert any("Communications" in area or "Subspace" in area for area in result.expertise_areas)

    def test_fallback_when_completely_empty(self, resolver):
        result = resolver.resolve(role_input="", detail_text="")
        assert isinstance(result, RoleResult)
        assert result.role_title == "Principal Subject Matter Expert"
        assert len(result.expertise_areas) > 0

    def test_fallback_with_entities(self, resolver):
        entities = [Entity(text="Python", label="TECHNOLOGY", start=0, end=6, confidence=0.9)]
        result = resolver.resolve(role_input="", detail_text="", entities=entities)
        assert "Software" in result.role_title
