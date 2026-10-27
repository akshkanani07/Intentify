"""Intentify Platform – FastAPI Application Factory and Entrypoint."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.exceptions import IntentifyError, PromptInjectionError, ValidationError
from app.core.logging_config import setup_logging
from app.knowledge.knowledge_manager import KnowledgeManager
from app.ml.model_manager import ModelManager

setup_logging()
logger = logging.getLogger("intentify.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup and shutdown lifecycle management."""
    settings = get_settings()
    logger.info("Initializing %s v%s in %s mode...", settings.APP_NAME, settings.VERSION, settings.ENVIRONMENT)

    # 1. Initialize and cache Knowledge Base
    km = KnowledgeManager()
    logger.info("Knowledge base active: %d roles, %d domains", len(km.get_roles()), len(km.get_domains()))

    # 2. Initialize Model Registry
    mm = ModelManager()
    logger.info("Model registry initialized: ready for local weights")

    yield

    logger.info("Shutting down %s gracefully...", settings.APP_NAME)


def create_app() -> FastAPI:
    """Application factory for Intentify AI backend."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="Autonomous AI Prompt Intelligence Platform powered by custom ML pipelines and local intelligence.",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global Exception Handlers
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
        logger.warning("Validation error on %s: %s", request.url.path, exc.message)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": "ValidationError", "message": exc.message, "details": exc.details},
        )

    @app.exception_handler(PromptInjectionError)
    async def injection_exception_handler(request: Request, exc: PromptInjectionError) -> JSONResponse:
        logger.warning("Prompt injection detected on %s: %s", request.url.path, exc.message)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "SecurityViolation", "message": exc.message, "details": exc.details},
        )

    @app.exception_handler(IntentifyError)
    async def intentify_exception_handler(request: Request, exc: IntentifyError) -> JSONResponse:
        logger.error("Internal application error on %s: %s", request.url.path, exc.message)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": exc.__class__.__name__, "message": exc.message, "details": exc.details},
        )

    # Mount API routers (both with prefix and at root for direct /generate-prompt compatibility)
    app.include_router(api_v1_router, prefix=settings.API_PREFIX)
    app.include_router(api_v1_router)

    # Root health and metadata endpoints
    @app.get("/", tags=["Health"])
    def root_status() -> dict[str, str]:
        return {
            "name": settings.APP_NAME,
            "version": settings.VERSION,
            "status": "online",
            "docs": "/docs" if settings.DEBUG else "disabled in production",
        }

    @app.get("/health", tags=["Health"])
    def health_check() -> dict[str, str]:
        return {"status": "healthy"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
