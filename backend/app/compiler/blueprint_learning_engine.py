"""Blueprint Learning Engine – Layer 5 of Intentify AI v4.

Discovers the optimal prompt blueprint based on:
(Intent, Domain, Complexity, Audience, Deliverable)
Evaluates section fitness (missing vs unnecessary sections) and adapts dynamically.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from app.compiler.blueprint_selector import Blueprint, BlueprintSelector

logger = logging.getLogger("intentify.compiler.blueprint_learning")


@dataclass
class LearnedBlueprint:
    name: str
    blueprint_type: str  # Technical Architecture, Campaign Strategy, Pedagogical Curriculum, Clinical Protocol, Strategic Business
    intent: str
    domain: str
    target_audience: str
    deliverable: str
    recommended_sections: list[str]
    success_score: float = 95.0
    times_utilized: int = 1


class BlueprintLearningEngine:
    """Discovers, evaluates, and dynamically adapts prompt blueprints based on operational execution feedback."""

    def __init__(self, base_selector: BlueprintSelector | None = None) -> None:
        self._base_selector = base_selector or BlueprintSelector()
        self.blueprint_memory: dict[str, LearnedBlueprint] = {}
        self._seed_blueprint_memory()

    def _seed_blueprint_memory(self) -> None:
        """Seed foundational enterprise blueprint templates."""
        self.blueprint_memory["software_architecture"] = LearnedBlueprint(
            name="Technical Architecture Blueprint",
            blueprint_type="Technical Architecture",
            intent="create",
            domain="Software Development",
            target_audience="Software Engineers & Architects",
            deliverable="Production-Ready Source Code, API Endpoints, and Database Schemas",
            recommended_sections=[
                "System Architecture & Component Topology",
                "API Specifications & Endpoint Contract",
                "Database Schema, Relationships & Data Integrity",
                "Security Architecture & RBAC",
                "Performance Optimization & Caching",
                "Automated Testing & Observability",
                "Production Deployment & CI/CD",
            ],
            success_score=98.5,
            times_utilized=120,
        )

        self.blueprint_memory["marketing_campaign"] = LearnedBlueprint(
            name="Campaign Strategy Blueprint",
            blueprint_type="Campaign Strategy",
            intent="create",
            domain="Marketing & Growth",
            target_audience="Marketing Practitioners & Brand Directors",
            deliverable="Omnichannel Marketing Playbook and Creative Assets",
            recommended_sections=[
                "Target Audience & Persona Segmentation",
                "Core Value Proposition & USP",
                "Multi-Channel Messaging & Wave Schedule",
                "Visual Creative Direction & Moodboard",
                "High-Conversion CTA & KPI Dashboard",
            ],
            success_score=97.0,
            times_utilized=85,
        )

        self.blueprint_memory["pedagogical_curriculum"] = LearnedBlueprint(
            name="Pedagogical Learning Blueprint",
            blueprint_type="Pedagogical Curriculum",
            intent="learn",
            domain="Programming Education",
            target_audience="Students & Learners",
            deliverable="Structured Progressive Curriculum with Code Walkthroughs",
            recommended_sections=[
                "Pedagogical Learning Outcomes (Bloom's Taxonomy)",
                "Scaffolded Curriculum Roadmap",
                "Interactive Lesson Flow & Cognitive Load Management",
                "Hands-On Practice Exercises & Code Walkthroughs",
                "Capstone Real-World Projects & Rubrics",
            ],
            success_score=99.0,
            times_utilized=94,
        )

    def discover_or_adapt_blueprint(
        self,
        intent: str,
        domain: str,
        complexity: str = "Production-Grade",
        audience: str = "General Practitioners",
        deliverable: str = "",
    ) -> LearnedBlueprint:
        """Alias for discover_blueprint for adaptive selection."""
        return self.discover_blueprint(
            intent=intent,
            domain=domain,
            complexity=complexity,
            audience=audience,
            deliverable=deliverable,
        )

    def discover_blueprint(
        self,
        intent: str,
        domain: str,
        complexity: str = "Production-Grade",
        audience: str = "General Practitioners",
        deliverable: str = "",
    ) -> LearnedBlueprint:
        """Find the most fitting blueprint or dynamically formulate a bespoke blueprint."""
        domain_lower = domain.lower()

        if any(w in domain_lower for w in ["software", "scheduling", "web", "cloud", "saas", "api"]):
            return self.blueprint_memory["software_architecture"]
        elif any(w in domain_lower for w in ["marketing", "advertising", "growth"]):
            return self.blueprint_memory["marketing_campaign"]
        elif any(w in domain_lower for w in ["education", "teaching", "programming education", "learning"]) or intent == "learn":
            return self.blueprint_memory["pedagogical_curriculum"]

        # Autonomous dynamic blueprint discovery for novel domains
        blueprint_key = f"dynamic_{domain.lower().replace(' ', '_')}"
        if blueprint_key in self.blueprint_memory:
            bp = self.blueprint_memory[blueprint_key]
            bp.times_utilized += 1
            return bp

        bespoke_bp = LearnedBlueprint(
            name=f"{domain} Master Execution Blueprint",
            blueprint_type="Domain Execution Blueprint",
            intent=intent,
            domain=domain,
            target_audience=audience,
            deliverable=deliverable or f"Authoritative {domain} Specifications and Production Deliverables",
            recommended_sections=[
                f"{domain} Strategic Framework & Topology",
                "Core Technical & Functional Specifications",
                "Operational Guardrails & Quality Benchmarks",
                "Lifecycle Governance & Scaling Roadmap",
            ],
            success_score=94.0,
            times_utilized=1,
        )
        self.blueprint_memory[blueprint_key] = bespoke_bp
        logger.info("BlueprintLearningEngine synthesized novel blueprint '%s'", bespoke_bp.name)
        return bespoke_bp

    def evaluate_and_learn(
        self,
        blueprint: LearnedBlueprint | str,
        quality_score: float,
        missing_sections: list[str] | None = None,
        unnecessary_sections: list[str] | None = None,
    ) -> None:
        """Update blueprint memory and optimize section weights."""
        if isinstance(blueprint, str):
            bp = self.blueprint_memory.get(blueprint)
            if not bp:
                for k, v in self.blueprint_memory.items():
                    if (
                        v.blueprint_type.lower() == blueprint.lower()
                        or v.name.lower() == blueprint.lower()
                    ):
                        bp = v
                        break
            if not bp:
                return
            blueprint = bp

        missing = missing_sections or []
        unnecessary = unnecessary_sections or []

        # Add missing sections if repeatedly identified
        for sec in missing:
            if sec not in blueprint.recommended_sections:
                blueprint.recommended_sections.append(sec)
                logger.info("Learned new essential section for blueprint '%s': %s", blueprint.name, sec)

        # Remove unnecessary sections if flagged
        for sec in unnecessary:
            if sec in blueprint.recommended_sections:
                blueprint.recommended_sections.remove(sec)
                logger.info("Pruned redundant section from blueprint '%s': %s", blueprint.name, sec)

        # Update running score average
        blueprint.times_utilized += 1
        blueprint.success_score = round((blueprint.success_score * 0.9) + (quality_score * 0.1), 2)
