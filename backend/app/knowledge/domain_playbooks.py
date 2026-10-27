"""Domain Playbooks Engine – Layer 4 of Intentify AI v4.

Provides expert thinking frameworks tailored per domain:
- Software Engineering Playbook (Architecture first: Scalability, Security, Performance, Maintainability, Testing, Deployment)
- Marketing Playbook (Customer psychology first: Audience, Emotion, Positioning, Conversion, CTA, Metrics)
- Education Playbook (Learning outcomes first: Objectives, Curriculum, Examples, Exercises, Assessment, Progress Tracking)
- Business Playbook (Market opportunity first: Market Analysis, Competition, Strategy, Revenue Model, Risks)
- Medical / Clinical Playbook (Patient safety and clinical rigor first)
- Legal / Compliance Playbook (Jurisdiction, Precedents, and Enforceability first)
- Unknown Domain Intelligence (Autonomous Temporary Playbook Synthesis)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("intentify.knowledge.domain_playbooks")


@dataclass
class PlaybookSection:
    heading: str
    focus: str
    directives: list[str] = field(default_factory=list)


@dataclass
class DomainPlaybook:
    domain_name: str
    philosophy: str  # Core thinking philosophy
    core_dimensions: list[str]
    sections: list[PlaybookSection]
    decision_priorities: list[str]
    is_temporary_synthesis: bool = False


class DomainPlaybooksEngine:
    """Manages expert playbooks and synthesizes temporary playbooks dynamically for novel or unknown domains."""

    def get_playbook(self, domain: str, goal: str, entities: list[str] | None = None) -> DomainPlaybook:
        domain_lower = domain.lower()
        entities = entities or []
        ent_str = ", ".join(entities[:5]) if entities else "core operational assets"

        # 1. Software Engineering Playbook
        if any(w in domain_lower for w in ["software", "scheduling", "web", "cloud", "saas", "api", "backend", "full stack"]):
            return DomainPlaybook(
                domain_name=domain,
                philosophy="Architecture first: Deconstruct components, guarantee zero-trust security, isolate tenant state, and design for horizontal elasticity.",
                core_dimensions=["Scalability", "Security", "Performance", "Maintainability", "Testing", "Deployment"],
                decision_priorities=["Security", "Correctness", "Scalability", "Maintainability", "Performance"],
                sections=[
                    PlaybookSection(
                        heading="System Architecture & Component Topology",
                        focus="Clean Architecture & Modularity",
                        directives=[
                            f"Decouple presentation, application domain services, and persistence layers for {goal}.",
                            "Employ dependency inversion to keep business logic completely agnostic of external frameworks.",
                            "Design stateless application tiers allowing effortless horizontal scaling behind a reverse proxy.",
                        ],
                    ),
                    PlaybookSection(
                        heading="API Specifications & Endpoint Contract",
                        focus="RESTful / GraphQL Formal Contract",
                        directives=[
                            "Define strict OpenAPI 3.1 request and response schemas with strong type validation.",
                            "Implement idempotent mutation keys to prevent duplicated side-effects during network retries.",
                            "Provide granular HTTP error status codes with machine-parseable error payloads.",
                        ],
                    ),
                    PlaybookSection(
                        heading="Database Schema, Relationships & Data Integrity",
                        focus="ACID Compliance & Multi-Tenant Data Isolation",
                        directives=[
                            f"Model normalized database relations supporting {ent_str}.",
                            "Enforce Row-Level Security (RLS) or tenant schema partitions to completely prevent cross-tenant data bleed.",
                            "Design composite indexes optimized for high-frequency queries and time-series ranges.",
                        ],
                    ),
                    PlaybookSection(
                        heading="Security Architecture & Role-Based Access Control (RBAC)",
                        focus="Zero Trust & OWASP Top 10 Defenses",
                        directives=[
                            "Issue cryptographically signed JWT tokens with short TTLs and secure refresh token rotation.",
                            "Enforce fine-grained RBAC permissions checked at both API gateways and domain service layers.",
                            "Implement strict parameterization to eliminate all injection vectors (SQL, NoSQL, command injection).",
                        ],
                    ),
                    PlaybookSection(
                        heading="Performance, Caching & Scalability Engine",
                        focus="Sub-100ms Latency & Asynchronous Queues",
                        directives=[
                            "Incorporate distributed in-memory caching (Redis) for hot read paths with automated invalidation strategies.",
                            "Offload long-running operations (email triggers, sync jobs) to asynchronous worker queues.",
                        ],
                    ),
                    PlaybookSection(
                        heading="Automated Testing & Observability Strategy",
                        focus="Test Pyramid & Distributed Tracing",
                        directives=[
                            "Mandate high-coverage unit test suites, integration tests, and concurrency stress benchmarks.",
                            "Inject structured JSON logging, Prometheus metrics, and OpenTelemetry distributed tracing context.",
                        ],
                    ),
                    PlaybookSection(
                        heading="Production Deployment, DevOps & Infrastructure as Code",
                        focus="Containerization & CI/CD Pipelines",
                        directives=[
                            "Provide hardened multi-stage Dockerfiles and production Docker Compose / Kubernetes manifests.",
                            "Formulate automated CI/CD pipelines with linting, security scanning, and zero-downtime rolling deploys.",
                        ],
                    ),
                ],
            )

        # 2. Marketing Playbook
        if any(w in domain_lower for w in ["marketing", "advertising", "growth", "brand"]):
            return DomainPlaybook(
                domain_name=domain,
                philosophy="Customer psychology first: Understand audience pain points, forge emotional resonance, articulate irresistible USPs, and engineer frictionless conversion funnels.",
                core_dimensions=["Audience", "Emotion", "Positioning", "Conversion", "Attribution"],
                decision_priorities=["Trust", "Emotion", "Conversion", "Brand Value"],
                sections=[
                    PlaybookSection(
                        heading="Target Audience Persona & Demographic Segmentation",
                        focus="Psychographic Triggers & Buyer Persona",
                        directives=[
                            f"Detail core demographic attributes, latent frustrations, and emotional aspirations for {goal}.",
                            "Map out customer awareness stages from problem-unaware to high-intent evaluation.",
                        ],
                    ),
                    PlaybookSection(
                        heading="Core Value Proposition & Unique Selling Proposition (USP)",
                        focus="Irresistible Competitive Differentiation",
                        directives=[
                            "Crystallize an undeniable value proposition that renders competitor alternatives obsolete.",
                            "Communicate quantifiable business/life outcomes rather than technical feature lists.",
                        ],
                    ),
                    PlaybookSection(
                        heading="Multi-Channel Campaign Messaging & Content Wave Schedule",
                        focus="Omnichannel Narrative Progression",
                        directives=[
                            "Architect sequenced content waves across paid acquisition, organic social, email nurture, and landing pages.",
                            "Draft high-conversion headline variants and hook angles using proven copywriting frameworks (AIDA, PAS).",
                        ],
                    ),
                    PlaybookSection(
                        heading="Visual Creative Direction & Aesthetic Standards",
                        focus="Brand Credibility & Moodboard Cohesion",
                        directives=[
                            "Establish strict art direction for imagery, color psychology, and video storytelling pacing.",
                        ],
                    ),
                    PlaybookSection(
                        heading="High-Conversion CTA Framework, Conversion Funnels & Metrics",
                        focus="Conversion Rate Optimization (CRO) & KPIs",
                        directives=[
                            "Design urgent, value-focused Call-to-Actions (CTAs) with risk-reversal guarantees.",
                            "Track leading and lagging metrics: CAC, LTV, ROAS, and conversion funnel drop-off rates.",
                        ],
                    ),
                ],
            )

        # 3. Education Playbook
        if any(w in domain_lower for w in ["education", "teaching", "programming education", "learning"]):
            return DomainPlaybook(
                domain_name=domain,
                philosophy="Learning outcomes first: Define measurable behavioral objectives, manage cognitive load through progressive scaffolding, reinforce concepts through active coding drills, and evaluate through authentic assessment.",
                core_dimensions=["Objectives", "Curriculum", "Pedagogy", "Exercises", "Assessment", "Retention"],
                decision_priorities=["Understanding", "Practice", "Retention", "Assessment"],
                sections=[
                    PlaybookSection(
                        heading="Pedagogical Learning Outcomes (Bloom's Taxonomy)",
                        focus="Measurable Behavioral Competencies",
                        directives=[
                            f"Formulate specific, measurable learning objectives spanning recall, comprehension, and synthesis for {goal}.",
                            "Ensure students achieve autonomous mastery rather than passive code copying.",
                        ],
                    ),
                    PlaybookSection(
                        heading="Scaffolded Curriculum & Step-by-Step Lesson Roadmap",
                        focus="Progressive Cognitive Scaffolding",
                        directives=[
                            "Sequence concepts logically, introducing concrete mental models before abstract syntax rules.",
                            "Divide complex tasks into bite-sized, non-intimidating learning milestones.",
                        ],
                    ),
                    PlaybookSection(
                        heading="Interactive Lesson Flow & Cognitive Load Management",
                        focus="Working Memory Optimization",
                        directives=[
                            "Execute the 'Explain-Demonstrate-Practice-Reflect' cycle for every module.",
                            "Avoid overwhelming learners with multiple competing abstractions in a single session.",
                        ],
                    ),
                    PlaybookSection(
                        heading="Hands-On Practice Exercises & Step-by-Step Walkthroughs",
                        focus="Active Retrieval & Debugging Drills",
                        directives=[
                            "Provide fully annotated, executable code walkthroughs followed by active student coding exercises.",
                            "Include intentional starter syntax and logic bugs for student diagnostic drills.",
                        ],
                    ),
                    PlaybookSection(
                        heading="Capstone Projects, Formative Assessment & Spaced Revision",
                        focus="Long-Term Retention & Authentic Mastery",
                        directives=[
                            "Conclude units with comprehensive, portfolio-grade capstone application projects.",
                            "Integrate weekly spaced repetition flashcards and formative self-assessment rubrics.",
                        ],
                    ),
                ],
            )

        # 4. Business & Strategy Playbook
        if any(w in domain_lower for w in ["business", "strategy", "finance", "entrepreneurship"]):
            return DomainPlaybook(
                domain_name=domain,
                philosophy="Market opportunity first: Analyze competitive landscape, establish durable economic moats, validate unit economics, and formulate actionable go-to-market strategies.",
                core_dimensions=["Market Opportunity", "Competition", "Unit Economics", "Strategy", "Execution"],
                decision_priorities=["Market Opportunity", "Unit Economics", "Competitive Moat", "Downside Risk"],
                sections=[
                    PlaybookSection(
                        heading="Market Analysis, TAM & Opportunity Sizing",
                        focus="Total Addressable Market & Macro Drivers",
                        directives=[
                            f"Size the Total Addressable Market (TAM), SAM, and SOM for {goal}.",
                            "Identify favorable market tailwinds and unmet consumer demand niches.",
                        ],
                    ),
                    PlaybookSection(
                        heading="Competitive Moat & Strategic Positioning",
                        focus="Defensible Competitive Advantages",
                        directives=[
                            "Map out direct and indirect competitors across price and capability axes.",
                            "Establish defensible moats (network effects, high switching costs, proprietary data).",
                        ],
                    ),
                    PlaybookSection(
                        heading="Unit Economics, Monetization & 3-Year Financial Model",
                        focus="Sustainable Margins & Cash Flow",
                        directives=[
                            "Detail pricing tiers, gross margins, CAC payback periods, and revenue projections.",
                        ],
                    ),
                    PlaybookSection(
                        heading="Go-To-Market (GTM) Strategy & Execution Milestones",
                        focus="Distribution Engine & Phased Rollout",
                        directives=[
                            "Formulate customer acquisition channels and a sequenced 90-day operational execution roadmap.",
                        ],
                    ),
                ],
            )

        # 5. Medical & Clinical Playbook
        if any(w in domain_lower for w in ["health", "medical", "hospital", "clinical"]):
            return DomainPlaybook(
                domain_name=domain,
                philosophy="Patient safety and clinical rigor first: Formulate evidence-based care protocols, ensure comprehensive differential diagnostics, and safeguard protected health information.",
                core_dimensions=["Patient Safety", "Clinical Rigor", "Diagnostic Accuracy", "Compliance", "Safety Thresholds"],
                decision_priorities=["Patient Safety", "Diagnostic Rigor", "Evidence Level", "Treatment Efficacy"],
                sections=[
                    PlaybookSection(
                        heading="Clinical Presentation, Etiology & Patient Context",
                        focus="Pathophysiological Presentation & History",
                        directives=[f"Contextualize clinical presentations and baseline risk markers for {goal}."],
                    ),
                    PlaybookSection(
                        heading="Diagnostic Workup & Differential Diagnosis (DDx)",
                        focus="Evidence-Based Clinical Workup",
                        directives=["Construct an acuity-ranked differential diagnosis matrix to systematically rule out mimics."],
                    ),
                    PlaybookSection(
                        heading="Evidence-Based Treatment Protocols & Interventions",
                        focus="Guideline-Adherent Therapy",
                        directives=["Formulate validated first-line and second-line pharmacotherapeutic and surgical pathways."],
                    ),
                    PlaybookSection(
                        heading="Contraindications, Drug Interactions & Patient Follow-up",
                        focus="Patient Safety Safeguards",
                        directives=["Document absolute contraindications, interaction red flags, and emergency care thresholds."],
                    ),
                ],
            )

        # 6. Autonomous Temporary Playbook Synthesis for Unknown / Emerging Domains
        logger.info("Synthesizing dynamic Temporary Playbook for novel domain: '%s'", domain)
        return DomainPlaybook(
            domain_name=domain,
            philosophy=f"Empirical domain rigor first: Deconstruct {domain} theoretical models, establish operational benchmarks, and deliver immediately actionable specifications for {goal}.",
            core_dimensions=["Foundational Principles", "Technical Specifications", "Quality Benchmarks", "Risk Governance"],
            decision_priorities=["Clarity", "Feasibility", "Rigor", "Value Delivery"],
            is_temporary_synthesis=True,
            sections=[
                PlaybookSection(
                    heading=f"{domain} Foundational Topology & Strategic Framework",
                    focus="Core Theoretical and Architectural Models",
                    directives=[
                        f"Deconstruct {goal} into foundational axioms, operational paradigms, and domain workflows.",
                        f"Account for dependencies and interactions among {ent_str}.",
                    ],
                ),
                PlaybookSection(
                    heading=f"Core Operational Deliverables & Execution Specs",
                    focus="Concrete Functional Standards",
                    directives=[
                        f"Formulate rigorous implementation standards and technical specifications for {goal}.",
                        "Ensure comprehensive coverage of all operational parameters with zero ambiguity.",
                    ],
                ),
                PlaybookSection(
                    heading=f"Quality Assurance, Failure Modes & Risk Governance",
                    focus="Verification Protocols & Safety Boundaries",
                    directives=[
                        f"Identify edge-case failure modes unique to {domain}.",
                        "Establish quantifiable acceptance tests and automated verification benchmarks.",
                    ],
                ),
                PlaybookSection(
                    heading=f"Lifecycle Governance & Long-Term Scalability Roadmap",
                    focus="Sustainable Maintenance & Horizon Scaling",
                    directives=[
                        f"Provide a phased deployment roadmap and governance strategy for {domain} assets.",
                    ],
                ),
            ],
        )
