"""Structured logging configuration with JSON and standard console formatter."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

try:
    from pythonjsonlogger.json import JsonFormatter as BaseJsonFormatter  # type: ignore[import-untyped]
except ImportError:
    class BaseJsonFormatter(logging.Formatter):  # type: ignore[no-redef]
        def format(self, record: logging.LogRecord) -> str:
            log_record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service": "intentify",
                "level": record.levelname.upper(),
                "logger": record.name,
                "message": record.getMessage(),
            }
            if record.exc_info and record.exc_info[1]:
                log_record["exception_type"] = type(record.exc_info[1]).__name__
                log_record["exception_message"] = str(record.exc_info[1])
            return json.dumps(log_record)


class IntentifyJsonFormatter(BaseJsonFormatter):  # type: ignore[misc]
    """Custom JSON log formatter adding service metadata."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.service_name = "intentify"

    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        if hasattr(super(), "add_fields"):
            super().add_fields(log_record, record, message_dict)
        log_record["timestamp"] = datetime.now(timezone.utc).isoformat()
        log_record["service"] = self.service_name
        log_record["level"] = record.levelname.upper()
        log_record["logger"] = record.name
        if record.exc_info and record.exc_info[1]:
            log_record["exception_type"] = type(record.exc_info[1]).__name__
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id  # type: ignore[attr-defined]


class PlainFormatter(logging.Formatter):
    """Human-readable formatter for development and console output."""

    FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    DATE_FMT = "%Y-%m-%d %H:%M:%S"

    def __init__(self) -> None:
        super().__init__(fmt=self.FORMAT, datefmt=self.DATE_FMT)


def setup_logging(level: str = "INFO", log_format: str = "plain") -> None:
    """Configure root and application loggers."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    handler = logging.StreamHandler(sys.stdout)
    if log_format.lower() == "json":
        handler.setFormatter(IntentifyJsonFormatter())
    else:
        handler.setFormatter(PlainFormatter())

    root_logger.handlers = [handler]
