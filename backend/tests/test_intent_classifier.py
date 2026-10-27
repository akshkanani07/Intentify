"""Tests for Step 6: Intent Classifier Engine."""

import pytest
from app.nlp.intent_classifier import IntentClassifier, IntentResult


@pytest.fixture
def classifier():
    return IntentClassifier()


class TestIntentClassifier:
    """Test suite verifying all 13 supported intents, multilingual recognition, and edge cases."""

    def test_all_13_supported_intents_english(self, classifier):
        test_cases = [
            ("Build a high throughput distributed microservice with FastAPI and Kafka", "create"),
            ("Draft a comprehensive executive summary for the Q3 investor presentation", "write"),
            ("Synthesize a list of 20 creative edge-case test inputs for our JSON parser", "generate"),
            ("Formulate a 90-day step-by-step engineering roadmap and timeline for cloud migration", "plan"),
            ("Perform an audit and deep-dive analysis of this PostgreSQL query execution plan", "analyze"),
            ("Explain how transformer multi-head self-attention mechanisms calculate QKV matrices step by step", "explain"),
            ("Compare PostgreSQL versus MongoDB across write throughput, ACID compliance, and schema flexibility", "compare"),
            ("Translate this customer onboarding handbook into Spanish and French", "translate"),
            ("Investigate the state-of-the-art literature on diffusion models for protein folding", "research"),
            ("Design the UI wireframe, navigation layout, and screen schema for our mobile app", "design"),
            ("Fix this NullPointerException crash in our authentication handler stack trace", "debug"),
            ("Optimize this slow Python loop to reduce latency and memory allocation by 50%", "improve"),
            ("Help me choose and decide between Apache Kafka and RabbitMQ for our architecture", "decide"),
        ]

        for text, expected_intent in test_cases:
            result = classifier.classify(text)
            assert isinstance(result, IntentResult)
            assert result.intent == expected_intent, (
                f"Failed for text: '{text}'. Expected '{expected_intent}', got '{result.intent}' (scores: {result.all_intents})"
            )
            assert result.confidence > 0.15

    def test_multilingual_gujarati_romanized(self, classifier):
        # Gujarati Romanized planning scenario
        text = "Udaipur ma destination wedding mate complete schedule ane timeline ayojan banavo"
        result = classifier.classify(text)
        assert result.intent in ["plan", "create"]
        assert result.confidence > 0.20

    def test_multilingual_gujarati_native_debug(self, classifier):
        # Native Gujarati script for debugging/fixing
        text = "આ સિસ્ટમ માં આવેલ ક્રેશ અને ભૂલ સુધારો"
        result = classifier.classify(text)
        assert result.intent == "debug"
        assert "ભૂલ સુધારો" in result.matched_keywords or "સુધારો" in result.matched_keywords or result.intent == "debug"

    def test_multilingual_hindi_romanized_compare(self, classifier):
        # Hindi Romanized comparison scenario
        text = "PostgreSQL aur MySQL ke beech me tulna karke dono ke pros and cons batao"
        result = classifier.classify(text)
        assert result.intent == "compare"
        assert result.confidence > 0.25

    def test_multilingual_devanagari_plan(self, classifier):
        # Native Devanagari planning scenario
        text = "अगले 6 महीनों के लिए विस्तृत परियोजना योजना और रोडमैप तैयार करें"
        result = classifier.classify(text)
        assert result.intent in ["plan", "create"]

    def test_multilingual_spanish_debug(self, classifier):
        text = "Depurar este error critico de conexion en la base de datos"
        result = classifier.classify(text)
        assert result.intent == "debug"

    def test_multilingual_french_improve(self, classifier):
        text = "Améliorer les performances et optimiser la vitesse de chargement"
        result = classifier.classify(text)
        assert result.intent == "improve"

    def test_secondary_intent_detection(self, classifier):
        # Compound prompt containing both comparison and decision
        text = "Compare Apache Kafka vs RabbitMQ across performance metrics and recommend which one we should decide to pick"
        result = classifier.classify(text)
        assert result.intent in ["compare", "decide"]
        assert result.secondary_intent is not None
        assert result.secondary_intent in ["compare", "decide", "analyze"]

    def test_direct_single_word_verbs(self, classifier):
        verbs = [
            ("debug", "debug"),
            ("optimize", "improve"),
            ("compare", "compare"),
            ("plan", "plan"),
            ("explain", "explain"),
            ("આયોજન", "plan"),
            ("योजना", "plan"),
        ]
        for word, expected in verbs:
            res = classifier.classify(word)
            assert res.intent == expected
            assert res.confidence >= 0.90
            assert res.method == "direct_verb"

    def test_probability_distribution_integrity(self, classifier):
        result = classifier.classify("Develop an AI autonomous agent with vector memory")
        assert len(result.all_intents) == 13
        # Check sum of probabilities equals 1.0 (within numerical tolerance)
        total_prob = sum(result.all_intents.values())
        assert 0.99 <= total_prob <= 1.01

    def test_empty_and_whitespace_input(self, classifier):
        res_empty = classifier.classify("")
        assert res_empty.intent == "create"
        assert res_empty.method == "fallback"

        res_space = classifier.classify("   \n\t  ")
        assert res_space.intent == "create"
        assert res_space.method == "fallback"
