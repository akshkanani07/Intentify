"""Comprehensive automated test suite for Step 3: Layer 1 – Language Intelligence."""

from __future__ import annotations

import pytest
from app.nlp.language_detector import LanguageDetector, LanguageResult
from app.nlp.script_detector import ScriptDetector
from app.nlp.transliteration import TransliterationHandler


@pytest.fixture(scope="module")
def detector() -> LanguageDetector:
    return LanguageDetector()


@pytest.fixture(scope="module")
def script_detector() -> ScriptDetector:
    return ScriptDetector()


@pytest.fixture(scope="module")
def translit_handler() -> TransliterationHandler:
    return TransliterationHandler()


# ── 1. Native Script Identification Tests ───────────────────────────────

def test_gujarati_native_script(detector: LanguageDetector):
    text = "મને લગ્ન માટે વેડિંગ પ્લાનર જોઈશે"
    res = detector.detect(text)
    assert res.language == "Gujarati"
    assert res.language_code == "gu"
    assert res.script == "Gujarati"
    assert not res.is_transliterated
    assert res.confidence >= 0.85


def test_hindi_devanagari_script(detector: LanguageDetector):
    text = "मुझे स्वास्थ्य और आहार के लिए एक पूर्ण योजना चाहिए"
    res = detector.detect(text)
    assert res.language == "Hindi"
    assert res.language_code == "hi"
    assert res.script == "Devanagari"
    assert not res.is_transliterated
    assert res.confidence >= 0.85


def test_arabic_script(detector: LanguageDetector):
    text = "أريد خطة تسويقية لمشروعي الجديد في التجارة الإلكترونية"
    res = detector.detect(text)
    assert res.language == "Arabic"
    assert res.language_code == "ar"
    assert res.script == "Arabic"
    assert res.confidence >= 0.85


def test_chinese_han_script(detector: LanguageDetector):
    text = "为我们的人工智能平台设计微服务架构和分布式数据库"
    res = detector.detect(text)
    assert res.language == "Chinese"
    assert res.language_code == "zh"
    assert res.script == "Han"
    assert res.confidence >= 0.85


def test_japanese_script(detector: LanguageDetector):
    text = "機械学習モデルのコードを生成してパイプラインを構築してください"
    res = detector.detect(text)
    assert res.language == "Japanese"
    assert res.language_code == "ja"
    assert res.script == "Japanese"
    assert res.confidence >= 0.85


def test_tamil_native_script(detector: LanguageDetector):
    text = "எனக்கு ஒரு புதிய இணைய பயன்பாடு உருவாக்க வேண்டும்"
    res = detector.detect(text)
    assert res.language == "Tamil"
    assert res.language_code == "ta"
    assert res.script == "Tamil"
    assert res.confidence >= 0.85


def test_telugu_native_script(detector: LanguageDetector):
    text = "నాకు సాఫ్ట్‌వేర్ ఆర్కిటెక్చర్ కోసం ప్రణాళిక కావాలి"
    res = detector.detect(text)
    assert res.language == "Telugu"
    assert res.language_code == "te"
    assert res.script == "Telugu"
    assert res.confidence >= 0.85


def test_russian_cyrillic_script(detector: LanguageDetector):
    text = "Разработать масштабируемую архитектуру для облачной платформы"
    res = detector.detect(text)
    assert res.language == "Russian"
    assert res.language_code == "ru"
    assert res.script == "Cyrillic"
    assert res.confidence >= 0.85


def test_english_latin_script(detector: LanguageDetector):
    text = "Build a fault-tolerant microservices architecture with Kafka and Redis"
    res = detector.detect(text)
    assert res.language == "English"
    assert res.language_code == "en"
    assert res.script == "Latin"
    assert not res.is_transliterated
    assert res.confidence >= 0.90


# ── 2. Transliteration / Romanized Indic Languages ───────────────────────

def test_romanized_gujarati_target_scenario(detector: LanguageDetector):
    """Explicit user test case: 'mare wedding planner mate prompt joiye'."""
    text = "mare wedding planner mate prompt joiye"
    res = detector.detect(text)
    assert res.language == "Gujarati"
    assert res.language_code == "gu"
    assert res.script == "Latin"
    assert res.is_transliterated is True
    assert "Gujarati (Romanized)" in res.detected_languages


def test_romanized_gujarati_conversational(detector: LanguageDetector):
    text = "kem chho tame mane ek saras python script banavi aapo"
    res = detector.detect(text)
    assert res.language == "Gujarati"
    assert res.language_code == "gu"
    assert res.is_transliterated is True


def test_romanized_hindi_hinglish(detector: LanguageDetector):
    text = "mujhe ek naya online store banane ke liye detailed business plan chahiye"
    res = detector.detect(text)
    assert res.language == "Hindi"
    assert res.language_code == "hi"
    assert res.is_transliterated is True
    assert "Hindi (Romanized)" in res.detected_languages


def test_romanized_tamil(detector: LanguageDetector):
    text = "enakku oru nalla wedding planner thevai eppadi panrathu"
    res = detector.detect(text)
    assert res.language == "Tamil"
    assert res.language_code == "ta"
    assert res.is_transliterated is True


def test_romanized_telugu(detector: LanguageDetector):
    text = "naaku oka manchi cloud architect kaavali ela cheyali"
    res = detector.detect(text)
    assert res.language == "Telugu"
    assert res.language_code == "te"
    assert res.is_transliterated is True


# ── 3. European Latin Languages ──────────────────────────────────────────

def test_spanish_detection(detector: LanguageDetector):
    text = "crear una aplicacion para gestionar tareas con microservicios y base de datos"
    res = detector.detect(text)
    assert res.language == "Spanish"
    assert res.language_code == "es"
    assert not res.is_transliterated


def test_french_detection(detector: LanguageDetector):
    text = "comment faire pour creer une architecture technique avec python et docker"
    res = detector.detect(text)
    assert res.language == "French"
    assert res.language_code == "fr"
    assert not res.is_transliterated


def test_german_detection(detector: LanguageDetector):
    text = "bitte erstellen sie eine architektur fuer cloud migration mit kubernetes"
    res = detector.detect(text)
    assert res.language == "German"
    assert res.language_code == "de"
    assert not res.is_transliterated


# ── 4. Mixed Language & Code-Switching Tests ─────────────────────────────

def test_code_switching_gujarati_and_english(detector: LanguageDetector):
    text = "mare REST API mate FastAPI ma high performance code joiye"
    res = detector.detect(text)
    assert res.language == "Gujarati"
    assert res.is_transliterated is True
    assert res.is_mixed is True
    assert "English" in res.detected_languages


def test_code_switching_devanagari_and_english(detector: LanguageDetector):
    text = "FastAPI और Docker के साथ एक REST API बनाइए"
    res = detector.detect(text)
    assert res.language == "Hindi"
    assert res.script == "Devanagari"
    assert res.is_mixed is True
    assert "English" in res.detected_languages


def test_code_switching_arabic_and_english(detector: LanguageDetector):
    text = "أريد كود Python مع Docker لنظام التوصيات"
    res = detector.detect(text)
    assert res.language == "Arabic"
    assert res.script == "Arabic"
    assert res.is_mixed is True
    assert "English" in res.detected_languages


# ── 5. Fine-Grained Script Profile Analysis ──────────────────────────────

def test_script_detector_profiles(script_detector: ScriptDetector):
    # Pure Gujarati
    p1 = script_detector.analyze_scripts("નમસ્તે")
    assert p1.primary_script == "Gujarati"
    assert p1.script_percentages["Gujarati"] == 100.0
    assert not p1.is_mixed

    # Mixed Devanagari + Latin
    p2 = script_detector.analyze_scripts("नमस्ते world")
    assert p2.is_mixed is True
    assert "Devanagari" in p2.script_counts
    assert "Latin" in p2.script_counts


# ── 6. Robustness & Boundary Conditions ──────────────────────────────────

def test_empty_and_whitespace_input(detector: LanguageDetector):
    res_empty = detector.detect("")
    assert res_empty.language == "English"
    assert res_empty.confidence == 1.0

    res_spaces = detector.detect("   \n\t   ")
    assert res_spaces.language == "English"


def test_single_word_inputs(detector: LanguageDetector):
    # Gujarati script
    res_gu = detector.detect("વેડિંગ")
    assert res_gu.language == "Gujarati"

    # Devanagari script
    res_hi = detector.detect("नमस्ते")
    assert res_hi.language == "Hindi"

    # English word
    res_en = detector.detect("Architecture")
    assert res_en.language == "English"


def test_symbols_and_numbers_only(detector: LanguageDetector):
    res_sym = detector.detect("$$$ 123456789 !!! ??? @@@")
    assert res_sym.language == "English"
    assert res_sym.script == "Latin"
