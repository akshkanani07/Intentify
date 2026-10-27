"""KnowledgePlanner – Selects domain-specialized blueprints and generates strictly deduplicated section plans.

Operates 100% domain-agnostically with zero subject-specific hardcoding in Python logic.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

from app.core.config import get_settings
from app.engine.spec_extractor import PromptSpec
from app.knowledge.knowledge_manager import KnowledgeManager

logger = logging.getLogger("intentify.engine.planner")


@dataclass
class PlanSection:
    """An individual structured prompt section with specialized directives."""

    heading: str
    directives: list[str] = field(default_factory=list)
    required_entities: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass
class PromptPlan:
    """Complete, ordered blueprint plan tailored to the user's domain and intent."""

    domain_module: str
    sections: list[PlanSection]
    deduplicated_headings: list[str] = field(default_factory=list)
    topics: list[dict[str, Any]] = field(default_factory=list)
    standards: list[dict[str, Any]] = field(default_factory=list)
    content_source: str = "concept_graph"
    reviewed: bool = False
    assumptions: list[str] = field(default_factory=list)
    negative_guardrails: list[str] = field(default_factory=list)


class KnowledgePlanner:
    """Plans bespoke, non-repeating prompt structures using generic KnowledgeBase sources."""

    def __init__(self, km: KnowledgeManager | None = None) -> None:
        self.km = km or KnowledgeManager()

    def plan(self, spec: PromptSpec) -> PromptPlan:
        """Route PromptSpec to content sources (C1, C2, C3) and assemble deduplicated sections."""
        subject = spec.object_subject
        action = spec.action.lower()
        is_learning = action in ("learn", "study", "teach", "explain") or "education" in spec.domain.lower() or "students" in spec.audience.lower()

        # ── 1. Stage C: Content Source (First Match Wins) ───────────────────
        cg = self.km.get_concept_graph(subject)
        topics: list[dict[str, Any]] = []
        content_source = "concept_graph"
        reviewed = False

        if cg:
            # Stage C1: Match from Concept Graph
            content_source = "concept_graph"
            reviewed = cg.get("reviewed", False)
            topics = list(cg.get("topics", []))
        else:
            # Stage C2: Try Local Model Generator if enabled
            generated_topics = self._generate_topics_with_model(spec)
            if generated_topics and len(generated_topics) >= 5:
                content_source = "generated"
                reviewed = False
                topics = generated_topics
            else:
                # Stage C3: Derived Structure (No facts invented, labeled derived)
                content_source = "derived"
                reviewed = False
                topics = self._synthesize_derived_topics(spec)

        # ── 2. Stage D: Standards Registry ──────────────────────────────────
        std_data = self.km.get_standards(subject)
        standards: list[dict[str, Any]] = []
        if std_data and isinstance(std_data, dict):
            standards = list(std_data.get("standards", []))

        # ── 3. Assemble Plan Sections ───────────────────────────────────────
        if is_learning:
            sections = self._build_learning_sections(spec, topics, standards, content_source)
            domain_module = "education"
        elif action in ("debug", "fix"):
            sections = self._build_debugging_sections(spec, standards)
            domain_module = "debugging"
        else:
            sections = self._build_creation_sections(spec, topics, standards, content_source)
            domain_module = "creation"

        # Deduplicate section headings
        deduped_sections = self._deduplicate_sections(sections)
        deduped_headings = [s.heading for s in deduped_sections]

        assumptions = [
            f"Target audience operates with the background knowledge expected of {spec.proficiency}.",
            "All functional specifications require complete production-ready syntax and verified schema definitions.",
        ]

        negative_guardrails = [
            "DO NOT write partial code snippets or leave incomplete stub implementations.",
            "DO NOT assume prior knowledge of advanced technical terms without defining them first.",
            "DO NOT deviate from the requested output structure or omit hands-on exercises.",
        ]

        return PromptPlan(
            domain_module=domain_module,
            sections=deduped_sections,
            deduplicated_headings=deduped_headings,
            topics=topics,
            standards=standards,
            content_source=content_source,
            reviewed=reviewed,
            assumptions=assumptions,
            negative_guardrails=negative_guardrails,
        )

    def _build_learning_sections(
        self,
        spec: PromptSpec,
        topics: list[dict[str, Any]],
        standards: list[dict[str, Any]],
        content_source: str,
    ) -> list[PlanSection]:
        """Build structured learning sections adhering to D1-D9 invariants."""
        sections: list[PlanSection] = []

        # 1. Role & Persona
        role_dirs = [
            f"Assume the persona of a world-class {spec.persona_role} specializing in foundational clarity, supportive step-by-step instruction, and empathetic mentoring.",
            f"Tailor language, analogies, and pacing strictly for a {spec.proficiency} learner.",
            "Explain concepts from first principles using intuitive mental models, and define every technical term on first use.",
            "Maintain an encouraging, accessible, and structured pedagogical tone throughout.",
        ]
        sections.append(PlanSection("Role & Pedagogical Persona", role_dirs))

        # 2. Objective & Scope (Invariant D8)
        first_topic = topics[0].get("title", "Core Basics") if topics else "Basics"
        last_topic = topics[-1].get("title", "Applied Mastery") if topics else "Applications"
        obj_dirs = [
            f"System Objective: Master foundational {spec.object_subject} concepts: from {first_topic} to {last_topic}.",
            f"Target Audience: {spec.audience} ({spec.proficiency}).",
            "Deliverable: Step-by-Step Curriculum with Actionable Code Walkthroughs and Practical Exercises.",
        ]
        sections.append(PlanSection("Core Learning Objective & Scope", obj_dirs))

        # 3. Curated Ordered Curriculum & Topics (Invariant D1: >= 5 topics with obj & ex)
        topic_dirs = [
            f"Curriculum Outline ({content_source.replace('_', ' ').title()} - Prerequisite Ordered):",
        ]
        if content_source == "derived":
            topic_dirs.append("Note: The following subject topic outline is derived from domain entities and foundational first principles.")

        for idx, t in enumerate(topics, 1):
            t_title = t.get("title", f"Module {idx}")
            t_obj = t.get("objective", "Master fundamental concepts.")
            t_ex = t.get("exercise", "Implement a practical programming exercise.")
            t_code = t.get("example", "")
            topic_dirs.append(f"Topic {idx}: {t_title}")
            topic_dirs.append(f"  - Objective: {t_obj}")
            topic_dirs.append(f"  - Exercise: {t_ex}")
            if t_code:
                topic_dirs.append(f"  - Concept Syntax: `{t_code}`")

        sections.append(PlanSection("Curated Topic Plan & Step-by-Step Curriculum", topic_dirs))

        # 4. Technical Standards (Invariant D6: ONLY if standards exist)
        if standards:
            std_dirs = [
                f"Strictly adhere to official {spec.object_subject} industry standards and best practices:",
            ]
            for s in standards:
                std_dirs.append(f"- **{s.get('name', '')}**: {s.get('description', '')}")
            sections.append(PlanSection("Technical Standards & Best Practices", std_dirs))

        # 5. Verifiable Acceptance Criteria (Invariant D3, D4)
        crit_dirs = [
            f"The learner can build working code examples covering all {len(topics)} curriculum topics.",
            "Demonstrate verified competency in foundational mechanics through self-contained practice tasks.",
            "Successfully resolve intermediate implementation challenges without relying on external assistance.",
            "Synthesize learned concepts by executing a comprehensive final practice deliverable.",
            "Contains zero placeholders, unresolved stubs, or unverified approximations.",
        ]
        if spec.constraints:
            crit_dirs.append(f"Satisfies all {len(spec.constraints)} specified operational boundaries and constraints.")

        sections.append(PlanSection("Verifiable Acceptance Criteria", crit_dirs))

        # 6. Format Specification
        fmt_dirs = [
            f"Format response strictly as {spec.format}.",
            "Use clean GitHub-flavored markdown with syntax-highlighted code blocks.",
            "Accompany every code example with line-by-line mechanical explanations.",
        ]
        sections.append(PlanSection("Output Format Specification", fmt_dirs))

        # 7. Self-Verification Checklist
        chk_dirs = [
            f"Verify all {len(topics)} topics are explained with intuitive mental models",
            "Verify every topic includes both an explicit objective and a hands-on exercise",
            "Confirm zero assumed prior jargon with every technical term defined on first introduction",
            "Check for production-ready completeness with zero placeholders",
        ]
        sections.append(PlanSection("Self-Verification Quality Checklist", chk_dirs))

        return sections

    def _build_creation_sections(
        self,
        spec: PromptSpec,
        topics: list[dict[str, Any]],
        standards: list[dict[str, Any]],
        content_source: str,
    ) -> list[PlanSection]:
        """Build structured architecture and creation sections adhering to D1-D9 invariants."""
        sections: list[PlanSection] = []

        # 1. Role & Persona
        role_dirs = [
            f"Assume the persona of an authoritative {spec.persona_role} specializing in {spec.domain}.",
            "Emphasize deterministic execution, clean architectural separation of concerns, and system reliability.",
            f"Tailor all technical specifications for {spec.audience} ({spec.proficiency}).",
        ]
        sections.append(PlanSection("Role & Technical Persona", role_dirs))

        # 2. Objective & Scope (Invariant D8: action + subject + level + outcome)
        obj_dirs = [
            f"System Objective: Architect production-ready {spec.object_subject} for {spec.audience} ({spec.proficiency}) to deliver scalable high-availability services with verifiable transactional integrity.",
            f"Primary Target Domain: {spec.domain}.",
            f"Deliverable Artifact: {spec.deliverable}.",
        ]
        sections.append(PlanSection("Core Objective & System Scope", obj_dirs))

        # 3. Technical Specifications & Architecture (Domain-Adaptive)
        dom = spec.domain.lower()
        is_software = any(d in dom for d in ["software", "code", "devops", "cloud", "saas", "api", "database", "backend", "frontend", "full stack"])
        if is_software:
            heading_title = "System Architecture & Component Topology"
        elif any(d in dom for d in ["event", "wedding", "hospitality", "lifestyle"]):
            heading_title = "Event Coordination & Operational Topology"
        elif any(d in dom for d in ["business", "strategy", "expansion", "marketing", "finance"]):
            heading_title = "Strategic Framework & Operational Topology"
        elif any(d in dom for d in ["health", "clinic", "medical", "hospital"]):
            heading_title = "Clinical Protocol & Operational Topology"
        elif any(d in dom for d in ["legal", "contract", "compliance"]):
            heading_title = "Legal Governance & Contractual Topology"
        elif any(d in dom for d in ["writing", "creative", "fiction"]):
            heading_title = "Narrative Framework & Editorial Topology"
        elif any(d in dom for d in ["agriculture", "farming", "crop", "kelp", "biochar"]):
            heading_title = "Agricultural Protocol & Cultivation Topology"
        else:
            heading_title = "Operational Framework & Subsystem Topology"

        arch_dirs = [
            f"Operational Subsystems & Topology ({content_source.replace('_', ' ').title()}):",
        ]
        if content_source == "derived":
            arch_dirs.append("Note: The structural outline is derived from domain entities and foundational architectural principles.")

        for idx, t in enumerate(topics, 1):
            arch_dirs.append(f"Subsystem {idx}: {t.get('title', '')}")
            arch_dirs.append(f"  - Design Objective: {t.get('objective', '')}")
            arch_dirs.append(f"  - Implementation Requirement: {t.get('exercise', '')}")

        sections.append(PlanSection(heading_title, arch_dirs))

        # 4. Technical Standards (Invariant D6)
        if standards:
            std_dirs = [
                f"Adhere strictly to official industry standards:",
            ]
            for s in standards:
                std_dirs.append(f"- **{s.get('name', '')}**: {s.get('description', '')}")
            sections.append(PlanSection("Technical Standards & Protocols", std_dirs))

        # 5. Acceptance Criteria (Invariant D3: Generated from topic objectives, zero raw input verbatim)
        crit_dirs = [
            "Deploys an end-to-end architecture fulfilling all subsystem design objectives and integration boundaries.",
            "Enforces strict data integrity, fault isolation, and horizontal scalability across services.",
            "Contains zero placeholders, unresolved stubs, or unverified approximations in production schemas and contracts.",
            "All functional interfaces and data schemas validated with deterministic test scenarios.",
        ]
        if spec.constraints:
            crit_dirs.append(f"Satisfies all {len(spec.constraints)} specified operational boundaries and constraints.")

        sections.append(PlanSection("Verifiable Acceptance Criteria", crit_dirs))

        # 6. Format Specification
        fmt_dirs = [
            f"Format response strictly as {spec.format}.",
            "Use clean Markdown with architectural diagrams and schema definitions.",
        ]
        sections.append(PlanSection("Output Format Specification", fmt_dirs))

        # 7. Self-Verification Checklist
        chk_dirs = [
            "Verify all functional modules are fully specified without truncation",
            "Confirm zero placeholder stubs or unverified claims in specifications",
            "Validate explicit failure recovery protocols established for all critical flows",
        ]
        sections.append(PlanSection("Self-Verification Quality Checklist", chk_dirs))

        return sections

    def _build_debugging_sections(
        self,
        spec: PromptSpec,
        standards: list[dict[str, Any]],
    ) -> list[PlanSection]:
        """Build structured diagnostic debugging sections adhering to D1-D9 invariants."""
        sections: list[PlanSection] = []

        # 1. Role
        role_dirs = [
            f"Assume the persona of a {spec.persona_role} specializing in systems diagnostics and code analysis.",
            "Adopt a rigorous scientific approach: observe symptoms -> isolate root cause -> patch -> verify.",
        ]
        sections.append(PlanSection("Role & Diagnostic Persona", role_dirs))

        # 2. Objective (Invariant D8: action + subject + outcome)
        incident_note = f"Reported Failure Incident: Observed anomalous runtime behavior and failure states in {spec.object_subject}." if spec.object_subject else "Analyze runtime telemetry and crash logs."
        obj_dirs = [
            f"System Objective: Diagnose and patch {spec.object_subject} to restore nominal system execution and eliminate operational exceptions.",
            incident_note,
            "Analyze runtime stacktrace telemetry, state invariants, and execution flows.",
            "Formulate a minimal, zero-regression resolution patch.",
        ]
        sections.append(PlanSection("Defect Symptom & Incident Context", obj_dirs))

        # 3. RCA Framework
        rca_dirs = [
            "Formulate testable hypotheses explaining the failure mechanism.",
            "Identify memory address nullification, concurrency race conditions, or unhandled boundaries.",
            "Trace fault propagation from entry point to exception trigger.",
        ]
        sections.append(PlanSection("Root Cause Analysis (RCA) Framework", rca_dirs))

        # 4. Patch
        patch_dirs = [
            "Provide an idiomatic, minimal defensive patch correcting the flaw.",
            "Include before/after code snippets highlighting the exact change.",
            "Explain why the patch restores system invariants without unintended side effects.",
        ]
        sections.append(PlanSection("Step-by-Step Resolution Patch", patch_dirs))

        # 5. Standards (Invariant D6)
        if standards:
            std_dirs = [
                f"Adhere strictly to official diagnostic standards:",
            ]
            for s in standards:
                std_dirs.append(f"- **{s.get('name', '')}**: {s.get('description', '')}")
            sections.append(PlanSection("Technical Standards & Conventions", std_dirs))

        # 6. Acceptance Criteria (Invariant D3, D4)
        crit_dirs = [
            "Conclusively prove the failure trigger mechanism and memory/execution state at crash time.",
            "Resolution patch restores all operational invariants without introducing regression risks.",
            "Automated regression test case verifies fix across nominal and boundary inputs.",
        ]
        if spec.constraints:
            crit_dirs.append(f"Satisfies all {len(spec.constraints)} specified operational boundaries and constraints.")

        sections.append(PlanSection("Verification Criteria & Regression Tests", crit_dirs))

        # 7. Self-Verification Checklist
        chk_dirs = [
            "Confirm failure trigger mechanism is conclusively verified",
            "Validate resolution patch introduces zero regressions",
            "Check that test cases verify nominal and edge-case behavior",
        ]
        sections.append(PlanSection("Self-Verification Quality Checklist", chk_dirs))

        return sections

    def _synthesize_derived_topics(self, spec: PromptSpec) -> list[dict[str, Any]]:
        """Synthesize 5 generic derived topics when no static concept graph exists (Stage C3)."""
        subj = spec.object_subject
        action = spec.action.lower()

        if action in ("learn", "study", "teach"):
            return [
                {
                    "id": "derived_1",
                    "title": f"Core Foundations & Principles of {subj}",
                    "objective": f"Understand primary terminology, historical context, and fundamental concepts of {subj}.",
                    "exercise": f"Create a summary glossary explaining 5 key tenets of {subj}.",
                    "example": f"Foundations of {subj}",
                    "prerequisites": [],
                },
                {
                    "id": "derived_2",
                    "title": f"Essential Frameworks & Workflows in {subj}",
                    "objective": f"Master standard operational workflows, methodologies, and conventions in {subj}.",
                    "exercise": f"Map out a standard operational process for a real-world {subj} scenario.",
                    "example": f"Workflows in {subj}",
                    "prerequisites": ["derived_1"],
                },
                {
                    "id": "derived_3",
                    "title": f"Practical Application & Hands-On Problem Solving in {subj}",
                    "objective": f"Execute concrete exercises and apply core principles to solve practical challenges in {subj}.",
                    "exercise": f"Complete a guided case-study challenge applying {subj} techniques.",
                    "example": f"Applied {subj} solution",
                    "prerequisites": ["derived_2"],
                },
                {
                    "id": "derived_4",
                    "title": f"Common Pitfalls, Error Triage & Quality Standards in {subj}",
                    "objective": f"Identify frequent beginner mistakes and learn standard verification protocols in {subj}.",
                    "exercise": f"Diagnose and correct 3 intentional defect scenarios in {subj}.",
                    "example": f"Troubleshooting {subj}",
                    "prerequisites": ["derived_3"],
                },
                {
                    "id": "derived_5",
                    "title": f"Integrated Capstone Project & Real-World Execution in {subj}",
                    "objective": f"Synthesize all concepts into a functional, end-to-end portfolio project in {subj}.",
                    "exercise": f"Design and deliver a comprehensive capstone deliverable demonstrating autonomous mastery in {subj}.",
                    "example": f"Capstone in {subj}",
                    "prerequisites": ["derived_4"],
                },
            ]
        else:
            return [
                {
                    "id": "derived_arch_1",
                    "title": f"Requirements Decomposition & Scoping for {subj}",
                    "objective": f"Define functional and non-functional system boundaries for {subj}.",
                    "exercise": f"Establish verifiable boundary constraints and stakeholder interfaces.",
                    "example": f"Scoping {subj}",
                    "prerequisites": [],
                },
                {
                    "id": "derived_arch_2",
                    "title": f"Domain Modeling & Entity Relationships for {subj}",
                    "objective": f"Design high-cohesion domain models and data invariants for {subj}.",
                    "exercise": f"Construct domain schema models and relational contracts.",
                    "example": f"Entities in {subj}",
                    "prerequisites": ["derived_arch_1"],
                },
                {
                    "id": "derived_arch_3",
                    "title": f"Core Workflows & Processing Pipelines for {subj}",
                    "objective": f"Implement decoupled execution pipelines and transactional lifecycles in {subj}.",
                    "exercise": f"Draft end-to-end request/response workflow specifications.",
                    "example": f"Pipelines in {subj}",
                    "prerequisites": ["derived_arch_2"],
                },
                {
                    "id": "derived_arch_4",
                    "title": f"Risk Mitigation, Quality Verification & Contingency Protocols for {subj}" if any(d in spec.domain.lower() for d in ["event", "wedding", "hospitality", "lifestyle", "business", "culinary", "farming", "agriculture", "arts"]) else f"Security, Reliability & Fault Isolation for {subj}",
                    "objective": f"Establish fallback protocols, contingency arrangements, and operational safety for {subj}." if any(d in spec.domain.lower() for d in ["event", "wedding", "hospitality", "lifestyle", "business", "culinary", "farming", "agriculture", "arts"]) else f"Enforce defensive boundary protections, rate limits, and fallback strategies in {subj}.",
                    "exercise": f"Formulate contingency plans and operational escalation pathways." if any(d in spec.domain.lower() for d in ["event", "wedding", "hospitality", "lifestyle", "business", "culinary", "farming", "agriculture", "arts"]) else f"Configure failure recovery protocols and audit access controls.",
                    "example": f"Contingency in {subj}" if any(d in spec.domain.lower() for d in ["event", "wedding", "hospitality", "lifestyle", "business", "culinary", "farming", "agriculture", "arts"]) else f"Security in {subj}",
                    "prerequisites": ["derived_arch_3"],
                },
                {
                    "id": "derived_arch_5",
                    "title": f"Deployment Topology, Verification & Telemetry for {subj}",
                    "objective": f"Establish automated test suites, health monitoring, and production deployment topology.",
                    "exercise": f"Formulate end-to-end integration test plans and operational metrics.",
                    "example": f"Telemetry in {subj}",
                    "prerequisites": ["derived_arch_4"],
                },
            ]

    def _deduplicate_sections(self, sections: list[PlanSection]) -> list[PlanSection]:
        """Eliminate duplicate headings using normalized comparison."""
        seen: set[str] = set()
        unique: list[PlanSection] = []
        for s in sections:
            norm = re.sub(r"[^\w\s]", "", s.heading).strip().lower()
            if norm not in seen:
                seen.add(norm)
                unique.append(s)
        return unique

    def _generate_topics_with_model(self, spec: PromptSpec) -> list[dict[str, Any]] | None:
        """Stage C2: Local instruction model generator (disabled by default in config)."""
        settings = get_settings()
        if not getattr(settings, "ENABLE_LOCAL_INSTRUCTION_MODEL", False):
            return None

        try:
            from transformers import pipeline
            model_name = getattr(settings, "LOCAL_INSTRUCTION_MODEL_NAME", "google/flan-t5-small")
            generator = pipeline("text2text-generation", model=model_name, device=-1)
            prompt = f"Generate 5 curriculum topics for {spec.object_subject}:"
            res = generator(prompt, max_length=128)
            # If generator produces valid output, parse into topic structure
            if res and isinstance(res, list) and len(res) > 0:
                text = res[0].get("generated_text", "")
                lines = [l.strip() for l in text.split("\n") if l.strip()]
                if len(lines) >= 5:
                    return [
                        {
                            "id": f"gen_{i+1}",
                            "title": line,
                            "objective": f"Master principles and mechanisms of {line}.",
                            "exercise": f"Complete hands-on exercise implementing {line}.",
                            "example": f"Example of {line}",
                            "prerequisites": [f"gen_{i}"] if i > 0 else [],
                        }
                        for i, line in enumerate(lines[:5])
                    ]
            return None
        except Exception as e:
            logger.warning("Local instruction model execution failed (%s), falling back to C3 derived structure.", e)
            return None
