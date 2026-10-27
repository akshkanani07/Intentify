"""Learning Memory Engine – Layer 12 of Intentify AI v4.

Remembers:
- Successful blueprints & prompt structures
- High-scoring domain patterns and architectural recipes
- User preferences across tone, format, and language
- Evolving feedback for future generation self-improvement
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from app.ml.embeddings import EmbeddingEngine

logger = logging.getLogger("intentify.learning.memory")


@dataclass
class PromptSuccessMemory:
    id: str
    goal: str
    domain: str
    intent: str
    aligned_role: str
    blueprint_type: str
    quality_score: float
    sections: list[str]
    smart_assumptions: list[str] = field(default_factory=list)
    timestamp: float = 0.0


@dataclass
class DomainPatternRecord:
    domain: str
    frequent_entities: list[str] = field(default_factory=list)
    effective_sections: list[str] = field(default_factory=list)
    average_quality: float = 95.0
    usage_count: int = 1


class LearningMemoryEngine:
    """In-memory and persistent vector memory storing successful prompt patterns and domain intelligence."""

    def __init__(
        self,
        storage_path: str | Path = "ml-engine/memory/learning_store.json",
        embedder: EmbeddingEngine | None = None,
    ) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._embedder = embedder or EmbeddingEngine()
        self.memories: list[PromptSuccessMemory] = []
        self.domain_patterns: dict[str, DomainPatternRecord] = {}
        self._load()

    def record_success(
        self,
        goal: str,
        domain: str,
        intent: str,
        aligned_role: str,
        blueprint_type: str,
        quality_score: float,
        sections: list[str],
        smart_assumptions: list[str] | None = None,
    ) -> PromptSuccessMemory:
        """Store a high-quality prompt execution in memory for future reference."""
        import time

        mem_id = f"mem_{len(self.memories) + 1:05d}"
        rec = PromptSuccessMemory(
            id=mem_id,
            goal=goal,
            domain=domain,
            intent=intent,
            aligned_role=aligned_role,
            blueprint_type=blueprint_type,
            quality_score=round(quality_score, 2),
            sections=sections,
            smart_assumptions=smart_assumptions or [],
            timestamp=time.time(),
        )
        self.memories.append(rec)

        # Update domain patterns
        d_lower = domain.lower()
        if d_lower not in self.domain_patterns:
            self.domain_patterns[d_lower] = DomainPatternRecord(
                domain=domain,
                effective_sections=sections[:7],
                average_quality=quality_score,
                usage_count=1,
            )
        else:
            pat = self.domain_patterns[d_lower]
            pat.usage_count += 1
            pat.average_quality = round((pat.average_quality * 0.8) + (quality_score * 0.2), 2)
            for s in sections:
                if s not in pat.effective_sections:
                    pat.effective_sections.append(s)

        logger.info("LearningMemory recorded success for '%s' (score=%.1f)", domain, quality_score)
        self._persist()
        return rec

    def record_domain_usage(
        self,
        domain: str,
        entities: list[str] | None = None,
        sections: list[str] | None = None,
        score: float = 95.0,
    ) -> None:
        """Record domain usage, frequent entities, and effective sections."""
        d_lower = domain.lower()
        entities = entities or []
        sections = sections or []
        if d_lower not in self.domain_patterns:
            self.domain_patterns[d_lower] = DomainPatternRecord(
                domain=domain,
                frequent_entities=entities[:10],
                effective_sections=sections[:7],
                average_quality=score,
                usage_count=1,
            )
        else:
            pat = self.domain_patterns[d_lower]
            pat.usage_count += 1
            for e in entities:
                if e not in pat.frequent_entities:
                    pat.frequent_entities.append(e)
            for s in sections:
                if s not in pat.effective_sections:
                    pat.effective_sections.append(s)
        self._persist()

    def retrieve_similar_patterns(self, query_text: str, domain: str, top_k: int = 2) -> list[PromptSuccessMemory]:
        """Find past high-scoring prompt blueprints for similar tasks."""
        if not self.memories:
            return []

        # Filter by domain first if available
        matched = [m for m in self.memories if m.domain.lower() == domain.lower()]
        if not matched:
            matched = self.memories

        # Rank by score and recency
        matched.sort(key=lambda x: (x.quality_score, x.timestamp), reverse=True)
        return matched[:top_k]

    def get_learned_domain_insights(self, domain: str) -> DomainPatternRecord | None:
        """Fetch accumulated domain patterns."""
        d_lower = domain.lower()
        if d_lower in self.domain_patterns:
            return self.domain_patterns[d_lower]
        for k, pat in self.domain_patterns.items():
            if k in d_lower or d_lower in k:
                return pat
        return None

    def _persist(self) -> None:
        try:
            payload = {
                "memories": [asdict(m) for m in self.memories[-500:]],  # keep last 500
                "domain_patterns": {k: asdict(v) for k, v in self.domain_patterns.items()},
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception as exc:
            logger.debug("Failed saving learning memory: %s", exc)

    def _load(self) -> None:
        if not self.storage_path.exists():
            # Seed foundational enterprise recipes
            self.record_success(
                goal="Build a production-grade scheduling website with automated calendar synchronization",
                domain="Scheduling SaaS Platform",
                intent="create",
                aligned_role="Senior Full Stack SaaS Architect",
                blueprint_type="Technical Architecture",
                quality_score=100.0,
                sections=[
                    "System Architecture & Component Topology",
                    "API Specifications & Endpoint Contract",
                    "Database Schema, Relationships & Data Integrity",
                    "Security Architecture & RBAC",
                    "Performance Optimization & Caching",
                    "Automated Testing & Observability",
                    "Production Deployment & CI/CD",
                ],
                smart_assumptions=[
                    "All scheduling events default to UTC internally with local client timezone rendering",
                    "Database defaults to PostgreSQL with optimistic locking to prevent double-booking",
                ],
            )
            return

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.memories = [PromptSuccessMemory(**m) for m in data.get("memories", [])]
            self.domain_patterns = {
                k: DomainPatternRecord(**v) for k, v in data.get("domain_patterns", {}).items()
            }
            logger.info("Loaded %d learning memories across %d domains", len(self.memories), len(self.domain_patterns))
        except Exception as exc:
            logger.debug("Failed loading learning memory: %s", exc)
