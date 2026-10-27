"""Transliteration and Romanized Dialect Handler for Indic and mixed languages."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger("intentify.nlp.transliteration")


@dataclass
class TransliterationResult:
    """Outcome of transliteration and Romanized language analysis."""

    is_transliterated: bool
    detected_base_language: str | None = None
    language_code: str | None = None
    confidence: float = 0.0
    matched_markers: list[str] = field(default_factory=list)
    english_word_count: int = 0
    indic_word_count: int = 0
    is_code_switched: bool = False


class TransliterationHandler:
    """Identifies and decodes Romanized Indic text (Gujarati, Hindi, Tamil, Telugu)."""

    # Comprehensive dictionaries of distinctive functional words in Romanized Indic dialects
    GUJARATI_ROMAN_MARKERS = {
        "mare": 3.0, "joiye": 3.0, "joie": 3.0, "mate": 2.5, "nathi": 3.0, "karo": 1.5,
        "kem": 2.5, "chhe": 3.0, "chho": 3.0, "karvu": 3.0, "karvanu": 3.0, "aapo": 2.5,
        "aapjo": 2.5, "tame": 2.5, "hu": 2.0, "mane": 2.5, "saras": 2.0, "lagan": 3.0,
        "aaje": 2.5, "pachhi": 2.5, "su": 2.0, "kahu": 2.0, "banavo": 2.5, "banavvu": 3.0,
        "tamaro": 2.5, "tamari": 2.5, "bhai": 1.5, "ben": 1.5, "ketla": 2.5, "kyare": 2.5,
        "joye": 3.0, "lejo": 2.0, "rakho": 2.0, "samjavo": 2.5, "samjan": 2.5,
    }

    HINDI_ROMAN_MARKERS = {
        "mujhe": 3.0, "chahiye": 3.0, "karna": 2.5, "kijiye": 2.5, "karo": 1.5,
        "hai": 2.0, "hain": 2.0, "kaise": 2.5, "kya": 2.0, "mera": 2.0, "meri": 2.0,
        "mere": 2.0, "hum": 1.5, "humko": 2.5, "aap": 2.0, "aapko": 2.5, "banao": 2.5,
        "batao": 2.5, "likho": 2.5, "acha": 2.0, "bohot": 2.0, "samjhao": 2.5,
        "hoga": 2.0, "hogi": 2.0, "sakte": 2.0, "sakti": 2.0, "nahi": 2.0, "bhi": 1.5,
        "lekin": 2.0, "aur": 1.5, "kyon": 2.0, "kab": 2.0, "kahan": 2.0, "kaun": 2.0,
        "kuch": 2.5, "kuchh": 2.5, "bana": 2.0, "banaye": 2.5, "kare": 2.0, "karen": 2.0,
    }

    TAMIL_ROMAN_MARKERS = {
        "enakku": 3.0, "venum": 3.0, "thevai": 3.0, "eppadi": 3.0, "panrathu": 3.0,
        "nalla": 2.5, "solla": 2.5, "ungaluku": 3.0, "theriyuma": 3.0, "panna": 2.5,
        "irukku": 3.0, "mudiyuma": 3.0, "eduthu": 2.5, "kodu": 2.5, "vaanga": 2.5,
    }

    TELUGU_ROMAN_MARKERS = {
        "naaku": 3.0, "kaavali": 3.0, "ela": 2.5, "cheyali": 3.0, "cheppandi": 3.0,
        "manchi": 2.5, "chesuko": 2.5, "meeku": 2.5, "telusa": 2.5, "undi": 2.5,
        "lekapothe": 3.0, "cheyandi": 3.0, "kuda": 2.0, "ippudu": 2.5, "eppudu": 2.5,
    }

    def analyze(self, text: str) -> TransliterationResult:
        """Evaluate if text written in Latin script is a transliterated regional language."""
        if not text or not text.strip():
            return TransliterationResult(is_transliterated=False)

        words = re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())
        if not words:
            return TransliterationResult(is_transliterated=False)

        # Score matching words against dictionaries
        scores = {
            "Gujarati": 0.0,
            "Hindi": 0.0,
            "Tamil": 0.0,
            "Telugu": 0.0,
        }
        matched: dict[str, list[str]] = {k: [] for k in scores}

        for word in words:
            if word in self.GUJARATI_ROMAN_MARKERS:
                scores["Gujarati"] += self.GUJARATI_ROMAN_MARKERS[word]
                matched["Gujarati"].append(word)

            if word in self.HINDI_ROMAN_MARKERS:
                scores["Hindi"] += self.HINDI_ROMAN_MARKERS[word]
                matched["Hindi"].append(word)

            if word in self.TAMIL_ROMAN_MARKERS:
                scores["Tamil"] += self.TAMIL_ROMAN_MARKERS[word]
                matched["Tamil"].append(word)

            if word in self.TELUGU_ROMAN_MARKERS:
                scores["Telugu"] += self.TELUGU_ROMAN_MARKERS[word]
                matched["Telugu"].append(word)

        sorted_scores = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        top_lang, top_score = sorted_scores[0]

        # Minimum score threshold for asserting transliteration
        if top_score >= 3.0:
            lang_codes = {
                "Gujarati": "gu",
                "Hindi": "hi",
                "Tamil": "ta",
                "Telugu": "te",
            }
            indic_count = len(matched[top_lang])
            english_count = max(0, len(words) - indic_count)
            confidence = min(0.98, 0.65 + (top_score / 15.0))

            return TransliterationResult(
                is_transliterated=True,
                detected_base_language=top_lang,
                language_code=lang_codes.get(top_lang, "en"),
                confidence=round(confidence, 2),
                matched_markers=matched[top_lang],
                english_word_count=english_count,
                indic_word_count=indic_count,
                is_code_switched=english_count > 0 and indic_count > 0,
            )

        return TransliterationResult(
            is_transliterated=False,
            english_word_count=len(words),
            indic_word_count=0,
            is_code_switched=False,
        )
