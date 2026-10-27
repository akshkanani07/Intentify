"""Tests for the Cognitive Prompt Compiler Engine (Enterprise Specification).

Verifies:
1. Audience & Experience Level Detection
2. Task & Tangible Deliverable Classification
3. Risk Analysis, Missing Information & Smart Assumptions
4. Cognitive Reasoner Self-Questioning & Answers
5. Dynamic Section Planner (Bespoke runtime headings per domain)
6. Deep Requirement & Constraint Intelligence
7. 12-Dimension Cognitive Quality Rubric & Gap Detection
8. End-to-End Cognitive Telemetry & Dynamic Heading Compilation
"""

import pytest
from app.api.v1.schemas.prompt import PromptGenerationRequest
from app.compiler.dynamic_section_planner import DynamicSectionPlanner
from app.nlp.audience_detector import AudienceDetector
from app.nlp.cognitive_reasoner import CognitiveReasoner
from app.nlp.requirement_intelligence import RequirementIntelligenceEngine
from app.nlp.risk_analysis_engine import RiskAnalysisEngine
from app.nlp.task_classifier import TaskClassifier
from app.engine.quality_engine import QualityEvaluator
from app.services.orchestrator import PromptOrchestrator


class TestAudienceAndTaskClassifiers:
    """Verifies audience archetype and task/deliverable classification."""

    def test_student_beginner_detection(self):
        detector = AudienceDetector()
        res = detector.detect("I want to learn Python from scratch as a complete beginner")
        assert res.target_audience == "Students & Learners"
        assert res.experience_level == "Novice / Beginner"
        assert res.pedagogical_mode is True

    def test_architect_senior_detection(self):
        detector = AudienceDetector()
        res = detector.detect("Architect high-throughput distributed caching on Kubernetes cluster", role_hint="Principal Architect")
        assert res.target_audience == "Software Engineers & Architects"
        assert "Senior" in res.experience_level or "Principal" in res.experience_level
        assert res.pedagogical_mode is False

    def test_task_deliverable_scheduling_saas(self):
        classifier = TaskClassifier()
        res = classifier.classify("Build a scheduling website with calendar sync", domain="Scheduling SaaS Platform")
        assert "Architecture" in res.task_type or "Full-Stack" in res.task_type
        assert "Production-Ready Source Code" in res.deliverable
        assert res.confidence >= 0.90

    def test_task_deliverable_curriculum(self):
        classifier = TaskClassifier()
        res = classifier.classify("Teach me Python step by step", intent="learn", domain="Programming Education")
        assert "Curriculum" in res.task_type
        assert "Structured Progressive Curriculum" in res.deliverable


class TestRiskAndCognitiveReasoningEngines:
    """Verifies domain failure modes, smart assumptions, and cognitive reasoning."""

    def test_scheduling_saas_risks_and_assumptions(self):
        engine = RiskAnalysisEngine()
        res = engine.analyze("Build an appointment booking SaaS", domain="Scheduling SaaS Platform")
        assert any("Timezone" in r or "double-booking" in r or "Race condition" in r for r in res.identified_risks)
        assert any("UTC" in a for a in res.smart_assumptions)
        assert len(res.smart_assumptions) >= 3

    def test_cognitive_reasoner_self_questioning(self):
        reasoner = CognitiveReasoner()
        res = reasoner.reason(
            raw_detail="I want to make a scheduling website",
            user_goal="Build a production-grade scheduling website with automated calendar synchronization",
            intent="create",
            requested_role="Senior Cloud Architect",
            aligned_role="Senior Full Stack SaaS Architect",
            domain="Scheduling SaaS Platform",
            sub_domains=["Scheduling & Booking SaaS", "Calendar Synchronization"],
            audience="Software Engineers & Architects",
            experience_level="Advanced / Senior",
            deliverable="Production-Ready Source Code, API Endpoints, and Database Schemas",
        )
        assert "production-grade" in res.what_user_wants_to_build.lower()
        assert res.is_role_appropriate is False
        assert "suboptimal" in res.role_adjustment_rationale.lower()
        assert any("Topology" in s or "Architecture" in s for s in res.required_sections)
        assert any("Clinical" in s for s in res.omitted_sections)


class TestDynamicSectionPlannerAndRequirementIntelligence:
    """Verifies dynamic runtime section headings and deep requirements."""

    def test_programming_bespoke_headings(self):
        planner = DynamicSectionPlanner()
        schema = planner.plan_sections("Scheduling SaaS Platform", "Build scheduling website")
        headings = [s.heading for s in schema.dynamic_sections]
        assert any("Architecture" in h for h in headings)
        assert any("API" in h for h in headings)
        assert any("Database" in h for h in headings)
        assert any("Security" in h for h in headings)
        assert any("Performance" in h for h in headings)
        assert any("Testing" in h for h in headings)
        assert any("Deployment" in h for h in headings)

    def test_teacher_bespoke_headings(self):
        planner = DynamicSectionPlanner()
        schema = planner.plan_sections("Programming Education", "Master Python programming")
        headings = [s.heading for s in schema.dynamic_sections]
        assert any("Learning Outcomes" in h for h in headings)
        assert any("Curriculum" in h for h in headings)
        assert any("Lesson Flow" in h for h in headings)
        assert any("Exercises" in h for h in headings)
        assert any("Projects" in h for h in headings)
        assert any("Assessment" in h for h in headings)

    def test_marketing_bespoke_headings(self):
        planner = DynamicSectionPlanner()
        schema = planner.plan_sections("Marketing Strategy", "Launch B2B SaaS campaign")
        headings = [s.heading for s in schema.dynamic_sections]
        assert any("Audience" in h for h in headings)
        assert any("USP" in h for h in headings)
        assert any("Consumer Psychology" in h for h in headings)
        assert any("Messaging" in h for h in headings)
        assert any("Visual" in h for h in headings)
        assert any("CTA" in h for h in headings)

    def test_medical_bespoke_headings(self):
        planner = DynamicSectionPlanner()
        schema = planner.plan_sections("Healthcare Software", "Hospital triage system")
        headings = [s.heading for s in schema.dynamic_sections]
        assert any("Clinical" in h for h in headings)
        assert any("Symptom" in h for h in headings)
        assert any("Diagnostic" in h for h in headings)
        assert any("Treatment" in h for h in headings)
        assert any("Contraindications" in h for h in headings)
        assert any("Follow-up" in h for h in headings)

    def test_deep_requirements_scheduling_saas(self):
        engine = RequirementIntelligenceEngine()
        bundle = engine.synthesize("Scheduling SaaS Platform", "Build scheduling website", "create")
        assert any("Authentication" in r for r in bundle.functional_requirements)
        assert any("Calendar Engine" in r for r in bundle.functional_requirements)
        assert any("Conflict Detection" in r for r in bundle.functional_requirements)
        assert any("Production Ready" in c for c in bundle.technical_constraints)
        assert any("Deprecated APIs" in c for c in bundle.technical_constraints)


class TestCognitiveQualityRubricAndEndToEndTelemetry:
    """Verifies 12-dimension quality scoring and full cognitive orchestrator telemetry."""

    def test_12_dimension_cognitive_rubric(self):
        evaluator = QualityEvaluator()
        prompt_text = (
            "### 1. Role & Persona\n"
            "You are an industry-leading Senior Full Stack SaaS Architect.\n\n"
            "### 2. Core Objective\n"
            "Your primary mission is to: Build a production-grade scheduling website.\n\n"
            "### 3. Context & Background\n"
            "- Primary Domain: Scheduling SaaS Platform\n"
            "- Target Audience: Software Engineers & Architects\n\n"
            "### 4. Technical & Functional Requirements\n"
            "- Implement calendar synchronization and conflict detection\n\n"
            "### 5. Guardrails & Operational Constraints\n"
            "- Must not use deprecated libraries\n"
            "- Production-ready completeness; strictly zero placeholders\n\n"
            "### 6. Step-by-Step Execution Instructions\n"
            "1. Architect system topology\n"
            "2. Implement database schemas\n\n"
            "### 7. Output Format Specification\n"
            "Deliver response in clean markdown.\n\n"
            "### 8. Documented Assumptions\n"
            "- All calendar calculations default to UTC\n\n"
            "### 9. Self-Verification Quality Checklist\n"
            "- [ ] Core objective executed completely"
        )
        score = evaluator.evaluate(prompt_text)
        assert score.total_score >= 90.0
        assert score.is_acceptable is True
        cog = score.cognitive_breakdown
        assert cog.role_alignment == 100.0
        assert cog.goal_accuracy == 100.0
        assert cog.domain_accuracy == 100.0
        assert cog.structure_depth == 100.0

    def test_orchestrator_end_to_end_cognitive_telemetry(self):
        orchestrator = PromptOrchestrator()
        req = PromptGenerationRequest(
            role="Senior Cloud Architect",
            detail="I want to make a scheduling website",
        )
        res = orchestrator.generate_prompt_sync(req)

        assert res.quality_score >= 90.0
        meta = res.metadata
        assert meta is not None
        assert meta.detected_intent == "create"
        assert meta.detected_domain == "Scheduling SaaS Platform"
        assert meta.aligned_role == "Senior Full Stack SaaS Architect"
        assert meta.target_audience == "Software Engineers & Architects"
        assert meta.experience_level in ["Advanced / Senior", "Intermediate / Practitioner"]
        assert meta.task_type is not None
        assert len(meta.identified_risks) >= 2
        assert len(meta.smart_assumptions) >= 2
        assert len(meta.dynamic_headings) >= 5
        assert "what_user_wants_to_build" in meta.cognitive_reasoning

        # Master prompt contains dynamic bespoke headings
        assert "System Architecture & Component Topology" in res.master_prompt
        assert "Verifiable Acceptance Criteria" in res.master_prompt
        assert "Output Format Specification" in res.master_prompt
        assert "Operational Guardrails" in res.master_prompt
        assert "Documented Assumptions" in res.master_prompt
