"""DynamicSectionPlanner – plans and synthesizes bespoke runtime headings and technical sections per domain."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("intentify.compiler.dynamic_section_planner")


@dataclass
class DynamicSection:
    """A runtime-generated specialized technical section."""

    heading: str
    content: str
    focus_keywords: list[str] = field(default_factory=list)


@dataclass
class PlannedSectionSchema:
    """The complete dynamic blueprint section schema synthesized for a domain."""

    domain: str
    category: str
    dynamic_sections: list[DynamicSection] = field(default_factory=list)
    custom_headings: list[str] = field(default_factory=list)


class DynamicSectionPlanner:
    """Generates unique, deep runtime domain sections tailored to the domain and task.

    Ensures no generic boilerplate headings are repeated when specialized domain headings apply.
    """

    def plan_sections(
        self,
        domain: str,
        goal: str,
        entities: list[dict[str, Any]] | None = None,
        context_hints: list[str] | None = None,
    ) -> PlannedSectionSchema:
        domain_lower = domain.lower()
        entities = entities or []
        entity_texts = [e.get("text", "") for e in entities if isinstance(e, dict) and e.get("text")]
        entity_str = ", ".join(entity_texts) if entity_texts else "core domain entities"

        # ── 1. Medical, Healthcare & Clinical Informatics ───────────
        if any(w in domain_lower for w in ["health", "medical", "hospital", "clinical"]):
            sections = [
                DynamicSection(
                    heading="Clinical Presentation, Etiology & Patient Context",
                    content=(
                        f"Contextualize patient demographics, risk factors, chief complaints, and pathophysiological mechanisms for {goal}. "
                        f"Establish rigorous baseline metrics and clinical history screening parameters."
                    ),
                    focus_keywords=["Clinical Presentation", "Etiology", "Patient Context"],
                ),
                DynamicSection(
                    heading="Symptom Triangulation, Physical Examination & Biomarkers",
                    content=(
                        f"Identify cardinal presenting symptoms, essential physical examination maneuvers, and high-yield laboratory/imaging biomarkers. "
                        f"Specify threshold values distinguishing benign presentations from emergent clinical deterioration."
                    ),
                    focus_keywords=["Symptoms", "Examination", "Biomarkers"],
                ),
                DynamicSection(
                    heading="Diagnostic Workup & Differential Diagnosis (DDx)",
                    content=(
                        f"Construct a prioritized differential diagnosis matrix ranked by epidemiological likelihood and clinical acuity. "
                        f"Detail step-wise diagnostic algorithms to systematically rule out life-threatening mimics."
                    ),
                    focus_keywords=["Diagnosis", "Differential Diagnosis", "DDx"],
                ),
                DynamicSection(
                    heading="Evidence-Based Treatment Protocols & Interventions",
                    content=(
                        f"Formulate first-line and second-line evidence-based pharmacotherapeutic and non-pharmacological interventions. "
                        f"Specify precise dosing guidelines, titration schedules, and clinical efficacy endpoints."
                    ),
                    focus_keywords=["Treatment", "Protocol", "Therapy"],
                ),
                DynamicSection(
                    heading="Contraindications, Drug Interactions & Adverse Red Flags",
                    content=(
                        f"Enumerate absolute and relative contraindications, cytochrome P450 pharmacokinetic drug interactions, "
                        f"and critical physiological red flags mandating immediate specialist escalation."
                    ),
                    focus_keywords=["Contraindications", "Red Flags", "Interactions"],
                ),
                DynamicSection(
                    heading="Longitudinal Follow-up, Patient Education & Safety Thresholds",
                    content=(
                        f"Establish follow-up evaluation intervals, patient self-monitoring protocols, and explicit instructions on when to seek "
                        f"emergency care. Ensure patient-friendly health literacy communication."
                    ),
                    focus_keywords=["Follow-up", "Patient Education", "Safety"],
                ),
            ]
            return PlannedSectionSchema(
                domain=domain,
                category="Medical & Clinical",
                dynamic_sections=sections,
                custom_headings=[s.heading for s in sections],
            )

        # ── 2. Programming & Software Engineering ───────────────────
        if any(w in domain_lower for w in ["software", "scheduling", "web", "cloud", "saas", "api", "backend"]):
            sections = [
                DynamicSection(
                    heading="System Architecture & Component Topology",
                    content=(
                        f"Deconstruct {goal} into modular, decoupled layers: presentation, business logic domain services, "
                        f"data persistence, and event-driven asynchronous queues. Enforce clean separation of concerns, "
                        f"dependency injection, and horizontal elasticity across stateless service nodes."
                    ),
                    focus_keywords=["Architecture", "Modularity", "Decoupling"],
                ),
                DynamicSection(
                    heading="API Specifications & Endpoint Contract",
                    content=(
                        f"Define idiomatic RESTful / GraphQL endpoint signatures with strict JSON schema request/response contracts. "
                        f"Include HTTP status codes, idempotent headers for write operations, comprehensive pagination, "
                        f"and rate limiting boundaries protecting sensitive routes."
                    ),
                    focus_keywords=["API", "Contracts", "REST", "Endpoints"],
                ),
                DynamicSection(
                    heading="Database Schema, Relationships & Data Integrity",
                    content=(
                        f"Design normalized relational schemas (PostgreSQL) or document structures supporting {entity_str}. "
                        f"Specify primary/foreign keys, multi-column composite indexes, unique constraints, and transaction isolation "
                        f"levels to guarantee ACID compliance and eliminate race conditions."
                    ),
                    focus_keywords=["Database", "Schema", "Indexes", "ACID"],
                ),
                DynamicSection(
                    heading="Security Architecture, Authentication & Access Control (RBAC)",
                    content=(
                        f"Implement enterprise-grade identity management using OAuth2 / JWT bearer tokens, bcrypt password hashing, "
                        f"and granular Role-Based Access Control (RBAC). Enforce OWASP Top 10 defenses including parameterized queries, "
                        f"CORS policies, CSP headers, and TLS in-flight encryption."
                    ),
                    focus_keywords=["Security", "Authentication", "RBAC", "OWASP"],
                ),
                DynamicSection(
                    heading="Performance Optimization, Caching & Scalability",
                    content=(
                        f"Incorporate distributed in-memory caching (Redis) for hot query read paths, connection pooling, "
                        f"and asynchronous background task workers (Celery/BullMQ). Ensure sub-100ms response latencies at peak concurrent load."
                    ),
                    focus_keywords=["Performance", "Caching", "Redis", "Scalability"],
                ),
                DynamicSection(
                    heading="Automated Testing Strategy & Observability",
                    content=(
                        f"Formulate a complete testing pyramid: unit tests with mocking, end-to-end integration tests for critical flows, "
                        f"and load testing assertions. Incorporate structured JSON logging, Prometheus metrics, and OpenTelemetry tracing."
                    ),
                    focus_keywords=["Testing", "Unit Tests", "Observability", "Metrics"],
                ),
                DynamicSection(
                    heading="Production Deployment, Infrastructure & CI/CD Pipeline",
                    content=(
                        f"Provide multi-stage containerized Dockerfiles, Docker Compose service definitions, and automated GitHub Actions CI/CD workflows. "
                        f"Include zero-downtime rolling deployment strategies, health-check probes, and automated rollback triggers."
                    ),
                    focus_keywords=["Deployment", "Docker", "CI/CD", "Infrastructure"],
                ),
            ]
            return PlannedSectionSchema(
                domain=domain,
                category="Software Engineering",
                dynamic_sections=sections,
                custom_headings=[s.heading for s in sections],
            )

        # ── 2. Teacher, Education & Pedagogy ────────────────────────
        if any(w in domain_lower for w in ["education", "teaching", "programming education", "learning"]):
            sections = [
                DynamicSection(
                    heading="Pedagogical Learning Outcomes (Bloom's Taxonomy)",
                    content=(
                        f"Articulate rigorous, measurable behavioral objectives spanning knowledge retention, conceptual comprehension, "
                        f"and practical synthesis for {goal}. Ensure students transition from passive syntax recall to autonomous problem solving."
                    ),
                    focus_keywords=["Learning Outcomes", "Bloom's Taxonomy", "Competencies"],
                ),
                DynamicSection(
                    heading="Scaffolded Curriculum & Step-by-Step Lesson Roadmap",
                    content=(
                        f"Structure curriculum into sequenced, bite-sized modules starting from core foundational mental models "
                        f"before introducing advanced nuances. Incorporate real-world analogies to anchor abstract principles."
                    ),
                    focus_keywords=["Curriculum", "Roadmap", "Scaffolding"],
                ),
                DynamicSection(
                    heading="Interactive Lesson Flow & Cognitive Load Management",
                    content=(
                        f"Design each lesson with the 'Explain-Demonstrate-Practice-Reflect' instructional cycle. "
                        f"Limit working memory saturation by presenting one core concept per code example with immediate interactive confirmation."
                    ),
                    focus_keywords=["Lesson Flow", "Cognitive Load", "Instructional Design"],
                ),
                DynamicSection(
                    heading="Hands-On Practice Exercises & Step-by-Step Walkthroughs",
                    content=(
                        f"Provide fully annotated, executable code walkthroughs accompanied by progressive practice challenges. "
                        f"Include intentional starter bugs for student debugging drills and self-guided solution reveals."
                    ),
                    focus_keywords=["Exercises", "Code Walkthroughs", "Hands-On Practice"],
                ),
                DynamicSection(
                    heading="Capstone Real-World Application Projects",
                    content=(
                        f"Formulate end-to-end capstone projects that synthesize all module competencies into a functional portfolio asset. "
                        f"Specify incremental milestone deliverables, edge-case requirements, and code style evaluation criteria."
                    ),
                    focus_keywords=["Projects", "Capstone", "Portfolio"],
                ),
                DynamicSection(
                    heading="Formative Assessment Rubrics, Quizzes & Spaced Revision",
                    content=(
                        f"Establish objective evaluation rubrics across code correctness, algorithmic efficiency, and idiomatic readability. "
                        f"Incorporate spaced repetition flashcard prompts and weekly cumulative review checkpoints to prevent concept decay."
                    ),
                    focus_keywords=["Assessment", "Rubrics", "Quizzes", "Spaced Repetition"],
                ),
            ]
            return PlannedSectionSchema(
                domain=domain,
                category="Education & Pedagogy",
                dynamic_sections=sections,
                custom_headings=[s.heading for s in sections],
            )

        # ── 3. Marketing, Growth & Brand Strategy ────────────────────
        if any(w in domain_lower for w in ["marketing", "advertising", "growth", "brand"]):
            sections = [
                DynamicSection(
                    heading="Target Audience Persona & Demographic Segmentation",
                    content=(
                        f"Detail primary and secondary buyer personas, psychographic profiles, behavioral pain points, and purchase triggers "
                        f"relevant to {goal}. Identify high-affinity channels where the target demographic is most receptive."
                    ),
                    focus_keywords=["Audience", "Personas", "Segmentation"],
                ),
                DynamicSection(
                    heading="Core Value Proposition & Unique Selling Proposition (USP)",
                    content=(
                        f"Crystallize an undeniable value proposition that distinguishes the offer from direct and indirect competitors. "
                        f"Frame the primary benefit in clear, benefit-driven language emphasizing immediate time-to-value."
                    ),
                    focus_keywords=["USP", "Value Proposition", "Differentiation"],
                ),
                DynamicSection(
                    heading="Consumer Psychology, Emotional Triggers & Objection Handling",
                    content=(
                        f"Leverage cognitive biases (social proof, loss aversion, authority signaling) to overcome buyer skepticism. "
                        f"Formulate preemptive rebuttals for top customer objections regarding price, complexity, and inertia."
                    ),
                    focus_keywords=["Consumer Psychology", "Objections", "Trust"],
                ),
                DynamicSection(
                    heading="Multi-Channel Campaign Messaging & Content Wave Schedule",
                    content=(
                        f"Architect an omnichannel content schedule across paid acquisition, organic social, email nurturing, and landing pages. "
                        f"Draft modular headlines, hooks, body copy variations, and compelling narrative arcs."
                    ),
                    focus_keywords=["Campaign", "Messaging", "Omnichannel"],
                ),
                DynamicSection(
                    heading="Visual Creative Direction & Brand Aesthetic Standards",
                    content=(
                        f"Provide clear creative guidelines for visual assets, typography, color palettes, and video pacing. "
                        f"Ensure cohesive aesthetic alignment that reinforces brand credibility across every customer touchpoint."
                    ),
                    focus_keywords=["Visual Direction", "Creative", "Branding"],
                ),
                DynamicSection(
                    heading="High-Conversion CTA Framework, Conversion Funnels & KPIs",
                    content=(
                        f"Formulate frictionless, high-urgency Call-to-Actions (CTAs) mapped to funnel stages. Establish leading and lagging KPIs: "
                        f"CTR, conversion rate, Customer Acquisition Cost (CAC), Return on Ad Spend (ROAS), and Lifetime Value (LTV)."
                    ),
                    focus_keywords=["CTA", "KPIs", "Conversion Rate", "Attribution"],
                ),
            ]
            return PlannedSectionSchema(
                domain=domain,
                category="Marketing & Growth",
                dynamic_sections=sections,
                custom_headings=[s.heading for s in sections],
            )

        # ── 5. Dynamic Synthesis for Unknown / Emerging Domains ─────
        # Dynamically synthesizes bespoke sections using domain taxonomy, action, and entity keywords
        sections = [
            DynamicSection(
                heading=f"{domain} Foundational Topology & Strategic Framework",
                content=(
                    f"Establish the macro architecture, foundational principles, and core theoretical models governing {goal}. "
                    f"Account for operational dependencies among {entity_str}."
                ),
                focus_keywords=["Framework", "Foundations", "Topology"],
            ),
            DynamicSection(
                heading=f"Core Operational Specifications & Deliverable Engineering",
                content=(
                    f"Formulate exact technical standards, execution workflows, and deliverable specifications for {goal}. "
                    f"Ensure zero ambiguity and comprehensive coverage of all functional requirements."
                ),
                focus_keywords=["Specifications", "Workflows", "Standards"],
            ),
            DynamicSection(
                heading=f"Quality Assurance, Verification Benchmarks & Failure Modes",
                content=(
                    f"Define rigorous qualitative and quantitative acceptance criteria. Enumerate domain-specific risk factors, "
                    f"edge-case failure modes, and automated verification protocols to ensure flawless execution."
                ),
                focus_keywords=["Quality", "Verification", "Benchmarks"],
            ),
            DynamicSection(
                heading=f"Lifecycle Governance, Maintenance & Scalability Roadmap",
                content=(
                    f"Provide a phased deployment and lifecycle governance plan. Detail ongoing monitoring, iteration cycles, "
                    f"and horizontal scalability mechanisms."
                ),
                focus_keywords=["Lifecycle", "Governance", "Roadmap"],
            ),
        ]
        return PlannedSectionSchema(
            domain=domain,
            category="Emerging / Specialized Industry",
            dynamic_sections=sections,
            custom_headings=[s.heading for s in sections],
        )
