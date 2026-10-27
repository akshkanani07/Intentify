"""BlueprintSelector – selects the optimal prompt blueprint for any intent, domain, and role."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from app.knowledge.knowledge_manager import KnowledgeManager

logger = logging.getLogger("intentify.compiler.blueprint_selector")


@dataclass
class Blueprint:
    """A prompt blueprint template describing how a prompt should be structured."""

    name: str
    intent: str
    domain: str
    description: str = ""
    steps: list[str] = field(default_factory=list)
    requirements: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    quality_focus: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


# ── Built-in blueprints for all 13 core operational intents ─────────────────

_BUILTIN_BLUEPRINTS: list[Blueprint] = [
    Blueprint(
        name="code_generation",
        intent="create",
        domain="software_engineering",
        description="Production blueprint for building, coding, and engineering new assets from scratch",
        steps=[
            "Deconstruct functional and non-functional specifications thoroughly",
            "Architect the core system topology, schemas, and design patterns",
            "Implement production-grade, typed, and idiomatic code with error handling",
            "Address edge cases, concurrency, security boundaries, and resilience",
            "Provide end-to-end execution verification, tests, and deployment commands",
        ],
        requirements=[
            "Include complete type annotations, docstrings, and architectural rationale",
            "Adhere strictly to modern production standards and Clean Architecture",
            "Handle exceptions defensively with informative error responses",
        ],
        constraints=[
            "Never use deprecated APIs, insecure libraries, or mock placeholders",
            "Ensure full standalone runnability with zero missing dependencies",
        ],
        quality_focus=["specificity", "constraints", "output_format"],
        tags=["create", "build", "code", "engineering", "development"],
    ),
    Blueprint(
        name="content_writing",
        intent="write",
        domain="content",
        description="Blueprint for composing authoritative prose, documentation, and stakeholder communications",
        steps=[
            "Define the core audience persona, register, and strategic purpose",
            "Formulate an outline with logical narrative progressions and headings",
            "Draft each section with compelling, precise, and articulate prose",
            "Incorporate concrete domain examples, data evidence, and case studies",
            "Review for editorial flow, persuasive impact, and clarity",
        ],
        requirements=[
            "Maintain an authoritative, consistent tone aligned with stakeholder expectations",
            "Structure content with hierarchical headings and digestible paragraphs",
            "Support arguments with empirical domain reasoning",
        ],
        constraints=[
            "Avoid buzzwords, filler phrases, and unsupported assertions",
            "Keep narrative focused, actionable, and free of fluff",
        ],
        quality_focus=["clarity", "context", "output_format"],
        tags=["write", "draft", "content", "communication", "article", "documentation"],
    ),
    Blueprint(
        name="data_synthesis",
        intent="generate",
        domain="data_intelligence",
        description="Blueprint for synthesizing datasets, brainstorming comprehensive taxonomies, and ideation",
        steps=[
            "Establish exact structural schemas, attributes, and data distributions",
            "Brainstorm an exhaustive and diverse catalog of ideas, records, or test cases",
            "Incorporate boundary conditions, rare edge cases, and high-entropy anomalies",
            "Format the generated output into structured tabular or JSON representations",
            "Verify data diversity, realism, and schema compliance",
        ],
        requirements=[
            "Ensure high entropy, statistical realism, and zero trivial repetitions",
            "Include comprehensive coverage of challenging edge cases",
            "Deliver structured, machine-parseable data",
        ],
        constraints=[
            "Do not truncate samples with ellipsis or placeholders",
            "Maintain consistent schema types across all entries",
        ],
        quality_focus=["specificity", "output_format", "clarity"],
        tags=["generate", "synthesize", "brainstorm", "list", "dataset", "ideas"],
    ),
    Blueprint(
        name="strategic_planning",
        intent="plan",
        domain="operations",
        description="Blueprint for formulating multi-phase roadmaps, logistics schedules, and execution timelines",
        steps=[
            "Define strategic milestones, key deliverables, and critical path objectives",
            "Map out phase-by-phase dependencies, resource allocation, and timelines",
            "Identify operational bottlenecks, failure modes, and mitigation contingencies",
            "Formulate cross-stakeholder communication and governance cadences",
            "Establish concrete acceptance gates, checklist items, and monitoring KPIs",
        ],
        requirements=[
            "Include concrete milestone deadlines, deliverables, and resource requirements",
            "Identify potential operational bottlenecks and mitigation strategies",
            "Establish clear ownership, checkpoints, and success metrics",
        ],
        constraints=[
            "Plans must be realistic, operationally feasible, and budget-conscious",
            "Account explicitly for schedule buffers and contingency margins",
        ],
        quality_focus=["specificity", "constraints", "ambiguity_handling"],
        tags=["plan", "roadmap", "strategy", "timeline", "schedule", "event", "wedding"],
    ),
    Blueprint(
        name="deep_analysis",
        intent="analyze",
        domain="research_analytics",
        description="Blueprint for diagnostic audits, telemetry breakdowns, and multi-factor evaluations",
        steps=[
            "Define analytical boundaries, diagnostic hypotheses, and telemetry scope",
            "Dissect raw data, traces, and metrics into constituent components",
            "Apply domain-specific analytical frameworks and statistical evaluations",
            "Isolate anomalies, performance trade-offs, and systemic vulnerabilities",
            "Formulate actionable, prioritized recommendations and remediation paths",
        ],
        requirements=[
            "Substantiate every finding with telemetry, metrics, or factual reasoning",
            "Distinguish clearly between direct correlations and root causes",
            "Provide prioritized, high-leverage recommendations",
        ],
        constraints=[
            "Acknowledge analytical limitations, margin of error, and confidence intervals",
            "Avoid unverified conjecture or subjective assertions",
        ],
        quality_focus=["specificity", "ambiguity_handling", "context"],
        tags=["analyze", "audit", "metrics", "review", "telemetry", "evaluation"],
    ),
    Blueprint(
        name="pedagogical_explanation",
        intent="explain",
        domain="education",
        description="Blueprint for conceptual deconstructions, tutorials, and educational walkthroughs",
        steps=[
            "Introduce the high-level intuition, fundamental motivation, and mental model",
            "Deconstruct underlying mechanics into progressive, logical layers",
            "Provide concrete code, visual analogies, or mathematical demonstrations",
            "Address subtle nuances, common misconceptions, and practical gotchas",
            "Synthesize actionable takeaways and practical self-assessment questions",
        ],
        requirements=[
            "Tailor linguistic complexity to the specified audience persona",
            "Use progressive disclosure: foundational concepts before advanced abstractions",
            "Provide memorable domain analogies and practical examples",
        ],
        constraints=[
            "Never introduce technical jargon without first defining it clearly",
            "Ensure explanations remain rigorous without over-simplification",
        ],
        quality_focus=["clarity", "context", "ambiguity_handling"],
        tags=["explain", "teach", "tutorial", "guide", "concept", "breakdown"],
    ),
    Blueprint(
        name="comparative_evaluation",
        intent="compare",
        domain="architecture",
        description="Blueprint for side-by-side trade-off evaluations, benchmarking, and differential analyses",
        steps=[
            "Define standardized evaluation criteria and weighted decision dimensions",
            "Perform rigorous, unbiased evaluations of each candidate against every criterion",
            "Construct a structured comparison matrix table highlighting differentials",
            "Analyze operational trade-offs, scalability limits, and lifecycle costs",
            "Deliver an authoritative, context-aware verdict and strategic recommendation",
        ],
        requirements=[
            "Evaluate all candidates using identical, objective dimensions",
            "Include explicit pros, cons, and context-dependent trade-offs",
            "Synthesize a clear, justified architectural verdict",
        ],
        constraints=[
            "Maintain strict impartiality; avoid personal preference bias",
            "Address total cost of ownership, maintainability, and lock-in risks",
        ],
        quality_focus=["specificity", "output_format", "ambiguity_handling"],
        tags=["compare", "benchmark", "versus", "tradeoff", "matrix", "evaluation"],
    ),
    Blueprint(
        name="localization_translation",
        intent="translate",
        domain="linguistics",
        description="Blueprint for multilingual translation, localization, and cross-cultural adaptation",
        steps=[
            "Analyze source semantic nuances, idiom register, and cultural context",
            "Translate content faithfully while adapting colloquial expressions naturally",
            "Preserve technical terminology, entity identifiers, and markdown formatting",
            "Validate grammatical fidelity, honorifics, and local cultural norms",
            "Provide bilingual alignment or side-by-side verification review",
        ],
        requirements=[
            "Maintain exact semantic intent while achieving natural native fluency",
            "Preserve all formatting tags, placeholders, and technical terms",
            "Respect cultural context and linguistic register",
        ],
        constraints=[
            "Do not perform literal word-for-word translation where meaning is distorted",
            "Never lose or hallucinate source semantic information",
        ],
        quality_focus=["clarity", "specificity", "output_format"],
        tags=["translate", "localize", "multilingual", "translation", "language"],
    ),
    Blueprint(
        name="scientific_research",
        intent="research",
        domain="science",
        description="Blueprint for state-of-the-art literature exploration and rigorous scientific synthesis",
        steps=[
            "Formulate precise research questions, methodology scopes, and hypotheses",
            "Survey state-of-the-art academic literature and empirical benchmarks",
            "Synthesize theoretical foundations and conflicting experimental paradigms",
            "Analyze open challenges, computational constraints, and future trajectories",
            "Document verified findings with rigorous citations and scientific taxonomy",
        ],
        requirements=[
            "Reference peer-reviewed principles, empirical studies, and SOTA benchmarks",
            "Highlight open research questions and theoretical frontiers",
            "Maintain academic rigor and scientific notation where applicable",
        ],
        constraints=[
            "Differentiate clearly between proven theorems and working hypotheses",
            "Avoid unverified speculation or pseudo-scientific claims",
        ],
        quality_focus=["clarity", "specificity", "context"],
        tags=["research", "investigate", "science", "literature", "sota", "study"],
    ),
    Blueprint(
        name="system_design",
        intent="design",
        domain="software_engineering",
        description="Blueprint for system architecture, schema modeling, and UI/UX wireframing",
        steps=[
            "Deconstruct functional scope, traffic volumes, and performance SLAs",
            "Architect modular component diagrams, data flows, and subsystem interfaces",
            "Specify database schemas, API contracts, and communication protocols",
            "Incorporate fault tolerance, horizontal elasticity, and disaster recovery",
            "Document key architectural decisions, rationale, and alternatives considered",
        ],
        requirements=[
            "Provide concrete schemas, entity relationship models, and interface specs",
            "Design for horizontal scalability, zero-downtime deployments, and telemetry",
            "Document Architectural Decision Records (ADRs) and trade-off rationales",
        ],
        constraints=[
            "Avoid monolithic bottlenecks and single points of failure",
            "Ensure all subsystems are loosely coupled and independently testable",
        ],
        quality_focus=["specificity", "constraints", "context"],
        tags=["design", "architecture", "system", "schema", "ui", "ux", "wireframe"],
    ),
    Blueprint(
        name="triage_debugging",
        intent="debug",
        domain="software_engineering",
        description="Blueprint for root-cause triage, stack-trace troubleshooting, and fault remediation",
        steps=[
            "Analyze the failure symptoms, stack trace, and environmental conditions",
            "Formulate diagnostic hypotheses to isolate the primary root cause",
            "Reproduce the bug mentally or with an isolated minimal test case",
            "Provide the complete, regression-free fix with explanation of mechanism",
            "Implement preventative guardrails, regression unit tests, and telemetry alerts",
        ],
        requirements=[
            "Explain the exact failure mechanism and root cause with precision",
            "Provide complete, tested remediation code without band-aid hacks",
            "Include preventative unit tests and monitoring alerts",
        ],
        constraints=[
            "Never suggest unverified trial-and-error workarounds",
            "Account for backward compatibility and race conditions",
        ],
        quality_focus=["specificity", "clarity", "constraints"],
        tags=["debug", "fix", "troubleshoot", "bug", "crash", "reproduce"],
    ),
    Blueprint(
        name="performance_optimization",
        intent="improve",
        domain="software_engineering",
        description="Blueprint for code refactoring, latency reduction, memory profiling, and scaling",
        steps=[
            "Profile current execution hotspots, memory allocations, and latency bottlenecks",
            "Deconstruct algorithm complexity and isolate suboptimal operations",
            "Implement high-performance refactoring (caching, async, indexing, zero-copy)",
            "Benchmark before vs. after metrics to quantify efficiency gains",
            "Document code clarity, maintainability impacts, and architectural tradeoffs",
        ],
        requirements=[
            "Demonstrate quantifiable complexity and latency reductions",
            "Preserve 100% functional equivalence and backward compatibility",
            "Include before/after benchmark comparisons",
        ],
        constraints=[
            "Do not sacrifice code readability for negligible micro-optimizations",
            "Ensure all edge cases and boundary tests pass without regression",
        ],
        quality_focus=["specificity", "constraints", "clarity"],
        tags=["improve", "optimize", "refactor", "performance", "latency", "scale"],
    ),
    Blueprint(
        name="architectural_decision",
        intent="decide",
        domain="strategy",
        description="Blueprint for strategic technology selection, framework evaluation, and trade-off governance",
        steps=[
            "Establish decision parameters, business objectives, and technical constraints",
            "Enumerate all viable strategic candidates and alternatives",
            "Evaluate operational overhead, talent availability, lock-in, and scalability",
            "Synthesize an authoritative Architectural Decision Record (ADR) with verdict",
            "Outline phased migration, rollback plans, and risk mitigation strategies",
        ],
        requirements=[
            "Deliver an authoritative, definitive recommendation with clear justification",
            "Structure as an Architectural Decision Record (ADR)",
            "Provide concrete transition steps and risk mitigation plans",
        ],
        constraints=[
            "Avoid ambiguous non-committal answers ('it depends' without guidance)",
            "Factor in total cost of ownership and long-term maintainability",
        ],
        quality_focus=["specificity", "ambiguity_handling", "output_format"],
        tags=["decide", "choose", "recommend", "decision", "adr", "selection"],
    ),
]

_GENERIC_BLUEPRINT = Blueprint(
    name="generic_execution",
    intent="create",
    domain="general",
    description="Universal fallback blueprint ensuring comprehensive, structured output",
    steps=[
        "Deconstruct the assignment objective, constraints, and success criteria",
        "Formulate a structured conceptual architecture and execution plan",
        "Deliver the complete solution with exhaustive detail and professional rigor",
        "Verify all edge cases, negative boundaries, and domain standards",
        "Review for total clarity, conciseness, and immediate actionability",
    ],
    requirements=[
        "Deliver an exhaustive, professional, and well-structured response",
        "Ensure accuracy, completeness, and immediate real-world utility",
    ],
    constraints=[
        "Maintain production-grade quality standards throughout",
        "Avoid placeholders, speculative claims, or generic filler",
    ],
    quality_focus=["clarity", "specificity", "output_format"],
    tags=["general", "universal"],
)


class BlueprintSelector:
    """Selects the most appropriate blueprint for a given intent, domain, and role."""

    def __init__(
        self,
        knowledge_manager: KnowledgeManager | None = None,
        extra_blueprints: list[Blueprint] | None = None,
    ) -> None:
        self._km = knowledge_manager or KnowledgeManager()
        self._blueprints: list[Blueprint] = list(_BUILTIN_BLUEPRINTS)
        if extra_blueprints:
            self._blueprints.extend(extra_blueprints)
        self._generic = _GENERIC_BLUEPRINT
        self._load_knowledge_base_blueprints()

    def _load_knowledge_base_blueprints(self) -> None:
        """Enrich registered blueprints with knowledge base configurations."""
        try:
            kb_blueprints = self._km.get_blueprints()
            for kbb in kb_blueprints:
                intent = kbb.get("intent", "").lower()
                name = kbb.get("id", f"kb_{intent}")
                # If blueprint for this intent doesn't exist, create it
                if not any(bp.intent == intent for bp in self._blueprints):
                    self._blueprints.append(
                        Blueprint(
                            name=name,
                            intent=intent,
                            domain="knowledge_base",
                            description=kbb.get("description", ""),
                            steps=[
                                "Understand objectives and requirements",
                                "Architect the solution components",
                                "Execute the solution with domain precision",
                                "Verify constraints and quality benchmarks",
                            ],
                            requirements=kbb.get("fallback_strategies", []),
                            constraints=["Strictly follow knowledge base guidelines"],
                            quality_focus=list(kbb.get("quality_weights", {}).keys()),
                            tags=[intent, "kb"],
                        )
                    )
        except Exception as exc:
            logger.debug("Knowledge base blueprint loading bypassed: %s", exc)

    def select_blueprint(self, intent: str, domain: str, role: str) -> Blueprint:
        """Select best blueprint based on intent, domain, and role matching."""
        intent_l = (intent or "create").lower().strip()
        domain_l = (domain or "general").lower().replace(" ", "_").strip()
        role_l = (role or "").lower()

        # 1. Exact Intent + Domain Match
        for bp in self._blueprints:
            if bp.intent == intent_l and bp.domain == domain_l:
                return bp

        # 2. Intent Match (Primary)
        for bp in self._blueprints:
            if bp.intent == intent_l:
                return bp

        # 3. Domain Match
        for bp in self._blueprints:
            if bp.domain == domain_l:
                return bp

        # 4. Tag Overlap
        search_tokens = {intent_l, domain_l} | set(role_l.split())
        best_bp: Blueprint | None = None
        best_score = 0
        for bp in self._blueprints:
            tag_set = {t.lower() for t in bp.tags}
            overlap = len(search_tokens & tag_set)
            if overlap > best_score:
                best_score = overlap
                best_bp = bp

        if best_bp is not None and best_score > 0:
            return best_bp

        # 5. Fallback
        return self._generic

    def list_blueprints(self) -> list[str]:
        """Return names of all registered blueprints."""
        return [bp.name for bp in self._blueprints]

    def get_blueprint_by_name(self, name: str) -> Blueprint:
        """Retrieve blueprint by exact name."""
        for bp in self._blueprints:
            if bp.name == name:
                return bp
        return self._generic
