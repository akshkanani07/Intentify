"""Knowledge Graph for domain ontologies, hierarchical categorization, and relational traversal."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from app.knowledge.knowledge_manager import KnowledgeManager

logger = logging.getLogger("intentify.knowledge.domain_graph")


@dataclass
class DomainNode:
    """A node in the domain knowledge graph."""

    id: str
    name: str
    category: str
    sub_domains: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    related_domain_ids: list[str] = field(default_factory=list)
    typical_roles: list[str] = field(default_factory=list)
    prompt_context_hints: list[str] = field(default_factory=list)
    is_dynamic: bool = False


class DomainKnowledgeGraph:
    """In-memory bidirectional knowledge graph representing domain taxonomy, relationships, and traversal."""

    def __init__(self, knowledge_manager: KnowledgeManager | None = None) -> None:
        self._km = knowledge_manager or KnowledgeManager()
        self.nodes: dict[str, DomainNode] = {}
        self.name_to_id: dict[str, str] = {}
        self.category_index: dict[str, list[str]] = {}
        self.subdomain_to_domain: dict[str, str] = {}
        self.role_to_domains: dict[str, list[str]] = {}
        self._build_graph()

    def _build_graph(self) -> None:
        """Construct knowledge graph from domains and roles catalog."""
        raw_domains = self._km.get_domains()

        for d in raw_domains:
            d_id = d.get("id", f"domain_{len(self.nodes) + 1:03d}")
            name = d.get("name", "Unknown Domain")
            category = d.get("category", "General")
            sub_domains = d.get("sub_domains", [])
            keywords = d.get("keywords", [])
            related_ids = d.get("related_domains", [])
            typical_roles = d.get("typical_roles", [])
            hints = d.get("prompt_context_hints", [])

            node = DomainNode(
                id=d_id,
                name=name,
                category=category,
                sub_domains=sub_domains,
                keywords=keywords,
                related_domain_ids=related_ids,
                typical_roles=typical_roles,
                prompt_context_hints=hints,
                is_dynamic=False,
            )

            self.nodes[d_id] = node
            self.name_to_id[name.lower()] = d_id

            # Category index
            if category not in self.category_index:
                self.category_index[category] = []
            self.category_index[category].append(d_id)

            # Subdomain mapping
            for sub in sub_domains:
                self.subdomain_to_domain[sub.lower()] = d_id

            # Role associations
            for role_id in typical_roles:
                if role_id not in self.role_to_domains:
                    self.role_to_domains[role_id] = []
                self.role_to_domains[role_id].append(d_id)

        logger.info(
            "DomainKnowledgeGraph built with %d domain nodes across %d categories",
            len(self.nodes),
            len(self.category_index),
        )

    def get_node(self, identifier: str) -> DomainNode | None:
        """Lookup node by ID or case-insensitive name."""
        if identifier in self.nodes:
            return self.nodes[identifier]
        ident_lower = identifier.lower().strip()
        if ident_lower in self.name_to_id:
            return self.nodes[self.name_to_id[ident_lower]]
        return None

    def get_related_domains(self, identifier: str) -> list[DomainNode]:
        """Retrieve neighboring domains connected via related_domains edges."""
        node = self.get_node(identifier)
        if not node:
            return []

        neighbors: list[DomainNode] = []
        for rel_id in node.related_domain_ids:
            if rel_id in self.nodes:
                neighbors.append(self.nodes[rel_id])
        return neighbors

    def get_category_siblings(self, identifier: str) -> list[DomainNode]:
        """Retrieve sibling domains sharing the same category."""
        node = self.get_node(identifier)
        if not node or node.category not in self.category_index:
            return []

        siblings: list[DomainNode] = []
        for d_id in self.category_index[node.category]:
            if d_id != node.id and d_id in self.nodes:
                siblings.append(self.nodes[d_id])
        return siblings

    def expand_context_hints(self, identifier: str) -> list[str]:
        """Aggregate prompt context hints from the node, its category siblings, and related domains."""
        node = self.get_node(identifier)
        if not node:
            return ["Maintain rigorous domain-standard methodologies."]

        hints: set[str] = set(node.prompt_context_hints)

        # Include hints from related domains
        for rel in self.get_related_domains(identifier)[:2]:
            for h in rel.prompt_context_hints:
                hints.add(h)

        return list(hints)

    def register_dynamic_domain(
        self,
        name: str,
        category: str = "Emerging / Specialized Industry",
        sub_domains: list[str] | None = None,
        context_hints: list[str] | None = None,
    ) -> DomainNode:
        """Dynamically add an emerging/novel domain node to the live knowledge graph."""
        clean_name = name.strip().title()
        d_id = f"dynamic_domain_{len(self.nodes) + 1:04d}"

        subs = sub_domains or [f"{clean_name} Principles", f"{clean_name} Execution"]
        hints = context_hints or [
            f"Adhere strictly to verified {clean_name} professional benchmarks",
            f"Address specialized domain edge cases and safety requirements in {clean_name}",
        ]

        node = DomainNode(
            id=d_id,
            name=clean_name,
            category=category,
            sub_domains=subs,
            keywords=[w.lower() for w in clean_name.split() if len(w) > 3],
            related_domain_ids=[],
            typical_roles=[],
            prompt_context_hints=hints,
            is_dynamic=True,
        )

        self.nodes[d_id] = node
        self.name_to_id[clean_name.lower()] = d_id

        if category not in self.category_index:
            self.category_index[category] = []
        self.category_index[category].append(d_id)

        for sub in subs:
            self.subdomain_to_domain[sub.lower()] = d_id

        logger.info("Registered dynamic domain in knowledge graph: '%s' (ID: %s)", clean_name, d_id)
        return node
