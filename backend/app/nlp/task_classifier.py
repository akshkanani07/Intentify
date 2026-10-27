"""TaskClassifier – classifies concrete operational task types and tangible deliverables."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("intentify.nlp.task_classifier")


@dataclass
class TaskDeliverableResult:
    """Classified task archetype and primary deliverable format."""

    task_type: str
    deliverable: str
    confidence: float
    execution_horizon: str  # Immediate, Iterative, Phased Roadmap


class TaskClassifier:
    """Maps user intent, entities, and domain into concrete task types and tangible deliverables."""

    def classify(self, text: str, intent: str = "create", domain: str = "Software Development") -> TaskDeliverableResult:
        text_lower = text.lower()
        domain_lower = domain.lower()

        # Software / SaaS
        if any(w in domain_lower for w in ["software", "scheduling", "web", "cloud", "saas", "api"]):
            if any(w in text_lower for w in ["debug", "fix", "error", "issue", "bug"]):
                return TaskDeliverableResult(
                    task_type="System Diagnostic & Root Cause Remediation",
                    deliverable="Root Cause Analysis, Corrective Code Patches, and Regression Test Suite",
                    confidence=0.94,
                    execution_horizon="Immediate",
                )
            return TaskDeliverableResult(
                task_type="Full-Stack Application & Architecture Engineering",
                deliverable="Production-Ready Source Code, API Endpoints, Database Schemas, and Deployment Manifests",
                confidence=0.96,
                execution_horizon="Phased Roadmap",
            )

        # Education & Learning
        if any(w in domain_lower for w in ["education", "teaching", "programming education", "learning"]) or intent == "learn":
            return TaskDeliverableResult(
                task_type="Pedagogical Curriculum & Concept Mastery Instruction",
                deliverable="Structured Progressive Curriculum, Step-by-Step Code Walkthroughs, and Hands-On Mastery Exercises",
                confidence=0.96,
                execution_horizon="Iterative",
            )

        # Healthcare / Clinical
        if any(w in domain_lower for w in ["health", "medical", "hospital", "clinical"]):
            if "software" in text_lower or "system" in text_lower or "app" in text_lower:
                return TaskDeliverableResult(
                    task_type="Healthcare Software & Clinical Informatics Engineering",
                    deliverable="HIPAA-Compliant Hospital Workflow Engine, EHR Integration Schema, and Doctor-Patient Portal Architecture",
                    confidence=0.95,
                    execution_horizon="Phased Roadmap",
                )
            return TaskDeliverableResult(
                task_type="Clinical Diagnostic Assessment & Care Protocol",
                deliverable="Evidence-Based Clinical Decision Support Algorithm, Differential Diagnosis, and Treatment Pathway",
                confidence=0.93,
                execution_horizon="Immediate",
            )

        # Marketing & Growth
        if any(w in domain_lower for w in ["marketing", "advertising", "growth", "brand"]):
            return TaskDeliverableResult(
                task_type="Omnichannel Marketing Strategy & High-Conversion Copywriting",
                deliverable="Comprehensive Campaign Blueprint, Positioning Strategy, Ad Copy Variants, and KPI Dashboard Specification",
                confidence=0.94,
                execution_horizon="Iterative",
            )

        # Legal & Compliance
        if any(w in domain_lower for w in ["legal", "compliance", "regulatory"]):
            return TaskDeliverableResult(
                task_type="Legal Instrument Drafting & Statutory Compliance Audit",
                deliverable="Legally Binding Contractual Provisions, Statutory Precedent Review, and Liability Mitigation Memorandum",
                confidence=0.93,
                execution_horizon="Immediate",
            )

        # Machine Learning / AI
        if any(w in domain_lower for w in ["machine learning", "data science", "ai", "deep learning"]):
            return TaskDeliverableResult(
                task_type="Machine Learning Pipeline & Model Engineering",
                deliverable="End-to-End Data Preprocessing Pipeline, PyTorch/Scikit-Learn Model Architecture, and Evaluation Benchmark Suite",
                confidence=0.95,
                execution_horizon="Phased Roadmap",
            )

        # Business / Finance
        if any(w in domain_lower for w in ["business", "finance", "strategy"]):
            return TaskDeliverableResult(
                task_type="Strategic Business Planning & Financial Valuation",
                deliverable="Executive Business Plan, Unit Economics Breakdown, Go-To-Market Engine, and 3-Year Pro Forma Financial Model",
                confidence=0.92,
                execution_horizon="Phased Roadmap",
            )

        # General Fallback
        return TaskDeliverableResult(
            task_type="Comprehensive Professional Solution Design",
            deliverable="Structured Technical Specification, Execution Strategy, and Production Deliverables",
            confidence=0.85,
            execution_horizon="Iterative",
        )
