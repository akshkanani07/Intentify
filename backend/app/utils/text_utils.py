"""Text processing utilities for NLP and prompt intelligence."""

from __future__ import annotations

import re
import unicodedata


def normalize_text(text: str) -> str:
    """Normalize unicode characters, remove invisible control chars, strip outer whitespace."""
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKC", text)
    # Remove non-printable control characters except newline and tab
    cleaned = "".join(ch for ch in normalized if ch == "\n" or ch == "\t" or not unicodedata.category(ch).startswith("C"))
    return cleaned.strip()


def clean_whitespace(text: str) -> str:
    """Collapse consecutive spaces/tabs and normalize excessive line breaks."""
    if not text:
        return ""
    # Replace multiple spaces/tabs with single space
    text = re.sub(r"[ \t]+", " ", text)
    # Replace 3 or more newlines with 2 newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_sentences(text: str) -> list[str]:
    """Split text into sentences using regex boundary matching for multiple languages."""
    if not text:
        return []
    # Match sentence terminators (., !, ?, ।, etc.)
    sentences = re.split(r"(?<=[.!?।॥؟\n])\s+", text)
    return [s.strip() for s in sentences if s.strip()]


def extract_keywords(text: str, max_keywords: int = 10) -> list[str]:
    """Basic keyword extractor based on word frequency and length filtering."""
    if not text:
        return []
    # Basic stopwords list
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
        "by", "from", "up", "about", "into", "over", "after", "is", "are", "was", "were",
        "be", "been", "being", "have", "has", "had", "do", "does", "did", "can", "could",
        "will", "would", "shall", "should", "may", "might", "must", "that", "this", "these",
        "those", "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them",
        "my", "your", "his", "its", "our", "their", "what", "which", "who", "when", "where",
        "why", "how", "all", "any", "both", "each", "few", "more", "most", "some", "such",
        "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "mate", "joiye"
    }
    words = re.findall(r"\b\w{3,}\b", text.lower())
    filtered = [w for w in words if w not in stop_words]
    
    # Frequency count
    counts: dict[str, int] = {}
    for word in filtered:
        counts[word] = counts.get(word, 0) + 1
        
    sorted_words = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return [word for word, _ in sorted_words[:max_keywords]]


def detect_script(text: str) -> str:
    """Identify the primary script of the input text using Unicode block detection."""
    if not text:
        return "Unknown"

    script_counts: dict[str, int] = {
        "Latin": 0,
        "Gujarati": 0,
        "Devanagari": 0,
        "Arabic": 0,
        "Han": 0,
        "Hiragana/Katakana": 0,
        "Tamil": 0,
        "Telugu": 0,
        "Cyrillic": 0,
    }

    for ch in text:
        cp = ord(ch)
        if 0x0041 <= cp <= 0x007A or 0x00C0 <= cp <= 0x024F:
            script_counts["Latin"] += 1
        elif 0x0A80 <= cp <= 0x0AFF:
            script_counts["Gujarati"] += 1
        elif 0x0900 <= cp <= 0x097F:
            script_counts["Devanagari"] += 1
        elif 0x0600 <= cp <= 0x06FF or 0x0750 <= cp <= 0x077F:
            script_counts["Arabic"] += 1
        elif 0x4E00 <= cp <= 0x9FFF:
            script_counts["Han"] += 1
        elif 0x3040 <= cp <= 0x30FF:
            script_counts["Hiragana/Katakana"] += 1
        elif 0x0B80 <= cp <= 0x0BFF:
            script_counts["Tamil"] += 1
        elif 0x0C00 <= cp <= 0x0C7F:
            script_counts["Telugu"] += 1
        elif 0x0400 <= cp <= 0x04FF:
            script_counts["Cyrillic"] += 1

    top_script = max(script_counts.items(), key=lambda kv: kv[1])
    return top_script[0] if top_script[1] > 0 else "Latin"


def truncate_text(text: str, max_chars: int = 5000, suffix: str = "...") -> str:
    """Truncate text safely at word boundary if it exceeds max_chars."""
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars - len(suffix)]
    last_space = truncated.rfind(" ")
    if last_space != -1:
        truncated = truncated[:last_space]
    return truncated + suffix
