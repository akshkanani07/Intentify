"""Autonomous Local Embedding Engine with subword n-gram hashing and dense semantic projections."""

from __future__ import annotations

import hashlib
import logging
import math
import re
from dataclasses import dataclass, field
from typing import Any
import numpy as np

logger = logging.getLogger("intentify.ml.embeddings")


@dataclass
class SearchResult:
    """Standardized semantic search result item."""

    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)
    index: int = -1


class VectorStore:
    """High-performance in-memory vector index with matrix cosine similarity."""

    def __init__(self, dimension: int = 384) -> None:
        self.dimension = dimension
        self.documents: list[str] = []
        self.metadata: list[dict[str, Any]] = []
        self.matrix: np.ndarray | None = None

    def add(self, text: str, vector: np.ndarray, meta: dict[str, Any] | None = None) -> None:
        """Add a single vector and its metadata to the store."""
        vec = vector.reshape(1, -1).astype(np.float32)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm

        self.documents.append(text)
        self.metadata.append(meta or {})

        if self.matrix is None:
            self.matrix = vec
        else:
            self.matrix = np.vstack([self.matrix, vec])

    def add_batch(self, texts: list[str], vectors: np.ndarray, metadata: list[dict[str, Any]] | None = None) -> None:
        """Batch add vectors to the matrix."""
        if len(texts) == 0:
            return

        vecs = vectors.astype(np.float32)
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normalized_vecs = vecs / norms

        self.documents.extend(texts)
        if metadata:
            self.metadata.extend(metadata)
        else:
            self.metadata.extend([{} for _ in texts])

        if self.matrix is None:
            self.matrix = normalized_vecs
        else:
            self.matrix = np.vstack([self.matrix, normalized_vecs])

    def search(self, query_vector: np.ndarray, top_k: int = 5, min_score: float = -1.0) -> list[SearchResult]:
        """Compute cosine similarity against all stored vectors via dot product."""
        if self.matrix is None or len(self.documents) == 0:
            return []

        q_vec = query_vector.flatten().astype(np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        # Matrix-vector dot product computes all cosine similarities simultaneously
        scores = np.dot(self.matrix, q_vec)

        # Retrieve top-k indices
        k = min(top_k, len(scores))
        if k == 0:
            return []

        ranked_indices = np.argsort(scores)[::-1][:k]

        results: list[SearchResult] = []
        for idx in ranked_indices:
            score = float(scores[idx])
            if score >= min_score:
                results.append(
                    SearchResult(
                        text=self.documents[idx],
                        score=round(score, 4),
                        metadata=self.metadata[idx],
                        index=int(idx),
                    )
                )
        return results

    def __len__(self) -> int:
        return len(self.documents)


class EmbeddingEngine:
    """Local, offline embedding engine supporting subword n-grams, semantic subspaces, and cosine projections."""

    # Curated semantic concept clusters mapped to reserved subspace dimensions
    SEMANTIC_CLUSTERS: dict[str, list[str]] = {
        "software": [
            "code", "programming", "developer", "software", "api", "rest", "backend", "frontend",
            "database", "fastapi", "python", "javascript", "react", "docker", "kubernetes", "git",
            "microservices", "sql", "postgres", "redis", "architecture", "endpoint", "server", "app"
        ],
        "wedding_events": [
            "wedding", "planner", "marriage", "bride", "groom", "ceremony", "reception", "catering",
            "banquet", "decor", "event", "hospitality", "venue", "guest", "lagan", "mandap", "timeline"
        ],
        "medical": [
            "doctor", "patient", "clinical", "hospital", "medicine", "health", "diagnosis", "therapy",
            "disease", "pharmacy", "treatment", "physician", "nurse", "surgery", "diet", "nutrition"
        ],
        "legal": [
            "lawyer", "attorney", "legal", "contract", "court", "compliance", "litigation", "counsel",
            "clause", "statute", "jurisdiction", "liability", "agreement", "intellectual", "patent"
        ],
        "finance": [
            "finance", "bank", "investment", "portfolio", "stock", "accounting", "tax", "audit",
            "revenue", "profit", "capital", "budget", "fiscal", "valuation", "fund", "crypto", "defi"
        ],
        "marketing": [
            "marketing", "seo", "campaign", "social", "brand", "advertising", "audience", "growth",
            "conversion", "funnel", "content", "leads", "cac", "roi", "customer", "analytics"
        ],
        "education": [
            "teacher", "student", "curriculum", "learning", "academic", "school", "university",
            "lesson", "pedagogy", "course", "education", "tutorial", "instruction", "exam"
        ],
        "engineering": [
            "mechanical", "electrical", "civil", "aerospace", "hardware", "circuit", "robotics",
            "structural", "manufacturing", "cad", "sensor", "motor", "stress", "tolerance"
        ],
    }

    # Stopwords with down-weighted contribution
    STOP_WORDS = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
        "by", "from", "up", "about", "into", "over", "after", "is", "are", "was", "were",
        "be", "been", "being", "have", "has", "had", "do", "does", "did", "can", "could",
        "will", "would", "shall", "should", "may", "might", "must", "that", "this", "these",
        "those", "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them"
    }

    def __init__(self, model_name: str = "multilingual-e5-small", dimension: int = 384) -> None:
        self.model_name = model_name
        self.dimension = dimension
        self._local_weights = None

    def _hash_token(self, token: str, seed: int = 0) -> int:
        """Stable cross-platform deterministic 32-bit hash."""
        data = f"{seed}:{token}".encode("utf-8")
        digest = hashlib.md5(data).digest()
        val = int.from_bytes(digest[:4], byteorder="big", signed=False)
        return val % self.dimension

    def encode_single(self, text: str) -> np.ndarray:
        """Compute 384-dimensional dense semantic embedding for a single text."""
        vec = np.zeros(self.dimension, dtype=np.float32)
        if not text or not text.strip():
            return vec

        clean = text.lower().strip()
        words = re.findall(r"\b\w+\b", clean)

        if not words:
            # Fallback for symbols or pure non-word characters
            for idx, ch in enumerate(clean):
                h = self._hash_token(ch, seed=idx)
                vec[h] += 1.0
            norm = np.linalg.norm(vec)
            return vec / norm if norm > 0 else vec

        # 1. Word unigrams with position & stopword weighting
        for idx, word in enumerate(words):
            weight = 0.3 if word in self.STOP_WORDS else 1.0
            position_decay = 1.0 / (1.0 + 0.03 * idx)
            effective_weight = weight * position_decay

            h1 = self._hash_token(word, seed=42)
            h2 = self._hash_token(word, seed=137)
            vec[h1] += effective_weight * 1.5
            vec[h2] += effective_weight * 0.75

            # 2. Subword character n-grams (3-grams, 4-grams) for morphology & transliteration
            if len(word) >= 4:
                # Trigrams
                for i in range(len(word) - 2):
                    tri = word[i:i + 3]
                    ht = self._hash_token(tri, seed=79)
                    vec[ht] += effective_weight * 0.4
                # Quadgrams
                for i in range(len(word) - 3):
                    quad = word[i:i + 4]
                    hq = self._hash_token(quad, seed=99)
                    vec[hq] += effective_weight * 0.6

        # 3. Dense Semantic Subspace Projection (boost dimensions for related concept clusters)
        words_set = set(words)
        for cluster_idx, (cluster_name, cluster_vocab) in enumerate(self.SEMANTIC_CLUSTERS.items()):
            # Check cluster overlap
            hits = len(words_set.intersection(cluster_vocab))
            if hits > 0:
                cluster_boost = math.log1p(hits) * 2.0
                # Activate cluster-specific coordinate block
                base_dim = (cluster_idx * 30) % (self.dimension - 30)
                for d in range(base_dim, base_dim + 25):
                    vec[d] += cluster_boost * (1.0 / (1.0 + 0.1 * (d - base_dim)))

        # 4. Global L2 Normalization (norm = 1.0)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm

        return vec.astype(np.float32)

    def encode(self, texts: list[str] | str, normalize: bool = True) -> np.ndarray:
        """Batch compute dense embedding matrix (N, 384)."""
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return np.zeros((0, self.dimension), dtype=np.float32)

        vectors = [self.encode_single(t) for t in texts]
        mat = np.array(vectors, dtype=np.float32)

        if normalize:
            norms = np.linalg.norm(mat, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            mat = mat / norms

        return mat

    def similarity(self, text1: str, text2: str) -> float:
        """Compute exact cosine similarity between two texts in range [-1.0, 1.0]."""
        v1 = self.encode_single(text1)
        v2 = self.encode_single(text2)
        sim = float(np.dot(v1, v2))
        return max(-1.0, min(1.0, round(sim, 4)))

    def batch_similarity(self, query: str, candidates: list[str]) -> np.ndarray:
        """Compute cosine similarities of query against all candidates."""
        if not candidates:
            return np.array([], dtype=np.float32)
        q_vec = self.encode_single(query)
        cand_mat = self.encode(candidates)
        return np.dot(cand_mat, q_vec)

    def find_nearest(
        self,
        query: str,
        candidates: list[str],
        top_k: int = 5,
    ) -> list[tuple[str, float]]:
        """Rank candidate strings by cosine similarity to query."""
        if not candidates:
            return []

        scores = self.batch_similarity(query, candidates)
        k = min(top_k, len(candidates))
        ranked_indices = np.argsort(scores)[::-1][:k]

        return [(candidates[i], float(scores[i])) for i in ranked_indices]

    def create_vector_store(self) -> VectorStore:
        """Instantiate an empty vector store configured for this engine."""
        return VectorStore(dimension=self.dimension)

    def embed_text(self, text: str) -> np.ndarray:
        """Alias for encode_single."""
        return self.encode_single(text)


DenseSemanticEmbeddingEngine = EmbeddingEngine

