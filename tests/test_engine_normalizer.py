"""Unit tests for InputNormalizer (Stage 1 of the new engine)."""

from __future__ import annotations

import pytest
from app.engine.normalizer import InputNormalizer, NormalizedInput


@pytest.fixture
def normalizer():
    return InputNormalizer()


def test_english_preamble_stripping(normalizer):
    res = normalizer.normalize("I want to build a scheduling website with calendar sync")
    assert res.core_content.lower() == "build a scheduling website with calendar sync" or "scheduling website" in res.core_content.lower()
    assert res.detected_language == "English"
    assert "i want to" in res.stripped_preamble.lower()


def test_want_to_learn_java_fix(normalizer):
    res = normalizer.normalize("want to learn java")
    # "want to" should be stripped
    assert res.core_content.lower() == "learn java" or "java" in res.core_content.lower()
    assert "want to" not in res.core_content.lower()


def test_gujarati_preamble_and_trailing_stripping(normalizer):
    res = normalizer.normalize("મારે Java શીખવું છે")
    assert res.detected_language == "Gujarati"
    assert res.primary_script == "Gujarati"
    assert "Java" in res.core_content
    assert "મારે" not in res.core_content
    assert "છે" not in res.core_content


def test_gujlish_wedding_scenario(normalizer):
    res = normalizer.normalize("mare wedding planner mate prompt joiye destination wedding in Udaipur with budget 50 lakh")
    assert res.detected_language == "Gujarati"
    assert "wedding" in res.core_content.lower()
    assert "udaipur" in res.core_content.lower()
    assert "50 lakh" in res.core_content.lower()


def test_hindi_preamble_stripping(normalizer):
    res = normalizer.normalize("मुझे एक रेस्टोरेंट के लिए बिजनेस प्लान बनाना है")
    assert res.detected_language == "Hindi"
    assert res.primary_script == "Devanagari"
    assert "रेस्टोरेंट" in res.core_content
    assert "मुझे" not in res.core_content


def test_lexicon_standardization(normalizer):
    res = normalizer.normalize("મારે 50 lac નું બજેટ છે")
    assert "lac" in res.lexicon_matches or "50 lac" in res.clean_text.lower()
    assert res.lexicon_matches.get("lac") == "lakh"
