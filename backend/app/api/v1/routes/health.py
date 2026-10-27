"""Health check endpoints."""

from __future__ import annotations

import logging
import time
from typing import Any

from fastapi import APIRouter

router = APIRouter()
logger = logging.getLogger("intentify.api.health")

_BOOT_TIME = time.time()


@router.get(
    "",
    summary="Basic health check",
    response_model=dict[str, str],
)
async def health() -> dict[str, str]:
    """Return a simple OK status."""
    return {"status": "healthy"}


@router.get(
    "/detailed",
    summary="Detailed health check",
    response_model=dict[str, Any],
)
async def health_detailed() -> dict[str, Any]:
    """Return detailed health information including uptime and subsystem status."""
    uptime_seconds = time.time() - _BOOT_TIME

    subsystems: dict[str, str] = {}

    # Check knowledge base availability
    try:
        from app.knowledge.knowledge_manager import KnowledgeManager
        km = KnowledgeManager()
        roles = km.get_roles()
        subsystems["knowledge_base"] = "healthy" if roles else "degraded"
    except Exception:
        subsystems["knowledge_base"] = "unavailable"

    # Check NLP pipeline
    try:
        from app.nlp.language_detector import LanguageDetector
        detector = LanguageDetector()
        result = detector.detect("test")
        subsystems["nlp_pipeline"] = "healthy" if result.language else "degraded"
    except Exception:
        subsystems["nlp_pipeline"] = "unavailable"

    # Check ML models
    try:
        from app.ml.model_manager import ModelManager
        mm = ModelManager()
        loaded = mm.list_models()
        subsystems["ml_models"] = "healthy" if loaded is not None else "degraded"
    except Exception:
        subsystems["ml_models"] = "unavailable"

    overall = "healthy"
    if any(v == "unavailable" for v in subsystems.values()):
        overall = "degraded"

    return {
        "status": overall,
        "uptime_seconds": round(uptime_seconds, 2),
        "subsystems": subsystems,
        "version": "0.1.0",
    }
