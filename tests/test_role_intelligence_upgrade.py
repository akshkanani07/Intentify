"""Tests for Intent Understanding & Role Intelligence Upgrade."""

import pytest
from app.api.v1.schemas.prompt import PromptGenerationRequest, PromptGenerationResponse
from app.services.orchestrator import PromptOrchestrator
from app.nlp.intent_engine import IntentEngine
from app.nlp.goal_extractor import GoalExtractor
from app.nlp.role_alignment_engine import RoleAlignmentEngine
from app.nlp.entity_relationship_engine import EntityRelationshipEngine
from app.knowledge.domain_resolver import DomainResolver


@pytest.fixture
def orchestrator():
    return PromptOrchestrator()


class TestIntentAndGoalEngines:
    """Verifies Module 1 and Module 2 independent intelligence."""

    def test_intent_engine_scheduling_website(self):
        ie = IntentEngine()
        result = ie.classify("I want to make a scheduling website")
        assert result.intent == "create"
        assert result.confidence >= 0.90
        assert result.action_verb == "Create"

    def test_intent_engine_learn_python(self):
        ie = IntentEngine()
        result = ie.classify("I want to learn Python")
        assert result.intent == "learn"
        assert result.confidence >= 0.90
        assert result.action_verb == "Master"

    def test_goal_extractor_separates_role_and_goal(self):
        ge = GoalExtractor()
        res = ge.extract_goal("I want to make scheduling website", role_input="Senior Cloud Architect")
        # Must not contain "Senior Cloud Architect:"
        assert "Senior Cloud Architect" not in res.user_goal
        assert "scheduling website" in res.user_goal.lower()
        assert res.action in ["Build", "Create"]
        assert res.deliverable == "Web Application"
        assert res.complexity == "Production SaaS"


class TestRoleAlignmentAndDomainIntelligence:
    """Verifies Module 3, 4, and 5 domain and persona alignment."""

    def test_role_alignment_senior_cloud_to_saas_architect(self):
        rae = RoleAlignmentEngine()
        res = rae.align_role("Senior Cloud Architect", "I want to make scheduling website")
        assert "Full Stack SaaS Architect" in res.final_role
        assert "Senior" in res.final_role
        assert res.alignment_status == "adjusted"

    def test_role_alignment_teacher_learner_to_python_instructor(self):
        rae = RoleAlignmentEngine()
        res = rae.align_role("Teacher", "I want to learn Python", intent="learn")
        assert res.final_role == "Python Instructor"
        assert res.alignment_status == "adjusted"

    def test_role_alignment_doctor_to_healthcare_architect(self):
        rae = RoleAlignmentEngine()
        res = rae.align_role("Doctor", "Create hospital management software")
        assert res.final_role == "Healthcare Technology Architect"
        assert res.alignment_status == "adjusted"

    def test_domain_intelligence_scheduling_saas(self):
        dr = DomainResolver()
        res = dr.resolve("I want to make a scheduling website")
        assert res.domain == "Scheduling SaaS Platform"
        assert res.category == "SaaS Application"
        assert any("Calendar" in s or "Booking" in s for s in res.sub_domains)

    def test_domain_intelligence_programming_education(self):
        dr = DomainResolver()
        res = dr.resolve("I want to learn Python")
        assert res.domain == "Programming Education"
        assert res.category in ("Technical Education", "Programming Education")

    def test_domain_intelligence_healthcare_software(self):
        dr = DomainResolver()
        res = dr.resolve("Create hospital management software")
        assert res.domain == "Healthcare Software"
        assert "Healthcare" in res.category or "Health" in res.category

    def test_entity_relationship_scheduling_entities(self):
        ere = EntityRelationshipEngine()
        res = ere.analyze("I want to make a scheduling website")
        extracted_names = [e.lower() for e in res.entity_names]
        assert "user" in extracted_names
        assert "appointment" in extracted_names
        assert "calendar" in extracted_names
        assert "availability" in extracted_names
        assert "notification" in extracted_names
        assert "authentication" in extracted_names


class TestEndToEndPipelineVerification:
    """Verifies the exact user verification test cases via full orchestrator."""

    def test_verification_case_1_senior_cloud_architect_scheduling(self, orchestrator):
        """Input: Role='Senior Cloud Architect', Detail='I want to make scheduling website'
        Expected:
            Role: Senior Full Stack SaaS Architect
            Intent: create
            Domain: Scheduling SaaS Platform
            Objective: Build a production-grade scheduling website...
        """
        req = PromptGenerationRequest(
            role="Senior Cloud Architect",
            detail="I want to make scheduling website",
        )
        res = orchestrator.generate_prompt_sync(req)

        assert isinstance(res, PromptGenerationResponse)
        assert res.metadata.detected_intent == "create"
        assert res.metadata.detected_domain == "Scheduling SaaS Platform"

        # Role section must contain Senior Full Stack SaaS Architect
        assert "Senior Full Stack SaaS Architect" in res.master_prompt

        # Objective must NOT contain "Senior Cloud Architect:"
        lines = res.master_prompt.split("\n")
        objective_text = ""
        for i, line in enumerate(lines):
            if "### 2. Core Objective" in line:
                objective_text = "\n".join(lines[i:i+5])
                break

        assert "Senior Cloud Architect:" not in objective_text, "Role was blindly copied into Objective!"
        assert "scheduling website" in objective_text.lower()
        assert res.quality_score >= 85.0

    def test_verification_case_2_teacher_learn_python(self, orchestrator):
        """Input: Role='Teacher', Detail='I want to learn Python'
        Expected:
            Intent: learn
            Domain: Programming Education
            Role: Python Instructor
        """
        req = PromptGenerationRequest(
            role="Teacher",
            detail="I want to learn Python",
        )
        res = orchestrator.generate_prompt_sync(req)

        assert isinstance(res, PromptGenerationResponse)
        assert res.metadata.detected_intent == "learn"
        assert res.metadata.detected_domain in ("Programming Education", "Software Development")
        assert "Python Instructor" in res.master_prompt
        assert "Teacher: I want to learn Python" not in res.master_prompt
        assert res.quality_score >= 85.0

    def test_verification_case_3_doctor_hospital_management(self, orchestrator):
        """Input: Role='Doctor', Detail='Create hospital management software'
        Expected:
            Domain: Healthcare Software
            Role: Healthcare Technology Architect
        """
        req = PromptGenerationRequest(
            role="Doctor",
            detail="Create hospital management software",
        )
        res = orchestrator.generate_prompt_sync(req)

        assert isinstance(res, PromptGenerationResponse)
        assert res.metadata.detected_domain in ("Healthcare Software", "Healthcare")
        assert "Healthcare Technology Architect" in res.master_prompt
        assert "Doctor: Create hospital management software" not in res.master_prompt
        assert res.quality_score >= 85.0
