"""Candidate Generator & Reranker – Synthesizes multiple prompt variants (Concise, Standard, Deep) and ranks them using QualityEngine."""

from __future__ import annotations

import copy
import logging
from dataclasses import dataclass, field
from typing import Any

from app.engine.composer import PromptComposer
from app.engine.planner import KnowledgePlanner, PromptPlan
from app.engine.quality_engine import QualityAudit, QualityEngine
from app.engine.spec_extractor import PromptSpec

logger = logging.getLogger("intentify.engine.reranker")


@dataclass
class CandidatePrompt:
    """An individual candidate master prompt variant."""

    style: str  # "concise", "standard", "deep"
    full_text: str
    audit: QualityAudit
    plan: PromptPlan


class CandidateReranker:
    """Generates three distinct prompt candidates and reranks them to return the highest-scoring master prompt."""

    def __init__(
        self,
        planner: KnowledgePlanner | None = None,
        composer: PromptComposer | None = None,
        quality_engine: QualityEngine | None = None,
    ) -> None:
        self.planner = planner or KnowledgePlanner()
        self.composer = composer or PromptComposer()
        self.quality_engine = quality_engine or QualityEngine()

    def generate_and_rerank(self, spec: PromptSpec) -> tuple[CandidatePrompt, list[CandidatePrompt]]:
        """Generate concise, standard, and deep candidates; score each; pick the optimal winner."""
        base_plan = self.planner.plan(spec)
        standards_registry = self.planner.km.list_standards()
        raw_input = spec.object_subject

        candidates: list[CandidatePrompt] = []

        # 1. Standard Candidate
        standard_text = self.composer.compose(spec, base_plan, style="standard")
        standard_audit = self.quality_engine.audit(standard_text, spec, raw_input=raw_input, standards_registry=standards_registry)
        candidates.append(CandidatePrompt(
            style="standard",
            full_text=standard_text,
            audit=standard_audit,
            plan=base_plan,
        ))

        # 2. Concise Candidate (Focused core directives, compact sections while preserving D1 topics)
        concise_plan = copy.deepcopy(base_plan)
        for sec in concise_plan.sections:
            if "curriculum" not in sec.heading.lower() and "topic" not in sec.heading.lower() and "અભ્યાસક્રમ" not in sec.heading.lower():
                if len(sec.directives) > 3:
                    sec.directives = sec.directives[:3]

        concise_text = self.composer.compose(spec, concise_plan, style="concise")
        concise_audit = self.quality_engine.audit(concise_text, spec, raw_input=raw_input, standards_registry=standards_registry)
        candidates.append(CandidatePrompt(
            style="concise",
            full_text=concise_text,
            audit=concise_audit,
            plan=concise_plan,
        ))

        # 3. Deep Candidate (Enriched with architectural / pedagogical depth & edge case validation)
        deep_plan = copy.deepcopy(base_plan)
        for sec in deep_plan.sections:
            if "objective" in sec.heading.lower() or "ઉદ્દેશ્ય" in sec.heading.lower():
                sec.directives.append("Mandate 100% production readiness with zero unaddressed operational edge cases.")
            elif "criteria" in sec.heading.lower() or "માપદંડ" in sec.heading.lower():
                sec.directives.append("Conduct comprehensive verification across all nominal and failure boundary states.")

        deep_text = self.composer.compose(spec, deep_plan, style="deep")
        deep_audit = self.quality_engine.audit(deep_text, spec, raw_input=raw_input, standards_registry=standards_registry)
        candidates.append(CandidatePrompt(
            style="deep",
            full_text=deep_text,
            audit=deep_audit,
            plan=deep_plan,
        ))

        # Sort: Hard check passes first, then highest total score
        ranked = sorted(candidates, key=lambda c: (not c.audit.hard_check_failed, c.audit.total_score), reverse=True)
        winner = ranked[0]

        # 4. S8: Single-Attempt Regeneration on Hard-Check Failure
        if winner.audit.hard_check_failed:
            import re
            audit_res = winner.audit.audit_result
            violations = audit_res.violations if audit_res else []
            logger.info(
                "Triggering S8 regeneration due to hard check failure in winner: %s",
                [v.name for v in violations if v.is_hard_check],
            )
            repaired_spec = copy.deepcopy(spec)
            repair_constraints = list(repaired_spec.constraints or [])

            for v in violations:
                if v.is_hard_check:
                    if "forbidden phrases" in v.explanation.lower():
                        hits = re.findall(r":\s*([^\.]+)", v.explanation)
                        if hits:
                            for phr in hits[0].split(","):
                                p_clean = phr.strip()
                                if p_clean:
                                    repair_constraints.append(f"avoid {p_clean}")
                    elif "alien heading" in v.explanation.lower():
                        m = re.search(r"alien heading '([^']+)'", v.explanation, re.IGNORECASE)
                        if m:
                            repair_constraints.append(f"exclude {m.group(1)}")

            repaired_spec.constraints = repair_constraints
            repaired_plan = self.planner.plan(repaired_spec)

            # Filter alien headings directly from sections if contract specified
            filtered_sections = []
            for sec in repaired_plan.sections:
                sec_h = sec.heading.lower()
                if repaired_spec.contract == "learn" and any(ah in sec_h for ah in ["system architecture", "resolution patch"]):
                    continue
                if repaired_spec.contract in ("build_app", "build_tool") and any(ah in sec_h for ah in ["curriculum", "resolution patch"]):
                    continue
                filtered_sections.append(sec)
            repaired_plan.sections = filtered_sections

            repaired_text = self.composer.compose(repaired_spec, repaired_plan, style=winner.style)
            repaired_audit = self.quality_engine.audit(
                repaired_text, repaired_spec, raw_input=raw_input, standards_registry=standards_registry
            )

            if (not repaired_audit.hard_check_failed) or (repaired_audit.total_score > winner.audit.total_score):
                logger.info(
                    "S8 regeneration improved score from %.1f to %.1f (hard_check_failed=%s)",
                    winner.audit.total_score, repaired_audit.total_score, repaired_audit.hard_check_failed,
                )
                winner = CandidatePrompt(
                    style=f"{winner.style}_repaired",
                    full_text=repaired_text,
                    audit=repaired_audit,
                    plan=repaired_plan,
                )
                candidates.append(winner)

        logger.info(
            "Reranker selected '%s' candidate with score %.1f/100 (hard_check_failed=%s)",
            winner.style, winner.audit.total_score, winner.audit.hard_check_failed
        )
        return winner, ranked
