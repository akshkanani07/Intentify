"""Comprehensive test suite for Intentify AI v4 — Self Learning Cognitive Prompt Intelligence Engine.

Verifies:
- Layer 1: Input Intelligence Engine (Multilingual, Writing Style, Formality, Emotion, Tokenization)
- Layer 2: 15 Intent Classification System
- Layer 3: Adaptive Knowledge Graph (Relationships, Traversal, Dynamic Learning)
- Layer 4: Domain Playbooks (Software, Marketing, Education, Business, Medical, Unknown Domain Synthesis)
- Layer 5: Blueprint Learning Engine (Dynamic discovery, section optimization)
- Layer 6: Expert Role Intelligence (Universal personas: Space Lawyer, Vertical Farmer, Master Gardener)
- Layer 7: Cognitive Reasoning Engine (Deep self-questioning and inference)
- Layer 8: Decision Framework Engine (Domain trade-off priority hierarchies)
- Layer 9: Master Prompt Compiler v4 (Dynamic 11+ section assembly)
- Layer 10: Quality Intelligence Engine v4 (10 dimensions, target 95+)
- Layer 11: Self-Improvement Loop (Autonomous feedback repair)
- Layer 12: Learning Memory Engine (Vector similarity, persistent pattern memorization)
- End-to-End Orchestrator v4 Pipeline
"""

from __future__ import annotations

import pytest
from app.api.v1.schemas.prompt import PromptGenerationRequest
from app.compiler.blueprint_learning_engine import BlueprintLearningEngine
from app.compiler.blueprint_selector import BlueprintSelector
from app.compiler.prompt_compiler import CompilationContext, PromptCompiler
from app.knowledge.adaptive_knowledge_graph import AdaptiveKnowledgeGraph
from app.knowledge.domain_playbooks import DomainPlaybooksEngine
from app.knowledge.role_resolver import RoleResolver
from app.learning.learning_memory import LearningMemoryEngine
from app.nlp.decision_framework import DecisionFrameworkEngine
from app.nlp.input_intelligence import InputIntelligenceEngine
from app.nlp.intent_engine import IntentEngine
from app.nlp.requirement_extractor import Requirements
from app.engine.quality_engine import QualityEvaluator
from app.services.orchestrator import PromptOrchestrator


class TestInputIntelligenceEngine:
    """Verifies Layer 1: Multilingual, Writing Style, Formality, and User Emotion."""

    def test_multilingual_and_script_detection(self):
        engine = InputIntelligenceEngine()

        res_guj = engine.analyze("મને એક શેડ્યુલિંગ વેબસાઇટ બનાવવી છે")
        assert res_guj.detected_language == "Gujarati"
        assert res_guj.primary_script == "Gujarati"

        res_hi = engine.analyze("मुझे एक शेड्यूलिंग वेबसाइट बनानी है")
        assert res_hi.detected_language == "Hindi"
        assert res_hi.primary_script == "Devanagari"

        res_en = engine.analyze("Architect a low-latency distributed booking cluster")
        assert res_en.detected_language == "English"
        assert res_en.primary_script == "Latin"

    def test_writing_style_and_formality(self):
        engine = InputIntelligenceEngine()

        res_tech = engine.analyze("Implement an asynchronous microservices architecture using FastAPI and PostgreSQL")
        assert res_tech.writing_style in ["Technical", "Imperative"]
        assert res_tech.formality_level in ["Formal", "Professional-Neutral"]

        res_urgent = engine.analyze("Urgent critical production outage in auth cluster, need immediate emergency fix")
        assert res_urgent.user_emotion == "Urgent"

        res_curious = engine.analyze("How to master Python programming paradigms and understand clean code")
        assert res_curious.user_emotion == "Curious"

    def test_sentence_and_token_segmentation(self):
        engine = InputIntelligenceEngine()
        res = engine.analyze("Build an API. Secure it with JWT. Deploy on Kubernetes.")
        assert len(res.sentences) == 3
        assert len(res.tokens) >= 8
        assert "api" in [t.lower() for t in res.tokens]


class TestIntentIntelligenceEngine:
    """Verifies Layer 2: All 15 intents explicitly recognized."""

    @pytest.mark.parametrize(
        ("text", "expected_intent"),
        [
            ("Build a calendar booking portal", "build"),
            ("Create a REST API with FastAPI", "create"),
            ("Learn how distributed locking works", "learn"),
            ("Explain the CAP theorem for architects", "explain"),
            ("Analyze the latency bottlenecks in database queries", "analyze"),
            ("Compare PostgreSQL vs Redis for session caching", "compare"),
            ("Fix the memory leak in worker threads", "fix"),
            ("Improve the query throughput and indexing", "improve"),
            ("Design a clean microservices architecture", "design"),
            ("Plan a 3-month product roadmap for SaaS", "plan"),
            ("Research zero-knowledge proofs in identity", "research"),
            ("Write an email campaign for product launch", "write"),
            ("Translate this user manual to Spanish", "translate"),
            ("Decide whether to adopt GraphQL or REST for mobile clients", "decide"),
            ("Optimize Docker container size and build time", "optimize"),
        ],
    )
    def test_all_15_intents(self, text, expected_intent):
        engine = IntentEngine()
        result = engine.classify(text)
        assert result.intent == expected_intent
        assert result.confidence >= 0.5


class TestAdaptiveKnowledgeGraph:
    """Verifies Layer 3: Ontology representation, traversal, and runtime dynamic learning."""

    def test_domain_ontology_retrieval(self):
        kg = AdaptiveKnowledgeGraph()
        rec = kg.query_domain("Scheduling SaaS Platform")
        assert rec is not None
        assert "Calendar" in rec.entities
        assert "Booking" in rec.entities
        assert any(r["source"] == "Scheduling SaaS" for r in rec.relationships)

    def test_runtime_concept_learning(self):
        kg = AdaptiveKnowledgeGraph()
        domain = "Quantum Cryptography Architecture"
        new_entities = ["Qubit Key Distribution", "Post-Quantum Dilithium", "Kyber Lattice"]

        rec = kg.dynamic_learn_concept(domain, new_entities)
        assert rec.domain_name == domain
        for ent in new_entities:
            assert ent in rec.entities

        # Re-query should find learned concept
        queried = kg.query_domain("Quantum Cryptography Architecture")
        assert queried is not None
        assert "Kyber Lattice" in queried.entities


class TestDomainPlaybooksEngine:
    """Verifies Layer 4: Domain thinking frameworks and autonomous synthesis for novel domains."""

    def test_software_playbook_priorities(self):
        engine = DomainPlaybooksEngine()
        pb = engine.get_playbook("Software Engineering", "Build API")
        assert pb.decision_priorities == ["Security", "Correctness", "Scalability", "Maintainability", "Performance"]
        assert any("Architecture" in s.heading for s in pb.sections)

    def test_marketing_playbook_priorities(self):
        engine = DomainPlaybooksEngine()
        pb = engine.get_playbook("Marketing & Growth", "Launch campaign")
        assert "Trust" in pb.decision_priorities
        assert "Emotion" in pb.decision_priorities
        assert any("Psychology" in s.heading or "Audience" in s.heading for s in pb.sections)

    def test_education_playbook_priorities(self):
        engine = DomainPlaybooksEngine()
        pb = engine.get_playbook("Education & Pedagogy", "Teach Python")
        assert "Understanding" in pb.decision_priorities
        assert "Practice" in pb.decision_priorities
        assert any("Learning" in s.heading or "Curriculum" in s.heading for s in pb.sections)

    def test_unknown_domain_temporary_playbook_synthesis(self):
        engine = DomainPlaybooksEngine()
        pb = engine.get_playbook("Orbital Space Colony Agriculture", "Design hydroponics in microgravity")
        assert pb.is_temporary_synthesis is True
        assert len(pb.sections) >= 3
        assert len(pb.decision_priorities) >= 3


class TestDecisionFrameworkEngine:
    """Verifies Layer 8: Domain trade-off priority rules and decision matrix."""

    def test_software_tradeoff_hierarchy(self):
        engine = DecisionFrameworkEngine()
        res = engine.resolve("Software Engineering")
        assert res.priority_hierarchy == ["Security", "Correctness", "Scalability", "Maintainability", "Performance"]
        assert "Security" in res.tradeoff_rationale
        assert len(res.decision_matrix) == 5

    def test_marketing_tradeoff_hierarchy(self):
        engine = DecisionFrameworkEngine()
        res = engine.resolve("Marketing Strategy")
        assert res.priority_hierarchy == ["Trust", "Emotion", "Conversion", "Brand Value"]

    def test_medical_tradeoff_hierarchy(self):
        engine = DecisionFrameworkEngine()
        res = engine.resolve("Medical & Healthcare")
        assert res.priority_hierarchy[0] == "Patient Safety"

    def test_unknown_domain_fallback_hierarchy(self):
        engine = DecisionFrameworkEngine()
        res = engine.resolve("Exoplanetary Mineral Extraction")
        assert res.priority_hierarchy == ["Clarity", "Feasibility", "Rigor", "Value Delivery"]
        assert len(res.decision_matrix) == 4


class TestBlueprintLearningAndMemory:
    """Verifies Layer 5 & 12: Adaptive blueprint selection and memory persistence."""

    def test_blueprint_discovery(self):
        ble = BlueprintLearningEngine()
        bp = ble.discover_blueprint("create", "Software Development")
        assert bp.blueprint_type == "Technical Architecture"
        assert len(bp.recommended_sections) >= 5

    def test_learning_memory_recording_and_retrieval(self, tmp_path):
        store_file = tmp_path / "test_memory.json"
        mem_engine = LearningMemoryEngine(storage_path=store_file)
        initial_len = len(mem_engine.memories)

        mem = mem_engine.record_success(
            goal="Build a microservices calendar booking API",
            domain="Scheduling SaaS Platform",
            intent="create",
            aligned_role="Senior Full Stack SaaS Architect",
            blueprint_type="Technical Architecture",
            quality_score=98.0,
            sections=["Architecture", "API", "Database", "Security"],
            smart_assumptions=["UTC storage", "Row-level tenant isolation"],
        )
        assert mem.id is not None
        assert len(mem_engine.memories) == initial_len + 1

        # Retrieval
        matches = mem_engine.retrieve_similar_patterns("calendar booking", "Scheduling SaaS Platform")
        assert len(matches) >= 1
        assert matches[0].domain == "Scheduling SaaS Platform"

        # Check domain insights
        insights = mem_engine.get_learned_domain_insights("Scheduling SaaS Platform")
        assert insights is not None
        assert insights.usage_count >= 1


class TestUniversalPersonaRoles:
    """Verifies Layer 6: Universal persona elevation for unconventional or novel professions."""

    @pytest.mark.parametrize(
        ("role_input", "detail", "expected_role_fragment"),
        [
            ("Space Lawyer", "Draft legal treaty for lunar mining rights", "Space"),
            ("Vertical Farmer", "Design automated nutrient delivery for indoor greens", "Farmer"),
            ("Master Gardener", "Plan organic soil pest management", "Gardener"),
            ("AI Ethicist", "Formulate audit framework for algorithmic bias", "Ethic"),
        ],
    )
    def test_unconventional_role_elevation(self, role_input, detail, expected_role_fragment):
        resolver = RoleResolver()
        resolved = resolver.resolve(role_input=role_input, detail_text=detail)
        assert expected_role_fragment.lower() in resolved.role.lower()
        assert len(resolved.expertise_areas) >= 1


class TestQualityIntelligenceV4:
    """Verifies Layer 10: 10-dimension cognitive scoring and 95+ target quality."""

    def test_ten_dimensions_and_target_score(self):
        evaluator = QualityEvaluator()
        prompt_text = (
            "### 1. Role & Persona\n"
            "You are an industry-leading **Senior Software Architect**, recognized for authoritative mastery in Distributed Systems.\n\n"
            "### 2. Core Objective\n"
            "Your primary mission is to: **Build a distributed high-throughput calendar scheduling engine**.\n\n"
            "### 3. Context & Background\n"
            "- **Primary Domain**: Software Development\n"
            "- **Target Audience**: Software Engineers & Architects\n\n"
            "### 4. Technical & Functional Requirements\n"
            "- Implement atomic booking with distributed locking\n"
            "- Enforce calendar sync over RFC 5545 iCalendar\n\n"
            "### 5. Guardrails & Operational Constraints\n"
            "- Never permit double-booking race conditions\n"
            "- Strictly zero unverified third-party libraries\n\n"
            "### 6. Step-by-Step Execution Instructions\n"
            "1. Architect system topology with stateless services\n"
            "2. Implement database schemas with foreign keys\n"
            "3. Deploy with Docker and Kubernetes\n\n"
            "### 7. Output Format Specification\n"
            "Deliver the complete response formatted as **Production Code with Markdown**.\n\n"
            "### 8. Documented Assumptions\n"
            "- Standard UTC timestamps apply with zero placeholders\n\n"
            "### 9. Self-Verification Quality Checklist\n"
            "- [ ] Core objective executed completely\n\n"
            "### 10. Cognitive Reasoning Strategy & Decision Framework\n"
            "- **Domain Priority Hierarchy**: Security > Correctness > Scalability\n\n"
            "### 11. Domain Architecture & Playbook Deep-Dive\n"
            "- **Core Engineering Dimensions**: Scalability, Security, Performance"
        )

        score = evaluator.evaluate(prompt_text)
        assert score.total_score >= 95.0
        assert score.is_acceptable is True

        v4_dims = score.cognitive_breakdown.v4_dimensions()
        assert len(v4_dims) == 10
        assert v4_dims["intent"] == 100.0
        assert v4_dims["goal"] == 100.0
        assert v4_dims["role"] == 100.0
        assert v4_dims["domain"] == 100.0
        assert v4_dims["blueprint"] == 100.0
        assert v4_dims["requirement"] == 100.0
        assert v4_dims["constraint"] == 100.0
        assert v4_dims["actionability"] == 100.0
        assert v4_dims["professional_quality"] == 100.0
        assert v4_dims["adaptability"] == 100.0


class TestOrchestratorV4EndToEnd:
    """Verifies complete 12-layer end-to-end integration and learning loop."""

    def test_full_pipeline_v4_telemetry_and_sections(self):
        orchestrator = PromptOrchestrator()
        req = PromptGenerationRequest(
            role="Senior Cloud Architect",
            detail="I want to make a scheduling website with calendar sync and payment gateway",
        )
        res = orchestrator.generate_prompt_sync(req)

        # 1. Quality Target >= 95
        assert res.quality_score >= 95.0

        # 2. Master Prompt contains all 11+ sections
        mp = res.master_prompt
        assert "### 1. Role & Persona" in mp
        assert "### 2. Core Objective" in mp
        assert "### 3. Context & Background" in mp
        assert "### 4. Technical & Functional Requirements" in mp
        assert "### 5. Guardrails & Operational Constraints" in mp
        assert "### 6. Step-by-Step Execution Instructions" in mp
        assert "### 7. Output Format Specification" in mp
        assert "### 8. Documented Assumptions" in mp
        assert "### 9. Self-Verification Quality Checklist" in mp
        assert "### 10. Cognitive Reasoning Strategy & Decision Framework" in mp
        assert "### 11. Domain Architecture & Playbook Deep-Dive" in mp

        # 3. Telemetry & Metadata
        meta = res.metadata
        assert meta is not None
        assert meta.detected_intent == "create"
        assert meta.aligned_role == "Senior Full Stack SaaS Architect"
        assert meta.writing_style is not None
        assert meta.formality_level is not None
        assert meta.user_emotion is not None
        assert len(meta.decision_priorities) >= 4
        assert meta.decision_priorities[0] == "Security"
        assert meta.learned_memories_count >= 1
