"""Main v1 API router aggregating health and prompt endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.prompt import router as prompt_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router, prefix="/health", tags=["health"])
api_v1_router.include_router(prompt_router, tags=["prompt"])

# Alias for backwards compatibility
router = api_v1_router
