"""Application settings management using pydantic-settings."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "Intentify"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    API_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # ── Database ─────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://intentify:intentify@localhost:5432/intentify"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # ── Redis ────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600

    # ── CORS ─────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]
    ALLOWED_HOSTS: list[str] = ["*"]

    # ── File Paths ───────────────────────────────────────────────
    KNOWLEDGE_BASE_DIR: str = "c:/intentify/knowledge-base"
    MODEL_DIR: str = "c:/intentify/ml-engine/models"
    LOG_DIR: str = "logs"

    # ── ML Models ────────────────────────────────────────────────
    EMBEDDING_MODEL_NAME: str = "multilingual-e5-small"
    INTENT_MODEL_PATH: str = "models/intent_classifier"
    DOMAIN_MODEL_PATH: str = "models/domain_classifier"
    ROLE_MODEL_PATH: str = "models/role_classifier"
    FASTTEXT_MODEL_PATH: str = "models/lid.176.bin"
    ENABLE_LOCAL_INSTRUCTION_MODEL: bool = False
    LOCAL_INSTRUCTION_MODEL_NAME: str = "google/flan-t5-small"

    # ── Quality ──────────────────────────────────────────────────
    QUALITY_THRESHOLD: float = 85.0
    QUALITY_SCORE_THRESHOLD: float = 85.0
    MAX_AUTO_IMPROVE_ITERATIONS: int = 3

    # ── Logging ──────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "plain"

    # ── Celery ───────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            import json
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        if isinstance(v, list):
            return v
        return ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
