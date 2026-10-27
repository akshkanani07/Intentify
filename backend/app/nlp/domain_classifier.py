"""Domain Classifier module – provides domain intelligence and classification interface."""

from __future__ import annotations

from app.knowledge.domain_graph import DomainKnowledgeGraph, DomainNode
from app.knowledge.domain_resolver import DomainResolver, DomainResult

# DomainClassifier provides domain classification and ontology routing
DomainClassifier = DomainResolver

__all__ = ["DomainClassifier", "DomainResolver", "DomainResult", "DomainKnowledgeGraph", "DomainNode"]
