"""High-level prompt service with caching and metrics."""

from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass, field

from app.api.v1.schemas.prompt import PromptGenerationRequest, PromptGenerationResponse
from app.services.orchestrator import PromptOrchestrator

logger = logging.getLogger("intentify.services.prompt_service")


@dataclass
class _CacheEntry:
    """In-memory cache entry for generated prompts."""

    response: PromptGenerationResponse
    created_at: float
    ttl: float = 3600.0

    @property
    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > self.ttl


@dataclass
class _Metrics:
    """Simple in-process metrics collector."""

    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_processing_ms: float = 0.0
    error_count: int = 0
    quality_scores: list[float] = field(default_factory=list)

    @property
    def avg_processing_ms(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.total_processing_ms / self.total_requests

    @property
    def avg_quality_score(self) -> float:
        if not self.quality_scores:
            return 0.0
        return sum(self.quality_scores) / len(self.quality_scores)

    @property
    def cache_hit_rate(self) -> float:
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return self.cache_hits / total

    def to_dict(self) -> dict[str, float | int]:
        return {
            "total_requests": self.total_requests,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": round(self.cache_hit_rate, 4),
            "avg_processing_ms": round(self.avg_processing_ms, 2),
            "avg_quality_score": round(self.avg_quality_score, 2),
            "error_count": self.error_count,
        }


class PromptService:
    """Wraps ``PromptOrchestrator`` with caching and lightweight metrics."""

    def __init__(
        self,
        orchestrator: PromptOrchestrator | None = None,
        cache_ttl: float = 3600.0,
        max_cache_size: int = 500,
    ) -> None:
        self._orchestrator = orchestrator or PromptOrchestrator()
        self._cache: dict[str, _CacheEntry] = {}
        self._cache_ttl = cache_ttl
        self._max_cache_size = max_cache_size
        self._metrics = _Metrics()

    # ── Public API ───────────────────────────────────────────────

    async def generate(self, request: PromptGenerationRequest) -> PromptGenerationResponse:
        """Generate a prompt, returning a cached result when possible."""
        self._metrics.total_requests += 1
        cache_key = self._build_cache_key(request)

        # Check cache
        entry = self._cache.get(cache_key)
        if entry is not None and not entry.is_expired:
            self._metrics.cache_hits += 1
            logger.debug("Cache hit for key=%s", cache_key[:12])
            return entry.response

        self._metrics.cache_misses += 1

        try:
            start = time.perf_counter()
            response = await self._orchestrator.generate_prompt(request)
            elapsed_ms = (time.perf_counter() - start) * 1000.0

            self._metrics.total_processing_ms += elapsed_ms
            self._metrics.quality_scores.append(response.quality_score)

            # Evict oldest entries if cache is full
            self._evict_if_needed()

            self._cache[cache_key] = _CacheEntry(
                response=response,
                created_at=time.time(),
                ttl=self._cache_ttl,
            )

            return response

        except Exception:
            self._metrics.error_count += 1
            raise

    def get_metrics(self) -> dict[str, float | int]:
        """Return current metrics snapshot."""
        return self._metrics.to_dict()

    def clear_cache(self) -> int:
        """Flush the in-memory cache and return the number of evicted entries."""
        count = len(self._cache)
        self._cache.clear()
        logger.info("Cache cleared, evicted %d entries", count)
        return count

    # ── Private helpers ──────────────────────────────────────────

    @staticmethod
    def _build_cache_key(request: PromptGenerationRequest) -> str:
        raw = f"{request.role}|{request.detail}|{request.language}|{request.tone}|{request.format}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def _evict_if_needed(self) -> None:
        if len(self._cache) < self._max_cache_size:
            return

        # Remove expired first
        expired_keys = [k for k, v in self._cache.items() if v.is_expired]
        for k in expired_keys:
            del self._cache[k]

        # If still over limit, remove oldest entries
        while len(self._cache) >= self._max_cache_size:
            oldest_key = min(self._cache, key=lambda k: self._cache[k].created_at)
            del self._cache[oldest_key]
