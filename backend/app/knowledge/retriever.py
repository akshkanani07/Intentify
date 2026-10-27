"""KnowledgeRetriever – Semantic vector retrieval over knowledge base chunks adhering to S4."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.ml.embeddings import EmbeddingEngine, VectorStore

logger = logging.getLogger("intentify.knowledge.retriever")


@dataclass
class RetrievedChunk:
    chunk_id: str
    content: str
    domain: str
    child_domain: str
    source: str  # concept_graph | taxonomy | standard | blueprint | contract | generated
    reviewed: bool
    score: float = 0.0


class KnowledgeRetriever:
    """FAISS-compatible dense vector retriever over knowledge base chunks."""

    def __init__(self, kb_dir: Path | str | None = None) -> None:
        if kb_dir is None:
            base = Path(__file__).resolve()
            for _ in range(5):
                base = base.parent
                cand = base / "knowledge-base"
                if cand.exists():
                    kb_dir = cand
                    break
            if kb_dir is None:
                kb_dir = Path("knowledge-base")

        self.kb_dir = Path(kb_dir)
        self.embedding_engine = EmbeddingEngine(dimension=384)
        self.vector_store = VectorStore(dimension=384)
        self.chunks: dict[str, RetrievedChunk] = {}
        self._build_index()

    def _build_index(self) -> None:
        """Harvest knowledge chunks across all KB assets and build the local vector index."""
        if not self.kb_dir.exists():
            logger.warning("Knowledge base dir %s does not exist", self.kb_dir)
            return

        texts: list[str] = []
        metas: list[dict[str, Any]] = []

        # 1. Concept Graphs
        cg_dir = self.kb_dir / "concept_graphs"
        if cg_dir.exists():
            for p in cg_dir.glob("*.json"):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    subject = data.get("subject", p.stem)
                    domain = data.get("domain", "General")
                    child_domain = data.get("child_domain", "")
                    reviewed = data.get("reviewed", False)
                    source = data.get("source", "concept_graph")

                    # Extract topics as a chunk
                    topics = data.get("topics", [])
                    topic_text = f"Subject: {subject}. Domain: {domain}. " + " ".join(
                        f"Topic: {t.get('title', '')} - {t.get('objective', '')}" for t in topics[:5]
                    )
                    chunk_id = f"cg_{p.stem}"
                    chunk = RetrievedChunk(
                        chunk_id=chunk_id,
                        content=topic_text,
                        domain=domain,
                        child_domain=child_domain,
                        source="concept_graph" if reviewed else "drafted",
                        reviewed=reviewed,
                    )
                    self.chunks[chunk_id] = chunk
                    texts.append(topic_text)
                    metas.append({"chunk_id": chunk_id})
                except Exception as e:
                    logger.debug("Error reading concept graph %s: %s", p, e)

        # 2. Taxonomy / Domain Tree
        tree_path = self.kb_dir / "taxonomy" / "domain_tree.json"
        if tree_path.exists():
            try:
                with open(tree_path, "r", encoding="utf-8") as f:
                    tree_data = json.load(f)
                parents = tree_data.get("parents", {})
                for parent_name, p_info in parents.items():
                    children = p_info.get("children", {})
                    child_names = list(children.keys())
                    tax_text = f"Taxonomy Domain: {parent_name}. Child Specializations: {', '.join(child_names)}."
                    chunk_id = f"tax_{parent_name.lower().replace(' ', '_')}"
                    chunk = RetrievedChunk(
                        chunk_id=chunk_id,
                        content=tax_text,
                        domain=parent_name,
                        child_domain="",
                        source="taxonomy",
                        reviewed=True,
                    )
                    self.chunks[chunk_id] = chunk
                    texts.append(tax_text)
                    metas.append({"chunk_id": chunk_id})
            except Exception as e:
                logger.debug("Error reading domain tree: %s", e)

        # 3. Standards
        std_dir = self.kb_dir / "standards"
        if std_dir.exists():
            for p in std_dir.glob("*.json"):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    name = data.get("name", p.stem)
                    domain = data.get("domain", "General")
                    rules = data.get("rules", [])
                    std_text = f"Standard: {name}. Domain: {domain}. " + " ".join(r.get("rule", "") for r in rules[:3])
                    chunk_id = f"std_{p.stem}"
                    chunk = RetrievedChunk(
                        chunk_id=chunk_id,
                        content=std_text,
                        domain=domain,
                        child_domain="",
                        source="standard",
                        reviewed=True,
                    )
                    self.chunks[chunk_id] = chunk
                    texts.append(std_text)
                    metas.append({"chunk_id": chunk_id})
                except Exception as e:
                    logger.debug("Error reading standard %s: %s", p, e)

        # Embed and index all chunks in vector store
        if texts:
            embeddings = self.embedding_engine.encode(texts)
            self.vector_store.add_batch(texts, embeddings, metas)
            logger.info("Indexed %d knowledge base chunks in vector store", len(texts))

    def retrieve(self, query: str, domain: str | None = None, top_k: int = 4) -> list[RetrievedChunk]:
        """Retrieve top-k relevant knowledge chunks, optionally boosting chunks from target domain."""
        if not self.chunks or len(self.vector_store) == 0:
            return []

        q_vec = self.embedding_engine.encode_single(query)
        results = self.vector_store.search(q_vec, top_k=top_k * 2)

        retrieved: list[RetrievedChunk] = []
        for r in results:
            cid = r.metadata.get("chunk_id", "")
            if cid in self.chunks:
                base_chunk = self.chunks[cid]
                # Domain alignment boost
                score = r.score
                if domain and base_chunk.domain.lower() == domain.lower():
                    score += 0.25
                retrieved.append(
                    RetrievedChunk(
                        chunk_id=base_chunk.chunk_id,
                        content=base_chunk.content,
                        domain=base_chunk.domain,
                        child_domain=base_chunk.child_domain,
                        source=base_chunk.source,
                        reviewed=base_chunk.reviewed,
                        score=round(score, 4),
                    )
                )

        retrieved.sort(key=lambda x: x.score, reverse=True)
        return retrieved[:top_k]

    def compute_content_share(self, chunks: list[RetrievedChunk]) -> dict[str, float]:
        """Compute proportion of reviewed, unreviewed, and generated content."""
        if not chunks:
            return {"reviewed": 0.0, "unreviewed": 0.0, "generated": 100.0}

        total_len = sum(len(c.content) for c in chunks)
        if total_len == 0:
            return {"reviewed": 0.0, "unreviewed": 0.0, "generated": 100.0}

        reviewed_len = sum(len(c.content) for c in chunks if c.reviewed)
        unreviewed_len = sum(len(c.content) for c in chunks if not c.reviewed and c.source != "generated")
        generated_len = sum(len(c.content) for c in chunks if c.source == "generated")

        return {
            "reviewed": round((reviewed_len / total_len) * 100.0, 1),
            "unreviewed": round((unreviewed_len / total_len) * 100.0, 1),
            "generated": round((generated_len / total_len) * 100.0, 1),
        }
