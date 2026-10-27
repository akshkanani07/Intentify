"""RequirementIntelligence – dynamically synthesizes domain-deep functional requirements and constraints at runtime."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("intentify.nlp.requirement_intelligence")


@dataclass
class DeepRequirementBundle:
    """Domain-deep functional requirements, constraints, and success criteria."""

    functional_requirements: list[str]
    technical_constraints: list[str]
    success_criteria: list[str]
    domain_tags: list[str] = field(default_factory=list)


class RequirementIntelligenceEngine:
    """Synthesizes rich, domain-specific requirements and constraints at runtime rather than naive keyword copies."""

    def synthesize(
        self,
        domain: str,
        goal: str,
        intent: str,
        entities: list[dict[str, Any]] | None = None,
    ) -> DeepRequirementBundle:
        domain_lower = domain.lower()
        entities = entities or []
        entity_texts = [e.get("text", "") for e in entities if isinstance(e, dict) and e.get("text")]

        # ── 1. Scheduling / SaaS Web Applications ───────────────────
        if any(w in domain_lower for w in ["scheduling", "booking", "calendar saas"]):
            requirements = [
                "Authentication & RBAC: Multi-tenant JWT/OAuth2 authentication with granular role separation (Host, Client, Organization Admin).",
                "Calendar Engine: Two-way calendar synchronization (Google Calendar, Microsoft Outlook, Apple iCal) via CalDAV/webhooks.",
                "Availability Engine: Timezone-aware availability calculation with buffer times between appointments and custom weekly working hours.",
                "Booking & Conflict Detection: Atomic transaction booking algorithm with database-level pessimistic/optimistic locking preventing concurrent double-booking.",
                "Recurring Events: Support for recurring booking patterns (daily, weekly, bi-weekly, custom intervals) with exception handling.",
                "Automated Notifications: Multi-channel confirmation, cancellation, and reminder triggers via transactional email (SendGrid/Postmark) and SMS/WhatsApp (Twilio).",
                "Timezone Normalization: Strict internal UTC storage with automated bidirectional conversion to client and host local timezones.",
                "Audit Logging: Comprehensive immutable audit logs for all reservation creations, reschedules, and cancellations.",
            ]
            constraints = [
                "Production Ready: Zero mock functions, placeholder TODO comments, or simulated database queries.",
                "No Deprecated APIs: Use only modern, actively supported library versions and framework conventions.",
                "Strict Data Isolation: Enforce tenant-level data isolation via tenant_id foreign keys and Row-Level Security (RLS).",
                "Sub-150ms Availability Latency: Calendar slot generation algorithms must calculate 30-day availability in under 150 milliseconds.",
                "Defensive Error Handling: Gracefully catch timezone parsing exceptions and API sync failures with structured JSON error responses.",
            ]
            criteria = [
                "100% test coverage on double-booking race condition prevention under concurrent load.",
                "Zero timezone skew across daylight saving time transition boundaries.",
                "Successful round-trip CalDAV webhook synchronization with mock calendar providers.",
            ]
            return DeepRequirementBundle(
                functional_requirements=requirements,
                technical_constraints=constraints,
                success_criteria=criteria,
                domain_tags=["SaaS", "Scheduling", "Multi-Tenant", "PostgreSQL"],
            )

        # ── 2. General Software Engineering / Web Backend ───────────
        if any(w in domain_lower for w in ["software", "web", "cloud", "api"]):
            requirements = [
                "Clean Architecture: Enforce strict separation between HTTP transport layer, core business domain logic, and data persistence repositories.",
                "Type Safety & Contracts: Complete type annotations across all functions, models, and interfaces (Pydantic / TypeScript strict mode).",
                "Comprehensive Data Persistence: Implement robust ORM/query layer with automated migration scripts, index definitions, and connection pooling.",
                "Resilience & Fault Tolerance: Circuit breaker patterns, exponential backoff retries for third-party integrations, and graceful shutdown listeners.",
                "Telemetry & Health: Expose structured JSON logging with correlation IDs, Prometheus metric collectors, and liveness/readiness probes.",
            ]
            constraints = [
                "Zero Insecure Dependencies: No packages with known CVE vulnerabilities or deprecated security protocols.",
                "OWASP Top 10 Compliance: Strict parameterization against SQL/NoSQL injection, CORS lockdown, and secure cookie/header configurations.",
                "Deterministic Builds: Provide pinned dependency manifests (requirements.txt / package.json with exact locks) and reproducible Dockerfiles.",
                "Comprehensive Automated Testing: Mandate unit test coverage >= 85% and end-to-end integration test coverage for all primary workflows.",
            ]
            criteria = [
                "Application boots and passes all test assertions in a pristine sandbox environment.",
                "API contracts strictly conform to OpenAPI 3.1 specifications.",
                "Zero unhandled runtime exceptions during boundary condition and malicious payload fuzzing.",
            ]
            return DeepRequirementBundle(
                functional_requirements=requirements,
                technical_constraints=constraints,
                success_criteria=criteria,
                domain_tags=["Software Engineering", "Clean Architecture", "Production Ready"],
            )

        # ── 3. Programming Education & Pedagogy ─────────────────────
        if any(w in domain_lower for w in ["education", "teaching", "programming education", "learning"]):
            requirements = [
                "Clear Pedagogical Objectives: Define actionable learning goals for every module following Bloom's Revised Taxonomy.",
                "Progressive Mental Models: Introduce syntax and architectural concepts through accessible analogies before formal technical definitions.",
                "Annotated Code Walkthroughs: Accompany every code sample with line-by-line mechanical explanations and memory visualization diagrams.",
                "Interactive Debugging Exercises: Provide deliberate starter code snippets with typical beginner syntax and logic traps for student diagnosis.",
                "Capstone Portfolio Projects: End each learning unit with a functional, real-world mini-project that reinforces combined concepts.",
                "Spaced Practice & Quizzes: Formative multi-choice and short-answer self-quizzes to solidify memory consolidation and retention.",
            ]
            constraints = [
                "Cognitive Load Management: Avoid introducing multiple advanced abstractions simultaneously (e.g., explain loops before list comprehensions).",
                "Idiomatic Modern Best Practices: Teach current standard conventions (PEP 8 for Python, ES2022+ for JavaScript) rather than obsolete patterns.",
                "Patient & Encouraging Register: Maintain an authoritative, structured, yet deeply supportive pedagogical tone.",
                "Zero Assumed Prior Jargon: Define every technical term (e.g., 'immutable', 'polymorphism', 'asynchronous') upon first introduction.",
            ]
            criteria = [
                "Students can independently complete capstone exercises without referring to starter hints.",
                "Progressive difficulty curve with zero unassisted conceptual leaps.",
                "Complete coverage of fundamental syntax, data structures, and algorithmic logic.",
            ]
            return DeepRequirementBundle(
                functional_requirements=requirements,
                technical_constraints=constraints,
                success_criteria=criteria,
                domain_tags=["Education", "Pedagogy", "Interactive Learning", "Beginner Friendly"],
            )

        # ── 4. Marketing, Growth & Brand Strategy ────────────────────
        if any(w in domain_lower for w in ["marketing", "advertising", "growth", "brand"]):
            requirements = [
                "Detailed Audience Persona: Quantify demographic, psychographic, and behavioral triggers of high-value buyer cohorts.",
                "Compelling Value Proposition: Craft crisp, differentiated Unique Selling Propositions (USPs) highlighting quantifiable outcomes.",
                "Psychological Triggers & Hooks: Integrate cognitive heuristics (social proof, urgency, exclusivity, risk reversal) in lead generation.",
                "Multi-Wave Content Strategy: Outline top-of-funnel awareness, middle-of-funnel consideration, and bottom-of-funnel conversion assets.",
                "Visual & Copy Standards: Specify brand voice tone guidelines, headline hooks, body copy formulas (AIDA, PAS), and visual creative briefs.",
                "Attribution & Measurement: Define exact conversion tracking frameworks, pixel setup, UTM tagging taxonomies, and performance KPIs.",
            ]
            constraints = [
                "Zero Misleading Claims: Ensure 100% compliance with FTC truth-in-advertising guidelines and substantiated benefit statements.",
                "No Deceptive Dark Patterns: Avoid manipulative countdown timers, deceptive opt-outs, or unsubstantiated scarcity claims.",
                "Brand Consistency: Adhere strictly to the defined brand tone, ensuring seamless cohesion across organic, paid, and lifecycle channels.",
                "Data Privacy Compliance: Ensure lead capture workflows comply fully with GDPR, CCPA, and CAN-SPAM regulations.",
            ]
            criteria = [
                "Every campaign asset directly connects to a measurable conversion KPI.",
                "Messaging resonates directly with the targeted customer segment's primary emotional pain points.",
                "Zero regulatory or platform policy compliance violations.",
            ]
            return DeepRequirementBundle(
                functional_requirements=requirements,
                technical_constraints=constraints,
                success_criteria=criteria,
                domain_tags=["Marketing", "Growth", "Conversion Optimization", "Brand Strategy"],
            )

        # ── 5. Medical, Clinical & Healthcare Software ───────────────
        if any(w in domain_lower for w in ["health", "medical", "hospital", "clinical"]):
            requirements = [
                "Clinical Workflow Alignment: Match clinical triage and care management pathways standardized in medical practice.",
                "EHR/EMR Interoperability: Support HL7, FHIR, and DICOM standards for seamless clinical data interchange.",
                "Diagnostic Support Algorithms: Incorporate validated medical decision-support logic with explicit evidence references.",
                "Audit & Traceability: Provide tamper-evident, append-only audit logging for all patient record access and updates.",
                "Role-Based Patient Safety: Separate administrative, nursing, and physician access levels with mandatory multi-factor authentication.",
            ]
            constraints = [
                "Strict HIPAA & HITECH Compliance: Guarantee end-to-end encryption for Protected Health Information (PHI) at rest and in transit.",
                "No Unsafe Treatment Prescriptions: Never output definitive medical advice without explicit clinician review disclaimers.",
                "Explicit Uncertainty Margins: Highlight boundary cases, contraindications, and mandatory emergency escalation pathways.",
                "High Availability: Medical workflows require 99.99% uptime with automated multi-zone failover redundancy.",
            ]
            criteria = [
                "Zero HIPAA compliance gaps or unauthorized PHI leakage in logs and telemetry.",
                "Clinician-verified diagnostic support workflow accuracy.",
                "Sub-second alert delivery for critical patient telemetry events.",
            ]
            return DeepRequirementBundle(
                functional_requirements=requirements,
                technical_constraints=constraints,
                success_criteria=criteria,
                domain_tags=["Healthcare", "HIPAA", "Clinical Informatics", "Patient Safety"],
            )

        # ── 6. Dynamic Fallback for General / Novel Domains ──────────
        requirements = [
            f"Synthesize comprehensive operational specifications and execution parameters for {goal}.",
            f"Establish modular, decoupled components supporting {', '.join(entity_texts) if entity_texts else 'core entities'}.",
            "Formulate step-wise execution milestones with quantifiable verification criteria.",
            "Incorporate industry-standard best practices, quality assurance, and lifecycle governance.",
        ]
        constraints = [
            "Produce immediately actionable, production-ready deliverables with zero placeholders or approximations.",
            "Maintain an authoritative, rigorous register aligned with principal domain practitioner standards.",
            "Adhere to all applicable regulatory, safety, and domain compliance standards.",
        ]
        criteria = [
            "All functional requirements are comprehensively fulfilled with zero ambiguities.",
            "Execution blueprint enables flawless implementation by domain specialists.",
        ]
        return DeepRequirementBundle(
            functional_requirements=requirements,
            technical_constraints=constraints,
            success_criteria=criteria,
            domain_tags=[domain, "Production Ready", "Professional Standard"],
        )
