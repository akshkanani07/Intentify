"""Role Alignment Engine – Evaluates and aligns user personas with task requirements."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

from app.ml.embeddings import EmbeddingEngine

logger = logging.getLogger("intentify.nlp.role_alignment_engine")


@dataclass
class AlignedRoleResult:
    """Intelligently validated and aligned role result."""

    final_role: str
    requested_role: str
    task_required_role: str
    alignment_status: str  # "matched", "adjusted", "synthesized"
    expertise_areas: list[str] = field(default_factory=list)
    reasoning: str = ""


class RoleAlignmentEngine:
    """Aligns user role with task requirements using semantic domain reasoning."""

    TASK_ROLE_MAPPING: list[tuple[re.Pattern[str], str, list[str]]] = [
        (
            re.compile(r"\b(?:scheduling\s+website|booking\s+(?:website|platform|system)|appointment\s+system)\b", re.IGNORECASE),
            "Full Stack SaaS Architect",
            ["Full Stack Web Engineering", "SaaS Multi-Tenancy", "Calendar & Availability Systems", "RESTful APIs", "Cloud Infrastructure"],
        ),
        (
            re.compile(r"\b(?:learn\s+python|python\s+tutorial|learning\s+python|study\s+python)\b", re.IGNORECASE),
            "Python Instructor",
            ["Python Pedagogy", "Core Language Syntax", "Data Structures & Algorithms", "Practical Code Instruction", "Software Design Patterns"],
        ),
        (
            re.compile(r"\b(?:hospital\s+management|clinical\s+system|ehr|emr|medical\s+software)\b", re.IGNORECASE),
            "Healthcare Technology Architect",
            ["Clinical Informatics", "EHR/EMR Architecture", "HL7/FHIR Protocols", "HIPAA & Patient Data Security", "Hospital Workflow Automation"],
        ),
        (
            re.compile(r"\b(?:ecommerce|shopping\s+cart|online\s+store|marketplace)\b", re.IGNORECASE),
            "Ecommerce Solution Architect",
            ["Ecommerce Platform Engineering", "Payment Gateway Integration", "High-Concurrency Inventory Management", "Catalog Indexing"],
        ),
        (
            re.compile(r"\b(?:wedding|event\s+coordination|ceremony\s+plan|summit|conference|gala|sangeet|mandap|લગ્ન|શાદી|शादी|समारोह)\b", re.IGNORECASE),
            "Luxury Event & Wedding Planner",
            ["High-Stakes Event Logistics", "Vendor & Venue Negotiation", "Budget Optimization", "Guest Hospitality & Protocol"],
        ),
        (
            re.compile(r"\b(?:kubernetes|k8s|zero-trust|multi-region|cloud\s+architecture)\b", re.IGNORECASE),
            "Senior Cloud Solutions Architect",
            ["Distributed Systems", "Kubernetes Orchestration", "Zero-Trust Security", "Multi-Region Resiliency", "GitOps CI/CD"],
        ),
        (
            re.compile(r"\b(?:debug|troubleshoot|bug|exception|stack\s+trace|segfault|deadlock|memory\s+leak|oom|timeout)\b", re.IGNORECASE),
            "Principal Software Debugging Engineer",
            ["Root-Cause Diagnostic Analysis", "Memory Profiling", "System Trace Inspection", "Automated Regression Testing"],
        ),
        (
            re.compile(r"\b(?:restaurant|food\s+business|culinary|thali|થાલી|રેસ્ટોરન્ટ|थाली|रेस्टोरेंट)\b", re.IGNORECASE),
            "Hospitality Strategy Consultant",
            ["Restaurant Operations", "Menu Costing & Supply Chain", "F&B Regulations", "Customer Experience Optimization"],
        ),
        (
            re.compile(r"\b(?:franchise|expansion|gtm|go-to-market|export|fleet|sop|cold-chain|microgrid|વેપાર|નિકાસ|વિસ્તાર)\b", re.IGNORECASE),
            "Principal Business Strategy Consultant",
            ["Market Entry & Scaling", "Unit Economics & Payback", "Operational SOP Development", "Supply Chain Architecture"],
        ),
    ]

    def __init__(self, embedding_engine: EmbeddingEngine | None = None) -> None:
        self._embedder = embedding_engine or EmbeddingEngine()

    def align_role(
        self,
        requested_role: str,
        detail_text: str,
        detected_domain: str = "",
        intent: str = "create",
    ) -> AlignedRoleResult:
        """Determines whether requested role matches task and adjusts persona intelligently."""
        clean_requested = requested_role.strip()
        lower_detail = detail_text.lower()
        lower_req = clean_requested.lower()

        # 1. Infer task-required role from task details
        task_required_role = "Domain Expert"
        expertise_areas: list[str] = []

        for pattern, inferred_role, default_expertise in self.TASK_ROLE_MAPPING:
            if pattern.search(lower_detail):
                task_required_role = inferred_role
                expertise_areas = default_expertise
                break

        # If no specific mapping matched, synthesize from domain
        if task_required_role == "Domain Expert" and detected_domain:
            safe_domain = detected_domain.replace('_', ' ').replace("Specialized Technical Domain", "Domain Strategy").title()
            task_required_role = f"Principal {safe_domain} Specialist"
            expertise_areas = [f"{safe_domain} Architecture", "Best Practices", "Execution Strategy"]

        # Case A: If user provided NO role -> Use task required role directly
        if not clean_requested:
            return AlignedRoleResult(
                final_role=task_required_role,
                requested_role="",
                task_required_role=task_required_role,
                alignment_status="synthesized",
                expertise_areas=expertise_areas,
                reasoning="Role synthesized directly from task intent and domain deliverable.",
            )

        # Case B: Learner Persona Specialization
        # e.g., User Role: Teacher, Task: I want to learn Python / Java
        # The user is expressing their personal background while seeking learning.
        # Master prompt must assume the role of the INSTRUCTOR / EXPERT who fulfills the objective.
        # Crucial Rule: AI persona must NEVER inflate user's learner proficiency!
        if intent == "learn" or any(w in lower_detail for w in ["learn", "teach", "study", "શીખવું", "સીખના", "सीखना", "tutorial", "curriculum"]):
            if "java" in lower_detail:
                final_role = "Java Programming Instructor"
                expertise_areas = ["Java Language Foundations", "JVM Architecture & Memory", "Object-Oriented Design", "Pedagogical Scaffolding", "Hands-on Practice Exercises"]
            elif "python" in lower_detail:
                final_role = "Python Instructor"
                expertise_areas = ["Python Pedagogy", "Core Syntax & Foundations", "Practical Exercises", "Object-Oriented Design"]
            elif "excel" in lower_detail:
                final_role = "Advanced Excel & Data Analytics Instructor"
                expertise_areas = ["Spreadsheet Modeling", "Formulas & Functions", "Data Visualization", "Step-by-Step Pedagogy"]
            elif detected_domain and detected_domain != "General":
                domain_title = detected_domain.replace("_", " ").title()
                final_role = f"{domain_title} Instructor"
                expertise_areas = [f"{domain_title} Pedagogy", "Foundational Concepts", "Hands-on Exercises", "Progressive Curriculum"]
            else:
                final_role = "Technical Pedagogy & Programming Instructor"
                expertise_areas = ["Foundational Instruction", "Syntax Walkthroughs", "Hands-on Exercises", "Progressive Learning Design"]

            return AlignedRoleResult(
                final_role=final_role,
                requested_role=clean_requested,
                task_required_role=final_role,
                alignment_status="adjusted",
                expertise_areas=expertise_areas,
                reasoning=f"Adjusted from learner background '{clean_requested}' to educational authority '{final_role}'. Learner proficiency remains foundational.",
            )

        # Case C: Domain crossover & Seniority Preservation
        # e.g. User Role: Senior Cloud Architect, Task: make scheduling website
        # -> Senior Full Stack SaaS Architect
        if "cloud" in lower_req or "architect" in lower_req:
            if "scheduling" in lower_detail or "saas" in lower_detail or "website" in lower_detail:
                seniority = "Senior " if "senior" in lower_req or "principal" in lower_req or "lead" in lower_req else ""
                final_role = f"{seniority}Full Stack SaaS Architect"
                expertise_areas = ["SaaS Multi-Tenancy", "Full-Stack Web Architecture", "Calendar & Scheduling Systems", "Cloud Deployment"]
                return AlignedRoleResult(
                    final_role=final_role,
                    requested_role=clean_requested,
                    task_required_role=task_required_role,
                    alignment_status="adjusted",
                    expertise_areas=expertise_areas,
                    reasoning=f"Combined '{clean_requested}' architectural seniority with full-stack SaaS deliverable.",
                )

        # Case D: Medical/Healthcare domain crossover
        # User Role: Doctor, Task: Create hospital management software
        # -> Healthcare Technology Architect
        if any(w in lower_req for w in ["doctor", "physician", "surgeon", "clinician"]):
            if any(w in lower_detail for w in ["hospital", "software", "management", "ehr", "emr", "clinic"]):
                final_role = "Healthcare Technology Architect"
                expertise_areas = ["Clinical Workflow Informatics", "Hospital Management Systems", "HIPAA Compliance", "HL7/FHIR Standards"]
                return AlignedRoleResult(
                    final_role=final_role,
                    requested_role=clean_requested,
                    task_required_role=task_required_role,
                    alignment_status="adjusted",
                    expertise_areas=expertise_areas,
                    reasoning=f"Aligned clinical domain '{clean_requested}' with healthcare software architecture.",
                )
            elif "ecommerce" in lower_detail or "website" in lower_detail:
                final_role = "Healthcare Technology Consultant with Ecommerce Platform Expertise"
                expertise_areas = ["Healthcare Commerce Systems", "Digital Health Platforms", "HIPAA Security", "Payment Integration"]
                return AlignedRoleResult(
                    final_role=final_role,
                    requested_role=clean_requested,
                    task_required_role=task_required_role,
                    alignment_status="adjusted",
                    expertise_areas=expertise_areas,
                    reasoning=f"Integrated requested role '{clean_requested}' with ecommerce technical requirements.",
                )

        # Case E: Direct or compatible match
        # If user provided a specific title that aligns with the task
        return AlignedRoleResult(
            final_role=clean_requested,
            requested_role=clean_requested,
            task_required_role=task_required_role,
            alignment_status="matched",
            expertise_areas=expertise_areas or [clean_requested, "System Design", "Execution Strategy"],
            reasoning=f"Retained user role '{clean_requested}' as compatible with target task.",
        )
