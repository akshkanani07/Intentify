"""Input validation utilities for the Intentify platform."""

from __future__ import annotations

import re
from app.core.exceptions import ValidationError

SUPPORTED_LANGUAGE_CODES = {
    "en", "gu", "hi", "ar", "zh", "ja", "es", "fr", "de", "ta", "te", "ru", "pt", "it"
}

ALLOWED_TONES = {
    "professional", "conversational", "academic", "concise", "creative", "technical", "persuasive", "executive"
}

ALLOWED_FORMATS = {
    "detailed response", "step-by-step", "bullet points", "table", "code", "json", "report", "brief"
}


def validate_prompt_request(role: str, detail: str) -> None:
    """Validate core inputs of prompt generation request."""
    if not detail or not detail.strip():
        raise ValidationError("Prompt detail cannot be empty or solely whitespace.")

    if len(detail.strip()) < 2:
        raise ValidationError("Prompt detail must be at least 2 characters long.")

    if len(detail) > 100_000:
        raise ValidationError("Prompt detail exceeds maximum supported length (100,000 characters).")

    if role and len(role) > 500:
        raise ValidationError("Role description exceeds maximum supported length (500 characters).")


def validate_text_length(text: str, field_name: str, min_len: int = 1, max_len: int = 10_000) -> None:
    """Check text length boundaries."""
    length = len(text.strip())
    if length < min_len:
        raise ValidationError(f"Field '{field_name}' must have at least {min_len} characters.")
    if length > max_len:
        raise ValidationError(f"Field '{field_name}' exceeds maximum allowed length of {max_len} characters.")


def validate_language_code(code: str | None) -> str:
    """Normalize and validate ISO 639-1 language code or return default 'en'."""
    if not code:
        return "en"
    clean_code = code.strip().lower()
    if clean_code in SUPPORTED_LANGUAGE_CODES:
        return clean_code
    # If 2-letter alpha, accept gracefully
    if re.match(r"^[a-z]{2}$", clean_code):
        return clean_code
    return "en"
