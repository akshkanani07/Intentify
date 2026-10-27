"""InputNormalizer – Stage 1 of the Intentify Premium Master Prompt Compiler Engine.

Performs:
- Unicode NFC normalization
- Script identification (Gujarati / Devanagari / Latin / Mixed)
- Multi-lingual conversational preamble & filler stripping
- Transliteration and lexicon standardization for common regional variants
"""

from __future__ import annotations

import json
import logging
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.nlp.script_detector import ScriptDetector, ScriptProfile

logger = logging.getLogger("intentify.engine.normalizer")


@dataclass
class NormalizedInput:
    """Standardized representation of user input following normalization and preamble stripping."""

    raw_text: str
    clean_text: str
    core_content: str
    stripped_preamble: str
    primary_script: str
    detected_language: str
    is_mixed: bool
    tokens: list[str] = field(default_factory=list)
    token_scripts: list[tuple[str, str]] = field(default_factory=list)
    lexicon_matches: dict[str, str] = field(default_factory=dict)
    char_count: int = 0
    word_count: int = 0


class InputNormalizer:
    """Normalizes input text, detects scripts, strips conversational preambles, and standardizes vocabulary."""

    # Leading conversational preamble patterns (case-insensitive)
    # Order matters: longer, more specific prefixes match first.
    PREAMBLE_PATTERNS: list[re.Pattern[str]] = [
        # Broken colloquial phrasings (never pass to object or prompt)
        re.compile(r"^(?:i\s+am\s+want\s+to\s+create\s+a|i\s+am\s+want\s+to\s+make\s+a|i\s+am\s+want\s+to|a\s+want\s+to)\s*", re.IGNORECASE),
        re.compile(r"^(?:help\s+me\s+learn|help\s+me\s+to\s+learn|help\s+me\s+build|help\s+me\s+make)\s*", re.IGNORECASE),
        # English preambles
        re.compile(r"^(?:please\s+)?(?:i\s+would\s+like\s+to|would\s+like\s+to)\s+(?:please\s+)?", re.IGNORECASE),
        re.compile(r"^(?:please\s+)?(?:i\s+want\s+to|want\s+to)\s+(?:please\s+)?", re.IGNORECASE),
        re.compile(r"^(?:please\s+)?(?:i\s+need\s+to|need\s+to)\s+(?:please\s+)?", re.IGNORECASE),
        re.compile(r"^(?:please\s+)?(?:i\s+wish\s+to|wish\s+to)\s+(?:please\s+)?", re.IGNORECASE),
        re.compile(r"^(?:can\s+you\s+help\s+me|help\s+me\s+to|help\s+me)\s+(?:to\s+)?", re.IGNORECASE),
        re.compile(r"^(?:can\s+you\s+please|could\s+you\s+please|can\s+you|could\s+you)\s+(?:to\s+)?", re.IGNORECASE),
        re.compile(r"^(?:please\s+give\s+me\s+a\s+|give\s+me\s+a\s+|provide\s+a\s+|generate\s+a\s+)", re.IGNORECASE),
        re.compile(r"^(?:please\s+write\s+a\s+|write\s+a\s+|make\s+a\s+|build\s+a\s+|create\s+a\s+)", re.IGNORECASE),
        re.compile(r"^(?:please\s+)", re.IGNORECASE),
        # Gujarati conversational preambles
        re.compile(r"^(?:કૃપા\s+કરીને\s+)?(?:મારે\s+|મને\s+|હું\s+)(?:એક\s+)?(?:નવું\s+|નવી\s+)?", re.IGNORECASE),
        re.compile(r"^(?:મારે\s+જોઈએ\s+છે|મને\s+આપો)\s*", re.IGNORECASE),
        re.compile(r"^(?:કૃપા\s+કરીને\s+)", re.IGNORECASE),
        # Hindi conversational preambles
        re.compile(r"^(?:कृपया\s+)?(?:मुझे\s+|मैं\s+|हम\s+)(?:एक\s+)?(?:नया\s+|नई\s+)?", re.IGNORECASE),
        re.compile(r"^(?:कृपया\s+मेरी\s+मदद\s+करें|मेरी\s+मदद\s+करें|कृपया\s+)", re.IGNORECASE),
        # Romanized / Gujlish / Hinglish preambles
        re.compile(r"^(?:mare\s+|mane\s+|hu\s+)(?:ek\s+)?", re.IGNORECASE),
        re.compile(r"^(?:mujhe\s+|main\s+)(?:ek\s+)?", re.IGNORECASE),
        re.compile(r"^(?:help\s+karo|banao\s+ek|banavo\s+ek)\s*", re.IGNORECASE),
    ]

    # Trailing polite / conversational suffixes
    TRAILING_PATTERNS: list[re.Pattern[str]] = [
        re.compile(r"\s+(?:જોઈએ\s+છે|જોઈએ|આપો|કરો|ચલાવો|શીખવું\s+છે|બનાવવું\s+છે)$", re.IGNORECASE),
        re.compile(r"\s+(?:चाहिए|दीजिए|करें|सीखना\s+है|बनाना\s+है)$", re.IGNORECASE),
        re.compile(r"\s+(?:please|asap|thank\s+you|thanks)$", re.IGNORECASE),
        re.compile(r"\s+(?:joiye\s+che|joiye|chahiye)$", re.IGNORECASE),
    ]

    # Standardized lexicon for regional, transliterated, and colloquial variants
    LEXICON_MAP: dict[str, str] = {
        "શીખવું": "learn",
        "શીખવ": "teach",
        "શીખો": "learn",
        "સીખના": "learn",
        "सीखना": "learn",
        "seekhna": "learn",
        "shikhvu": "learn",
        "બનાવવું": "build",
        "બનાવો": "build",
        "बनाना": "build",
        "banao": "build",
        "banavo": "build",
        "lakh": "lakh",
        "lac": "lakh",
        "લાખ": "lakh",
        "લાખનું": "lakh",
        "લાખમાં": "lakh",
        "લાખનુ": "lakh",
        "lacs": "lakh",
        "lakhs": "lakh",
        "વેબસાઇટ": "website",
        "વેબસાટ": "website",
        "वेबसाइट": "website",
        "योजना": "plan",
        "સુધારો": "fix",
        "ડીબગ": "debug",
    }

    def __init__(self, script_detector: ScriptDetector | None = None) -> None:
        self._script_detector = script_detector or ScriptDetector()
        self.lexicon_map: dict[str, str] = dict(self.LEXICON_MAP)
        # Load external knowledge base lexicons if present
        lex_dir = Path("c:/intentify/knowledge-base/lexicon")
        if not lex_dir.exists():
            cand = Path(__file__).resolve()
            for _ in range(5):
                cand = cand.parent
                if (cand / "knowledge-base" / "lexicon").exists():
                    lex_dir = cand / "knowledge-base" / "lexicon"
                    break
        if lex_dir.exists():
            for p in lex_dir.glob("*.json"):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            for k, v in data.items():
                                self.lexicon_map[k.lower()] = str(v)
                except Exception:
                    pass

    def normalize(self, text: str) -> NormalizedInput:
        """Execute deep normalization, script identification, and preamble stripping."""
        raw = text or ""

        # 1. Unicode NFC Normalization
        norm = unicodedata.normalize("NFC", raw).strip()

        # 2. Whitespace and Control Character Normalization
        clean = re.sub(r"[\r\t\f\v]+", " ", norm)
        clean = re.sub(r"\s+", " ", clean).strip()

        # 3. Script Detection
        script_profile = self._script_detector.analyze_scripts(clean)
        primary_script = script_profile.primary_script
        is_mixed = script_profile.is_mixed

        # 4. Multi-lingual Preamble Stripping
        stripped = clean
        preamble_matched = ""
        for pat in self.PREAMBLE_PATTERNS:
            m = pat.search(stripped)
            if m:
                preamble_matched = m.group(0).strip()
                stripped = stripped[m.end():].strip()
                break

        # Strip trailing conversational filler
        for pat in self.TRAILING_PATTERNS:
            stripped = pat.sub("", stripped).strip()

        # 5. Clean punctuation edge artifacts
        core_content = stripped.strip(".,;:?!- ")
        if not core_content:
            core_content = clean

        # 6. Lexicon Standardizations & Spelling Corrections
        tokens = re.findall(r"[\w\u0A80-\u0AFF\u0900-\u097F]+", clean, re.UNICODE)
        lexicon_matches: dict[str, str] = {}
        for t in tokens:
            t_lower = t.lower()
            if t_lower in self.lexicon_map:
                lexicon_matches[t] = self.lexicon_map[t_lower]

        # Apply substitutions to core_content (sorted by length descending, avoiding subtoken corruption like .js in Node.js)
        standardized_core = core_content
        sorted_lexicon = sorted(lexicon_matches.items(), key=lambda x: len(x[0]), reverse=True)
        for orig_token, repl in sorted_lexicon:
            if orig_token.lower() == "js":
                pattern = rf"(?<!\.)\b{re.escape(orig_token)}\b"
            else:
                pattern = rf"\b{re.escape(orig_token)}\b"
            standardized_core = re.sub(pattern, repl, standardized_core, flags=re.IGNORECASE)
        core_content = standardized_core

        # 7. Language Detection
        detected_lang = self._infer_language(clean, primary_script, is_mixed)

        token_scripts: list[tuple[str, str]] = []
        for t in tokens:
            scr = "Common"
            for ch in t:
                code = ord(ch)
                if 0x0A80 <= code <= 0x0AFF:
                    scr = "Gujarati"
                    break
                elif 0x0900 <= code <= 0x097F:
                    scr = "Devanagari"
                    break
                elif ("a" <= ch <= "z") or ("A" <= ch <= "Z"):
                    scr = "Latin"
                    break
            token_scripts.append((t, scr))

        return NormalizedInput(
            raw_text=raw,
            clean_text=clean,
            core_content=core_content,
            stripped_preamble=preamble_matched,
            primary_script=primary_script,
            detected_language=detected_lang,
            is_mixed=is_mixed,
            tokens=tokens,
            token_scripts=token_scripts,
            lexicon_matches=lexicon_matches,
            char_count=len(clean),
            word_count=len(tokens),
        )

    def _infer_language(self, text: str, primary_script: str, is_mixed: bool) -> str:
        """Infer language based on script distribution and lexicon signals."""
        if primary_script == "Gujarati":
            return "Gujarati"
        if primary_script == "Devanagari":
            return "Hindi"

        # Check Romanized Gujarati / Hindi (Gujlish / Hinglish)
        text_lower = text.lower()
        guj_markers = ["mare", "mane", "joiye", "nathi", "mate", "karvu", "che", "kem", "su", "evu", "karo", "banavo", "kai"]
        hi_markers = ["mujhe", "karna", "chahiye", "kuch", "kaise", "kare", "hai", "nahi", "shadi", "banao", "bana", "batao"]

        guj_hits = sum(1 for w in guj_markers if re.search(rf"\b{w}\b", text_lower))
        hi_hits = sum(1 for w in hi_markers if re.search(rf"\b{w}\b", text_lower))

        if guj_hits >= 2 or (guj_hits >= 1 and ("joiye" in text_lower or "banavo" in text_lower)):
            return "Gujarati"
        if hi_hits >= 2 or (hi_hits >= 1 and ("chahiye" in text_lower or ("kuch" in text_lower and "banao" in text_lower))):
            return "Hindi"

        if is_mixed and any(ord(c) >= 0x0A80 and ord(c) <= 0x0AFF for c in text):
            return "Gujarati"
        if is_mixed and any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in text):
            return "Hindi"

        return "English"
