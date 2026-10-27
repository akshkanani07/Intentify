"""Tests for Step 10: Quality Evaluator & Auto-Improvement Feedback Loop."""

import pytest
from app.compiler.blueprint_selector import BlueprintSelector
from app.compiler.prompt_compiler import CompilationContext, PromptCompiler
from app.core.config import get_settings
from app.knowledge.knowledge_manager import KnowledgeManager
from app.nlp.requirement_extractor import Requirements
from app.engine.quality_engine import QualityBreakdownResult, QualityEvaluator, QualityScore
from app.services.orchestrator import PromptOrchestrator


@pytest.fixture
def km():
    return KnowledgeManager()


@pytest.fixture
def evaluator():
    return QualityEvaluator(threshold=85.0)


@pytest.fixture
def compiler(km):
    return PromptCompiler(knowledge_manager=km)


@pytest.fixture
def blueprint_selector(km):
    return BlueprintSelector(knowledge_manager=km)


class TestQualityEvaluator:
    """Verifies the 100-point rubric and evaluation logic."""

    def test_rubric_weights_and_maximums(self, evaluator):
        """Check all 6 evaluation dimensions and their weights summing to 100 points."""
        breakdown = QualityBreakdownResult(
            clarity=20.0,
            specificity=20.0,
            context=15.0,
            constraints=15.0,
            output_format=15.0,
            ambiguity_handling=15.0,
        )
        d = breakdown.to_dict()
        assert d["clarity"] == 20.0
        assert d["specificity"] == 20.0
        assert d["context"] == 15.0
        assert d["constraints"] == 15.0
        assert d["output_format"] == 15.0
        assert d["ambiguity_handling"] == 15.0
        assert sum(d.values()) == 100.0

    def test_compiled_master_prompt_scores_above_threshold(self, evaluator, compiler, blueprint_selector):
        """A complete 9-part Master Prompt should achieve >= 85 points."""
        bp = blueprint_selector.select_blueprint("create", "software_engineering", "Senior Software Architect")
        reqs = Requirements(
            goal="Architect a production-ready asynchronous microservices cluster",
            audience="developers",
            tone="technical",
            format="Production Code with Inline Architectural Annotations",
            constraints=["Never use blocking I/O", "Strictly zero unverified dependencies"],
            deadline="within 10 days",
            budget="$10,000",
            platform="Linux, Docker, AWS",
            location="us-east-1",
            entities=[{"text": "FastAPI", "label": "TECHNOLOGY"}],
            success_criteria=["100% test coverage", "Zero runtime exceptions"],
        )
        ctx = CompilationContext(
            role="Senior Software Architect",
            expertise_areas=["Distributed systems", "Clean Architecture"],
            intent="create",
            domain="Software Development",
            sub_domains=["Backend", "Cloud Architecture"],
            requirements=reqs,
            entities=reqs.entities,
            blueprint=bp,
            output_format="Production Code with Inline Architectural Annotations",
            original_detail="Architect a production-ready asynchronous microservices cluster",
        )

        master = compiler.compile(ctx)
        score = evaluator.evaluate(master.full_text)

        assert isinstance(score, QualityScore)
        assert score.total_score >= 85.0
        assert score.is_acceptable is True
        assert score.breakdown.clarity >= 15.0
        assert score.breakdown.specificity >= 15.0
        assert score.breakdown.context >= 12.0
        assert score.breakdown.constraints >= 12.0
        assert score.breakdown.output_format >= 12.0
        assert score.breakdown.ambiguity_handling >= 12.0

    def test_low_quality_prompt_scores_below_threshold(self, evaluator):
        """Primitive, unstructured input should score significantly below 85 points."""
        poor_prompt = "Write code for a simple website."
        score = evaluator.evaluate(poor_prompt)

        assert isinstance(score, QualityScore)
        assert score.total_score < 85.0
        assert score.is_acceptable is False
        assert len(score.failed_rules) >= 1

    def test_suggest_improvements_for_weak_prompt(self, evaluator):
        """Evaluator must provide targeted recommendations for failing dimensions."""
        poor_prompt = "Fix my bug please."
        score = evaluator.evaluate(poor_prompt)
        suggestions = evaluator.suggest_improvements(poor_prompt, score)

        assert isinstance(suggestions, list)
        assert len(suggestions) >= 2
        # Should flag missing constraints, format, or steps
        assert any("boundary" in s.lower() or "structure" in s.lower() or "assumptions" in s.lower() for s in suggestions)

    def test_auto_improvement_loop_in_orchestrator(self):
        """Test orchestrator re-compilation loop when initial quality is below threshold."""
        orchestrator = PromptOrchestrator()
        from app.api.v1.schemas.prompt import PromptGenerationRequest

        req = PromptGenerationRequest(
            role="",
            detail="mare wedding planner mate prompt joiye destination wedding in Udaipur with budget 50 lakh",
        )

        response = orchestrator.generate_prompt_sync(req)
        assert response.quality_score >= 85.0
        assert ("Role" in response.master_prompt or "ભૂમિકા" in response.master_prompt)
        assert ("Checklist" in response.master_prompt or "યાદી" in response.master_prompt or "માપદંડ" in response.master_prompt)
        assert response.breakdown.total >= 85.0
        assert len(response.assumptions) >= 2
    def test_check_grammar_breaks_detection(self):
        """Invariant: Raw grammar breaks like 'a want to' or 'i am want' are penalized with -20."""
        from app.engine.validators import check_grammar_breaks

        bad_prompt = "### 1. Role\nYou are an expert.\n### 2. Objective\nI am want to build a tool.\n"
        passed, msg, penalty, hits = check_grammar_breaks(bad_prompt)
        assert passed is False
        assert penalty == 20.0
        assert "i am want" in hits

        clean_prompt = "### 1. Role\nYou are a Principal Architect.\n### 2. Objective\nArchitect a scalable microservices cluster.\n"
        passed, msg, penalty, hits = check_grammar_breaks(clean_prompt)
        assert passed is True
        assert penalty == 0.0
        assert len(hits) == 0

    def test_check_d3_raw_input_leak_criteria(self):
        """Invariant D3: User's raw phrasing must not leak verbatim into acceptance criteria."""
        from app.engine.validators import check_d3_raw_input_leak

        raw_input = "i am want to create a project management tool"
        leaked_prompt = (
            "### 1. Role\nYou are an expert.\n"
            "### 2. Core Objective\n"
            "Architect and construct an enterprise task orchestration and milestone tracker.\n"
            "### 3. Acceptance Criteria\n"
            "Fulfills the core objective: 'i am want to create a project management tool'.\n"
        )
        passed, msg, penalty, ratio = check_d3_raw_input_leak(leaked_prompt, raw_input)
        assert passed is False
        assert penalty == 10.0
        assert ratio > 0.30

        clean_prompt = (
            "### 1. Role\nYou are an expert.\n"
            "### 2. Core Objective\n"
            "Architect and construct an enterprise task orchestration and milestone tracker.\n"
            "### 3. Acceptance Criteria\nVerify end-to-end task dependency resolution.\n"
        )
        passed, msg, penalty, ratio = check_d3_raw_input_leak(clean_prompt, raw_input)
        assert passed is True
        assert penalty == 0.0

    def test_score_honesty_hard_check_capping(self):
        """Invariant D7: Any hard check failure caps score at 70.0, ensuring score < 85."""
        from app.engine.validators import calculate_d7_score

        # Normal penalties without hard check failure
        score_normal = calculate_d7_score(penalties=[10.0], hard_check_failed=False)
        assert score_normal == 90.0

        # Hard check failure caps strictly at 70.0
        score_hard_capped = calculate_d7_score(penalties=[20.0], hard_check_failed=True)
        assert score_hard_capped <= 70.0

