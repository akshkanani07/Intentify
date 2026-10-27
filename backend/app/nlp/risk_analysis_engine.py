"""RiskAnalysisEngine – pinpoints domain failure modes, detects missing information, and synthesizes smart assumptions."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("intentify.nlp.risk_analysis_engine")


@dataclass
class RiskAnalysisResult:
    """Detailed risk assessment, identified gaps, and generated smart assumptions."""

    identified_risks: list[str]
    missing_information: list[str]
    smart_assumptions: list[str]
    risk_level: str  # Low, Moderate, High, Critical
    compliance_flags: list[str] = field(default_factory=list)


class RiskAnalysisEngine:
    """Performs deep failure-mode analysis, detects missing information, and formulates high-confidence assumptions."""

    DOMAIN_RISK_MAP = {
        "Scheduling SaaS Platform": [
            "Timezone skew and daylight saving boundary errors in appointment booking",
            "Race conditions and double-booking during concurrent reservation requests",
            "Notification delivery dropouts and calendar synchronization latency",
            "Tenant data bleed across multi-tenant database partitions",
        ],
        "Software Development": [
            "Unsanitized inputs leading to injection vulnerabilities (OWASP Top 10)",
            "Unbounded memory or connection pool exhaustion under sudden traffic spikes",
            "Lack of idempotency in API write operations leading to duplicated state",
            "Inadequate observability and missing distributed tracing in production",
        ],
        "Programming Education": [
            "Premature introduction of complex abstractions causing student cognitive overload",
            "Abstract code examples lacking interactive real-world debugging context",
            "Absence of formative feedback loops and incremental verification checkpoints",
            "Passive lecture flow without active hands-on coding reinforcement",
        ],
        "Healthcare Software": [
            "PHI / EHR exposure violating HIPAA, HITECH, and clinical data governance",
            "Latency or desynchronization in real-time patient vital sign alerts",
            "Lack of tamper-evident audit logging for medical record modifications",
            "Single point of failure in hospital admission and triage queuing",
        ],
        "Marketing": [
            "Non-compliance with FTC advertising guidelines and truth-in-advertising statutes",
            "Audience fatigue and brand erosion from repetitive or aggressive messaging",
            "Misattribution of conversion channels leading to wasted media spend",
            "Overpromising deliverable outcomes or creating legally actionable product claims",
        ],
        "Legal": [
            "Drafting unenforceable covenants or ambiguous indemnity obligations",
            "Overlooking governing jurisdiction statutory requirements and recent case precedent",
            "Failure to address dispute resolution venue and arbitration procedures",
        ],
    }

    def analyze(
        self,
        text: str,
        domain: str = "Software Development",
        intent: str = "create",
        entities: list[Any] | None = None,
    ) -> RiskAnalysisResult:
        text_lower = text.lower()
        domain_lower = domain.lower()

        # 1. Determine Domain Risks
        matched_risks: list[str] = []
        for d_key, risks in self.DOMAIN_RISK_MAP.items():
            if d_key.lower() in domain_lower or domain_lower in d_key.lower():
                matched_risks.extend(risks)
                break

        if not matched_risks:
            if "software" in domain_lower or "code" in text_lower:
                matched_risks = self.DOMAIN_RISK_MAP["Software Development"]
            elif "learn" in text_lower or "education" in domain_lower:
                matched_risks = self.DOMAIN_RISK_MAP["Programming Education"]
            else:
                matched_risks = [
                    "Ambiguity in stakeholder requirements leading to misaligned deliverables",
                    "Unstated operational constraints causing scope creep and execution friction",
                    "Lack of standardized quality verification metrics across milestones",
                ]

        # 2. Detect Missing Information Gaps
        missing: list[str] = []
        if any(w in domain_lower for w in ["software", "saas", "web"]):
            if not any(w in text_lower for w in ["postgres", "mysql", "mongodb", "redis", "sqlite", "database"]):
                missing.append("Database engine and persistence layer preference not specified")
            if not any(w in text_lower for w in ["python", "typescript", "go", "rust", "java", "react", "next"]):
                missing.append("Target programming language / technology stack not explicitly mandated")
            if not any(w in text_lower for w in ["aws", "gcp", "azure", "docker", "kubernetes", "cloud"]):
                missing.append("Production deployment target and cloud infrastructure unspecified")
            if "schedule" in text_lower or "booking" in text_lower:
                if not any(w in text_lower for w in ["timezone", "utc", "gmt"]):
                    missing.append("Timezone handling policy and multi-region synchronization rules unspecified")

        if any(w in domain_lower for w in ["education", "learn", "curriculum"]):
            if not any(w in text_lower for w in ["week", "hour", "day", "duration"]):
                missing.append("Course duration, weekly time commitment, and milestone pacing undefined")
            if not any(w in text_lower for w in ["project", "exercise", "exam", "quiz"]):
                missing.append("Preferred project evaluation format and certification standard unspecified")

        if any(w in domain_lower for w in ["health", "hospital", "medical"]):
            if not any(w in text_lower for w in ["hipaa", "gdpr", "compliance"]):
                missing.append("Regional health compliance mandate (HIPAA, GDPR, HL7/FHIR) unspecified")

        # 3. Formulate Smart Assumptions to bridge gaps
        assumptions: list[str] = []
        if any(w in domain_lower for w in ["scheduling", "saas"]):
            assumptions.append("All scheduling events and calendar calculations default to UTC internally with client-side local timezone rendering")
            assumptions.append("Database defaults to PostgreSQL with optimistic locking and row-level security to prevent booking race conditions")
            assumptions.append("Authentication employs modern JWT bearer tokens with Role-Based Access Control (RBAC: Admin, Host, Client)")
            assumptions.append("System is designed for high availability with asynchronous notification queues (Redis / Celery)")
        elif any(w in domain_lower for w in ["software", "web", "api"]):
            assumptions.append("Implementation uses modern production-grade architecture (FastAPI / Next.js / TypeScript) with clean modularity")
            assumptions.append("Security adheres to OWASP Top 10 standards with strict input validation and zero plaintext secrets")
            assumptions.append("Comprehensive unit and integration test suite is mandated using standardized testing frameworks")
        elif any(w in domain_lower for w in ["education", "learn"]):
            assumptions.append("Instruction assumes beginner-to-intermediate entry point with progressive cognitive difficulty")
            assumptions.append("Curriculum balances 40% conceptual explanation with 60% active hands-on coding and project exercises")
            assumptions.append("Includes immediate error-correction guidance for common beginner syntax and runtime mistakes")
        elif any(w in domain_lower for w in ["health", "medical"]):
            assumptions.append("System assumes full HIPAA and HL7/FHIR standard compliance with encrypted PHI at rest and in transit")
            assumptions.append("All clinical recommendations require explicit certified practitioner sign-off with clear uncertainty margins")
        else:
            assumptions.append("Standard enterprise best practices and modular architecture apply throughout execution")
            assumptions.append("Deliverables must be immediately production-ready with zero placeholders or superficial approximations")
            assumptions.append("All operational steps include explicit validation criteria and automated verification checkpoints")

        # Risk level determination
        risk_level = "Moderate"
        if any(w in domain_lower for w in ["health", "medical", "legal", "financial"]):
            risk_level = "High"
        elif len(missing) >= 3:
            risk_level = "Moderate"
        else:
            risk_level = "Low"

        return RiskAnalysisResult(
            identified_risks=matched_risks[:4],
            missing_information=missing[:4],
            smart_assumptions=assumptions[:4],
            risk_level=risk_level,
            compliance_flags=["Zero Trust Security", "Production Readiness"] if "software" in domain_lower else ["Quality Rigor"],
        )
