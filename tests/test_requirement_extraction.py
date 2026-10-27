"""Tests for Step 8: Requirement Extraction Engine covering all 11 dimensions."""

import pytest
from app.nlp.entity_extractor import Entity, EntityExtractor
from app.nlp.requirement_extractor import RequirementExtractor, Requirements


@pytest.fixture
def entity_extractor():
    return EntityExtractor()


@pytest.fixture
def requirement_extractor(entity_extractor):
    return RequirementExtractor(entity_extractor=entity_extractor)


class TestEntityExtractor:
    """Verifies NER extraction for TECHNOLOGY, PLATFORM, LOCATION, METRIC, BUDGET, TIMEFRAME."""

    def test_extract_multiclass_entities(self, entity_extractor):
        text = (
            "Deploy FastAPI microservices on AWS in Frankfurt with 99.9% uptime "
            "budget $5,000 within 2 weeks"
        )
        entities = entity_extractor.extract(text)
        labels = {e.label for e in entities}
        assert "TECHNOLOGY" in labels
        assert "PLATFORM" in labels
        assert "METRIC" in labels
        assert "BUDGET" in labels
        assert "TIMEFRAME" in labels

    def test_extract_indian_locations_and_currencies(self, entity_extractor):
        text = "Destination wedding in Udaipur with budget 50 lakh within 3 days"
        entities = entity_extractor.extract(text)
        labels = {e.label for e in entities}
        assert "LOCATION" in labels
        assert "BUDGET" in labels
        assert "TIMEFRAME" in labels

        loc = next(e for e in entities if e.label == "LOCATION")
        assert loc.text == "Udaipur"


class TestRequirementExtractor:
    """Verifies all 11 dimensions of RequirementExtractor."""

    def test_all_11_dimensions_technical_scenario(self, requirement_extractor):
        text = (
            "Act as a Senior Cloud Architect to design a Kubernetes distributed microservices system on AWS for developers.\n"
            "Must not use hosted AI APIs.\n"
            "Avoid single points of failure.\n"
            "Keep latency under 50ms.\n"
            "Deadline: within 2 weeks.\n"
            "Budget: $10,000.\n"
            "Location: in San Francisco.\n"
            "Provide output as a Comparison Matrix Table with authoritative tone."
        )

        req = requirement_extractor.extract(text)
        assert isinstance(req, Requirements)

        # 1. Goal
        assert "Kubernetes" in req.goal or "microservices" in req.goal
        # 2. Audience
        assert req.audience == "developers"
        # 3. Tone
        assert req.tone == "authoritative"
        # 4. Format
        assert req.format == "Comparison Matrix Table"
        # 5. Constraints
        assert len(req.constraints) >= 2
        assert any("hosted AI APIs" in c for c in req.constraints)
        assert any("under 50ms" in c or "points of failure" in c for c in req.constraints)
        # 6. Deadline
        assert "within 2 weeks" in req.deadline
        # 7. Budget
        assert "$10,000" in req.budget
        # 8. Platform
        assert "AWS" in req.platform or "Kubernetes" in req.platform
        # 9. Location
        assert "San Francisco" in req.location
        # 10. Entities
        assert len(req.entities) >= 4
        # 11. Success Criteria
        assert len(req.success_criteria) >= 4

    def test_wedding_planner_target_scenario(self, requirement_extractor):
        text = (
            "mare wedding planner mate prompt joiye destination wedding in Udaipur with budget 50 lakh within 3 days for wedding guests.\n"
            "Must not exceed budget.\n"
            "Do not schedule outdoor rituals in afternoon heat.\n"
            "Format: Event Master Coordination Plan."
        )

        req = requirement_extractor.extract(text)
        assert isinstance(req, Requirements)

        assert "destination wedding" in req.goal.lower() or "wedding" in req.goal.lower()
        assert req.location == "Udaipur"
        assert "50 lakh" in req.budget
        assert "within 3 days" in req.deadline
        assert req.audience == "wedding_guests"
        assert req.format == "Event Master Coordination Plan"
        assert len(req.constraints) >= 2
        assert any("exceed budget" in c for c in req.constraints)

    def test_negative_constraints_detection(self, requirement_extractor):
        text = (
            "Build an autonomous pipeline.\n"
            "- Never use external paid APIs\n"
            "- Do not write mock implementations\n"
            "- Strictly avoid third-party CDNs\n"
            "- Limit memory footprint to 512MB"
        )
        req = requirement_extractor.extract(text)
        assert len(req.constraints) >= 4
        assert any("Never use" in c for c in req.constraints)
        assert any("Do not write" in c for c in req.constraints)

    def test_empty_and_whitespace_fallback(self, requirement_extractor):
        req = requirement_extractor.extract("")
        assert req.goal != ""
        assert req.audience == "general audience"
        assert req.tone == "professional"
        assert req.format == "Detailed Technical Response"
        assert len(req.constraints) > 0
        assert len(req.success_criteria) >= 3

        req_ws = requirement_extractor.extract("   \n\t  ")
        assert req_ws.goal != ""
        assert req_ws.tone == "professional"

    def test_to_dict_serialization(self, requirement_extractor):
        text = "Write a technical executive brief for investors within 24 hours"
        req = requirement_extractor.extract(text)
        d = req.to_dict()
        assert isinstance(d, dict)
        assert "goal" in d
        assert "audience" in d
        assert "tone" in d
        assert "format" in d
        assert "constraints" in d
        assert "deadline" in d
        assert "budget" in d
        assert "platform" in d
        assert "location" in d
        assert "entities" in d
        assert "success_criteria" in d
