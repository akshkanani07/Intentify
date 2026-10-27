"""Tests for Step 9: Prompt Compiler & Blueprint Selection Engine."""

import pytest
from app.compiler.blueprint_selector import Blueprint, BlueprintSelector
from app.compiler.prompt_compiler import CompilationContext, MasterPrompt, PromptCompiler
from app.knowledge.knowledge_manager import KnowledgeManager
from app.nlp.requirement_extractor import Requirements


@pytest.fixture
def km():
    return KnowledgeManager()


@pytest.fixture
def blueprint_selector(km):
    return BlueprintSelector(knowledge_manager=km)


@pytest.fixture
def compiler(km):
    return PromptCompiler(knowledge_manager=km)


class TestBlueprintSelector:
    """Verifies that BlueprintSelector covers all 13 core operational intents."""

    def test_all_13_intents_have_dedicated_blueprints(self, blueprint_selector):
        all_intents = [
            "create", "write", "generate", "plan", "analyze", "explain",
            "compare", "translate", "research", "design", "debug", "improve", "decide"
        ]
        for intent in all_intents:
            bp = blueprint_selector.select_blueprint(intent=intent, domain="general", role="expert")
            assert isinstance(bp, Blueprint)
            assert bp.intent == intent
            assert len(bp.steps) >= 4
            assert len(bp.requirements) >= 2
            assert len(bp.constraints) >= 1

    def test_domain_specific_blueprint_match(self, blueprint_selector):
        bp = blueprint_selector.select_blueprint(intent="create", domain="software_engineering", role="Architect")
        assert bp.name == "code_generation"
        assert "production" in bp.description.lower() or "code" in bp.description.lower()

    def test_fallback_blueprint(self, blueprint_selector):
        bp = blueprint_selector.select_blueprint(intent="unknown_intent", domain="unknown_domain", role="worker")
        assert isinstance(bp, Blueprint)
        assert len(bp.steps) > 0


class TestPromptCompiler:
    """Verifies 9-part Master Prompt structure, completeness, and context propagation."""

    def test_master_prompt_has_all_9_sections(self, compiler, blueprint_selector):
        bp = blueprint_selector.select_blueprint("create", "Technology", "Software Architect")
        reqs = Requirements(
            goal="Build a high-performance distributed caching cluster with Redis and FastAPI",
            audience="developers",
            tone="technical",
            format="Production Code with Inline Architectural Annotations",
            constraints=["Must not block async event loop", "Zero external dependencies beyond redis-py"],
            deadline="within 1 week",
            budget="$5,000",
            platform="Linux, Docker, AWS",
            location="us-east-1",
            entities=[{"text": "Redis", "label": "TECHNOLOGY"}, {"text": "FastAPI", "label": "TECHNOLOGY"}],
            success_criteria=["Sub-millisecond latency for cache hits", "100% test coverage"],
        )

        ctx = CompilationContext(
            role="Principal Distributed Systems Architect",
            expertise_areas=["Distributed caching", "High-throughput async systems", "Fault tolerance"],
            intent="create",
            domain="Software Development",
            sub_domains=["Backend", "Distributed Systems", "Cloud"],
            requirements=reqs,
            entities=reqs.entities,
            blueprint=bp,
            language="English",
            tone="technical",
            output_format="Production Code with Inline Architectural Annotations",
            original_detail="Build distributed caching cluster with Redis and FastAPI",
        )

        master = compiler.compile(ctx)
        assert isinstance(master, MasterPrompt)

        # Verify all 9 sections exist and are non-empty
        assert "### 1. Role & Persona" in master.role_section
        assert "Principal Distributed Systems Architect" in master.role_section

        assert "### 2. Core Objective" in master.objective_section
        assert "Build a high-performance distributed caching cluster" in master.objective_section

        assert "### 3. Context & Background" in master.context_section
        assert "Software Development" in master.context_section
        assert "us-east-1" in master.context_section

        assert "### 4. Technical & Functional Requirements" in master.requirements_section
        assert "Linux, Docker, AWS" in master.requirements_section
        assert "Sub-millisecond latency" in master.requirements_section

        assert "### 5. Guardrails & Operational Constraints" in master.constraints_section
        assert "Must not block async event loop" in master.constraints_section
        assert "$5,000" in master.constraints_section

        assert "### 6. Step-by-Step Execution Instructions" in master.instructions_section
        assert "1." in master.instructions_section

        assert "### 7. Output Format Specification" in master.output_format_section
        assert "Production Code with Inline Architectural Annotations" in master.output_format_section

        assert "### 8. Documented Assumptions" in master.assumptions_section
        assert len(master.assumptions) >= 3

        assert "### 9. Self-Verification Quality Checklist" in master.quality_checklist_section
        assert "- [ ]" in master.quality_checklist_section

        # Full text verification: contains all 9 section headers in sequence
        full = master.full_text
        for i in range(1, 10):
            assert f"### {i}." in full

    def test_wedding_planner_master_prompt_scenario(self, compiler, blueprint_selector):
        """User scenario: 'mare wedding planner mate prompt joiye destination wedding in Udaipur'."""
        bp = blueprint_selector.select_blueprint("plan", "Hospitality & Lifestyle", "Wedding Planning Expert")
        reqs = Requirements(
            goal="Coordinate a 3-day luxury destination wedding in Udaipur for 500 guests",
            audience="wedding_guests",
            tone="authoritative",
            format="Event Master Coordination Plan",
            constraints=["Must not exceed ₹50 Lakh budget", "Avoid outdoor ceremonies during peak afternoon heat"],
            deadline="within 3 days",
            budget="50 lakh",
            platform="",
            location="Udaipur",
            entities=[{"text": "Udaipur", "label": "LOCATION"}, {"text": "50 lakh", "label": "BUDGET"}],
            success_criteria=["Complete 3-day run of show", "Contingency plan for weather"],
        )

        ctx = CompilationContext(
            role="Wedding Planning Expert",
            expertise_areas=["Destination wedding logistics", "Royal palace venue coordination", "Vendor management"],
            intent="plan",
            domain="Event Planning & Weddings",
            sub_domains=["Destination Weddings", "Vendor Logistics", "Hospitality"],
            requirements=reqs,
            entities=reqs.entities,
            blueprint=bp,
            language="English",
            tone="authoritative",
            output_format="Event Master Coordination Plan",
            original_detail="mare wedding planner mate prompt joiye destination wedding in Udaipur",
        )

        master = compiler.compile(ctx)

        assert "Wedding Planning Expert" in master.role_section
        assert "Udaipur" in master.context_section
        assert "Event Master Coordination Plan" in master.output_format_section
        assert "50 lakh" in master.constraints_section
        assert "### 9. Self-Verification Quality Checklist" in master.quality_checklist_section

    def test_auto_improvement_enhancement_notes(self, compiler, blueprint_selector):
        """Test that improvement hints from QualityEvaluator feedback loop are incorporated."""
        bp = blueprint_selector.select_blueprint("create", "general", "expert")
        reqs = Requirements(goal="Develop authentication service")
        ctx = CompilationContext(
            role="Security Architect",
            expertise_areas=["OAuth2", "PKCE", "Zero Trust"],
            intent="create",
            domain="Security",
            sub_domains=["Authentication"],
            requirements=reqs,
            entities=[],
            blueprint=bp,
            improvement_hints=[
                "Clarify specific OAuth2 token revocation flow",
                "Add explicit cryptographic hashing algorithm requirement (Argon2id)",
            ],
            iteration=1,
        )

        master = compiler.compile(ctx)
        assert "Quality Enhancement Mandates" in master.full_text
        assert "Argon2id" in master.full_text
        assert "OAuth2 token revocation flow" in master.full_text
