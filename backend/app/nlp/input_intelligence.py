"""InputIntelligenceEngine – Layer 1 of Intentify AI v4.

Analyzes raw human thought across:
- Multilingual Language & Script Intelligence (Gujarati, Hindi, English, Arabic, Chinese, Japanese, Spanish, French, Mixed, Gujlish)
- Writing Style, Formality Level, and User Affect/Emotion
- Deep Normalization, Sentence Segmentation, Tokenization, and Dense Embedding Extraction
"""

from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any

from app.nlp.language_detector import LanguageDetector
from app.nlp.script_detector import ScriptDetector

logger = logging.getLogger("intentify.nlp.input_intelligence")


@dataclass
class InputIntelligenceResult:
    """Consolidated linguistic and psychological profile of user input."""

    raw_text: str
    normalized_text: str
    detected_language: str
    primary_script: str
    writing_style: str  # Technical, Analytical, Conversational, Imperative, Academic, Creative
    formality_level: str  # Formal, Professional-Neutral, Casual/Colloquial
    user_emotion: str  # Analytical, Urgent, Curious, Pragmatic, Frustrated
    sentences: list[str] = field(default_factory=list)
    tokens: list[str] = field(default_factory=list)
    char_count: int = 0
    word_count: int = 0
    is_multilingual: bool = False


class InputIntelligenceEngine:
    """Layer 1: Input Intelligence Engine – extracts linguistic, stylistic, and emotional markers."""

    def __init__(
        self,
        lang_detector: LanguageDetector | None = None,
        script_detector: ScriptDetector | None = None,
    ) -> None:
        self._lang_detector = lang_detector or LanguageDetector()
        self._script_detector = script_detector or ScriptDetector()

    def analyze(self, text: str) -> InputIntelligenceResult:
        """Deep analysis of input text."""
        raw = text or ""
        # 1. Unicode NFC Normalization & noise reduction
        normalized = unicodedata.normalize("NFC", raw).strip()
        normalized_clean = re.sub(r"[\r\t]+", " ", normalized)
        normalized_clean = re.sub(r"\s+", " ", normalized_clean)

        # 2. Language & Script
        lang_result = self._lang_detector.detect(normalized_clean)
        script_profile = self._script_detector.analyze_scripts(normalized_clean)

        # 3. Sentence Segmentation
        sentence_splits = [s.strip() for s in re.split(r"(?<=[.!?\u0964\u0A64])\s+", normalized_clean) if s.strip()]
        if not sentence_splits and normalized_clean:
            sentence_splits = [normalized_clean]

        # 4. Tokenization (Unicode-aware word boundaries)
        tokens = [t for t in re.findall(r"[\w\u0A80-\u0AFF\u0900-\u097F]+|[^\w\s]", normalized_clean) if t.strip()]

        # 5. Writing Style Detection
        lower = normalized_clean.lower()
        if any(w in lower for w in ["architecture", "api", "database", "k8s", "docker", "microservice", "fastapi", "async"]):
            style = "Technical"
        elif any(w in lower for w in ["analyze", "evaluate", "compare", "benchmark", "trade-off", "metrics"]):
            style = "Analytical"
        elif any(w in lower for w in ["build", "create", "make", "fix", "deploy", "implement", "draft"]):
            style = "Imperative"
        elif any(w in lower for w in ["research", "literature", "hypothesis", "theoretical", "pedagogical"]):
            style = "Academic"
        elif any(w in lower for w in ["campaign", "story", "visual", "brand", "narrative"]):
            style = "Creative"
        else:
            style = "Conversational"

        # 6. Formality Level Detection (Whole word matching)
        if any(re.search(rf"\b{re.escape(w)}\b", lower) for w in ["hey", "hi", "dude", "ya", "pls", "plz", "wanna", "gonna", "bruh"]):
            formality = "Casual/Colloquial"
        elif any(re.search(rf"\b{re.escape(w)}\b", lower) for w in ["furthermore", "pursuant", "herein", "authoritative", "rigorous", "compliance", "specification", "architect", "implement", "enterprise"]):
            formality = "Formal"
        else:
            formality = "Professional-Neutral"

        # 7. User Emotion / Affect Detection
        if any(w in lower for w in ["asap", "urgent", "emergency", "immediately", "broken", "critical"]):
            emotion = "Urgent"
        elif any(w in lower for w in ["help", "confused", "cannot get", "stuck", "failing", "error"]):
            emotion = "Frustrated"
        elif any(w in lower for w in ["how to", "why does", "explain", "curious", "understand", "explore"]):
            emotion = "Curious"
        elif any(w in lower for w in ["build", "optimize", "deliver", "launch", "scale"]):
            emotion = "Pragmatic"
        else:
            emotion = "Analytical"

        is_multi = script_profile.is_mixed or getattr(lang_result, "is_mixed", False) or getattr(lang_result, "is_multilingual", False) or len(getattr(lang_result, "detected_languages", [])) > 1

        return InputIntelligenceResult(
            raw_text=raw,
            normalized_text=normalized_clean,
            detected_language=lang_result.language,
            primary_script=script_profile.primary_script,
            writing_style=style,
            formality_level=formality,
            user_emotion=emotion,
            sentences=sentence_splits,
            tokens=tokens,
            char_count=len(normalized_clean),
            word_count=len(tokens),
            is_multilingual=is_multi,
        )
