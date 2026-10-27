"""Application settings singleton with caching."""

from __future__ import annotations

from functools import lru_cache

from app.core.config import Settings


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached application-wide Settings instance.

    The first call reads from environment / ``.env``; subsequent calls
    return the same object without re-parsing.
    """
    return Settings()
