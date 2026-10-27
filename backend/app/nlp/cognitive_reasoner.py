"""CognitiveReasoner – executes rigorous internal AI self-questioning and inference before prompt compilation."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("intentify.nlp.cognitive_reasoner")


@dataclass
class CognitiveReasoningResult:
    """Explicit answers to core cognitive questions guiding prompt compilation."""

    what_user_wants_to_build: str
    what_user_wants_to_learn: str
    what_user_wants_to_solve: str
    what_user_wants_to_write: str
    actual_user_goal: str
    is_role_appropriate: bool
    role_adjustment_rationale: str
    primary_domain: str
    sub_domains: list[str]
    target_audience: str
    experience_level: str
    primary_deliverable: str
    required_sections: list[str]
    omitted_sections: list[str]
    cognitive_synthesis_summary: str


class CognitiveReasoner:
    """Interrogates and reasons through user intent, role, domain, audience, and deliverable needs.

    Ensures the AI compiler acts as an authoritative domain architect rather than a naive text repeater.
    """

    def reason(
        self,
        raw_detail: str,
        user_goal: str,
        intent: str,
        requested_role: str,
        aligned_role: str,
        domain: str,
        sub_domains: list[str],
        audience: str,
        experience_level: str,
        deliverable: str,
    ) -> CognitiveReasoningResult:
        detail_lower = raw_detail.lower()

        # 1. What does the user want to build?
        if intent in ["create", "build", "develop", "design"] or any(w in detail_lower for w in ["make", "build", "create", "develop", "system", "website", "app"]):
            what_build = f"A production-grade {user_goal.lower()}"
        else:
            what_build = "N/A (Task is oriented toward analytical, educational, or strategic outcomes)"

        # 2. What does the user want to learn?
        if intent == "learn" or any(w in detail_lower for w in ["learn", "teach", "study", "master", "understand", "tutorial"]):
            what_learn = f"Core foundations, syntax idioms, and practical mastery of {user_goal.replace('learn', '').strip()}"
        else:
            what_learn = "N/A (Task is oriented toward active construction, production, or execution)"

        # 3. What does the user want to solve?
        if intent in ["debug", "fix", "improve"] or any(w in detail_lower for w in ["fix", "error", "bug", "solve", "issue"]):
            what_solve = f"Remediate execution failures, architectural bottlenecks, and defects in {raw_detail}"
        else:
            what_solve = f"Eliminate operational complexity in deploying and scaling {user_goal.lower()}"

        # 4. What does the user want written?
        if intent in ["write", "research", "explain"]:
            what_write = f"Authoritative technical documentation, strategic specifications, and stakeholder communications for {user_goal}"
        else:
            what_write = f"Idiomatic, clean-architecture production code, configuration schemas, and deployment guides"

        # 5. Role Appropriateness Evaluation
        if not requested_role or requested_role.strip().lower() == aligned_role.strip().lower():
            is_role_appropriate = True
            role_rationale = f"Persona '{aligned_role}' directly aligns with {domain} execution authority."
        else:
            is_role_appropriate = False
            role_rationale = (
                f"Requested persona '{requested_role}' is suboptimal for executing '{user_goal}'. "
                f"Elevated and specialized to '{aligned_role}' for authoritative domain mastery."
            )

        # 6. Dynamic Section Planning & Omission
        required_sections = [
            "Expert Role & Persona",
            "Mission & Core Objective",
            "Context & Background",
            "Technical & Functional Requirements",
        ]
        omitted_sections = []

        if any(w in domain.lower() for w in ["software", "scheduling", "web", "cloud"]):
            required_sections.extend([
                "System Topology & Architectural Blueprint",
                "API Contracts, Data Models & Schema Design",
                "Security, Access Control (RBAC) & Data Isolation",
                "Concurrency, Performance & Scalability Protocols",
                "Testing Strategy, Observability & CI/CD Deployment",
            ])
            omitted_sections.extend(["Consumer Psychology", "Clinical Diagnostics", "Pedagogical Scaffolding"])
        elif any(w in domain.lower() for w in ["education", "teaching", "programming education"]):
            required_sections.extend([
                "Pedagogical Learning Outcomes (Bloom's Taxonomy)",
                "Scaffolded Curriculum & Weekly Roadmap",
                "Interactive Lesson Flow & Cognitive Load Management",
                "Hands-On Coding Exercises & Walkthroughs",
                "Capstone Real-World Projects & Assessment Rubrics",
            ])
            omitted_sections.extend(["High-Scale Concurrency", "Clinical Differential Diagnosis", "FTC Advertising Compliance"])
        elif any(w in domain.lower() for w in ["health", "medical", "hospital"]):
            required_sections.extend([
                "Clinical Workflow & Patient Data Architecture",
                "HIPAA / Clinical Compliance & Audit Trails",
                "Diagnostic Workup & Safety Thresholds",
                "EHR Integration & System Interoperability",
            ])
            omitted_sections.extend(["Consumer Advertising Funnels", "Student Lesson Flow"])
        elif any(w in domain.lower() for w in ["marketing", "advertising"]):
            required_sections.extend([
                "Target Audience & Buyer Persona Matrix",
                "Unique Selling Proposition (USP) & Emotional Drivers",
                "Multi-Channel Campaign Messaging & Wave Schedule",
                "Visual Creative Direction & CTA Framework",
                "Performance KPIs & Attribution Tracking",
            ])
            omitted_sections.extend(["Database Indexing Strategy", "Clinical Differential Diagnosis"])
        else:
            # Dynamic synthesis for unknown / general domains
            required_sections.extend([
                f"{domain} Strategic Framework & Methodology",
                f"Core Operational Deliverables & Execution Specs",
                f"Risk Mitigation, Compliance & Quality Benchmarks",
            ])

        required_sections.extend([
            "Guardrails & Operational Constraints",
            "Step-by-Step Execution Instructions",
            "Structured Output Specification",
            "Smart Documented Assumptions",
            "Self-Verification Quality Checklist",
        ])

        summary = (
            f"Cognitive Assessment: Identified objective '{user_goal}' under domain '{domain}'. "
            f"Assigned persona '{aligned_role}' addressing '{audience}' at '{experience_level}' proficiency. "
            f"Formulated {len(required_sections)} bespoke execution sections with {len(omitted_sections)} irrelevant modules pruned."
        )

        return CognitiveReasoningResult(
            what_user_wants_to_build=what_build,
            what_user_wants_to_learn=what_learn,
            what_user_wants_to_solve=what_solve,
            what_user_wants_to_write=what_write,
            actual_user_goal=user_goal,
            is_role_appropriate=is_role_appropriate,
            role_adjustment_rationale=role_rationale,
            primary_domain=domain,
            sub_domains=sub_domains,
            target_audience=audience,
            experience_level=experience_level,
            primary_deliverable=deliverable,
            required_sections=required_sections,
            omitted_sections=omitted_sections,
            cognitive_synthesis_summary=summary,
        )
