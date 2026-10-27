"""Entity Relationship Engine – Extracts explicit and ontological domain entities and relationships."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

from app.nlp.entity_extractor import Entity, EntityExtractor

logger = logging.getLogger("intentify.nlp.entity_relationship_engine")


@dataclass
class EntityRelationshipResult:
    """Entities and structural domain relationships."""

    entities: list[Entity]
    entity_names: list[str]
    domain_entities: list[str] = field(default_factory=list)
    relationships: list[str] = field(default_factory=list)


class EntityRelationshipEngine:
    """Understands core domain entities and architectural relationships from user intent."""

    # Curated domain entity ontologies
    DOMAIN_ONTOLOGY_ENTITIES: list[tuple[re.Pattern[str], list[str], list[str]]] = [
        (
            re.compile(r"\b(?:scheduling\s+website|booking|appointment|calendar\s+(?:app|system))\b", re.IGNORECASE),
            [
                "User",
                "Appointment",
                "Calendar",
                "Availability",
                "Event",
                "Notification",
                "Payment",
                "Authentication",
            ],
            [
                "User manages Availability slots across Calendar",
                "User schedules Appointment linked to specific Event",
                "System dispatches automated Notification upon Confirmation",
                "Authentication protects User profile and Payment ledger",
            ],
        ),
        (
            re.compile(r"\b(?:learn\s+python|python\s+curriculum|python\s+tutorial|programming\s+education)\b", re.IGNORECASE),
            [
                "Python Syntax",
                "Variables & Data Types",
                "Control Flow",
                "Functions & Scope",
                "Data Structures (Lists, Dictionaries)",
                "Object-Oriented Programming (OOP)",
                "Error Handling & Exceptions",
                "Standard Libraries & Virtual Environments",
            ],
            [
                "Variables and Data Types feed into Control Flow statements",
                "Functions encapsulate Data Structures for modular programming",
                "OOP classes model real-world concepts with Error Handling",
            ],
        ),
        (
            re.compile(r"\b(?:hospital\s+management|clinical\s+system|ehr|emr)\b", re.IGNORECASE),
            [
                "Patient Records",
                "Doctor & Clinician Profiles",
                "Appointment Schedules",
                "EHR / Clinical Notes",
                "Prescription & Pharmacy",
                "Billing & Insurance Claims",
                "Bed & Ward Allocation",
                "HIPAA Audit Logs",
            ],
            [
                "Patient Records associate with Doctor Profiles through Appointment Schedules",
                "EHR Clinical Notes generate Prescription orders in Pharmacy",
                "Bed Allocation connects with Billing and Insurance Claims under HIPAA auditing",
            ],
        ),
        (
            re.compile(r"\b(?:kubernetes|k8s|zero-trust|multi-region|cloud\s+architecture)\b", re.IGNORECASE),
            [
                "Kubernetes Cluster",
                "Mutual TLS (mTLS)",
                "Ingress Controller",
                "Control Plane",
                "Worker Nodes",
                "GitOps Pipeline",
                "Telemetry & Metrics",
                "Failover Mechanism",
            ],
            [
                "Ingress Controller enforces Mutual TLS for service communication",
                "Control Plane coordinates Worker Nodes across multi-region environments",
                "GitOps Pipeline manages cluster state with automated Failover",
            ],
        ),
        (
            re.compile(r"\b(?:wedding|event\s+coordination|ceremony\s+plan)\b", re.IGNORECASE),
            [
                "Guest Registry",
                "Venue & Banquet Hall",
                "Ceremony Timeline",
                "Catering & Menu",
                "Decor & Audio-Visual",
                "Vendor Contracts",
                "Budget Ledger",
                "VIP Hospitality Protocol",
            ],
            [
                "Guest Registry informs Venue capacity and Catering portions",
                "Ceremony Timeline orchestrates Decor and Vendor Contracts",
                "Budget Ledger monitors VIP Hospitality and overall expenditures",
            ],
        ),
    ]

    def __init__(self, base_extractor: EntityExtractor | None = None) -> None:
        self._base = base_extractor or EntityExtractor()

    def analyze(self, text: str, domain: str = "") -> EntityRelationshipResult:
        """Extracts both explicit textual entities and implied domain relational entities."""
        # 1. Base explicit entity extraction
        explicit_entities = self._base.extract(text)
        explicit_names = [e.text for e in explicit_entities]

        # 2. Match ontological domain entities
        lower_text = text.lower()
        domain_entities: list[str] = []
        relationships: list[str] = []

        for pattern, entities, rels in self.DOMAIN_ONTOLOGY_ENTITIES:
            if pattern.search(lower_text):
                domain_entities = entities
                relationships = rels
                break

        # 3. If domain entities matched, add them as domain entity records if not already in explicit list
        final_entities = list(explicit_entities)
        seen_texts = {e.text.lower() for e in final_entities}

        for d_ent in domain_entities:
            if d_ent.lower() not in seen_texts:
                final_entities.append(Entity(text=d_ent, label="DOMAIN_ENTITY", start=0, end=len(d_ent)))
                seen_texts.add(d_ent.lower())
                explicit_names.append(d_ent)

        return EntityRelationshipResult(
            entities=final_entities,
            entity_names=explicit_names,
            domain_entities=domain_entities,
            relationships=relationships,
        )
