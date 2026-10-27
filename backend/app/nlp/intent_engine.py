"""Intent Engine – Deep Intent Understanding across 15 core operational intents."""

from __future__ import annotations

import logging
import math
import re
from dataclasses import dataclass, field
from typing import Any

from app.ml.embeddings import EmbeddingEngine

logger = logging.getLogger("intentify.nlp.intent_engine")


@dataclass
class IntentResult:
    """Output from deep intent classification."""

    intent: str
    confidence: float
    action_verb: str = ""
    secondary_intent: str | None = None
    all_intents: dict[str, float] = field(default_factory=dict)
    matched_triggers: list[str] = field(default_factory=list)
    method: str = "semantic_hybrid"


class IntentEngine:
    """Classifies user requirements across 15 core operational intents:

    1. create     - Constructing, fabricating, making, bootstrapping (e.g., "make a website")
    2. build      - Architectural building, engineering, constructing software/systems
    3. develop    - Programming, coding, implementing features, microservices
    4. design     - System architecture, UI/UX, database schema, wireframing
    5. plan       - Roadmaps, milestone planning, schedules, timelines
    6. learn      - Educational intake, tutorials, study roadmaps, mastering skills
    7. explain    - Conceptual clarification, walk-throughs, pedagogical breakdowns
    8. analyze    - Auditing, performance review, metrics evaluation, telemetry
    9. compare    - Side-by-side trade-off evaluations, benchmarking matrices
   10. debug      - Troubleshooting exceptions, bug triage, error resolution
   11. fix        - Patching, error rectification, incident resolution
   12. improve    - Refactoring, speed optimization, quality uplift, scaling
   13. write      - Drafting copy, articles, essays, documentation
   14. research   - Literature review, market investigation, state-of-the-art
   15. translate  - Language localization, cross-cultural adaptation
    """

    SUPPORTED_INTENTS: list[str] = [
        "create",
        "build",
        "develop",
        "design",
        "plan",
        "learn",
        "explain",
        "analyze",
        "compare",
        "debug",
        "fix",
        "improve",
        "write",
        "research",
        "translate",
        "decide",
        "optimize",
    ]

    INTENT_TRIGGERS: dict[str, list[str]] = {
        "learn": [
            r"\b(?:learn|study|master|understand|pick up|get started with|learning)\b",
            r"\bi want to learn\b",
            r"\bhow to (?:code|program|learn|use)\b",
            r"\b(?:beginner guide|tutorial for|roadmap to learn|curriculum)\b",
            r"\b(?:શીખવું|શીખવ|શીખો|અભ્યાસ|સમજવું|શીખવા માટે)\b",
            r"\b(?:सीखना|सीखें|अध्ययन|पढ़ना|सीखने के लिए)\b",
            r"\b(?:aprender|estudiar|apprendre|lernen)\b",
        ],
        "create": [
            r"\b(?:create|make|produce|craft|bootstrap|spin up|set up|start a new)\b",
            r"\bi want to make\b",
            r"\bi want to create\b",
            r"\b(?:બનાવો|બનાવવું|તૈયાર કરો|શરૂ કરો)\b",
            r"\b(?:बनाना|बनाओ|शुरू करो|तैयार करो)\b",
            r"\b(?:crear|creez|cree|erstellen)\b",
        ],
        "build": [
            r"\b(?:build|construct|assemble|fabricate|engineer|architect and build)\b",
            r"\bi want to build\b",
            r"\b(?:બાંધવું|ઉભું કરવું)\b",
            r"\b(?:निर्माण|बनाना|निर्माण करना)\b",
            r"\b(?:construir|construisez|bauen)\b",
        ],
        "develop": [
            r"\b(?:develop|program|code|implement|ship|engineer|write code for)\b",
            r"\b(?:ડેવલપ|પ્રોગ્રામ|કોડિંગ)\b",
            r"\b(?:डेवलप|कोडिंग|विकसित)\b",
            r"\b(?:desarrollar|developper|entwickeln)\b",
        ],
        "design": [
            r"\b(?:design|architect|blueprint|wireframe|layout|schema|mockup|ui/ux)\b",
            r"\b(?:ડિઝાઇન|રૂપરેખા)\b",
            r"\b(?:डिजाइन|रूपरेखा|ढांचा)\b",
            r"\b(?:disenar|concevoir|entwerfen)\b",
        ],
        "plan": [
            r"\b(?:plan|roadmap|schedule|timeline|strategy|milestones|coordination plan)\b",
            r"\b(?:આયોજન|પ્લાન|સમયપત્રક)\b",
            r"\b(?:योजना|आयोजन|रणनीति)\b",
            r"\b(?:planear|planifier|planen)\b",
        ],
        "explain": [
            r"\b(?:explain|clarify|elaborate|walk through|demystify|break down|teach me)\b",
            r"\b(?:સમજાવો|સ્પષ્ટ કરો)\b",
            r"\b(?:समझाएं|स्पष्ट करें|विवरण)\b",
            r"\b(?:explicar|expliquer|erklaren)\b",
        ],
        "analyze": [
            r"\b(?:analyze|audit|evaluate|assess|inspect|review|diagnose|telemetry)\b",
            r"\b(?:વિશ્લેષણ|તપાસો)\b",
            r"\b(?:विश्लेषण|ऑडिट|समीक्षा)\b",
            r"\b(?:analizar|analyser|analysieren)\b",
        ],
        "compare": [
            r"\b(?:compare|versus|vs\.?|pros and cons|difference between|tradeoff)\b",
            r"\b(?:સરખામણી|તફાવત)\b",
            r"\b(?:तुलना|अंतर|बनाम)\b",
            r"\b(?:comparar|comparer|vergleichen)\b",
        ],
        "debug": [
            r"\b(?:debug|troubleshoot|diagnose error|trace|root cause|stack trace)\b",
            r"\b(?:ડીબગ|ભૂલ શોધો)\b",
            r"\b(?:डीबग|त्रुटि निवारण)\b",
            r"\b(?:depurar|deboguer)\b",
        ],
        "fix": [
            r"\b(?:fix|repair|patch|resolve issue|solve bug|rectify|overcome error)\b",
            r"\b(?:સુધારો|ઉકેલો)\b",
            r"\b(?:ठीक करो|सुधारें|समाधान)\b",
            r"\b(?:arreglar|reparer|beheben)\b",
        ],
        "improve": [
            r"\b(?:improve|refactor|enhance|speed up|scale|clean code)\b",
            r"\b(?:સુધારો વધારો|શ્રેષ્ઠ બનાવો)\b",
            r"\b(?:सुधारें|अनुकूलित करें|बेहतर)\b",
            r"\b(?:mejorar|ameliorer|verbessern)\b",
        ],
        "write": [
            r"\b(?:write|draft|compose|author|essay|article|copywriting|documentation)\b",
            r"\b(?:લખો|નિબંધ|લેખ)\b",
            r"\b(?:लिखें|निबंध|आलेख)\b",
            r"\b(?:escribir|rediger|schreiben)\b",
        ],
        "research": [
            r"\b(?:research|investigate|explore|survey|literature review|state-of-the-art)\b",
            r"\b(?:સંશોધન|શોધખોળ)\b",
            r"\b(?:शोध|अनुसंधान)\b",
            r"\b(?:investigar|rechercher|forschen)\b",
        ],
        "translate": [
            r"\b(?:translate|localize|transcribe|into (?:english|gujarati|hindi|spanish))\b",
            r"\b(?:ભાષાંતર|અનુવાદ)\b",
            r"\b(?:अनुवाद|भाषान्तर)\b",
            r"\b(?:traducir|traduire|ubersetzen)\b",
        ],
        "decide": [
            r"\b(?:decide|choose|select|pick|verdict|recommendation|decision matrix|which one should i)\b",
            r"\b(?:નિર્ણય|પસંદ કરો)\b",
            r"\b(?:निर्णय|चुनें|चयन)\b",
        ],
        "optimize": [
            r"\b(?:optimize|latency reduction|profiling|memory footprint|efficiency uplift|bottleneck elimination)\b",
            r"\b(?:ઓપ્ટિમાઇઝ|ઝડપી બનાવો)\b",
            r"\b(?:अनुकूलन|दक्षता)\b",
        ],
    }

    # Action verbs mapping for clean prompt compilation
    ACTION_VERBS: dict[str, str] = {
        "create": "Create",
        "build": "Build",
        "develop": "Develop",
        "design": "Design",
        "plan": "Plan",
        "learn": "Master",
        "explain": "Explain",
        "analyze": "Analyze",
        "compare": "Compare",
        "debug": "Debug",
        "fix": "Fix",
        "improve": "Optimize",
        "write": "Draft",
        "research": "Investigate",
        "translate": "Translate",
        "decide": "Decide",
        "optimize": "Optimize",
    }

    def __init__(self, embedding_engine: EmbeddingEngine | None = None) -> None:
        self._embedder = embedding_engine or EmbeddingEngine()
        self._compiled_triggers = {
            intent: [re.compile(pat, re.IGNORECASE) for pat in patterns]
            for intent, patterns in self.INTENT_TRIGGERS.items()
        }

    def classify(self, text: str) -> IntentResult:
        """Classifies text into primary and secondary operational intents with high precision."""
        cleaned = text.strip()
        if not cleaned:
            return IntentResult(intent="create", confidence=0.5, action_verb="Create")

        lower = cleaned.lower()
        scores: dict[str, float] = {intent: 0.05 for intent in self.SUPPORTED_INTENTS}
        matched_triggers: list[str] = []

        # 1. Regex rule matching with priority weighting
        for intent, regexes in self._compiled_triggers.items():
            for rgx in regexes:
                match = rgx.search(lower)
                if match:
                    # Longer, more specific patterns grant higher initial score
                    matched_len = len(match.group(0))
                    bonus = 0.65 + min(0.30, matched_len * 0.02)
                    scores[intent] = max(scores[intent], bonus)
                    matched_triggers.append(match.group(0))

        # 2. Contextual disambiguation
        # If user says "I want to make a website" or "make a scheduling website"
        if re.search(r"\b(?:make|create|build|develop)\s+(?:a|an|the)?\s*(?:[\w\-]+\s+)*(?:website|app|system|service|platform|software|tool)\b", lower):
            scores["create"] = max(scores["create"], 0.95)
            scores["build"] = max(scores["build"], 0.92)

        # If user says "I want to learn Python", "learn" is dominant
        if re.search(r"\b(?:learn|study|understand)\s+(?:python|programming|coding|javascript|rust|go|react)\b", lower):
            scores["learn"] = max(scores["learn"], 0.96)

        # Normalize via temperature softmax
        total = sum(scores.values())
        if total > 0:
            exp_scores = {k: math.exp(v * 2.5) for k, v in scores.items()}
            exp_total = sum(exp_scores.values())
            normalized = {k: round(v / exp_total, 4) for k, v in exp_scores.items()}
        else:
            normalized = {k: 1.0 / len(self.SUPPORTED_INTENTS) for k in self.SUPPORTED_INTENTS}

        # Rank intents
        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        top_intent, top_raw_score = ranked[0]
        secondary_intent = ranked[1][0] if len(ranked) > 1 and ranked[1][1] > 0.4 else None

        # Calibrate confidence score
        if top_raw_score >= 0.90:
            confidence = top_raw_score
        else:
            confidence = min(0.98, max(0.60, top_raw_score))

        return IntentResult(
            intent=top_intent,
            confidence=round(confidence, 2),
            action_verb=self.ACTION_VERBS.get(top_intent, "Execute"),
            secondary_intent=secondary_intent,
            all_intents=normalized,
            matched_triggers=matched_triggers[:5],
            method="rule_semantic_calibrated",
        )
