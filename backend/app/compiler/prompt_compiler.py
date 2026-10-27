"""PromptCompiler – assembles an enterprise-grade Master Prompt from extracted context and dynamic domain blueprints."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

from app.compiler.blueprint_selector import Blueprint
from app.compiler.template_engine import TemplateEngine
from app.knowledge.knowledge_manager import KnowledgeManager

logger = logging.getLogger("intentify.compiler.prompt_compiler")


@dataclass
class CompilationContext:
    """All structured context gathered by the intelligence pipeline fed into the compiler."""

    role: str
    expertise_areas: list[str]
    intent: str
    domain: str
    sub_domains: list[str]
    requirements: Any  # Requirements dataclass from requirement_extractor
    entities: list[dict[str, object]]
    blueprint: Blueprint
    language: str = "English"
    tone: str = "professional"
    output_format: str = "Detailed Technical Response"
    original_detail: str = ""
    improvement_hints: list[str] = field(default_factory=list)
    iteration: int = 0
    audience: str = "General Practitioners"
    experience_level: str = "Intermediate / Practitioner"
    deliverable: str = ""
    planned_schema: Any = None  # PlannedSectionSchema from dynamic_section_planner
    smart_assumptions: list[str] = field(default_factory=list)
    identified_risks: list[str] = field(default_factory=list)
    deep_requirements: Any = None  # DeepRequirementBundle from requirement_intelligence
    decision_framework: Any = None  # DecisionRuleResult from decision_framework
    playbook: Any = None  # DomainPlaybook from domain_playbooks
    cognitive_reasoning: Any = None


@dataclass
class MasterPrompt:
    """Compiled master prompt containing core foundational sections and bespoke dynamic domain sections."""

    role_section: str
    objective_section: str
    context_section: str
    requirements_section: str
    constraints_section: str
    instructions_section: str
    output_format_section: str
    assumptions_section: str
    quality_checklist_section: str
    full_text: str
    assumptions: list[str] = field(default_factory=list)
    dynamic_sections: list[dict[str, str]] = field(default_factory=list)
    decision_framework_section: str = ""
    playbook_section: str = ""


class PromptCompiler:
    """Assembles an enterprise-grade Master Prompt with dynamic runtime domain sections."""

    def __init__(
        self,
        template_engine: TemplateEngine | None = None,
        knowledge_manager: KnowledgeManager | None = None,
    ) -> None:
        self._engine = template_engine or TemplateEngine()
        self._km = knowledge_manager or KnowledgeManager()

    def compile(self, ctx: CompilationContext) -> MasterPrompt:
        """Build all core prompt sections, append bespoke dynamic domain sections, and assemble into MasterPrompt."""
        role_section = self._build_role(ctx)
        objective_section = self._build_objective(ctx)
        context_section = self._build_context(ctx)
        requirements_section = self._build_requirements(ctx)
        constraints_section = self._build_constraints(ctx)
        instructions_section = self._build_instructions(ctx)
        output_format_section = self._build_output_format(ctx)
        assumptions = self._build_assumptions(ctx)
        assumptions_section = self._format_assumptions(assumptions)
        quality_checklist_section = self._build_quality_checklist(ctx)

        sections = [
            role_section,
            objective_section,
            context_section,
            requirements_section,
            constraints_section,
            instructions_section,
            output_format_section,
            assumptions_section,
            quality_checklist_section,
        ]

        # Cognitive Reasoning & Decision Framework Section
        decision_section = self._build_decision_framework(ctx)
        if decision_section:
            sections.append(decision_section)

        # Domain Architecture & Playbook Deep-Dive Section
        playbook_section = self._build_playbook(ctx)
        if playbook_section:
            sections.append(playbook_section)

        # Dynamic runtime domain sections (Architecture, API, Database, Security, etc.)
        dynamic_section_dicts: list[dict[str, str]] = []
        if ctx.planned_schema and getattr(ctx.planned_schema, "dynamic_sections", None):
            base_idx = len(sections) + 1
            for offset, dyn in enumerate(ctx.planned_schema.dynamic_sections):
                curr_idx = base_idx + offset
                sec_text = f"### {curr_idx}. {dyn.heading}\n{dyn.content}"
                sections.append(sec_text)
                dynamic_section_dicts.append({
                    "index": str(curr_idx),
                    "heading": dyn.heading,
                    "content": dyn.content,
                })

        # Append auto-improvement directives if present in feedback loop
        if ctx.improvement_hints:
            enhancement = self._build_enhancement_section(ctx.improvement_hints)
            sections.append(enhancement)

        # Deduplicate sections by normalized heading to prevent duplicate topics across modules
        seen_headings: set[str] = set()
        deduped_sections: list[str] = []
        for sec in sections:
            if not sec or not sec.strip():
                continue
            first_line = sec.strip().split("\n", 1)[0]
            heading_match = re.search(r"^###\s*(?:\d+\.\s*)?(.+)$", first_line)
            if heading_match:
                norm_h = re.sub(r"[^\w\s]", "", heading_match.group(1)).strip().lower()
                if norm_h in seen_headings:
                    logger.info("Deduplicating duplicate section heading: '%s'", heading_match.group(1))
                    continue
                seen_headings.add(norm_h)
            deduped_sections.append(sec)

        # Renumber ### headers sequentially
        renumbered_sections: list[str] = []
        for idx, sec in enumerate(deduped_sections, 1):
            renumbered_sec = re.sub(r"^###\s*(?:\d+\.\s*)?", f"### {idx}. ", sec, count=1)
            renumbered_sections.append(renumbered_sec)

        full_text = "\n\n".join(section for section in renumbered_sections if section.strip())

        logger.info(
            "Compiled Master Prompt: %d chars across %d sections (iteration=%d)",
            len(full_text),
            len(sections),
            ctx.iteration,
        )

        return MasterPrompt(
            role_section=role_section,
            objective_section=objective_section,
            context_section=context_section,
            requirements_section=requirements_section,
            constraints_section=constraints_section,
            instructions_section=instructions_section,
            output_format_section=output_format_section,
            assumptions_section=assumptions_section,
            quality_checklist_section=quality_checklist_section,
            full_text=full_text,
            assumptions=assumptions,
            dynamic_sections=dynamic_section_dicts,
            decision_framework_section=decision_section,
            playbook_section=playbook_section,
        )

    # ── 1. Role Section ──────────────────────────────────────────

    def _build_role(self, ctx: CompilationContext) -> str:
        expertise = ", ".join(ctx.expertise_areas) if ctx.expertise_areas else ctx.domain
        return (
            "### 1. Role & Persona\n"
            f"You are an industry-leading **{ctx.role}**, recognized for authoritative mastery in {expertise}. "
            "Approach this assignment with the rigorous precision, strategic clarity, and uncompromising execution standards of a principal practitioner."
        )

    # ── 2. Objective Section ─────────────────────────────────────

    def _build_objective(self, ctx: CompilationContext) -> str:
        goal = getattr(ctx.requirements, "goal", "") or ctx.original_detail
        # Strip any role prefix if present
        if ctx.role and goal.lower().startswith(ctx.role.lower()):
            goal = re.sub(rf"^{re.escape(ctx.role)}\s*[:\-–]\s*", "", goal, flags=re.IGNORECASE)
        # Clean subjective conversational prefixes and colloquial grammar breaks
        goal = re.sub(
            r"^(?:i am want to|a want to|want to|i want to|i need to|please|can you|could you|help me(?: learn)?)\s+(?:make|create|build|develop|learn|design)?\s*",
            "",
            goal,
            flags=re.IGNORECASE,
        )
        # Ensure goal starts with an action verb if not already
        if not any(goal.lower().startswith(v) for v in ["build", "create", "develop", "design", "plan", "master", "diagnose", "analyze", "draft", "implement", "execute", "solve", "learn"]):
            goal = f"Build a {goal}" if not goal.lower().startswith("a ") else f"Build {goal}"

        goal = goal.strip().rstrip(".")
        return (
            "### 2. Core Objective\n"
            f"Your primary mission is to: **{goal}**.\n\n"
            "Ensure every facet of this directive is thoroughly executed with zero ambiguity, omissions, or superficial approximations."
        )

    # ── 3. Context Section ───────────────────────────────────────

    def _build_context(self, ctx: CompilationContext) -> str:
        lines = [
            "### 3. Context & Background",
            f"- **Primary Domain**: {ctx.domain}",
        ]
        if ctx.sub_domains:
            lines.append(f"- **Domain Specializations**: {', '.join(ctx.sub_domains)}")
        lines.append(f"- **Target Audience**: {ctx.audience}")
        lines.append(f"- **Proficiency Horizon**: {ctx.experience_level}")
        if ctx.deliverable:
            lines.append(f"- **Primary Deliverable**: {ctx.deliverable}")
        lines.append(f"- **Operational Language**: {ctx.language}")
        lines.append(f"- **Communication Tone**: {ctx.tone.title()}")

        req = ctx.requirements
        if hasattr(req, "location") and req.location:
            lines.append(f"- **Geographic Location / Venue**: {req.location}")

        if ctx.entities:
            entity_summaries = []
            for e in ctx.entities:
                text = e.get("text", "")
                lbl = e.get("label", "")
                if text and lbl:
                    entity_summaries.append(f"{text} ({lbl})")
            if entity_summaries:
                lines.append(f"- **Key Domain Entities**: {', '.join(entity_summaries[:8])}")

        return "\n".join(lines)

    # ── 4. Requirements Section ──────────────────────────────────

    def _build_requirements(self, ctx: CompilationContext) -> str:
        lines = ["### 4. Technical & Functional Requirements"]
        req = ctx.requirements

        if hasattr(req, "goal") and req.goal:
            lines.append(f"- **Core Deliverable**: {req.goal}")
        if hasattr(req, "platform") and req.platform:
            lines.append(f"- **Target Platform / Runtime**: {req.platform}")

        # Deep synthesized functional requirements
        if ctx.deep_requirements and getattr(ctx.deep_requirements, "functional_requirements", None):
            lines.append("- **Domain-Specific Functional Specifications**:")
            for fr in ctx.deep_requirements.functional_requirements:
                lines.append(f"  - {fr}")

        if hasattr(req, "success_criteria") and req.success_criteria:
            lines.append("- **Verifiable Acceptance Criteria**:")
            for sc in req.success_criteria:
                lines.append(f"  - {sc}")

        # Blueprint requirements
        if ctx.blueprint and ctx.blueprint.requirements:
            lines.append("- **Blueprint Quality Benchmarks**:")
            for br in ctx.blueprint.requirements:
                lines.append(f"  - {br}")

        if len(lines) == 1:
            lines.append("- Provide a comprehensive, modular, and production-ready solution.")
            lines.append("- Ensure all functional requirements are met end-to-end.")

        return "\n".join(lines)

    # ── 5. Constraints Section ───────────────────────────────────

    def _build_constraints(self, ctx: CompilationContext) -> str:
        lines = ["### 5. Guardrails & Operational Constraints"]
        req = ctx.requirements

        if hasattr(req, "constraints") and req.constraints:
            lines.append("- **Operational Guardrails & Prohibitions**:")
            for c in req.constraints:
                lines.append(f"  - {c}")

        # Deep synthesized constraints
        if ctx.deep_requirements and getattr(ctx.deep_requirements, "technical_constraints", None):
            lines.append("- **Domain Safety & Execution Constraints**:")
            for tc in ctx.deep_requirements.technical_constraints:
                lines.append(f"  - {tc}")

        if hasattr(req, "deadline") and req.deadline:
            lines.append(f"- **Mandatory Timeline**: {req.deadline}")
        if hasattr(req, "budget") and req.budget:
            lines.append(f"- **Budget Allocation Ceiling**: {req.budget}")

        if ctx.blueprint and ctx.blueprint.constraints:
            for bc in ctx.blueprint.constraints:
                lines.append(f"- {bc}")

        lines.append("- **Quality Mandates**: Production-ready completeness; strictly zero placeholders, TODOs, or mock stubs.")
        return "\n".join(lines)

    # ── 6. Instructions Section ──────────────────────────────────

    def _build_instructions(self, ctx: CompilationContext) -> str:
        lines = ["### 6. Step-by-Step Execution Instructions"]
        if ctx.blueprint and ctx.blueprint.steps:
            for idx, step in enumerate(ctx.blueprint.steps, 1):
                lines.append(f"{idx}. {step}")
        else:
            lines.extend([
                "1. Analyze all objectives, parameters, and boundary conditions systematically.",
                "2. Formulate the core architectural and conceptual structure.",
                "3. Execute the implementation with rigorous attention to detail and standards.",
                "4. Verify all edge cases, negative constraints, and compliance factors.",
                "5. Review for total clarity, completeness, and immediate actionability.",
            ])
        return "\n".join(lines)

    # ── 7. Output Format Section ─────────────────────────────────

    def _build_output_format(self, ctx: CompilationContext) -> str:
        fmt = ctx.output_format or "Detailed Technical Response"
        return (
            "### 7. Output Format Specification\n"
            f"Deliver the complete response strictly formatted as **{fmt}**.\n"
            "- Use clean GitHub-flavored markdown with structured headers, bullet points, and demarcated blocks.\n"
            "- Provide exhaustive and un-truncated details directly inline without referring the reader to external links."
        )

    # ── 8. Assumptions Section ───────────────────────────────────

    def _build_assumptions(self, ctx: CompilationContext) -> list[str]:
        assumptions: list[str] = []

        # Smart assumptions synthesized by RiskAnalysisEngine
        if ctx.smart_assumptions:
            assumptions.extend(ctx.smart_assumptions)

        # Knowledge Base Domain-specific assumptions
        try:
            kb_assumptions = self._km.get_assumptions()
            domain_assumptions_map = kb_assumptions.get("domain_assumptions", {})
            for dom_key, d_assumps in domain_assumptions_map.items():
                if dom_key.lower() in ctx.domain.lower() or ctx.domain.lower() in dom_key.lower():
                    assumptions.extend(d_assumps[:2])
                    break
        except Exception as exc:
            logger.debug("Failed loading domain assumptions: %s", exc)

        req = ctx.requirements
        if hasattr(req, "audience") and req.audience and not any("target audience" in a.lower() for a in assumptions):
            assumptions.append(f"Target audience operates with the background knowledge expected of {req.audience}")
        elif not any("target audience" in a.lower() for a in assumptions):
            assumptions.append(f"Target audience operates with the background knowledge expected of {ctx.audience}")

        if not (hasattr(req, "platform") and req.platform) and not any("infrastructure" in a.lower() for a in assumptions):
            assumptions.append(f"Standard enterprise infrastructure and deployment conventions for {ctx.domain} apply")

        if not (hasattr(req, "deadline") and req.deadline) and not any("timeline" in a.lower() for a in assumptions):
            assumptions.append("Standard development and milestone timelines apply with reasonable schedule contingency")

        assumptions.append(f"Deliverable must be composed in {ctx.language} maintaining a {ctx.tone} register")

        # Deduplicate while preserving order
        unique_assumptions: list[str] = []
        for a in assumptions:
            if a not in unique_assumptions:
                unique_assumptions.append(a)

        return unique_assumptions[:6]

    def _format_assumptions(self, assumptions: list[str]) -> str:
        if not assumptions:
            return ""
        lines = ["### 8. Documented Assumptions"]
        for a in assumptions:
            lines.append(f"- {a}")
        return "\n".join(lines)

    # ── 9. Quality Checklist Section ─────────────────────────────

    def _build_quality_checklist(self, ctx: CompilationContext) -> str:
        fmt = ctx.output_format or "Detailed Technical Response"
        return (
            "### 9. Self-Verification Quality Checklist\n"
            "Verify all items before output delivery:\n"
            "- [ ] Core objective executed completely and without ambiguity\n"
            f"- [ ] Role persona authority and {ctx.tone} tone maintained throughout\n"
            "- [ ] All stated constraints, timeline limits, and budget ceilings respected\n"
            f"- [ ] Output format strictly complies with '{fmt}'\n"
            "- [ ] Zero placeholder code, stubs, TODOs, or unverified claims\n"
            "- [ ] Documented assumptions validated for operational safety"
        )

    # ── 10. Cognitive Reasoning Strategy & Decision Framework ────

    def _build_decision_framework(self, ctx: CompilationContext) -> str:
        df = ctx.decision_framework
        if not df:
            return ""

        priorities_str = " > ".join(df.priority_hierarchy) if hasattr(df, "priority_hierarchy") else "Clarity > Rigor > Value"
        rationale = getattr(df, "tradeoff_rationale", "")
        lines = [
            "### 10. Cognitive Reasoning Strategy & Decision Framework",
            f"- **Domain Priority Hierarchy**: {priorities_str}",
        ]
        if rationale:
            lines.append(f"- **Trade-off Philosophy**: {rationale}")

        matrix = getattr(df, "decision_matrix", [])
        if matrix:
            lines.append("- **Governance Rules & Decision Matrix**:")
            for item in matrix:
                rank = item.get("rank", "")
                dim = item.get("dimension", "")
                rule = item.get("rule", "")
                lines.append(f"  - **Rank {rank} ({dim})**: {rule}")

        return "\n".join(lines)

    # ── 11. Domain Architecture & Playbook Deep-Dive ─────────────

    def _build_playbook(self, ctx: CompilationContext) -> str:
        pb = ctx.playbook
        if not pb:
            return ""

        lines = [
            "### 11. Domain Architecture & Playbook Deep-Dive",
            f"- **Domain Thinking Philosophy**: {getattr(pb, 'philosophy', '')}",
        ]
        dims = getattr(pb, "core_dimensions", [])
        if dims:
            lines.append(f"- **Core Engineering Dimensions**: {', '.join(dims)}")

        sections = getattr(pb, "sections", [])
        if sections:
            lines.append("- **Expert Directives & Architectural Pillars**:")
            for sec in sections[:3]:
                heading = getattr(sec, "heading", "")
                focus = getattr(sec, "focus", "")
                directives = getattr(sec, "directives", [])
                lines.append(f"  - **{heading}** ({focus}):")
                for d in directives[:3]:
                    lines.append(f"    - {d}")

        return "\n".join(lines)

    def _build_enhancement_section(self, hints: list[str]) -> str:
        lines = ["### Quality Enhancement Mandates (Auto-Improvement Loop)"]
        for hint in hints:
            lines.append(f"- **Mandate**: {hint}")
        return "\n".join(lines)
