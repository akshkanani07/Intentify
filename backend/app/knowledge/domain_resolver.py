"""Domain Intelligence & Resolver Engine – integrates Knowledge Graph ontologies, dense semantic retrieval, and unlimited dynamic domains."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

from app.knowledge.domain_graph import DomainKnowledgeGraph, DomainNode
from app.knowledge.knowledge_manager import KnowledgeManager
from app.nlp.entity_extractor import Entity

logger = logging.getLogger("intentify.knowledge.domain_resolver")


@dataclass
class DomainResult:
    """Resolved domain identification and ontological context."""

    domain: str
    sub_domains: list[str] = field(default_factory=list)
    child_domain: str = ""
    confidence: float = 0.8
    is_dynamic: bool = False
    category: str = "General"
    context_hints: list[str] = field(default_factory=list)
    related_domains: list[str] = field(default_factory=list)
    matched_method: str = "lexical"


class DomainResolver:
    """Classifies user requirements into domains using Knowledge Graph ontologies, semantic embeddings, and dynamic synthesis for unlimited industries."""

    # Multilingual vocabulary mapping to canonical domain categories
    MULTILINGUAL_DOMAIN_INDICATORS: dict[str, list[str]] = {
        "Healthcare": [
            "medical", "medicine", "doctor", "clinical", "hospital", "patient", "diagnosis",
            "therapy", "pharmacy", "cardiology", "oncology", "dawai", "ilaj", "arogya",
            "દવા", "આરોગ્ય", "હોસ્પિટલ", "દર્દી", "તબીબ", "યોગાસન", "આહાર", "વેલનેસ", "યોગ", "માનસિક શાંતિ", "તણાવ", "दवा", "इलाज", "स्वास्थ्य", "चिकित्सा", "रोगी", "अस्पताल", "योगा", "तनाव", "wellness", "diet", "nutrition", "vitals", "clinical trial"
        ],
        "Healthcare Software": [
            "hospital management", "clinical software", "ehr", "emr", "telemedicine", "triage",
            "patient portal", "healthcare app", "medical records", "telehealth", "hipaa", "audit"
        ],
        "Legal": [
            "legal", "law", "attorney", "lawyer", "court", "compliance", "litigation", "contract",
            "statute", "patent", "intellectual property", "kanun", "kanoon", "adalat",
            "કાયદો", "અદાલત", "કાનૂન", "कानून", "अदालत", "मुकदमा", "juridique", "droit"
        ],
        "Agriculture": [
            "agriculture", "farming", "crop", "soil", "harvest", "fertilizer", "agronomy",
            "irrigation", "cultivation", "kheti", "krishi", "khedut", "kisan", "kelp", "biochar",
            "vertical farming", "hydroponic", "soil carbon",
            "ખેતી", "ખેડૂત", "પાક", "खेती", "किसान", "कृषि", "फसल"
        ],
        "Finance": [
            "finance", "financial", "banking", "bank", "investment", "portfolio", "stock",
            "accounting", "tax", "audit", "revenue", "fiscal", "capital", "crypto", "defi",
            "paisa", "vitta", "naana", "નાણાકીય", "वित्त", "निवेश"
        ],
        "Marketing": [
            "marketing", "seo", "branding", "campaign", "social media", "advertising", "audience",
            "growth hacking", "content marketing", "funnel", "conversion", "leads", "pr", "viral", "referral", "growth loop", "reward mechanism",
            "જાહેરાત", "માર્કેટિંગ", "विपणन", "मार्केटिंग", "प्रचार", "mercado"
        ],
        "Business Strategy": [
            "business", "strategy", "expansion", "franchise", "gtm", "go-to-market", "market entry",
            "restaurant", "culinary", "thali", "cafe", "food business", "supply chain", "dairy",
            "textile", "solar farm", "solar", "fleet", "ev fleet", "logistics", "export", "b2b", "d2c",
            "sop manual", "unit economics", "cac", "cold-chain",
            "વેપાર", "ધંધો", "બિઝનેસ", "રેસ્ટોરન્ટ", "ડેરી", "કાપડ", "નિકાસ", "વ્યવસાય", "વ્યૂહરચના",
            "વિસ્તાર", "થાલી", "विस्तार", "व्यवसाय", "रणनीति", "व्यापार", "दुकान", "रेस्टोरेंट", "थाली"
        ],
        "Education": [
            "education", "pedagogy", "curriculum", "teaching", "student", "school", "university",
            "e-learning", "academic", "syllabus", "shikshan", "padhai", "shala",
            "શિક્ષણ", "શાળા", "વિદ્યાર્થી", "શીખવું", "શીખવો", "સીખના", "સીખની", "शिक्षा", "पढ़ाई", "अध्यापन", "सीखना", "सीखनी", "पढ़ना", "जावा", "प्रोग्रामિંગ", "प्रोग्रामिंग", "éducation", "dart", "flutter", "excel", "formulas", "vlookup", "pivot tables", "financial modeling", "learn", "teach", "tutorial", "curriculum", "study"
        ],
        "Travel": [
            "travel", "tourism", "itinerary", "safari", "trip", "vacation", "tour", "hotel", "flight", "sightseeing", "hiking", "eco-tourism",
            "મુસાફરી", "પ્રવાસ", "पर्यटन", "यात्रा", "सफर"
        ],
        "Event Planning & Weddings": [
            "wedding", "marriage", "bride", "groom", "ceremony", "reception", "event planner",
            "banquet", "catering", "mandap", "lagan", "shadi", "vivah", "prasang", "sangeet",
            "haldi", "decor", "udaipur", "destination wedding", "summit", "conference", "convention",
            "gala", "venue", "runway", "high-fashion",
            "લગ્ન", "વિવાહ", "પ્રસંગ", "સંગીત", "મંડપ", "આયોજન", "ઉદયપુર", "અમદાવાદ", "શાહી",
            "શાસ્ત્રોક્ત", "शादी", "विवाह", "समारोह", "संगीत", "मंडप", "सगाई", "हल्दी", "सम्मेलन", "आयोजन"
        ],
        "Engineering": [
            "engineering", "mechanical", "electrical", "civil", "aerospace", "hardware", "cad",
            "thermodynamics", "robotics", "structural", "machinery", "satellite", "orbital", "collision avoidance", "space debris",
            "ઈજનેરી", "મિકેનિકલ", "अभियांत्रिकी", "इंजीनियरिंग"
        ],
        "Science": [
            "science", "physics", "chemistry", "biology", "quantum", "astrophysics", "genetics",
            "molecular", "entanglement", "laboratory", "scientific", "vigyan", "marine", "acoustic sensor",
            "વિજ્ઞાન", "ભૌતિકવિજ્ઞાન", "રસાયણશાસ્ત્ર", "विज्ञान", "भौतिकी", "रसायन"
        ],
        "Arts": [
            "creative", "fiction", "novel", "poetry", "screenplay", "worldbuilding", "character arcs",
            "storytelling", "music", "composition", "illustration", "fine arts", "kalakar", "rachnatmak",
            "કલા", "વાર્તા", "સંગીત", "कला", "कविता", "कहानी", "संगीत"
        ],
        "Design": [
            "design", "dashboard", "ui", "ux", "wireframe", "prototype", "figma", "user interface", "user experience", "design system", "mockup", "interaction design", "visual design",
            "ડીઝાઇન", "ડિઝાઇન", "डिजाइन", "रूपांकन"
        ],
        "Writing": [
            "writing", "writer", "article", "blog", "copywriting", "runbook", "adr", "whitepaper", "documentation", "technical writing", "disaster recovery runbook", "playbook", "specification", "guide",
            "લેખન", "દસ્તાવેજ", "लेखन", "प्रलेखन"
        ],
        "Research": [
            "research", "academic", "literature", "paper", "survey", "synthesis", "rlhf", "post-quantum", "cryptography", "lattice", "nist", "peer-reviewed", "methodology",
            "સંશોધન", "અભ્યાસ", "अनुसंधान", "शोध"
        ],
        "Software Development": [
            "software", "programming", "code", "backend", "frontend", "api", "database",
            "fastapi", "python", "javascript", "react", "docker", "kubernetes", "cloud",
            "microservices", "rest api", "full stack", "devops", "solidity", "node.js", "next.js",
            "c++", "cpp", "netty", "kafka", "postgresql", "postgres", "flink", "telemetry", "iot", "concurrency", "high-concurrency", "event-driven", "pipeline", "multi-tenant", "schema isolation", "row-level security", "distributed", "spring boot", "spring"
        ],
    }

    def __init__(
        self,
        knowledge_manager: KnowledgeManager | None = None,
        domain_graph: DomainKnowledgeGraph | None = None,
    ) -> None:
        self._km = knowledge_manager or KnowledgeManager()
        self._graph = domain_graph or DomainKnowledgeGraph(knowledge_manager=self._km)
        self._semantic_store: Any = None
        self._domain_tree: dict[str, Any] = self._load_domain_tree()

    def _load_domain_tree(self) -> dict[str, Any]:
        import json
        from pathlib import Path
        tree_candidates = [
            Path(__file__).resolve().parents[3] / "knowledge-base" / "taxonomy" / "domain_tree.json",
            Path(__file__).resolve().parents[2] / "knowledge-base" / "taxonomy" / "domain_tree.json",
        ]
        for p in tree_candidates:
            if p.exists():
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception as e:
                    logger.warning("Failed to load domain_tree.json from %s: %s", p, e)
        return {}

    def _get_semantic_store(self) -> Any:
        if self._semantic_store is None:
            from app.knowledge.semantic_store import SemanticKnowledgeStore
            self._semantic_store = SemanticKnowledgeStore(knowledge_manager=self._km)
        return self._semantic_store

    def resolve(self, text: str, entities: list[Entity] | None = None) -> DomainResult:
        """Resolve text into a domain using lexical indicators, entity mapping, knowledge graph, dense semantics, and dynamic synthesis."""
        if not text or not text.strip():
            return DomainResult(
                domain="General",
                sub_domains=["General Strategy", "Operational Best Practices"],
                confidence=0.50,
                is_dynamic=False,
                category="General",
                context_hints=["Maintain universal quality, clarity, and precision."],
                related_domains=[],
                matched_method="fallback",
            )

        text_lower = text.lower().strip()

        # 0. Hierarchical Taxonomy Matching (Step 1 Domain Tree)
        matched_parent: str | None = None
        matched_child: str | None = None
        longest_child_match = 0

        parents_data = self._domain_tree.get("parents", {}) if self._domain_tree else {}
        for p_name, p_val in parents_data.items():
            for c_name, c_val in p_val.get("children", {}).items():
                for trig in c_val.get("triggers", []):
                    t_clean = trig.lower().strip()
                    pattern = r"(?:^|[^\w\u0A80-\u0AFF\u0900-\u097F])" + re.escape(t_clean) + r"(?:[^\w\u0A80-\u0AFF\u0900-\u097F]|$)"
                    if re.search(pattern, text_lower):
                        if len(t_clean) > longest_child_match:
                            longest_child_match = len(t_clean)
                            matched_parent = p_name
                            matched_child = c_name

        # If a specific child specialization matched with high confidence (trigger len >= 4)
        if matched_parent and matched_child and longest_child_match >= 4:
            sub_list = [matched_child, f"{matched_parent} Specialization"]
            return DomainResult(
                domain=matched_parent,
                child_domain=matched_child,
                sub_domains=sub_list,
                confidence=0.96,
                is_dynamic=False,
                category=matched_parent,
                context_hints=[f"Enforce {matched_parent} architecture patterns tailored for {matched_child}."],
                related_domains=[matched_parent],
                matched_method="domain_tree_child",
            )

        # 0. Tier 0: Semantic Specialized Domain Intelligence
        if re.search(r"\b(?:scheduling\s+website|booking\s+(?:website|platform|system)|appointment\s+(?:system|app)|calendar\s+saas)\b", text_lower):
            return DomainResult(
                domain="Scheduling SaaS Platform",
                child_domain="Scheduling & Booking SaaS",
                sub_domains=["Scheduling & Booking SaaS", "Calendar Synchronization", "Multi-Tenant Architecture", "User Authentication & RBAC"],
                confidence=0.96,
                is_dynamic=False,
                category="SaaS Application",
                context_hints=["Design scalable multi-tenant calendar data models", "Implement timezone-aware availability algorithms", "Incorporate automated reminders & webhooks"],
                related_domains=["Web Application Development", "Cloud Architecture", "Database Engineering"],
                matched_method="semantic_specialized",
            )

        if re.search(r"\b(?:hospital\s+management|clinical\s+(?:management|software)|ehr|emr|patient\s+record\s+system)\b", text_lower):
            return DomainResult(
                domain="Healthcare Software",
                sub_domains=["Hospital Workflow Automation", "EHR / EMR Integration", "HIPAA & Clinical Data Security", "Doctor & Patient Portals"],
                confidence=0.96,
                is_dynamic=False,
                category="Healthcare & Clinical Informatics",
                context_hints=["Ensure strict HIPAA / GDPR compliance", "Support HL7 / FHIR data exchange protocols", "Incorporate role-based access control for medical staff"],
                related_domains=["Medical & Healthcare", "Software Engineering", "Cybersecurity"],
                matched_method="semantic_specialized",
            )

        if re.search(r"\b(?:learn\s+python|python\s+curriculum|python\s+tutorial|programming\s+education|coding\s+course)\b", text_lower):
            return DomainResult(
                domain="Programming Education",
                sub_domains=["Python Programming Pedagogy", "Computer Science Foundations", "Hands-On Coding Exercises", "Algorithmic Problem Solving"],
                confidence=0.96,
                is_dynamic=False,
                category="Technical Education",
                context_hints=["Structure modules progressively from syntax to real-world projects", "Provide interactive code examples with error analysis", "Incorporate verification milestones"],
                related_domains=["Education & Pedagogy", "Software Engineering"],
                matched_method="semantic_specialized",
            )

        if re.search(r"\b(?:debug|fix|troubleshoot|diagnose|segfault|deadlock|memory\s+leak|nullpointer\w*|stacktrace|root\s+cause)\b", text_lower):
            return DomainResult(
                domain="Debugging",
                sub_domains=["Root-Cause Diagnostic Analysis", "System Trace Inspection", "Automated Regression Testing", "Defect Isolation & Patch Verification"],
                confidence=0.96,
                is_dynamic=False,
                category="Diagnostic Engineering & RCA",
                context_hints=["Isolate failure mechanism with reproduction test case", "Formulate minimal zero-regression resolution patch"],
                related_domains=["Software Development", "Systems Diagnostics"],
                matched_method="semantic_specialized",
            )

        # 1. Tier 1: Multilingual Domain Indicator Matching (Weighted Best-Match)
        category_scores: dict[str, float] = {}
        for category_name, indicator_kws in self.MULTILINGUAL_DOMAIN_INDICATORS.items():
            for kw in indicator_kws:
                pattern = r"(?:^|[^\w\u0A80-\u0AFF\u0900-\u097F])" + re.escape(kw.lower()) + r"(?:[^\w\u0A80-\u0AFF\u0900-\u097F]|$)"
                hits = len(re.findall(pattern, text_lower))
                if hits > 0:
                    weight = 1.0 + min(2.5, len(kw) / 4.0)
                    category_scores[category_name] = category_scores.get(category_name, 0.0) + hits * weight

        if category_scores:
            best_cat = max(category_scores, key=category_scores.get)
            canonical_domain = best_cat
            if best_cat == "Event Planning & Weddings":
                canonical_domain = "Hospitality & Event Planning"
            elif best_cat == "Business Strategy":
                canonical_domain = "Business & Strategy"

            graph_node = self._graph.get_node(canonical_domain) or self._graph.get_node(best_cat)
            if graph_node:
                related_names = [n.name for n in self._graph.get_related_domains(graph_node.id)]
                return DomainResult(
                    domain=graph_node.name,
                    sub_domains=graph_node.sub_domains,
                    confidence=0.94,
                    is_dynamic=False,
                    category=graph_node.category,
                    context_hints=self._graph.expand_context_hints(graph_node.id),
                    related_domains=related_names,
                    matched_method="lexical",
                )
            if best_cat in self._graph.category_index:
                d_ids = self._graph.category_index[best_cat]
                first_node = self._graph.nodes[d_ids[0]]
                related_names = [n.name for n in self._graph.get_related_domains(first_node.id)]
                return DomainResult(
                    domain=canonical_domain,
                    sub_domains=first_node.sub_domains,
                    confidence=0.92,
                    is_dynamic=False,
                    category=best_cat,
                    context_hints=self._graph.expand_context_hints(first_node.id),
                    related_domains=related_names,
                    matched_method="lexical",
                )
            return DomainResult(
                domain=canonical_domain,
                sub_domains=[f"{canonical_domain} Operations", f"{canonical_domain} Management"],
                confidence=0.92,
                is_dynamic=False,
                category=best_cat,
                context_hints=[f"Adhere to {canonical_domain} best practices and standards."],
                related_domains=[],
                matched_method="lexical",
            )

        # 2. Tier 2: Entity-based Contextual Domain Inference
        if entities:
            for ent in entities:
                ent_lower = ent.text.lower()
                if ent.label == "TECHNOLOGY":
                    if any(w in text_lower for w in ["learn", "teach", "tutorial", "curriculum", "study"]):
                        return DomainResult(
                            domain="Programming Education",
                            sub_domains=["Code Pedagogy", f"{ent.text} Foundations", "Hands-On Exercises"],
                            confidence=0.92,
                            is_dynamic=False,
                            category="Technical Education",
                            context_hints=["Provide structured modules", "Explain syntax step-by-step"],
                            related_domains=["Education", "Software Engineering"],
                            matched_method="entity_context",
                        )
                    if any(w in ent_lower for w in ["kubernetes", "docker", "aws", "azure", "gcp", "terraform"]):
                        return DomainResult(
                            domain="Cloud Computing & DevOps",
                            sub_domains=["Kubernetes Orchestration", "Infrastructure as Code", "CI/CD & Observability"],
                            confidence=0.92,
                            is_dynamic=False,
                            category="Technology & Cloud Infrastructure",
                            context_hints=["Design for high availability and zero-trust", "Automate deployment pipelines"],
                            related_domains=["Distributed Systems", "Site Reliability Engineering"],
                            matched_method="entity_context",
                        )
                    dev_node = self._graph.get_node("Software Development")
                    hints = self._graph.expand_context_hints("Software Development") if dev_node else ["Specify architecture patterns", "Include technology stack"]
                    return DomainResult(
                        domain="Software Development",
                        sub_domains=["Backend", "Cloud Architecture", "System Design"],
                        confidence=0.90,
                        is_dynamic=False,
                        category="Technology",
                        context_hints=hints,
                        related_domains=["DevOps", "Database Administration"],
                        matched_method="entity",
                    )

        # 3. Tier 3: Dense Vector Semantic Search across Catalog Domains
        try:
            store = self._get_semantic_store()
            semantic_matches = store.search_domains(text, top_k=2, min_score=0.45)
            if semantic_matches:
                top = semantic_matches[0]
                d_meta = top.metadata
                node_id = d_meta.get("id", "")
                graph_node = self._graph.get_node(node_id) or self._graph.get_node(top.text)

                sub_domains = graph_node.sub_domains if graph_node else d_meta.get("sub_domains", [])
                category = graph_node.category if graph_node else d_meta.get("category", "General")
                hints = self._graph.expand_context_hints(graph_node.id) if graph_node else d_meta.get("prompt_context_hints", [])
                related_names = [n.name for n in self._graph.get_related_domains(graph_node.id)] if graph_node else []

                return DomainResult(
                    domain=d_meta.get("name", top.text),
                    sub_domains=sub_domains,
                    confidence=round(top.score, 2),
                    is_dynamic=False,
                    category=category,
                    context_hints=hints,
                    related_domains=related_names,
                    matched_method="semantic",
                )
        except Exception as exc:
            logger.debug("Semantic domain retrieval bypassed: %s", exc)

        # 4. Tier 4: Autonomous Dynamic Domain Synthesis for Unlimited & Emerging Industries
        return self._synthesize_dynamic_domain(text)

    def _synthesize_dynamic_domain(self, text: str) -> DomainResult:
        """Autonomously construct an ontological domain profile for novel or emerging industries."""
        lower_text = text.lower()

        # Prioritize core activity archetypes if present
        if re.search(r"\b(?:teach|learn|curriculum|tutorial|study|education)\b", lower_text):
            return DomainResult(
                domain="Programming Education" if any(w in lower_text for w in ["code", "programming", "python", "java", "kotlin", "sql", "postgres", "c++", "rust", "golang"]) else "Education",
                sub_domains=["Pedagogy & Curriculum Design", "Core Foundations", "Hands-on Exercises"],
                confidence=0.90,
                is_dynamic=False,
                category="Education",
                context_hints=["Structure modules progressively", "Include actionable exercises"],
                related_domains=["Education"],
                matched_method="dynamic_intent",
            )
        if re.search(r"\b(?:travel|itinerary|tour|trip|vacation|hiking)\b", lower_text):
            return DomainResult(
                domain="Travel",
                sub_domains=["Itinerary Planning", "Logistics & Transport", "Hospitality Management"],
                confidence=0.90,
                is_dynamic=False,
                category="Travel",
                context_hints=["Provide day-by-day schedules", "Include local logistics"],
                related_domains=["Hospitality & Lifestyle"],
                matched_method="dynamic_intent",
            )
        if re.search(r"\b(?:research|geopolitical|scientific\s+study|literature\s+review)\b", lower_text):
            return DomainResult(
                domain="Research",
                sub_domains=["Methodological Analysis", "Empirical Evaluation", "Literature Synthesis"],
                confidence=0.90,
                is_dynamic=False,
                category="Research",
                context_hints=["Apply rigorous analytical methodology", "Synthesize verified citations"],
                related_domains=["Science", "Strategy"],
                matched_method="dynamic_intent",
            )
        if re.search(r"\b(?:design|ui|ux|wireframe|figma|design\s+system)\b", lower_text):
            return DomainResult(
                domain="Design",
                sub_domains=["Design Systems & Tokens", "Interaction Design", "User Experience Standards"],
                confidence=0.90,
                is_dynamic=False,
                category="Design",
                context_hints=["Enforce accessibility guidelines", "Specify typography and color hierarchy"],
                related_domains=["Frontend Development", "Creative"],
                matched_method="dynamic_intent",
            )
        if re.search(r"\b(?:whitepaper|author|draft|screenplay|essay|documentation)\b", lower_text):
            return DomainResult(
                domain="Writing",
                sub_domains=["Technical Documentation", "Editorial Review", "Content Strategy"],
                confidence=0.90,
                is_dynamic=False,
                category="Writing",
                context_hints=["Ensure clear voice and logical argumentation", "Adhere to publication guidelines"],
                related_domains=["Creative", "Communications"],
                matched_method="dynamic_intent",
            )
        if re.search(r"\b(?:legal|ip|msa|contract|patent|licensing|intellectual\s+property)\b", lower_text):
            return DomainResult(
                domain="Legal",
                sub_domains=["Contractual Architecture", "Intellectual Property Governance", "Regulatory Compliance"],
                confidence=0.90,
                is_dynamic=False,
                category="Legal",
                context_hints=["Draft unambiguous covenants", "Specify governing jurisdiction"],
                related_domains=["Corporate Governance", "Compliance"],
                matched_method="dynamic_intent",
            )

        # Extract prominent capitalized noun phrases or multi-letter domain tokens
        significant_words = re.findall(r"\b[A-Z][a-zA-Z\-]{3,}\b|\b[a-zA-Z\-]{5,}\b", text)
        stop_words = {
            "please", "prompt", "master", "detailed", "expert", "generate", "create", "provide",
            "write", "about", "teach", "learn", "study", "plan", "build", "design", "analyze",
            "develop", "investigate", "diagnose", "formulate", "coordinate", "establish",
            "architect", "implement", "organize"
        }
        filtered = [w for w in significant_words if w.lower() not in stop_words]

        if len(filtered) >= 2:
            primary_domain = f"{filtered[0].title()} {filtered[1].title()}"
        elif filtered:
            primary_domain = f"{filtered[0].title()} Strategy"
        else:
            primary_domain = "Strategic Domain"

        sub_domains = [
            f"Core {primary_domain} Frameworks & Methodologies",
            f"{primary_domain} Operational Execution & Compliance",
            f"Risk Mitigation, Edge Cases & Verification in {primary_domain}",
        ]
        context_hints = [
            f"Maintain strict alignment with industry-standard benchmarks in {primary_domain}.",
            f"Account for specialized edge cases, regulations, and execution risks relevant to {primary_domain}.",
            f"Ensure all recommendations are actionable, modular, and verifiable by {primary_domain} practitioners.",
        ]

        # Register in live knowledge graph
        dynamic_node = self._graph.register_dynamic_domain(
            name=primary_domain,
            category="Emerging / Specialized Industry",
            sub_domains=sub_domains,
            context_hints=context_hints,
        )

        return DomainResult(
            domain=dynamic_node.name,
            sub_domains=dynamic_node.sub_domains,
            confidence=0.75,
            is_dynamic=True,
            category=dynamic_node.category,
            context_hints=context_hints,
            related_domains=[],
            matched_method="dynamic",
        )
