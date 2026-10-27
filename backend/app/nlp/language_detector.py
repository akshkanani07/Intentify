"""Autonomous Multi-Lingual Intelligence and Script Detection Engine."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

from app.nlp.script_detector import ScriptDetector, ScriptProfile
from app.nlp.transliteration import TransliterationHandler, TransliterationResult

logger = logging.getLogger("intentify.nlp.language_detector")


@dataclass
class LanguageResult:
    """Comprehensive linguistic intelligence profile of input text."""

    language: str
    language_code: str
    script: str
    confidence: float
    is_mixed: bool = False
    is_transliterated: bool = False
    detected_languages: list[str] = field(default_factory=list)
    script_profile: ScriptProfile | None = None
    transliteration_profile: TransliterationResult | None = None
    target_prompt_language: str = "English"


class LanguageDetector:
    """Local, high-performance multilingual and script identification engine.

    Supports 12+ languages across multiple scripts and transliterated dialects:
    - Gujarati (Native script & Romanized)
    - Hindi (Devanagari script & Romanized Hinglish)
    - English
    - Arabic
    - Chinese (Simplified & Traditional Han)
    - Japanese (Hiragana, Katakana, Kanji)
    - Spanish
    - French
    - German
    - Tamil (Native script & Romanized)
    - Telugu (Native script & Romanized)
    - Russian (Cyrillic)
    """

    SCRIPT_TO_LANGUAGE: dict[str, tuple[str, str]] = {
        "Gujarati": ("Gujarati", "gu"),
        "Devanagari": ("Hindi", "hi"),
        "Arabic": ("Arabic", "ar"),
        "Han": ("Chinese", "zh"),
        "Japanese": ("Japanese", "ja"),
        "Tamil": ("Tamil", "ta"),
        "Telugu": ("Telugu", "te"),
        "Cyrillic": ("Russian", "ru"),
    }

    # Distinctive European / Latin lexical profiles
    LATIN_LANGUAGE_LEXICONS: dict[str, tuple[str, set[str]]] = {
        "es": (
            "Spanish",
            {"para", "como", "hacer", "por", "que", "crear", "escribir", "con", "una", "este", "esta", "todos", "pero", "mas", "del", "los", "las"}
        ),
        "fr": (
            "French",
            {"pour", "comment", "faire", "avec", "dans", "ecrire", "creer", "une", "votre", "cette", "aussi", "plus", "mais", "tout", "nous", "vous"}
        ),
        "de": (
            "German",
            {"fuer", "fur", "wie", "machen", "bitte", "erstellen", "schreiben", "eine", "dieser", "nicht", "auch", "aber", "nach", "haben", "werden"}
        ),
        "pt": (
            "Portuguese",
            {"para", "como", "fazer", "com", "uma", "este", "criar", "escrever", "mais", "mas", "sobre", "voce", "todos"}
        ),
        "it": (
            "Italian",
            {"per", "come", "fare", "con", "una", "questo", "creare", "scrivere", "piu", "ma", "tutti", "anche", "della"}
        ),
    }

    def __init__(self) -> None:
        self.script_detector = ScriptDetector()
        self.transliteration_handler = TransliterationHandler()

    def detect(self, text: str) -> LanguageResult:
        """Analyze text and determine script, language, transliteration, and code-switching."""
        if not text or not text.strip():
            return LanguageResult(
                language="English",
                language_code="en",
                script="Latin",
                confidence=1.0,
                is_mixed=False,
                is_transliterated=False,
                detected_languages=["English"],
                target_prompt_language="English",
            )

        clean_text = text.strip()
        script_profile = self.script_detector.analyze_scripts(clean_text)
        primary_script = script_profile.primary_script

        # Handle Code-Switching with English Loanwords:
        # If a non-Latin native script has significant presence (>= 4 characters or >= 20%),
        # the grammatical carrier language is that native script, even if technical terms
        # in Latin script have more total characters (e.g. "FastAPI और Docker के साथ REST API बनाइए").
        non_latin_candidates = [
            (script, count) for script, count in script_profile.script_counts.items()
            if script != "Latin" and (count >= 4 or script_profile.script_percentages.get(script, 0.0) >= 20.0)
        ]

        target_script = primary_script
        if non_latin_candidates and (primary_script == "Latin" or script_profile.is_mixed):
            sorted_non_latin = sorted(non_latin_candidates, key=lambda kv: kv[1], reverse=True)
            target_script = sorted_non_latin[0][0]

        # 1. Non-Latin Native Scripts (direct or prioritized)
        if target_script in self.SCRIPT_TO_LANGUAGE:
            lang_name, lang_code = self.SCRIPT_TO_LANGUAGE[target_script]
            has_latin = "Latin" in script_profile.script_counts and script_profile.script_counts["Latin"] >= 2
            detected = [lang_name]
            if has_latin:
                detected.append("English")

            confidence = min(0.99, max(0.85, script_profile.script_percentages.get(target_script, 80.0) / 100.0))

            return LanguageResult(
                language=lang_name,
                language_code=lang_code,
                script=target_script,
                confidence=round(confidence, 2),
                is_mixed=has_latin or script_profile.is_mixed,
                is_transliterated=False,
                detected_languages=detected,
                script_profile=script_profile,
                target_prompt_language=lang_name,
            )

        # 2. Latin Script: Check for Transliterated Indic Languages (Gujarati, Hindi, Tamil, Telugu)
        translit_profile = self.transliteration_handler.analyze(clean_text)
        if translit_profile.is_transliterated and translit_profile.detected_base_language:
            base_lang = translit_profile.detected_base_language
            lang_code = translit_profile.language_code or "en"
            detected = [f"{base_lang} (Romanized)"]
            if translit_profile.english_word_count > 0:
                detected.append("English")

            return LanguageResult(
                language=base_lang,
                language_code=lang_code,
                script="Latin",
                confidence=translit_profile.confidence,
                is_mixed=translit_profile.is_code_switched,
                is_transliterated=True,
                detected_languages=detected,
                script_profile=script_profile,
                transliteration_profile=translit_profile,
                target_prompt_language=base_lang,
            )

        # 3. Latin Script: Check for European Languages
        words = set(re.findall(r"\b[a-zA-Z]{2,}\b", clean_text.lower()))
        for code, (lang_name, lexicon) in self.LATIN_LANGUAGE_LEXICONS.items():
            overlap = words.intersection(lexicon)
            if len(overlap) >= 2:
                has_en_overlap = len(words.intersection({"the", "is", "for", "with", "and"})) > 0
                detected = [lang_name]
                if has_en_overlap:
                    detected.append("English")

                confidence = min(0.95, 0.70 + (len(overlap) * 0.05))
                return LanguageResult(
                    language=lang_name,
                    language_code=code,
                    script="Latin",
                    confidence=round(confidence, 2),
                    is_mixed=has_en_overlap,
                    is_transliterated=False,
                    detected_languages=detected,
                    script_profile=script_profile,
                    target_prompt_language=lang_name,
                )

        # 4. Default: Standard English
        return LanguageResult(
            language="English",
            language_code="en",
            script="Latin",
            confidence=0.92,
            is_mixed=False,
            is_transliterated=False,
            detected_languages=["English"],
            script_profile=script_profile,
            target_prompt_language="English",
        )
