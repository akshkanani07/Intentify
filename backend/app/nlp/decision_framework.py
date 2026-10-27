"""Decision Framework Engine – Layer 8 of Intentify AI v4.

Defines domain-specific trade-off hierarchies and decision priority frameworks:
- Software: Security > Correctness > Scalability > Maintainability > Performance
- Marketing: Trust > Emotion > Conversion > Brand Value
- Education: Understanding > Practice > Retention > Assessment
- Business: Market Opportunity > Unit Economics > Competitive Moat > Downside Risk
- Medical: Patient Safety > Diagnostic Rigor > Evidence Level > Treatment Efficacy
- Legal: Statutory Compliance > Enforceability > Risk Shielding > Precedent Alignment
- General / Novel: Clarity > Feasibility > Rigor > Value Delivery
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("intentify.nlp.decision_framework")


@dataclass
class DecisionRuleResult:
    """Structured decision framework governing trade-offs during execution."""

    domain: str
    priority_hierarchy: list[str]
    tradeoff_rationale: str
    decision_matrix: list[dict[str, str]] = field(default_factory=list)


class DecisionFrameworkEngine:
    """Establishes authoritative domain priority hierarchies and trade-off principles."""

    FRAMEWORKS = {
        "Software Engineering": {
            "priorities": ["Security", "Correctness", "Scalability", "Maintainability", "Performance"],
            "rationale": "Security and functional correctness are non-negotiable prerequisites. A high-performance or scalable service that leaks tenant data or behaves indeterminately is an enterprise failure.",
            "rules": [
                {"rank": "1", "dimension": "Security", "rule": "Never sacrifice data isolation or cryptographic integrity for convenience or speed."},
                {"rank": "2", "dimension": "Correctness", "rule": "Eliminate race conditions and state inconsistencies before pursuing throughput optimizations."},
                {"rank": "3", "dimension": "Scalability", "rule": "Architect stateless horizontally elastically scalable tiers with decentralized caching."},
                {"rank": "4", "dimension": "Maintainability", "rule": "Enforce clean architecture, decoupling, and high test coverage for long-term viability."},
                {"rank": "5", "dimension": "Performance", "rule": "Optimize algorithms, indexing, and connection pools to achieve sub-100ms response targets."},
            ],
        },
        "Marketing & Growth": {
            "priorities": ["Trust", "Emotion", "Conversion", "Brand Value"],
            "rationale": "Customer trust is the bedrock of long-term customer lifetime value (LTV). Short-term conversion tricks that compromise buyer confidence destroy brand equity.",
            "rules": [
                {"rank": "1", "dimension": "Trust", "rule": "100% compliance with truth-in-advertising guidelines; zero deceptive dark patterns."},
                {"rank": "2", "dimension": "Emotion", "rule": "Anchor value propositions in genuine customer pain points and aspirational identities."},
                {"rank": "3", "dimension": "Conversion", "rule": "Remove friction from customer touchpoints with crystal-clear, urgent CTAs."},
                {"rank": "4", "dimension": "Brand Value", "rule": "Maintain consistent, authoritative aesthetic standards across all creative touchpoints."},
            ],
        },
        "Education & Pedagogy": {
            "priorities": ["Understanding", "Practice", "Retention", "Assessment"],
            "rationale": "Conceptual comprehension must precede rote execution. Passive memorization without hands-on retrieval drills leads to rapid knowledge decay.",
            "rules": [
                {"rank": "1", "dimension": "Understanding", "rule": "Ground abstract concepts in relatable concrete mental models before introducing formal syntax."},
                {"rank": "2", "dimension": "Practice", "rule": "Reinforce every concept with immediate active coding drills and guided error triage."},
                {"rank": "3", "dimension": "Retention", "rule": "Incorporate cumulative spaced repetition to combat forgetting curves."},
                {"rank": "4", "dimension": "Assessment", "rule": "Use authentic project-based assessments and objective rubrics to measure actual competency."},
            ],
        },
        "Business & Strategy": {
            "priorities": ["Market Opportunity", "Unit Economics", "Competitive Moat", "Downside Risk"],
            "rationale": "A large addressable market with viable unit economics forms the foundation of durable enterprise value. Downside risks must be identified early.",
            "rules": [
                {"rank": "1", "dimension": "Market Opportunity", "rule": "Target expanding markets with acute, underserved customer pain points."},
                {"rank": "2", "dimension": "Unit Economics", "rule": "Validate CAC payback, gross margins, and contribution margins early."},
                {"rank": "3", "dimension": "Competitive Moat", "rule": "Build defensible network effects, switching costs, or proprietary datasets."},
                {"rank": "4", "dimension": "Downside Risk", "rule": "Stress-test assumptions against macroeconomic downturns and regulatory shifts."},
            ],
        },
        "Medical & Healthcare": {
            "priorities": ["Patient Safety", "Diagnostic Rigor", "Evidence Level", "Treatment Efficacy"],
            "rationale": "Primum non nocere (First, do no harm). Patient safety and clinical validation supersede all other considerations in medical workflows.",
            "rules": [
                {"rank": "1", "dimension": "Patient Safety", "rule": "Mandate explicit clinician verification boundaries and privacy governance."},
                {"rank": "2", "dimension": "Diagnostic Rigor", "rule": "Systematically rule out high-acuity life-threatening differential diagnoses."},
                {"rank": "3", "dimension": "Evidence Level", "rule": "Adhere strictly to peer-reviewed clinical guidelines and validated biomarkers."},
                {"rank": "4", "dimension": "Treatment Efficacy", "rule": "Formulate targeted therapeutic pathways with clear escalation thresholds."},
            ],
        },
    }

    def get_decision_framework(self, domain: str) -> DecisionRuleResult:
        """Alias for resolve to retrieve decision framework."""
        return self.resolve(domain)

    def resolve(self, domain: str) -> DecisionRuleResult:
        domain_lower = domain.lower()

        if any(w in domain_lower for w in ["software", "scheduling", "web", "cloud", "saas", "api"]):
            match_key = "Software Engineering"
        elif any(w in domain_lower for w in ["marketing", "advertising", "growth"]):
            match_key = "Marketing & Growth"
        elif any(w in domain_lower for w in ["education", "teaching", "programming education", "learning"]):
            match_key = "Education & Pedagogy"
        elif any(w in domain_lower for w in ["business", "strategy", "finance"]):
            match_key = "Business & Strategy"
        elif any(w in domain_lower for w in ["health", "medical", "hospital", "clinical"]):
            match_key = "Medical & Healthcare"
        else:
            return DecisionRuleResult(
                domain=domain,
                priority_hierarchy=["Clarity", "Feasibility", "Rigor", "Value Delivery"],
                tradeoff_rationale=f"In {domain}, clear technical clarity and operational feasibility take precedence to ensure zero ambiguity during execution.",
                decision_matrix=[
                    {"rank": "1", "dimension": "Clarity", "rule": "Eliminate vague approximations in favor of exact specifications."},
                    {"rank": "2", "dimension": "Feasibility", "rule": "Ensure all proposed methodologies are practically implementable with available tools."},
                    {"rank": "3", "dimension": "Rigor", "rule": "Apply principal domain practitioner standards and verification checks."},
                    {"rank": "4", "dimension": "Value Delivery", "rule": "Produce production-ready deliverables that immediately fulfill stakeholder objectives."},
                ],
            )

        data = self.FRAMEWORKS[match_key]
        return DecisionRuleResult(
            domain=match_key,
            priority_hierarchy=data["priorities"],
            tradeoff_rationale=data["rationale"],
            decision_matrix=data["rules"],
        )
