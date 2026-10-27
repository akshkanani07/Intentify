"""Config module – thin re-export wrapper around core settings."""

from app.config.settings import get_settings

__all__ = ["get_settings"]
