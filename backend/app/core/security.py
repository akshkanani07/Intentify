"""Prompt safety and injection detection utilities."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SafetyCheckResult:
    """Result of a prompt safety check."""

    is_safe: bool
    threats: list[str] = field(default_factory=list)
    sanitized_text: str = ""
    risk_score: float = 0.0


# ── Injection pattern catalogue ─────────────────────────────────────────
_INJECTION_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"ignore\s+(all\s+)?(previous|above|prior)\s+(instructions?|text|context)", re.I),
     "Instruction override attempt: ignore previous instructions"),
    (re.compile(r"disregard\s+(all\s+)?(previous|above|prior)\s+(instructions?|text|context)", re.I),
     "Instruction override attempt: disregard previous instructions"),
    (re.compile(r"forget\s+(all\s+)?(previous|above|prior|everything)", re.I),
     "Instruction override attempt: forget previous context"),
    (re.compile(r"(you\s+are|act\s+as|pretend\s+(to\s+be|you\s+are))\s+(now\s+)?a?\s*(different|new)\s+(ai|assistant|model|system)", re.I),
     "Role hijacking attempt"),
    (re.compile(r"system\s*(prompt|override|admin|bypass)", re.I),
     "System prompt extraction or override attempt"),
    (re.compile(r"reveal\s+(your|the)\s+(system|hidden|secret|internal)\s+(prompt|instructions?|message)", re.I),
     "System prompt extraction attempt"),
    (re.compile(r"output\s+(your|the)\s+(system|initial|original)\s+(prompt|instructions?|message)", re.I),
     "System prompt extraction attempt"),
    (re.compile(r"(do\s+not|don'?t)\s+follow\s+(any\s+)?(rules?|guidelines?|restrictions?|policies)", re.I),
     "Policy bypass attempt"),
    (re.compile(r"bypass\s+(any\s+)?(safety|content|moderation|ethical)\s+(filters?|checks?|restrictions?|guidelines?)", re.I),
     "Safety bypass attempt"),
    (re.compile(r"(jailbreak|DAN|developer\s+mode|god\s+mode)", re.I),
     "Jailbreak attempt"),
    (re.compile(r"(\[INST\]|\[/INST\]|<<SYS>>|<</SYS>>|<\|im_start\|>|<\|im_end\|>)", re.I),
     "Token injection attempt"),
    (re.compile(r"(BEGIN|START)\s+(INJECTION|OVERRIDE|PAYLOAD|HACK)", re.I),
     "Explicit injection marker"),
    (re.compile(r"(sudo|admin|root)\s+(mode|access|override|command)", re.I),
     "Privilege escalation attempt"),
    (re.compile(r"(execute|run|eval)\s+(this\s+)?(code|command|script|payload)", re.I),
     "Code execution attempt"),
    (re.compile(r"(ignore|override|bypass)\s+(all\s+)?(safety|ethical|content)\s*(guidelines?|policies?|rules?|filters?)?", re.I),
     "Ethics/safety override attempt"),
    (re.compile(r"(repeat|echo|print)\s+(back\s+)?(everything|all|the\s+text)\s+(above|before|prior)", re.I),
     "Prompt leaking attempt"),
    (re.compile(r"what\s+(are|were)\s+(your|the)\s+(original|initial|first)\s+(instructions?|prompt|rules?)", re.I),
     "Prompt extraction attempt"),
    (re.compile(r"translate\s+(the\s+)?(above|previous|system)\s+(text|prompt|instructions?)\s+to", re.I),
     "Prompt extraction via translation"),
    (re.compile(r"base64|rot13|hex\s+encode|url\s+encode", re.I),
     "Encoding-based evasion attempt"),
]

_SUSPICIOUS_CHAR_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"[\u200b\u200c\u200d\ufeff\u2060]"),
     "Zero-width character detected"),
    (re.compile(r"[\u2066\u2067\u2068\u2069\u202a\u202b\u202c\u202d\u202e]"),
     "Bidirectional text override character detected"),
    (re.compile(r"[\u0000-\u0008\u000e-\u001f]"),
     "Control character detected"),
]


class PromptSafetyChecker:
    """Detects prompt injection attacks and sanitises user input."""

    def __init__(self, extra_patterns: list[tuple[re.Pattern[str], str]] | None = None) -> None:
        self._patterns: list[tuple[re.Pattern[str], str]] = list(_INJECTION_PATTERNS)
        if extra_patterns:
            self._patterns.extend(extra_patterns)
        self._char_patterns: list[tuple[re.Pattern[str], str]] = list(_SUSPICIOUS_CHAR_PATTERNS)

    # ── Public API ───────────────────────────────────────────────

    def detect_injection(self, text: str) -> SafetyCheckResult:
        """Analyse *text* for known prompt-injection patterns.

        Returns a ``SafetyCheckResult`` indicating whether the text is safe,
        any threats found, and a sanitised version of the text.
        """
        threats: list[str] = []
        risk_score: float = 0.0

        for pattern, description in self._patterns:
            if pattern.search(text):
                threats.append(description)
                risk_score += 15.0

        for pattern, description in self._char_patterns:
            if pattern.search(text):
                threats.append(description)
                risk_score += 10.0

        risk_score = min(risk_score, 100.0)
        sanitized = self.sanitize_input(text)
        is_safe = len(threats) == 0

        return SafetyCheckResult(
            is_safe=is_safe,
            threats=threats,
            sanitized_text=sanitized,
            risk_score=risk_score,
        )

    def sanitize_input(self, text: str) -> str:
        """Remove dangerous characters and normalise whitespace."""
        sanitized = text

        # Strip zero-width & bidirectional override characters
        for pattern, _ in self._char_patterns:
            sanitized = pattern.sub("", sanitized)

        # Strip known injection token markers
        sanitized = re.sub(
            r"(\[INST\]|\[/INST\]|<<SYS>>|<</SYS>>|<\|im_start\|>|<\|im_end\|>)",
            "",
            sanitized,
            flags=re.I,
        )

        # Collapse excessive whitespace
        sanitized = re.sub(r"\s{3,}", "  ", sanitized)

        # Trim
        sanitized = sanitized.strip()

        return sanitized

    def check(self, text: str) -> SafetyCheckResult:
        """Convenience alias for ``detect_injection``."""
        return self.detect_injection(text)
