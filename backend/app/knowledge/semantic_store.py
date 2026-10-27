"""Semantic Knowledge Store – pre-indexed vector stores for roles, domains, blueprints, and templates."""

from __future__ import annotations

import logging
from typing import Any

from app.knowledge.knowledge_manager import KnowledgeManager
from app.ml.embeddings import EmbeddingEngine, SearchResult, VectorStore

logger = logging.getLogger("intentify.knowledge.semantic_store")


class SemanticKnowledgeStore:
    """Indexes knowledge base artifacts into dense vector stores for sub-millisecond semantic retrieval."""

    _instance: SemanticKnowledgeStore | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> SemanticKnowledgeStore:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._is_indexed = False
        return cls._instance

    def __init__(
        self,
        knowledge_manager: KnowledgeManager | None = None,
        embedding_engine: EmbeddingEngine | None = None,
    ) -> None:
        if getattr(self, "_is_indexed", False):
            return

        self._km = knowledge_manager or KnowledgeManager()
        self._engine = embedding_engine or EmbeddingEngine()

        self.role_store = VectorStore(dimension=self._engine.dimension)
        self.domain_store = VectorStore(dimension=self._engine.dimension)
        self.blueprint_store = VectorStore(dimension=self._engine.dimension)
        self.template_store = VectorStore(dimension=self._engine.dimension)

        self._build_indices()
        self._is_indexed = True

    def _build_indices(self) -> None:
        """Pre-compute dense embeddings for all knowledge base records."""
        # 1. Index Roles
        roles = self._km.get_roles()
        for r in roles:
            title = r.get("title", "")
            category = r.get("category", "")
            aliases = " ".join(r.get("aliases", []))
            expertise = " ".join(r.get("expertise_areas", []))
            keywords = " ".join(r.get("keywords", []))

            # Rich composite representation for semantic search
            doc = f"{title} {aliases} {category} {expertise} {keywords}"
            vec = self._engine.encode_single(doc)
            self.role_store.add(text=title, vector=vec, meta=r)

        # 2. Index Domains
        domains = self._km.get_domains()
        for d in domains:
            name = d.get("name", "")
            category = d.get("category", "")
            sub_domains = " ".join(d.get("sub_domains", []))
            keywords = " ".join(d.get("keywords", []))
            hints = " ".join(d.get("prompt_context_hints", []))

            doc = f"{name} {category} {sub_domains} {keywords} {hints}"
            vec = self._engine.encode_single(doc)
            self.domain_store.add(text=name, vector=vec, meta=d)

        # 3. Index Blueprints
        blueprints = self._km.get_blueprints()
        for bp in blueprints:
            intent = bp.get("intent", "")
            name = bp.get("name", "")
            desc = bp.get("description", "")
            examples = " ".join(bp.get("example_prompts", []))

            doc = f"{intent} {name} {desc} {examples}"
            vec = self._engine.encode_single(doc)
            self.blueprint_store.add(text=intent, vector=vec, meta=bp)

        # 4. Index Output Formats / Templates
        templates = self._km.get_templates()
        for tpl in templates:
            name = tpl.get("name", "")
            desc = tpl.get("description", "")
            intents = " ".join(tpl.get("suitable_intents", []))
            domains_list = " ".join(tpl.get("suitable_domains", []))

            doc = f"{name} {desc} {intents} {domains_list}"
            vec = self._engine.encode_single(doc)
            self.template_store.add(text=name, vector=vec, meta=tpl)

        logger.info(
            "Semantic store indexed: %d roles, %d domains, %d blueprints, %d templates",
            len(self.role_store),
            len(self.domain_store),
            len(self.blueprint_store),
            len(self.template_store),
        )

    def search_roles(self, query: str, top_k: int = 5, min_score: float = 0.15) -> list[SearchResult]:
        """Perform semantic similarity search across indexed professional roles."""
        q_vec = self._engine.encode_single(query)
        return self.role_store.search(q_vec, top_k=top_k, min_score=min_score)

    def search_domains(self, query: str, top_k: int = 5, min_score: float = 0.15) -> list[SearchResult]:
        """Perform semantic similarity search across indexed industry domains."""
        q_vec = self._engine.encode_single(query)
        return self.domain_store.search(q_vec, top_k=top_k, min_score=min_score)

    def search_blueprints(self, query: str, top_k: int = 3) -> list[SearchResult]:
        """Find the most semantically relevant intent blueprint for a query."""
        q_vec = self._engine.encode_single(query)
        return self.blueprint_store.search(q_vec, top_k=top_k)

    def search_templates(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """Find the most fitting output format templates for a task description."""
        q_vec = self._engine.encode_single(query)
        return self.template_store.search(q_vec, top_k=top_k)
