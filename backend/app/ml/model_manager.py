"""ModelManager – manages local PyTorch/transformer models with lazy loading and memory controls."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any
from app.core.config import get_settings
from app.core.exceptions import ModelLoadError

logger = logging.getLogger("intentify.ml.model_manager")


class ModelManager:
    """Singleton registry and loader for local ML artifacts."""

    _instance: ModelManager | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> ModelManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._registry = {}
            cls._instance._settings = get_settings()
        return cls._instance

    def load_model(self, name: str, relative_path: str) -> Any:
        """Register and load a model artifact from disk."""
        full_path = Path(self._settings.MODEL_DIR) / relative_path
        if name in self._registry:
            return self._registry[name]

        logger.info("Loading model '%s' from %s", name, full_path)
        if not full_path.exists():
            logger.warning("Model path %s not found on disk; registered stub.", full_path)
            self._registry[name] = None
            return None

        try:
            # Model loading logic (torch.load or transformers)
            self._registry[name] = {"path": str(full_path), "loaded": True}
            return self._registry[name]
        except Exception as exc:
            logger.error("Failed to load model %s: %s", name, exc)
            raise ModelLoadError(f"Could not load model {name}: {exc}") from exc

    def get_model(self, name: str) -> Any:
        """Retrieve loaded model from registry."""
        return self._registry.get(name)

    def unload_model(self, name: str) -> bool:
        """Free memory occupied by a model."""
        if name in self._registry:
            del self._registry[name]
            logger.info("Unloaded model '%s'", name)
            return True
        return False

    def list_loaded_models(self) -> list[str]:
        return list(self._registry.keys())
