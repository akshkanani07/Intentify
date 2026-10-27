"""Safety and prompt injection detection wrapper with heuristic and ML hooks."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from app.core.security import PromptSafetyChecker

logger = logging.getLogger("intentify.quality.safety_checker")


@dataclass
class SafetyCheckResult:
    """Outcome of prompt safety audit."""

    is_safe: bool
    threats: list[str] = field(default_factory=list)
    sanitized_text: str = ""
    risk_level: str = "low"  # low, medium, high, critical


class SafetyChecker:
    """Evaluates user prompt inputs for injection vulnerabilities, jailbreaks, and sensitive data leakage."""

    def __init__(self, core_checker: PromptSafetyChecker | None = None) -> None:
        self._core = core_checker or PromptSafetyChecker()

    def check(self, text: str) -> SafetyCheckResult:
        """Analyze text for prompt injection vectors."""
        result = self._core.detect_injection(text)
        risk = "low"
        if not result.is_safe:
            risk = "critical" if any("override" in p.lower() or "ignore" in p.lower() for p in result.matched_patterns) else "high"

        return SafetyCheckResult(
            is_safe=result.is_safe,
            threats=result.matched_patterns,
            sanitized_text=self._core.sanitize_input(text),
            risk_level=risk,
        )
