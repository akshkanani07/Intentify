"""QualityEngine – Objective multi-criteria rubric evaluator with strict penalty enforcement."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

from app.engine.spec_extractor import PromptSpec
from app.engine.validators import run_all_validators, QualityAuditResult

logger = logging.getLogger("intentify.engine.quality_engine")


@dataclass
class QualityBreakdownResult:
    """Individual scores across 6 canonical evaluation dimensions."""

    clarity: float = 20.0
    specificity: float = 20.0
    context: float = 15.0
    constraints: float = 15.0
    output_format: float = 15.0
    ambiguity_handling: float = 15.0

    def to_dict(self) -> dict[str, float]:
        return {
            "clarity": round(self.clarity, 2),
            "specificity": round(self.specificity, 2),
            "context": round(self.context, 2),
            "constraints": round(self.constraints, 2),
            "output_format": round(self.output_format, 2),
            "ambiguity_handling": round(self.ambiguity_handling, 2),
        }


@dataclass
class CognitiveQualityBreakdown:
    """Cognitive evaluation scores across enterprise reasoning dimensions."""

    intent_accuracy: float = 100.0
    goal_accuracy: float = 100.0
    role_alignment: float = 100.0
    domain_accuracy: float = 100.0
    blueprint_accuracy: float = 100.0
    requirement_completeness: float = 100.0
    constraint_quality: float = 100.0
    audience_match: float = 100.0
    deliverable_match: float = 100.0
    reasoning_quality: float = 100.0
    structure_depth: float = 100.0
    professionalism: float = 100.0
    role_accuracy: float = 100.0
    requirement_coverage: float = 100.0
    constraint_coverage: float = 100.0
    actionability: float = 100.0
    professional_quality: float = 100.0
    adaptability: float = 100.0

    def to_dict(self) -> dict[str, float]:
        return {
            "intent_accuracy": self.intent_accuracy,
            "goal_accuracy": self.goal_accuracy,
            "role_alignment": self.role_alignment,
            "domain_accuracy": self.domain_accuracy,
            "blueprint_accuracy": self.blueprint_accuracy,
            "requirement_completeness": self.requirement_completeness,
            "constraint_quality": self.constraint_quality,
            "audience_match": self.audience_match,
            "deliverable_match": self.deliverable_match,
            "reasoning_quality": self.reasoning_quality,
            "structure_depth": self.structure_depth,
            "professionalism": self.professionalism,
            "role_accuracy": self.role_accuracy,
            "requirement_coverage": self.requirement_coverage,
            "constraint_coverage": self.constraint_coverage,
            "actionability": self.actionability,
            "professional_quality": self.professional_quality,
            "adaptability": self.adaptability,
        }

    def v4_dimensions(self) -> dict[str, float]:
        return {
            "intent": self.intent_accuracy,
            "goal": self.goal_accuracy,
            "role": self.role_alignment,
            "domain": self.domain_accuracy,
            "blueprint": self.blueprint_accuracy,
            "requirement": self.requirement_completeness,
            "constraint": self.constraint_quality,
            "actionability": self.actionability,
            "professional_quality": self.professional_quality,
            "adaptability": self.adaptability,
        }


@dataclass
class QualityAudit:
    """Rigorous quality evaluation result including rule bonuses and penalty breakdowns."""

    total_score: float
    is_acceptable: bool
    threshold: float = 85.0
    dimension_scores: dict[str, float] = field(default_factory=dict)
    penalties: list[str] = field(default_factory=list)
    bonuses: list[str] = field(default_factory=list)
    hard_check_failed: bool = False
    status: str = 'final'
    audit_result: QualityAuditResult | None = None
    score_before_cap: float = 100.0
    score_after_cap: float = 100.0

    @property
    def breakdown(self) -> QualityBreakdownResult:
        return QualityBreakdownResult(
            clarity=self.dimension_scores.get("clarity", 20.0),
            specificity=self.dimension_scores.get("specificity", 20.0),
            context=self.dimension_scores.get("context", 15.0),
            constraints=self.dimension_scores.get("constraints", 15.0),
            output_format=self.dimension_scores.get("output_format", 15.0),
            ambiguity_handling=self.dimension_scores.get("ambiguity_handling", 15.0),
        )

    @property
    def cognitive_breakdown(self) -> CognitiveQualityBreakdown:
        return CognitiveQualityBreakdown()

    @property
    def detected_gaps(self) -> list[str]:
        if not self.audit_result:
            return []
        return [v.explanation for v in self.audit_result.violations]

    @property
    def failed_rules(self) -> list[str]:
        if not self.audit_result:
            return []
        return [v.code for v in self.audit_result.violations]


class QualityEngine:
    """Evaluates master prompts honestly, enforcing D1-D9 invariants and strict penalties."""

    def __init__(self, threshold: float = 85.0) -> None:
        self.threshold = threshold

    def audit(
        self,
        prompt_text: str,
        spec: PromptSpec | None = None,
        raw_input: str = "",
        standards_registry: dict[str, Any] | None = None,
        ml_adjustment: float = 0.0,
        forbidden_phrases: list[str] | None = None,
        forbidden_headings: list[str] | None = None,
        expected_keywords: list[str] | None = None,
        expected_proficiency: str | None = None,
        expected_domain: str | None = None,
        expected_child: str | None = None,
        expected_intent: str | None = None,
    ) -> QualityAudit:
        text = prompt_text or ""
        lower = text.lower()

        # If raw_input not explicitly supplied, extract from spec
        effective_raw = raw_input or (getattr(spec, "object_subject", "") if spec else "")

        # ── 1. Run Invariant Validators D1 - D9 & Golden Checks ──────
        audit_res = run_all_validators(
            prompt_text=text,
            spec=spec,
            raw_input=effective_raw,
            standards_registry=standards_registry,
            ml_adjustment=ml_adjustment,
            forbidden_phrases=forbidden_phrases,
            forbidden_headings=forbidden_headings,
            expected_keywords=expected_keywords,
            expected_proficiency=expected_proficiency,
            expected_domain=expected_domain,
            expected_child=expected_child,
            expected_intent=expected_intent,
        )

        penalties = [f"-{p['penalty']:.0f} {p['reason']}" for p in audit_res.penalties]
        bonuses: list[str] = []

        # ── 2. Positive Dimension Breakdown for Telemetry ─────────
        clarity = 20.0
        specificity = 20.0
        context = 15.0
        constraints = 15.0
        output_format = 15.0
        ambiguity_handling = 15.0

        for v in audit_res.violations:
            if v.code in ("D1", "D8"):
                clarity = max(0.0, clarity - v.penalty)
            elif v.code in ("D3", "D4"):
                constraints = max(0.0, constraints - v.penalty)
            elif v.code == "D5":
                context = max(0.0, context - v.penalty)
            elif v.code == "D6":
                specificity = max(0.0, specificity - v.penalty)
            elif v.code == "D2":
                ambiguity_handling = max(0.0, ambiguity_handling - v.penalty)

        dimension_scores = {
            "clarity": round(clarity, 1),
            "specificity": round(specificity, 1),
            "context": round(context, 1),
            "constraints": round(constraints, 1),
            "output_format": round(output_format, 1),
            "ambiguity_handling": round(ambiguity_handling, 1),
            "penalties_applied": sum(p["penalty"] for p in audit_res.penalties),
        }

        final_score = audit_res.total_score

        return QualityAudit(
            total_score=final_score,
            is_acceptable=final_score >= self.threshold and not audit_res.hard_check_failed,
            threshold=self.threshold,
            dimension_scores=dimension_scores,
            penalties=penalties,
            bonuses=bonuses,
            hard_check_failed=audit_res.hard_check_failed,
            status=getattr(audit_res, 'status', 'draft' if audit_res.hard_check_failed else 'final'),
            audit_result=audit_res,
            score_before_cap=audit_res.score_before_cap,
            score_after_cap=audit_res.score_after_cap,
        )

    def evaluate(self, prompt_text: str, spec: PromptSpec | None = None) -> QualityAudit:
        """Alias for audit() ensuring unified evaluator interface."""
        return self.audit(prompt_text=prompt_text, spec=spec)

    def suggest_improvements(self, prompt: str, quality_audit: QualityAudit) -> list[str]:
        """Generate actionable improvement recommendations from audit violations."""
        suggestions = []
        if quality_audit.audit_result:
            suggestions.extend([v.explanation for v in quality_audit.audit_result.violations])
        if len(prompt.strip().splitlines()) < 5:
            suggestions.extend([
                "Define boundary constraints and negative guardrails.",
                "Specify clear output structure and deliverable requirements.",
                "Document operational assumptions and domain context.",
            ])
        return suggestions

# Type Aliases for Backward Compatibility
QualityEvaluator = QualityEngine
QualityScore = QualityAudit
