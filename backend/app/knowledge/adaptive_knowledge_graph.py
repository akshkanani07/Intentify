"""Adaptive Knowledge Graph Engine – Layer 3 of Intentify AI v4.

Multi-hop semantic knowledge graph representing:
Role -> Skills -> Domain -> Sub Domain -> Entities -> Relationships -> Requirements -> Constraints -> Blueprints -> Examples
Supports dynamic runtime node learning and traversal.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from app.knowledge.knowledge_manager import KnowledgeManager

logger = logging.getLogger("intentify.knowledge.adaptive_graph")


@dataclass
class GraphEntity:
    id: str
    name: str
    entity_type: str
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphRelationship:
    source_id: str
    relation: str  # HAS, REQUIRES, CONSTRAINED_BY, IMPLEMENTS, MAPS_TO
    target_id: str
    weight: float = 1.0


@dataclass
class DomainOntologyRecord:
    domain_name: str
    category: str
    sub_domains: list[str] = field(default_factory=list)
    roles: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    relationships: list[dict[str, str]] = field(default_factory=list)
    requirements: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    best_practices: list[str] = field(default_factory=list)
    common_mistakes: list[str] = field(default_factory=list)
    industry_standards: list[str] = field(default_factory=list)


class AdaptiveKnowledgeGraph:
    """Dynamic, evolving in-memory knowledge graph supporting multi-hop traversal and runtime learning."""

    def __init__(self, knowledge_manager: KnowledgeManager | None = None) -> None:
        self._km = knowledge_manager or KnowledgeManager()
        self.entities: dict[str, GraphEntity] = {}
        self.relationships: list[GraphRelationship] = []
        self.domain_ontologies: dict[str, DomainOntologyRecord] = {}
        self._initialize_core_graph()

    def _initialize_core_graph(self) -> None:
        """Seed graph from knowledge catalog and canonical domain relationships."""
        raw_domains = self._km.get_domains()
        for d in raw_domains:
            name = d.get("name", "")
            cat = d.get("category", "General")
            subs = d.get("sub_domains", [])
            roles = d.get("typical_roles", [])
            hints = d.get("prompt_context_hints", [])

            rec = DomainOntologyRecord(
                domain_name=name,
                category=cat,
                sub_domains=subs,
                roles=roles,
                requirements=hints,
            )
            self.domain_ontologies[name.lower()] = rec

        # Enrich canonical domain relation sets
        self._seed_canonical_subgraph(
            domain="Scheduling SaaS Platform",
            category="SaaS Application",
            sub_domains=["Scheduling & Booking SaaS", "Calendar Synchronization", "Multi-Tenant Architecture"],
            roles=["Senior Full Stack SaaS Architect", "Cloud Systems Architect"],
            skills=["Distributed Locking", "CalDAV Protocol", "Timezone Calculation", "RBAC Security"],
            entities=["Calendar", "Booking", "Availability", "Timezone", "Notification", "Payment", "Authentication"],
            relationships=[
                {"source": "Scheduling SaaS", "relation": "HAS", "target": "Calendar"},
                {"source": "Scheduling SaaS", "relation": "HAS", "target": "Booking Engine"},
                {"source": "Scheduling SaaS", "relation": "HAS", "target": "Availability Algorithm"},
                {"source": "Scheduling SaaS", "relation": "HAS", "target": "Timezone Handler"},
                {"source": "Scheduling SaaS", "relation": "HAS", "target": "Notification Queue"},
                {"source": "Scheduling SaaS", "relation": "HAS", "target": "Payment Gateway"},
                {"source": "Scheduling SaaS", "relation": "HAS", "target": "Authentication & RBAC"},
                {"source": "Booking Engine", "relation": "REQUIRES", "target": "Pessimistic/Optimistic Concurrency Lock"},
                {"source": "Calendar", "relation": "REQUIRES", "target": "Two-Way CalDAV Sync"},
            ],
            requirements=[
                "Store all booking timestamps in UTC with client-side local conversion",
                "Prevent race conditions and double-booking using atomic database transactions",
                "Implement asynchronous transactional notification webhooks",
            ],
            constraints=[
                "Zero double-booking tolerance under high concurrent load",
                "Row-level security tenant isolation must be enforced",
            ],
            best_practices=["Idempotent booking tokens", "Buffer times between slots", "Webhook signature verification"],
            common_mistakes=["Naive local datetime storage", "Unindexed availability queries", "Synchronous third-party calendar calls"],
            industry_standards=["RFC 5545 (iCalendar)", "OAuth 2.0 / OpenID Connect", "ISO 8601 UTC"],
        )

        self._seed_canonical_subgraph(
            domain="Programming Education",
            category="Technical Education",
            sub_domains=["Python Programming Pedagogy", "Computer Science Foundations", "Hands-On Exercises"],
            roles=["Python Instructor", "Computer Science Professor"],
            skills=["Instructional Scaffolding", "Bloom's Taxonomy", "Cognitive Load Management", "Interactive Debugging"],
            entities=["Learning Objectives", "Curriculum", "Mental Models", "Code Walkthroughs", "Practice Drills", "Quizzes", "Capstone"],
            relationships=[
                {"source": "Programming Education", "relation": "HAS", "target": "Learning Objectives"},
                {"source": "Programming Education", "relation": "HAS", "target": "Scaffolded Curriculum"},
                {"source": "Programming Education", "relation": "HAS", "target": "Practice Drills"},
                {"source": "Learning Objectives", "relation": "REQUIRES", "target": "Bloom's Revised Taxonomy"},
                {"source": "Curriculum", "relation": "CONSTRAINED_BY", "target": "Working Memory Limits"},
            ],
            requirements=[
                "Progressive difficulty curve introducing one core abstraction per lesson",
                "Interactive hands-on coding drills accompanied by intentional error analysis",
            ],
            constraints=[
                "Avoid overwhelming learners with complex syntax tricks prematurely",
                "Define all technical jargon immediately upon first introduction",
            ],
            best_practices=["Explain-Demonstrate-Practice-Reflect cycle", "Memory visualization diagrams"],
            common_mistakes=["Lecturing without active coding", "Skipping fundamental error triage"],
            industry_standards=["Bloom's Taxonomy", "PEP 8", "Constructivist Learning Theory"],
        )

        self._seed_canonical_subgraph(
            domain="Healthcare Software",
            category="Healthcare Technology",
            sub_domains=["Hospital Workflow Automation", "EHR / EMR Integration", "Clinical Data Security"],
            roles=["Healthcare Technology Architect", "Clinical Informatics Specialist"],
            skills=["HL7/FHIR Standards", "HIPAA Compliance", "Clinical Triage Informatics", "Audit Trails"],
            entities=["Patient Records", "Clinical Triage", "EHR Integration", "Doctor Portal", "Audit Logs", "Security Layer"],
            relationships=[
                {"source": "Healthcare Software", "relation": "HAS", "target": "Patient Records"},
                {"source": "Healthcare Software", "relation": "HAS", "target": "Clinical Triage"},
                {"source": "Healthcare Software", "relation": "HAS", "target": "EHR Integration"},
                {"source": "Patient Records", "relation": "CONSTRAINED_BY", "target": "HIPAA Privacy Rule"},
                {"source": "EHR Integration", "relation": "IMPLEMENTS", "target": "HL7 FHIR Release 4"},
            ],
            requirements=[
                "Strict end-to-end encryption for all Protected Health Information (PHI)",
                "Tamper-evident append-only clinical audit logging",
            ],
            constraints=[
                "Never diagnose or prescribe without mandatory clinician verification warnings",
                "High availability architecture with zero single-point-of-failure",
            ],
            best_practices=["Role-based least privilege access", "FHIR JSON schemas", "Deterministic triage alert routing"],
            common_mistakes=["Storing unencrypted PHI in logs", "Unverified external drug interaction models"],
            industry_standards=["HIPAA Title II", "HL7 FHIR R4", "HITECH Act", "DICOM"],
        )

    def _seed_canonical_subgraph(
        self,
        domain: str,
        category: str,
        sub_domains: list[str],
        roles: list[str],
        skills: list[str],
        entities: list[str],
        relationships: list[dict[str, str]],
        requirements: list[str],
        constraints: list[str],
        best_practices: list[str],
        common_mistakes: list[str],
        industry_standards: list[str],
    ) -> None:
        rec = DomainOntologyRecord(
            domain_name=domain,
            category=category,
            sub_domains=sub_domains,
            roles=roles,
            skills=skills,
            entities=entities,
            relationships=relationships,
            requirements=requirements,
            constraints=constraints,
            best_practices=best_practices,
            common_mistakes=common_mistakes,
            industry_standards=industry_standards,
        )
        self.domain_ontologies[domain.lower()] = rec

        # Register entities and relationships
        for e in entities:
            e_id = f"ent_{len(self.entities) + 1:04d}"
            self.entities[e.lower()] = GraphEntity(id=e_id, name=e, entity_type="DOMAIN_CONCEPT")

        for r in relationships:
            self.relationships.append(
                GraphRelationship(
                    source_id=r["source"],
                    relation=r["relation"],
                    target_id=r["target"],
                )
            )

    def query_domain(self, domain_name: str) -> DomainOntologyRecord | None:
        """Retrieve full ontology record by exact or partial domain match."""
        name_lower = domain_name.lower().strip()
        if name_lower in self.domain_ontologies:
            return self.domain_ontologies[name_lower]

        for k, rec in self.domain_ontologies.items():
            if k in name_lower or name_lower in k:
                return rec

        return None

    def get_related_entities(self, domain_name: str) -> list[str]:
        """Fetch all entities connected to this domain."""
        rec = self.query_domain(domain_name)
        if rec and rec.entities:
            return rec.entities

        # Fallback traversal
        related = []
        for r in self.relationships:
            if domain_name.lower() in r.source_id.lower():
                related.append(r.target_id)
        return related

    def dynamic_learn_concept(
        self,
        domain: str,
        new_entities: list[str],
        category: str = "Emerging / Specialized",
    ) -> DomainOntologyRecord:
        """Dynamically expand the knowledge graph with newly observed concepts and entities."""
        name_key = domain.lower().strip()
        if name_key in self.domain_ontologies:
            rec = self.domain_ontologies[name_key]
        else:
            rec = DomainOntologyRecord(
                domain_name=domain,
                category=category,
                sub_domains=[f"{domain} Core", f"{domain} Applied"],
                entities=list(new_entities),
                requirements=[f"Adhere to rigorous {domain} specifications"],
                constraints=[f"Ensure complete operational reliability in {domain}"],
            )
            self.domain_ontologies[name_key] = rec

        for e in new_entities:
            if e not in rec.entities:
                rec.entities.append(e)

        logger.info("AdaptiveKnowledgeGraph learned %d entities for domain '%s'", len(new_entities), domain)
        return rec
