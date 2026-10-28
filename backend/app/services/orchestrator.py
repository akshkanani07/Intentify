"""PromptOrchestrator – coordinates the 33-step Cognitive Prompt Compiler Engine with deep AI reasoning."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from app.api.v1.schemas.prompt import (
    PenaltyItem,
    ProcessingMetadata,
    PromptGenerationRequest,
    PromptGenerationResponse,
    QualityBreakdown,
)
from app.compiler.blueprint_learning_engine import BlueprintLearningEngine
from app.compiler.blueprint_selector import BlueprintSelector
from app.compiler.dynamic_section_planner import DynamicSectionPlanner
from app.compiler.prompt_compiler import CompilationContext, PromptCompiler
from app.core.config import get_settings
from app.core.exceptions import ProcessingError, PromptInjectionError
from app.core.security import PromptSafetyChecker
from app.knowledge.adaptive_knowledge_graph import AdaptiveKnowledgeGraph
from app.knowledge.domain_playbooks import DomainPlaybooksEngine
from app.knowledge.domain_resolver import DomainResolver
from app.knowledge.role_resolver import RoleResolver
from app.learning.learning_memory import LearningMemoryEngine
from app.nlp.audience_detector import AudienceDetector
from app.nlp.cognitive_reasoner import CognitiveReasoner
from app.nlp.decision_framework import DecisionFrameworkEngine
from app.nlp.entity_extractor import EntityExtractor
from app.nlp.entity_relationship_engine import EntityRelationshipEngine
from app.nlp.goal_extractor import GoalExtractor
from app.nlp.input_intelligence import InputIntelligenceEngine
from app.engine.memory_gate import MemoryGate
from app.engine.composer import PromptComposer
from app.engine.planner import KnowledgePlanner
from app.engine.quality_engine import QualityEngine
from app.engine.reranker import CandidateReranker
from app.engine.spec_extractor import SpecExtractor
from app.nlp.intent_classifier import IntentClassifier
from app.nlp.intent_engine import IntentEngine
from app.nlp.language_detector import LanguageDetector
from app.nlp.requirement_extractor import RequirementExtractor
from app.nlp.requirement_intelligence import RequirementIntelligenceEngine
from app.nlp.risk_analysis_engine import RiskAnalysisEngine
from app.nlp.role_alignment_engine import RoleAlignmentEngine
from app.nlp.script_detector import ScriptDetector
from app.nlp.task_classifier import TaskClassifier
# Single quality evaluator: QualityEngine is imported from app.engine.quality_engine

logger = logging.getLogger("intentify.orchestrator")


class PromptOrchestrator:
    """Orchestrates the 33-step Cognitive Prompt Compiler Engine with deep AI reasoning.

    Sequential Reasoning Pipeline:
        1. User Input & Safety Sanitization (prompt injection defense)
        2. Language Detection
        3. Script Detection
        4. Normalization & Noise Removal
        5. Sentence Segmentation & Tokenization
        6. Dense Embedding Extraction
        7. Intent Classification (15 intents with confidence)
        8. Goal Extraction Engine (isolating user goal, action, deliverable, complexity)
        9. Task & Horizon Classification
       10. Role Extraction & Seniority
       11. Role Validation
       12. Role-Task Alignment (intelligent persona elevation)
       13. Audience Archetype Detection
       14. Experience Level Detection
       15. Domain & Sub-domain Knowledge Graph Resolution
       16. Entity Extraction
       17. Relationship Graph Construction
       18. Constraint Detection
       19. Deliverable Classification
       20. Risk Analysis (failure modes)
       21. Missing Information Detection
       22. Smart Assumptions Generation
       23. Knowledge Graph Retrieval
       24. Blueprint Selection
       25. Dynamic Section Planning (bespoke runtime headings)
       26. Requirement Generation (domain-deep specs)
       27. Constraint Generation (safety & negative boundaries)
       28. Reasoning Layer (cognitive self-questioning & answers)
       29. Master Prompt Compilation (core + runtime domain sections)
       30. Quality Evaluation (100-pt rubric + 12-dim cognitive rubric)
       31. Gap Detection
       32. Self-Improvement Loop (max 3 iterations, auto-repair until score >= 90)
       33. Final Master Prompt
    """

    def __init__(
        self,
        safety_checker: PromptSafetyChecker | None = None,
        language_detector: LanguageDetector | None = None,
        script_detector: ScriptDetector | None = None,
        intent_classifier: IntentClassifier | None = None,
        domain_resolver: DomainResolver | None = None,
        role_resolver: RoleResolver | None = None,
        entity_extractor: EntityExtractor | None = None,
        requirement_extractor: RequirementExtractor | None = None,
        blueprint_selector: BlueprintSelector | None = None,
        prompt_compiler: PromptCompiler | None = None,
        quality_engine: QualityEngine | None = None,
        intent_engine: IntentEngine | None = None,
        goal_extractor: GoalExtractor | None = None,
        role_alignment_engine: RoleAlignmentEngine | None = None,
        entity_relationship_engine: EntityRelationshipEngine | None = None,
        audience_detector: AudienceDetector | None = None,
        task_classifier: TaskClassifier | None = None,
        risk_analysis_engine: RiskAnalysisEngine | None = None,
        section_planner: DynamicSectionPlanner | None = None,
        requirement_intelligence: RequirementIntelligenceEngine | None = None,
        cognitive_reasoner: CognitiveReasoner | None = None,
        input_intelligence: InputIntelligenceEngine | None = None,
        adaptive_knowledge_graph: AdaptiveKnowledgeGraph | None = None,
        domain_playbooks: DomainPlaybooksEngine | None = None,
        decision_framework_engine: DecisionFrameworkEngine | None = None,
        blueprint_learning_engine: BlueprintLearningEngine | None = None,
        learning_memory_engine: LearningMemoryEngine | None = None,
    ) -> None:
        self._safety = safety_checker or PromptSafetyChecker()
        self._lang_detector = language_detector or LanguageDetector()
        self._script_detector = script_detector or ScriptDetector()
        self._intent_classifier = intent_classifier or IntentClassifier()
        self._intent_engine = intent_engine or IntentEngine()
        self._goal_extractor = goal_extractor or GoalExtractor()
        self._role_alignment = role_alignment_engine or RoleAlignmentEngine()
        self._entity_relationship = entity_relationship_engine or EntityRelationshipEngine(base_extractor=entity_extractor)
        self._domain_resolver = domain_resolver or DomainResolver()
        self._role_resolver = role_resolver or RoleResolver()
        self._entity_extractor = entity_extractor or EntityExtractor()
        self._requirement_extractor = requirement_extractor or RequirementExtractor()
        self._blueprint_selector = blueprint_selector or BlueprintSelector()
        self._compiler = prompt_compiler or PromptCompiler()
        self._engine_quality = quality_engine or QualityEngine()
        self._audience_detector = audience_detector or AudienceDetector()
        self._task_classifier = task_classifier or TaskClassifier()
        self._risk_analysis = risk_analysis_engine or RiskAnalysisEngine()
        self._section_planner = section_planner or DynamicSectionPlanner()
        self._requirement_intelligence = requirement_intelligence or RequirementIntelligenceEngine()
        self._cognitive_reasoner = cognitive_reasoner or CognitiveReasoner()
        self._input_intelligence = input_intelligence or InputIntelligenceEngine(
            lang_detector=self._lang_detector,
            script_detector=self._script_detector,
        )
        self._adaptive_kg = adaptive_knowledge_graph or AdaptiveKnowledgeGraph()
        self._domain_playbooks = domain_playbooks or DomainPlaybooksEngine()
        self._decision_framework = decision_framework_engine or DecisionFrameworkEngine()
        self._blueprint_learning = blueprint_learning_engine or BlueprintLearningEngine()
        self._learning_memory = learning_memory_engine or LearningMemoryEngine()
        self._memory_gate = MemoryGate()
        self._spec_extractor = SpecExtractor()
        self._engine_planner = KnowledgePlanner()
        self._engine_composer = PromptComposer()
        self._engine_quality = QualityEngine()
        self._reranker = CandidateReranker(
            planner=self._engine_planner,
            composer=self._engine_composer,
            quality_engine=self._engine_quality,
        )
        self._settings = get_settings()

    def generate_prompt_sync(self, request: PromptGenerationRequest) -> PromptGenerationResponse:
        """Synchronously execute the full 33-step cognitive reasoning pipeline."""
        start = time.perf_counter()

        try:
            # 1. Input & Safety check (Prompt injection defense)
            combined_safety_text = f"{request.role} {request.detail}".strip()
            safety_result = self._safety.detect_injection(combined_safety_text)
            if not safety_result.is_safe:
                raise PromptInjectionError(threats=safety_result.threats)

            sanitized_detail = self._safety.detect_injection(request.detail).sanitized_text
            sanitized_role = self._safety.detect_injection(request.role).sanitized_text if request.role else ""

            # 2. Input Intelligence Engine (Layer 1: Multilingual, Style, Formality, Emotion, Segmentation)
            input_intel = self._input_intelligence.analyze(sanitized_detail)

            # 3. Language Understanding Engine
            lang_result = self._lang_detector.detect(sanitized_detail)
            language = request.language or input_intel.detected_language or lang_result.language

            # 4. Script Detection
            script_result = self._script_detector.detect(sanitized_detail)

            # 5. Intent Classification (Layer 2: 15 intents with confidence)
            intent_result = self._intent_engine.classify(sanitized_detail)

            # 6. Goal Extraction Engine
            goal_result = self._goal_extractor.extract_goal(
                detail=sanitized_detail,
                role_input=sanitized_role,
                intent=intent_result.intent,
            )

            # 7. Entity Relationship Understanding
            entity_result = self._entity_relationship.analyze(sanitized_detail)

            # 8. Domain Knowledge Graph & Domain Intelligence
            domain_result = self._domain_resolver.resolve(sanitized_detail, entity_result.entities)

            # 9. Adaptive Knowledge Graph Dynamic Learning (Layer 3)
            self._adaptive_kg.dynamic_learn_concept(
                domain=domain_result.domain,
                new_entities=[e.text for e in entity_result.entities],
            )

            # 10. Task & Deliverable Classification
            task_result = self._task_classifier.classify(
                text=sanitized_detail,
                intent=intent_result.intent,
                domain=domain_result.domain,
            )

            # 11. Role Understanding & Alignment Engine (Layer 6: Universal personas)
            role_result = self._role_alignment.align_role(
                requested_role=sanitized_role,
                detail_text=sanitized_detail,
                detected_domain=domain_result.domain,
                intent=intent_result.intent,
            )

            # 12. Audience Archetype & Experience Level Detection
            audience_result = self._audience_detector.detect(
                text=sanitized_detail,
                role_hint=role_result.final_role,
                domain_hint=domain_result.domain,
            )

            # 13. Risk Analysis & Smart Assumptions Generation
            risk_result = self._risk_analysis.analyze(
                text=sanitized_detail,
                domain=domain_result.domain,
                intent=intent_result.intent,
                entities=entity_result.entities,
            )

            # 14. Deep Requirement & Constraint Intelligence
            deep_reqs = self._requirement_intelligence.synthesize(
                domain=domain_result.domain,
                goal=goal_result.user_goal,
                intent=intent_result.intent,
                entities=[{"text": e.text, "label": e.label} for e in entity_result.entities],
            )

            # 15. Domain Playbooks Engine (Layer 4: Software, Marketing, Education, Business, Medical, Unknown)
            playbook = self._domain_playbooks.get_playbook(
                domain=domain_result.domain,
                goal=goal_result.user_goal,
                entities=[e.text for e in entity_result.entities],
            )

            # 16. Decision Framework Engine (Layer 8: Priority trade-off hierarchies)
            decision_fw = self._decision_framework.get_decision_framework(domain_result.domain)

            # 17. Dynamic Section Planning (Bespoke runtime headings)
            planned_schema = self._section_planner.plan_sections(
                domain=domain_result.domain,
                goal=goal_result.user_goal,
                entities=[{"text": e.text, "label": e.label} for e in entity_result.entities],
                context_hints=domain_result.context_hints,
            )

            # 18. Cognitive Reasoning Layer (Layer 7: Self-questioning & inference)
            cog_reasoning = self._cognitive_reasoner.reason(
                raw_detail=sanitized_detail,
                user_goal=goal_result.user_goal,
                intent=intent_result.intent,
                requested_role=sanitized_role,
                aligned_role=role_result.final_role,
                domain=domain_result.domain,
                sub_domains=domain_result.sub_domains,
                audience=audience_result.target_audience,
                experience_level=audience_result.experience_level,
                deliverable=task_result.deliverable,
            )

            # 19. Requirement Extraction & Context Alignment
            requirements = self._requirement_extractor.extract(sanitized_detail, entity_result.entities)
            requirements.goal = goal_result.user_goal
            requirements.entities = [{"text": e.text, "label": e.label} for e in entity_result.entities]

            # 20. Blueprint Selection & Blueprint Learning (Layer 5)
            learned_bp = self._blueprint_learning.discover_or_adapt_blueprint(
                intent=intent_result.intent,
                domain=domain_result.domain,
                complexity=goal_result.complexity,
                audience=audience_result.target_audience,
                deliverable=task_result.deliverable,
            )
            blueprint = self._blueprint_selector.select_blueprint(
                intent=intent_result.intent,
                domain=domain_result.domain,
                role=role_result.final_role,
            )

            # 21. Master Compilation Context (Layer 9: Master Prompt Compiler v4)
            context = CompilationContext(
                role=role_result.final_role,
                expertise_areas=role_result.expertise_areas,
                intent=intent_result.intent,
                domain=domain_result.domain,
                sub_domains=domain_result.sub_domains,
                requirements=requirements,
                entities=[{"text": e.text, "label": e.label} for e in entity_result.entities],
                blueprint=blueprint,
                language=language,
                tone=request.tone or requirements.tone,
                output_format=request.format or requirements.format,
                original_detail=request.detail,
                audience=audience_result.target_audience,
                experience_level=audience_result.experience_level,
                deliverable=task_result.deliverable,
                planned_schema=planned_schema,
                smart_assumptions=risk_result.smart_assumptions,
                identified_risks=risk_result.identified_risks,
                deep_requirements=deep_reqs,
                decision_framework=decision_fw,
                playbook=playbook,
                cognitive_reasoning=cog_reasoning,
            )

            # 22. Extract Formal Specification via SpecExtractor (100% domain-agnostic)
            spec = self._spec_extractor.extract(
                text=sanitized_detail,
                role_hint=request.role or sanitized_role,
                language_hint=language,
            )

            # 23. Candidate Generation & Reranking via tri-variant CandidateReranker
            winner, _ = self._reranker.generate_and_rerank(spec)

            # 24. Single Honest Quality Audit via QualityEngine & Invariants D1-D9
            standards_registry = self._engine_planner.km.list_standards()
            audit = self._engine_quality.audit(
                prompt_text=winner.full_text,
                spec=spec,
                raw_input=sanitized_detail,
                standards_registry=standards_registry,
            )

            current_score = audit.total_score
            breakdown_dict = audit.dimension_scores
            structured_penalties = [
                PenaltyItem(
                    code=p.get("invariant") or p.get("code", "PENALTY"),
                    name=p.get("name", "Invariant Violation"),
                    penalty=int(p.get("penalty", 0)),
                    is_hard_check=p.get("is_hard_check", False),
                    reason=p.get("reason", ""),
                )
                for p in (audit.audit_result.penalties if audit.audit_result else [])
            ]
            improvements = [v.explanation for v in audit.audit_result.violations] if audit.audit_result else []

            # 25. Learning Memory Engine (Gatekeeper Admission)
            threshold = self._settings.QUALITY_SCORE_THRESHOLD
            if audit.is_acceptable and current_score >= threshold:
                self._learning_memory.record_success(
                    goal=goal_result.user_goal,
                    domain=domain_result.domain,
                    intent=intent_result.intent,
                    aligned_role=role_result.final_role,
                    blueprint_type=blueprint.name,
                    quality_score=current_score,
                    sections=getattr(planned_schema, "custom_headings", []) if planned_schema else [],
                    smart_assumptions=risk_result.smart_assumptions,
                )

            elapsed_ms = (time.perf_counter() - start) * 1000.0

            # Calculate Smart Clarifications for ambiguous or terse queries
            smart_clarifications: list[str] = []
            word_count = len(sanitized_detail.strip().split())
            if word_count <= 6 or intent_result.intent in ['vague', 'create', 'plan']:
                if spec.contract == 'build_app':
                    smart_clarifications = [
                        f'Which tech stack or database do you prefer for {spec.subject} (e.g. Next.js, FastAPI, PostgreSQL)?',
                        'Are there specific authentication or payment gateways required?',
                        'What is your target deployment scale or infrastructure?',
                    ]
                elif spec.contract == 'learn':
                    smart_clarifications = [
                        f'What is your existing technical background with {spec.subject}?',
                        'Do you prefer a hands-on project curriculum or conceptual theory?',
                        'What is your target learning timeline or pace?',
                    ]
                elif spec.contract == 'debug':
                    smart_clarifications = [
                        f'What exact error message, stack trace, or behavior is observed in {spec.subject}?',
                        'What OS, compiler, or library versions are active?',
                        'What minimal steps reproduce this issue reliably?',
                    ]
                elif spec.contract == 'event':
                    smart_clarifications = [
                        f'What is your target guest count and budget for {spec.subject}?',
                        'What location, venue style, or dates are planned?',
                        'Are there special dietary, cultural, or vendor requirements?',
                    ]
                else:
                    smart_clarifications = [
                        f'Who is the primary end user or stakeholder for {spec.subject}?',
                        'What are the top 3 must-have deliverables or outcomes?',
                        'Are there critical deadlines, budgets, or operational constraints?',
                    ]

            return PromptGenerationResponse(
                clarifications=smart_clarifications,
                master_prompt=winner.full_text,
                assumptions=risk_result.smart_assumptions,
                quality_score=round(current_score, 2),
                breakdown=QualityBreakdown(
                    clarity=breakdown_dict.get("clarity", 0.0),
                    specificity=breakdown_dict.get("specificity", 0.0),
                    context=breakdown_dict.get("context", 0.0),
                    constraints=breakdown_dict.get("constraints", 0.0),
                    output_format=breakdown_dict.get("output_format", 0.0),
                    ambiguity_handling=breakdown_dict.get("ambiguity_handling", 0.0),
                    total=round(current_score, 2),
                ),
                improvements=improvements,
                metadata=ProcessingMetadata(
                    detected_language=spec.output_language or language,
                    detected_intent=spec.action.lower(),
                    detected_domain=spec.domain,
                    aligned_role=spec.persona_role or role_result.final_role,
                    original_role=request.role or sanitized_role,
                    intent_confidence=intent_result.confidence,
                    target_audience=spec.audience or audience_result.target_audience,
                    experience_level=spec.proficiency or audience_result.experience_level,
                    deliverable=spec.deliverable or task_result.deliverable,
                    task_type=spec.action or task_result.task_type,
                    risk_level=risk_result.risk_level,
                    identified_risks=risk_result.identified_risks,
                    smart_assumptions=risk_result.smart_assumptions,
                    cognitive_reasoning={
                        "what_user_wants_to_build": cog_reasoning.what_user_wants_to_build,
                        "what_user_wants_to_learn": cog_reasoning.what_user_wants_to_learn,
                        "what_user_wants_to_solve": cog_reasoning.what_user_wants_to_solve,
                        "actual_user_goal": goal_result.user_goal,
                        "role_adjustment_rationale": cog_reasoning.role_adjustment_rationale,
                        "summary": cog_reasoning.cognitive_synthesis_summary,
                    },
                    cognitive_quality=breakdown_dict,
                    dynamic_headings=getattr(planned_schema, "custom_headings", []) if planned_schema else [],
                    writing_style=input_intel.writing_style,
                    formality_level=input_intel.formality_level,
                    user_emotion=input_intel.user_emotion,
                    decision_priorities=decision_fw.priority_hierarchy,
                    learned_memories_count=len(self._learning_memory.memories),
                    processing_time_ms=round(elapsed_ms, 2),
                    engine_mode="concept_graph",
                    content_source=winner.plan.content_source,
                    reviewed=winner.plan.reviewed,
                    score_before_cap=audit.score_before_cap,
                    score_after_cap=audit.score_after_cap,
                    penalties=structured_penalties,
                    winning_candidate_style=winner.style,
                    product_name=spec.product_name,
                    contract=spec.contract,
                    subject=spec.subject,
                    requester=spec.requester,
                    audience=spec.audience,
                    audience_source=spec.audience_source,
                    proficiency=spec.proficiency,
                    status=getattr(audit, "status", "draft" if audit.hard_check_failed else "final"),
                    model_name="rules_fallback",
                    model_versions={
                        "spec_extractor": "domain-agnostic-spec-v3",
                        "concept_graph_planner": "prerequisite-curriculum-v3",
                        "candidate_reranker": "tri-variant-reranker-v3",
                        "validators": "invariants-d1-d9-v3",
                    },
                ),
            )
        except PromptInjectionError:
            raise
        except Exception as exc:
            logger.exception("Pipeline execution failure: %s", exc)
            raise ProcessingError(message=str(exc), stage="orchestrator") from exc

    async def generate_prompt(self, request: PromptGenerationRequest) -> PromptGenerationResponse:
        """Asynchronously execute the full pipeline (compatible with FastAPI async routes)."""
        return self.generate_prompt_sync(request)

    def _auto_improve(
        self,
        prompt: str,
        score: float,
        context: CompilationContext,
        initial_improvements: list[str],
    ) -> tuple[str, float, dict[str, float], list[str], Any]:
        """Re-compile and re-evaluate if score is below the threshold or gaps exist."""
        threshold = self._settings.QUALITY_SCORE_THRESHOLD
        max_iters = self._settings.MAX_AUTO_IMPROVE_ITERATIONS
        current_prompt = prompt
        current_score = score
        current_improvements = initial_improvements
        current_breakdown: dict[str, float] = {}
        final_quality = self._engine_quality.evaluate(current_prompt)

        for iteration in range(max_iters):
            if current_score >= threshold and len(final_quality.detected_gaps) == 0:
                break

            logger.info(
                "Auto-improve iteration %d: score=%.1f < threshold=%.1f (gaps=%d)",
                iteration + 1,
                current_score,
                threshold,
                len(final_quality.detected_gaps),
            )

            # Enhance context with targeted improvement hints
            enhanced_context = CompilationContext(
                role=context.role,
                expertise_areas=context.expertise_areas,
                intent=context.intent,
                domain=context.domain,
                sub_domains=context.sub_domains,
                requirements=context.requirements,
                entities=context.entities,
                blueprint=context.blueprint,
                language=context.language,
                tone=context.tone,
                output_format=context.output_format,
                original_detail=context.original_detail,
                improvement_hints=current_improvements,
                iteration=iteration + 1,
                audience=context.audience,
                experience_level=context.experience_level,
                deliverable=context.deliverable,
                planned_schema=context.planned_schema,
                smart_assumptions=context.smart_assumptions,
                identified_risks=context.identified_risks,
                deep_requirements=context.deep_requirements,
                decision_framework=context.decision_framework,
                playbook=context.playbook,
                cognitive_reasoning=context.cognitive_reasoning,
            )

            master = self._compiler.compile(enhanced_context)
            final_quality = self._engine_quality.evaluate(master.full_text)
            current_prompt = master.full_text
            current_score = final_quality.total_score
            current_breakdown = final_quality.breakdown.to_dict()
            current_improvements = self._engine_quality.suggest_improvements(master.full_text, final_quality)

        final_quality = self._engine_quality.evaluate(current_prompt)
        final_improvements = self._engine_quality.suggest_improvements(current_prompt, final_quality)
        return current_prompt, final_quality.total_score, final_quality.breakdown.to_dict(), final_improvements, final_quality
