"""Intent Classification Engine supporting 13 core prompt intents with hybrid lexical & semantic ML scoring."""

from __future__ import annotations

import logging
import math
import re
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from app.ml.embeddings import DenseSemanticEmbeddingEngine, EmbeddingEngine

logger = logging.getLogger("intentify.nlp.intent_classifier")


@dataclass
class IntentResult:
    """Output from intent classification."""

    intent: str
    confidence: float
    all_intents: dict[str, float] = field(default_factory=dict)
    secondary_intent: str | None = None
    matched_keywords: list[str] = field(default_factory=list)
    method: str = "hybrid"


class IntentClassifier:
    """Classifies user requirements across 13 core operational intents.

    Intents supported:
        1. create      - Building, developing, coding, implementing from scratch
        2. write       - Drafting copy, articles, documentation, essays, creative writing
        3. generate    - Brainstorming, synthesizing datasets, ideation, lists
        4. plan        - Roadmaps, schedules, workflows, milestone formulation
        5. analyze     - Auditing, telemetry breakdown, review, metric examination
        6. explain     - Step-by-step guides, educational breakdowns, conceptual clarification
        7. compare     - Side-by-side trade-off evaluations, benchmarking, differential analysis
        8. translate   - Language localization, cross-cultural adaptation, translation
        9. research    - Deep investigation, state-of-the-art literature review, exploration
       10. design      - System architecture, UI/UX wireframing, schema, visual modeling
       11. debug       - Troubleshooting stack traces, bug triage, root-cause resolution
       12. improve     - Performance optimization, refactoring, quality enhancement
       13. decide      - Architectural decision-making, framework/tool selection, tradeoffs
    """

    SUPPORTED_INTENTS: list[str] = [
        "create",
        "write",
        "generate",
        "plan",
        "analyze",
        "explain",
        "compare",
        "translate",
        "research",
        "design",
        "debug",
        "improve",
        "decide",
    ]

    # Multilingual keywords per intent across English, Gujarati, Hindi, Spanish, and French
    INTENT_KEYWORDS: dict[str, list[str]] = {
        "debug": [
            # English
            "fix", "fixing", "fixes", "bug", "bugs", "error", "errors", "issue", "issues",
            "troubleshoot", "troubleshooting", "debug", "debugging", "crash", "crashes",
            "crashing", "solve", "exception", "exceptions", "fail", "failures", "broken",
            "trace", "log", "reproduce", "remediation",
            # Gujarati (Romanized & Native)
            "bhul sudharo", "khoti cheez", "bhul", "ક્રેશ", "ભૂલ સુધારો", "દોષ નિવારણ", "ખામી",
            # Hindi (Romanized & Native)
            "galti theek", "dosh theek", "truti", "bug theek karo", "गलती सुधारो", "त्रुटि निवारण",
            # Spanish & French
            "depurar", "corregir", "fallo", "déboguer", "corriger", "bogue", "panne"
        ],
        "improve": [
            # English
            "optimize", "optimization", "optimizing", "refactor", "refactoring", "enhance",
            "enhancing", "enhancement", "upgrade", "upgrading", "improve", "improving",
            "improvement", "better", "speed up", "scale", "scaling", "polish", "streamline",
            "boost", "latency reduction", "performance",
            # Gujarati (Romanized & Native)
            "sudharo", "sudharvu", "sarun karo", "ગતિ વધારો", "સુધારો", "સુધારવું", "ઉત્કૃષ્ટ",
            # Hindi (Romanized & Native)
            "sudhar", "behtar", "tez karo", "सुधारो", "बेहतर बनाओ", "गति बढ़ाएं",
            # Spanish & French
            "mejorar", "optimizar", "pulir", "améliorer", "optimiser", "accélérer"
        ],
        "compare": [
            # English
            "compare", "comparing", "comparison", "difference", "differences", "versus",
            "vs", "benchmark", "benchmarking", "pros and cons", "contrast", "trade-off",
            "tradeoff", "which is better", "differential",
            # Gujarati (Romanized & Native)
            "sarkhamani", "tulna", "tafavat", "સરખામણી", "તુલના", "તફાવત",
            # Hindi (Romanized & Native)
            "tulna", "antar", "bhed", "farak", "तुलना", "अंतर", "भेद", "बनाम",
            # Spanish & French
            "comparar", "diferencia", "frente a", "comparer", "différence", "contre"
        ],
        "decide": [
            # English
            "choose", "choosing", "select", "selecting", "selection", "recommend",
            "recommendation", "decide", "deciding", "decision", "evaluating options",
            "pick", "choice", "verdict", "should i use", "which should",
            # Gujarati (Romanized & Native)
            "pasandgi", "nirnay", "chuno", "પસંદગી", "નિર્ણય", "કયું પસંદ કરવું",
            # Hindi (Romanized & Native)
            "faisla", "chayan", "nirnay", "chuno", "फैसला", "निर्णय", "चयन", "कौन सा चुनें",
            # Spanish & French
            "decidir", "elegir", "seleccionar", "décider", "choisir", "sélectionner"
        ],
        "analyze": [
            # English
            "analyze", "analyzing", "analysis", "audit", "auditing", "breakdown",
            "assess", "assessing", "assessment", "evaluate", "evaluating", "evaluation",
            "inspect", "inspection", "metrics", "review", "reviewing", "examination",
            "data", "deep dive", "deep-dive", "telemetry", "profiling",
            # Gujarati (Romanized & Native)
            "tapas", "vishleshan", "mulyankan", "તપાસ", "વિશ્લેષણ", "મૂલ્યાંકન",
            # Hindi (Romanized & Native)
            "vishleshan", "jaanch", "samiksha", "mulyankan", "विश्लेषण", "समीक्षा", "जांच",
            # Spanish & French
            "analizar", "evaluar", "auditar", "analyser", "évaluer", "auditer"
        ],
        "research": [
            # English
            "research", "researching", "investigate", "investigating", "explore",
            "survey", "find out", "study", "literature", "state of the art", "discover", "findings", "sota",
            # Gujarati (Romanized & Native)
            "shodh", "sanshodhan", "tapash", "શોધ", "સંશોધન", "અભ્યાસ",
            # Hindi (Romanized & Native)
            "khoj", "anushandhan", "shodh", "adhyayan", "शोध", "खोज", "अनुसंधान", "अध्ययन",
            # Spanish & French
            "investigar", "estudiar", "rechercher", "étudier", "explorer"
        ],
        "plan": [
            # English
            "plan", "planning", "plans", "roadmap", "strategy", "strategies", "schedule",
            "scheduling", "milestone", "milestones", "timeline", "step-by-step", "workflow",
            "organize", "organizing", "itinerary", "wedding",
            # Gujarati (Romanized & Native)
            "ayojan", "plan", "yojna", "karyakram", "આયોજન", "પ્લાન", "તૈયારી", "રોડમેપ",
            # Hindi (Romanized & Native)
            "yojana", "taiyari", "karyakram", "samay-sarani", "योजना", "तैयारी", "कार्यक्रम",
            # Spanish & French
            "planear", "planificar", "hoja de ruta", "planifier", "itinéraire", "stratégie"
        ],
        "design": [
            # English
            "design", "designing", "ui", "ux", "architecture", "wireframe", "schema",
            "prototype", "prototyping", "layout", "visual", "mockup", "blueprint", "diagram", "interface",
            # Gujarati (Romanized & Native)
            "naksho", "design", "aarekhan", "ડિઝાઇન", "આરેખન", "નકશો",
            # Hindi (Romanized & Native)
            "rooprekha", "praroop", "design", "naksha", "रूपरेखा", "प्रारूप", "डिज़ाइन",
            # Spanish & French
            "diseñar", "diseño", "esquema", "concevoir", "maquette", "schéma"
        ],
        "translate": [
            # English
            "translate", "translating", "translation", "localize", "localizing", "localization",
            "convert language", "multilingual", "transliterate", "interpretation",
            # Gujarati (Romanized & Native)
            "bhashantar", "anuvad", "ભાષાંતર", "અનુવાદ", "રૂપાંતર",
            # Hindi (Romanized & Native)
            "anuvad", "tarjuma", "bhashantar", "अनुवाद", "तर्जुमा", "भाषांतर",
            # Spanish & French
            "traducir", "traducción", "localizar", "traduire", "traduction", "adapter"
        ],
        "explain": [
            # English
            "explain", "explaining", "explanation", "teach", "teaching", "understand",
            "clarify", "clarifying", "clarification", "how does", "what is", "guide me",
            "tutorial", "overview", "demystify", "walkthrough", "concept", "why does",
            # Gujarati (Romanized & Native)
            "samjavo", "samjavvu", "spashtata", "સમજાવો", "સમજાવવું", "સ્પષ્ટ કરો",
            # Hindi (Romanized & Native)
            "samjhao", "batao", "samjhana", "spasht karo", "समझाइए", "समझाओ", "बताओ",
            # Spanish & French
            "explicar", "aclarar", "enseñar", "expliquer", "clarifier", "enseigner"
        ],
        "write": [
            # English
            "write", "writing", "draft", "drafting", "compose", "composing", "essay",
            "email", "article", "blog", "story", "speech", "documentation", "copywriting", "script", "letter",
            # Gujarati (Romanized & Native)
            "lakho", "lakhvu", "nibandh", "lekh", "લખો", "લખવું", "નિબંધ", "લેખ",
            # Hindi (Romanized & Native)
            "likho", "likhna", "lekh", "patra", "लिखो", "लिखना", "लेख", "पत्र",
            # Spanish & French
            "escribir", "redactar", "componer", "écrire", "rédiger", "composer"
        ],
        "generate": [
            # English
            "generate", "generating", "produce", "synthesize", "synthesizing", "list",
            "ideas", "brainstorm", "test cases", "sample data", "mock data", "catalog", "prompts",
            # Gujarati (Romanized & Native)
            "utpann", "vicharo", "yadi", "ઉત્પન્ન કરો", "યાદી", "વિચારો",
            # Hindi (Romanized & Native)
            "utpann", "srijan", "suchi", "उत्पन्न", "सृजन", "सूची", "विचार",
            # Spanish & French
            "generar", "sintetizar", "générer", "synthétiser", "produire"
        ],
        "create": [
            # English
            "create", "creating", "creation", "build", "building", "develop", "developing",
            "development", "implement", "implementing", "implementation", "make", "construct",
            "setup", "initialize", "craft", "code", "author", "formulate",
            # Gujarati (Romanized & Native)
            "banavo", "banavvu", "rachna", "બનાવો", "બનાવવું", "રચના",
            # Hindi (Romanized & Native)
            "banao", "banana", "nirman", "तैयार करो", "बनाओ", "बनाना", "निर्माण",
            # Spanish & French
            "crear", "construir", "desarrollar", "créer", "construire", "développer"
        ],
    }

    # Canonical semantic representations for dense subspace projection
    INTENT_SEMANTIC_ANCHORS: dict[str, str] = {
        "create": "Build, develop, implement, and engineer a full new software system or functional component from scratch.",
        "write": "Draft, write, and compose high-quality prose, documentation, article, essay, or email communication.",
        "generate": "Brainstorm, synthesize, and produce a creative list, dataset, mock examples, or ideas.",
        "plan": "Formulate a detailed strategic plan, roadmap, timeline, schedule, or operational milestone workflow.",
        "analyze": "Examine, review, audit, inspect, and evaluate data, architecture, performance, or telemetry metrics.",
        "explain": "Clarify, teach, and explain complex concepts, algorithms, mechanics, or architectural patterns step-by-step.",
        "compare": "Perform a comparative trade-off analysis, benchmark, differential comparison, and pros-and-cons evaluation.",
        "translate": "Translate, localize, and adapt text across languages and cultural terminology.",
        "research": "Investigate, explore, survey literature, and conduct rigorous academic or scientific state-of-the-art research.",
        "design": "Design user interfaces, visual wireframes, UX workflows, system architectures, and database schemas.",
        "debug": "Triage, troubleshoot, trace root-causes, and resolve bugs, runtime exceptions, and system failures.",
        "improve": "Refactor, optimize, enhance performance, reduce latency, and polish existing codebases or workflows.",
        "decide": "Recommend and decide between multiple architectural options, frameworks, or strategic directions.",
    }

    def __init__(self, embedding_engine: EmbeddingEngine | None = None) -> None:
        self._embedding_engine = embedding_engine or EmbeddingEngine()
        self._anchor_vectors: dict[str, np.ndarray] = {}
        self._precompute_anchor_vectors()

    def _precompute_anchor_vectors(self) -> None:
        """Precompute 384-dimensional dense vectors for all 13 intent semantic anchors."""
        for intent, anchor_text in self.INTENT_SEMANTIC_ANCHORS.items():
            self._anchor_vectors[intent] = self._embedding_engine.encode_single(anchor_text)

    def classify(self, text: str) -> IntentResult:
        """Classify input text into one of the 13 supported intents using hybrid lexical + semantic scoring."""
        if not text or not text.strip():
            uniform = {intent: round(1.0 / len(self.SUPPORTED_INTENTS), 4) for intent in self.SUPPORTED_INTENTS}
            return IntentResult(
                intent="create",
                confidence=0.50,
                all_intents=uniform,
                secondary_intent=None,
                matched_keywords=[],
                method="fallback",
            )

        text_clean = text.strip()
        text_lower = text_clean.lower()

        # Check for direct single-word or short exact verb intent commands
        direct_verb = self._check_direct_intent_verb(text_clean)
        if direct_verb:
            all_intents = {i: (0.95 if i == direct_verb else 0.05 / 12) for i in self.SUPPORTED_INTENTS}
            return IntentResult(
                intent=direct_verb,
                confidence=0.95,
                all_intents=all_intents,
                secondary_intent=None,
                matched_keywords=[text_clean],
                method="direct_verb",
            )

        # 1. Lexical Matching across multilingual keywords (longest keywords first to prevent sub-token collisions)
        lexical_scores: dict[str, float] = {intent: 0.0 for intent in self.SUPPORTED_INTENTS}
        matched_keywords: list[str] = []

        # Context exclusion: phrases where "plan" is an object/noun, not the directive action
        masked_text = text_lower
        for non_plan_phrase in ["execution plan", "query plan", "floor plan", "data plan", "test plan"]:
            masked_text = masked_text.replace(non_plan_phrase, "query_artifact")

        all_kw_items: list[tuple[str, str]] = []
        for intent, kws in self.INTENT_KEYWORDS.items():
            for kw in kws:
                all_kw_items.append((intent, kw))
        all_kw_items.sort(key=lambda item: len(item[1]), reverse=True)

        matched_intervals: list[tuple[int, int]] = []
        for intent, kw in all_kw_items:
            pat = r"(?:^|[^\w\u0A80-\u0AFF\u0900-\u097F])(" + re.escape(kw.lower()) + r")(?:[^\w\u0A80-\u0AFF\u0900-\u097F]|$)"
            for match in re.finditer(pat, masked_text):
                start, end = match.span(1)
                # Avoid overlapping with a previously matched longer keyword
                if not any(s <= start and end <= e for s, e in matched_intervals):
                    matched_intervals.append((start, end))
                    weight = 3.0 if len(kw.split()) > 1 else 1.8
                    lexical_scores[intent] += weight
                    matched_keywords.append(kw)

        # 2. Semantic Subspace Cosine Similarity
        query_vec = self._embedding_engine.encode_single(text_clean)
        semantic_scores: dict[str, float] = {}

        for intent, anchor_vec in self._anchor_vectors.items():
            cos_sim = float(np.dot(query_vec, anchor_vec))
            semantic_scores[intent] = max(0.0, cos_sim + 1.0)

        # 3. Hybrid Fusion & Softmax Calibration
        max_lex = max(lexical_scores.values())
        if max_lex > 0:
            alpha = 0.65
        else:
            alpha = 0.10

        logits = np.array([
            alpha * lexical_scores[intent] + (1.0 - alpha) * semantic_scores[intent]
            for intent in self.SUPPORTED_INTENTS
        ])

        # Temperature-calibrated softmax (temperature = 0.65 for clean distinction)
        temperature = 0.65
        exp_logits = np.exp((logits - np.max(logits)) / temperature)
        probs = exp_logits / np.sum(exp_logits)

        prob_dict = {
            self.SUPPORTED_INTENTS[idx]: round(float(probs[idx]), 4)
            for idx in range(len(self.SUPPORTED_INTENTS))
        }

        # Sort intents by probability
        ranked = sorted(prob_dict.items(), key=lambda kv: kv[1], reverse=True)
        top_intent, top_conf = ranked[0]
        second_intent = ranked[1][0] if len(ranked) > 1 and ranked[1][1] >= 0.12 else None

        return IntentResult(
            intent=top_intent,
            confidence=top_conf,
            all_intents=prob_dict,
            secondary_intent=second_intent,
            matched_keywords=list(set(matched_keywords)),
            method="hybrid",
        )

    def _check_direct_intent_verb(self, text: str) -> str | None:
        """Detect if input is a single action verb or very short direct imperative."""
        words = text.strip().split()
        if len(words) == 1:
            first = words[0].lower()
            if first in self.SUPPORTED_INTENTS:
                return first
            # Common synonyms as single words
            synonyms = {
                "build": "create", "fix": "debug", "audit": "analyze",
                "roadmap": "plan", "review": "analyze", "clarify": "explain",
                "teach": "explain", "enhance": "improve", "optimize": "improve",
                "select": "decide", "choose": "decide", "ayojan": "plan",
                "આયોજન": "plan", "બનાવો": "create", "લખો": "write",
                "योजना": "plan", "बनाओ": "create", "लिखो": "write"
            }
            if first in synonyms:
                return synonyms[first]
        return None
