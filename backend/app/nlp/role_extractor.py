"""Multilingual Role & Persona Extraction Engine using pattern parsing and noun phrase analysis."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("intentify.nlp.role_extractor")


@dataclass
class ExtractedRoleCandidate:
    """A role candidate extracted from raw text with position and confidence."""

    candidate: str
    confidence: float
    source_pattern: str
    seniority: str | None = None
    clean_role: str = ""


class RoleExtractor:
    """Extracts professional role personas from unformatted, multilingual human input."""

    # Seniority prefixes
    SENIORITY_LEVELS = [
        "Principal", "Chief", "Staff", "Lead", "Senior", "Head of", "Director of",
        "Junior", "Associate", "Executive", "VP of", "Consultant", "Specialist"
    ]

    # Multilingual pronouns and filler words to strip from role candidates
    PRONOUN_FILLERS = {
        # Gujarati Romanized
        "mare", "mane", "amare", "tame", "tamari", "aapne", "maro", "mari", "maru", "ek",
        # Hindi Romanized
        "mujhe", "mera", "meri", "mere", "humko", "aapko", "humein", "ek", "kisi",
        # English
        "a", "an", "the", "good", "great", "experienced", "expert", "professional",
        "some", "any", "best", "qualified", "certified"
    }

    # Role indicator patterns across English, Romanized Indic, and Native scripts
    ROLE_EXTRACTION_PATTERNS: list[tuple[str, float, str]] = [
        # Explicit English intent expressions
        (r"\b(?:act as|you are|be a|as a|role of|persona of)\s+(?:an?|the)?\s*([a-zA-Z\s]{3,40}?)(?=[,\.\n\(\)]|\bto\b|\bfor\b|\bwith\b|\bwho\b|\bthat\b|$)", 0.95, "en_prefix"),
        (r"\b(?:prompt for|prompt mate|prompt chahiye for)\s+(?:an?|the)?\s*([a-zA-Z\s]{3,40}?)(?=[,\.\n\(\)]|\bto\b|\bfor\b|\bwith\b|\bwho\b|\bthat\b|$)", 0.90, "en_prompt_for"),
        (r"\b(?:i need|i want|looking for|require)\s+(?:an?|the)?\s*([a-zA-Z\s]{3,40}?)(?:\s+to\b|\s+who can\b|\s+for\b|$)", 0.85, "en_need"),

        # Gujarati Romanized suffix indicators: "<role> mate", "<role> joiye"
        (r"([a-zA-Z\s]{3,40}?)\s+(?:mate prompt|mate joiye|mate|joiye)", 0.92, "gu_roman_suffix"),

        # Hindi Romanized suffix indicators: "<role> ke liye", "<role> chahiye"
        (r"([a-zA-Z\s]{3,40}?)\s+(?:ke liye prompt|ke liye|chahiye)", 0.92, "hi_roman_suffix"),

        # Native Gujarati script
        (r"([\u0A80-\u0AFF\s]{3,40}?)\s+(?:માટે|જોઈએ|જોઈશે|તરિકે)", 0.95, "gu_native_script"),

        # Native Devanagari script (Hindi)
        (r"([\u0900-\u097F\s]{3,40}?)\s+(?:के लिए|चाहिए|के रूप में)", 0.95, "hi_native_script"),

        # Spanish expressions
        (r"\b(?:actua como|eres un|como un|rol de)\s+([a-zA-Z\s]{3,40}?)(?=[,\.\n]|\bpara\b|$)", 0.90, "es_prefix"),

        # French expressions
        (r"\b(?:agis en tant que|tu es un|comme un|role de)\s+([a-zA-Z\s]{3,40}?)(?=[,\.\n]|\bpour\b|$)", 0.90, "fr_prefix"),
    ]

    def extract_candidates(self, text: str) -> list[ExtractedRoleCandidate]:
        """Extract candidate role strings from input text."""
        if not text or not text.strip():
            return []

        candidates: list[ExtractedRoleCandidate] = []
        seen: set[str] = set()

        for pattern, base_conf, pat_name in self.ROLE_EXTRACTION_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                raw_match = match.group(1).strip()
                clean = self._clean_candidate(raw_match)
                if clean and clean.lower() not in seen and len(clean.split()) <= 6:
                    seen.add(clean.lower())
                    seniority = self._detect_seniority(raw_match)
                    candidates.append(
                        ExtractedRoleCandidate(
                            candidate=raw_match,
                            clean_role=clean,
                            confidence=base_conf,
                            source_pattern=pat_name,
                            seniority=seniority,
                        )
                    )

        # Sort candidates by confidence
        candidates.sort(key=lambda c: c.confidence, reverse=True)
        return candidates

    def extract_primary_role(self, text: str) -> str | None:
        """Return the highest-confidence cleaned role string or None."""
        candidates = self.extract_candidates(text)
        return candidates[0].clean_role if candidates else None

    def _clean_candidate(self, raw: str) -> str:
        """Strip pronouns, articles, and meaningless prepositions from candidate string."""
        tokens = re.findall(r"\b[\w\u0A80-\u0AFF\u0900-\u097F\-]+\b", raw)
        filtered = [t for t in tokens if t.lower() not in self.PRONOUN_FILLERS]

        if not filtered:
            return ""

        joined = " ".join(filtered).strip()
        # Ensure it has substance
        if len(joined) < 3 or joined.isdigit():
            return ""

        return joined.title()

    def _detect_seniority(self, text: str) -> str | None:
        """Detect seniority prefix if present."""
        text_lower = text.lower()
        for level in self.SENIORITY_LEVELS:
            if re.search(r"\b" + re.escape(level.lower()) + r"\b", text_lower):
                return level
        return None
