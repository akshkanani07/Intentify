"""AudienceDetector – detects target audience archetype and experience level from user input."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("intentify.nlp.audience_detector")


@dataclass
class AudienceResult:
    """Structured audience and experience level analysis."""

    target_audience: str
    experience_level: str
    confidence: float
    detected_markers: list[str] = field(default_factory=list)
    pedagogical_mode: bool = False
    explicit_self_seniority: bool = False


class AudienceDetector:
    """Analyzes text to infer the target audience and technical/domain experience level.

    Supports multilingual markers (English, Gujarati, Hindi).
    Strict priority order:
      (a) Explicit self-description in user text (ALWAYS wins).
      (b) Explicit role in request (role_hint).
      (c) Action = learn -> default to Beginner unless (a) or (b) contradicts it.
      (d) Technical vocabulary is WEAK evidence (for non-learning only).
    """

    SENIOR_SELF_PATTERNS = [
        r"\b(?:i\s+am\s+(?:a\s+)?senior|i'm\s+(?:a\s+)?senior|as\s+a\s+senior|senior\s+(?:software\s+)?(?:engineer|developer|architect)|principal\s+(?:software\s+)?(?:engineer|architect)|\d+\+?\s*years?(?:\s+of)?\s+experience)\b",
        r"(?:હું\s+સિનિયર\s+છું|સિનિયર\s+એન્જિનિયર|વર્ષોનો\s+અનુભવ)",
        r"(?:मैं\s+सीनियर\s+हूँ|वरिष्ठ\s+इंजीनियर|वर्षों\s+का\s+अनुभव)",
    ]

    BEGINNER_SELF_PATTERNS = [
        r"\b(?:i\s+am\s+(?:a\s+)?beginner|i'm\s+(?:a\s+)?beginner|as\s+a\s+beginner|new\s+to\s+this|new\s+to\s+programming|first\s+time|just\s+starting|student|i\s+am\s+(?:a\s+)?student|i'm\s+(?:a\s+)?student|newbie|novice)\b",
        r"\b(?:like\s+i(?:'m|\s+am)\s+\d+|eli5|explain\s+simply|for\s+(?:a\s+)?child|for\s+beginners|from\s+scratch|basics?\s+only)\b",
        r"(?:હું\s+નવો\s+છું|હું\s+શિખાઉ\s+છું|હું\s+વિદ્યાર્થી\s+છું|પહેલી\s+વાર|શરૂઆતથી|સરળ\s+ભાષામાં)",
        r"(?:मैं\s+शुरुआती\s+हूँ|मैं\s+नया\s+हूँ|पहली\s+बार|शुरुआती\s+स्तर|छात्र\s+हूँ|सरल\s+भाषा\s+में)",
    ]

    ADVANCED_TECH_PATTERNS = [
        r"\b(?:production|scalable|distributed|multi-region|high\s+performance|high\s+availability|zero\s+trust|fault\s+tolerant|segfault|segmentation\s+fault|deadlock|memory\s+leak|oom|concurrency|kafka\s+cluster|microservice|microservices|commercial\s+ev\s+fleet|fleet|franchise\s+expansion|gtm\s+strategy|unit\s+economics|hipaa|satellite|collision\s+avoidance|sub-millisecond|p99|deep\s+dive|expert|mission\s+critical)\b",
        r"\b(?:franchise|expansion|sop|cold-chain|distribution|go-to-market|gtm|cac|fleet|commercial|export|scaling|pricing\s+strategy|microgrid)\b",
        r"\b(?:orbital|space\s+debris|sequestration|carbon\s+credit|acoustic\s+sensor)\b",
        r"\b(?:hospital\s+management|telemedicine|triage|ehr|emr|audit|clinical\s+software)\b",
        r"\b(?:ingress|netty|fastapi|spring\s+boot|mw|solar|grid|enterprise|governance|compliance|executive|abm|b2b)\b",
        r"\b(?:ઉચ્ચ|સિનિયર|જટિલ|પ્રોડક્શન|વિસ્તાર|નિકાસ|વેપાર|ટેક્સટાઈલ|ડેરી|સપ્લાય|કોલ્ડ|સ્ટોરેજ|ડિસ્ટ્રિબ્યુશન|સોલર|ગ્રીડ|મોડેલિંગ|મેગાવોટ)\b",
        r"\b(?:उन्नत|वरिष्ठ|जटिल|उत्पादन|विस्तार|व्यापार|कैफे|क्लाउड\s+किचन|सप्लाई|कोल्ड|स्टोरेज|वितरण|सोलर|ग्रिड)\b",
    ]

    VAGUE_PATTERNS = [
        r"\b(?:kuch\s+(?:banao|build|banavo|make|naya)|help\s+me|help|make\s+something|give\s+code|idea\s+batao|કંઈક\s+બનાવો|કંઈક\s+નવું|कुछ\s+બનાઓ|कुछ\s+बनाओ|મદદ\s+કરો)\b",
    ]

    AUDIENCE_PATTERNS = {
        "Students & Learners": [
            r"\b(?:student|learner|beginner|scratch|basics?|tutorial|teach|learn|school|college|university)\b",
            r"\b(?:વિદ્યાર્થી|શીખવું|શરૂઆત|મૂળભૂત|વિદ્યાર્થીઓ)\b",
            r"\b(?:छात्र|सीखना|शुरुआती|मूलभूत|ट्यूटोरियल)\b",
        ],
        "Software Engineers & Architects": [
            r"\b(?:developer|engineer|coder|programmer|architect|devops|backend|frontend|fullstack|sre)\b",
            r"\b(?:ડેવલપર|એન્જિનિયર|પ્રોગ્રામર|આર્કિટેક્ટ)\b",
            r"\b(?:डेवलपर|इंजीनियर|प्रोग्रामर|आर्किटेक्ट)\b",
        ],
        "Enterprise Leadership & Executives": [
            r"\b(?:executive|c-level|ceo|cto|cfo|director|stakeholder|investor|leadership|board|management|enterprise)\b",
            r"\b(?:મેનેજમેન્ટ|લીડરશીપ|ડિરેક્ટર|રોકાણકાર)\b",
            r"\b(?:प्रबंधन|नेतृत्व|निवेशक|कार्यकारी)\b",
        ],
        "Medical & Healthcare Clinicians": [
            r"\b(?:doctor|clinician|nurse|physician|surgeon|patient|medical\s+staff|healthcare\s+workers)\b",
            r"\b(?:ડોક્ટર|તબીબ|દર્દી|નર્સ)\b",
            r"\b(?:डॉक्टर|चिकित्सक|मरीज|रोगी)\b",
        ],
        "Legal & Regulatory Counsel": [
            r"\b(?:lawyer|attorney|counsel|judge|paralegal|compliance\s+officer|litigant)\b",
            r"\b(?:વકીલ|ન્યાયાધીશ|કાનૂની\s+સલાહકાર)\b",
            r"\b(?:वकील|न्यायाधीश|कानूनी\s+सलाहकार)\b",
        ],
        "Marketing & Growth Practitioners": [
            r"\b(?:marketer|advertiser|growth\s+hacker|copywriter|brand\s+manager|sales\s+rep)\b",
            r"\b(?:માર્કેટર|સેલ્સ|જાહેરાત)\b",
            r"\b(?:विपणक|बिक्री|विज्ञापन)\b",
        ],
        "General End-Users & Consumers": [
            r"\b(?:user|consumer|customer|public|client|visitor|shopper|guest)\b",
            r"\b(?:ગ્રાહક|વપરાશકર્તા|મુલાકાતી)\b",
            r"\b(?:उपयोगकर्ता|ग्राहक|जनता)\b",
        ],
    }

    def detect(self, text: str, role_hint: str = "", domain_hint: str = "", action_hint: str = "") -> AudienceResult:
        """Infer target audience archetype and experience level from text and contextual hints."""
        text_clean = text.strip()
        text_lower = text_clean.lower()
        role_clean = role_hint.strip()
        role_lower = role_clean.lower()

        # Check learning intent indicators
        is_learning = (
            action_hint.lower() in ("learn", "study", "teach")
            or any(k in text_lower for k in [
                "learn", "study", "curriculum", "teach", "tutorial", "syllabus",
                "shikhvu", "shikhavu", "sikho", "sikhvu",
                "શીખવું", "શીખવ", "સીખના", "સીખવું", "सीखना", "सीखनी", "सीखें", "पढ़ना", "पढ़ाई", "पढ़ना", "पढ़ाई"
            ])
        )

        # -------------------------------------------------------------
        # TIER A: Explicit self-description in user text (ALWAYS wins)
        # -------------------------------------------------------------
        # 1. Senior self-description
        for pat in self.SENIOR_SELF_PATTERNS:
            if re.search(pat, text_lower, re.I):
                exp = "Principal / Enterprise Architect" if ("principal" in text_lower or "enterprise architect" in text_lower) else "Advanced / Senior"
                return AudienceResult(
                    target_audience="Software Engineers & Architects",
                    experience_level=exp,
                    confidence=0.98,
                    detected_markers=["explicit_senior_self_description"],
                    pedagogical_mode=is_learning,
                    explicit_self_seniority=True,
                )

        # 2. Beginner self-description
        for pat in self.BEGINNER_SELF_PATTERNS:
            if re.search(pat, text_lower, re.I):
                return AudienceResult(
                    target_audience="Students & Learners",
                    experience_level="Novice / Beginner",
                    confidence=0.98,
                    detected_markers=["explicit_beginner_self_description"],
                    pedagogical_mode=True,
                    explicit_self_seniority=False,
                )

        # -------------------------------------------------------------
        # TIER B: Explicit role in request (role_hint)
        # -------------------------------------------------------------
        if role_lower:
            if re.search(r"\b(?:student|learner|intern|beginner|novice|junior)\b", role_lower):
                return AudienceResult(
                    target_audience="Students & Learners",
                    experience_level="Novice / Beginner",
                    confidence=0.95,
                    detected_markers=["explicit_learner_role_hint"],
                    pedagogical_mode=True,
                    explicit_self_seniority=False,
                )
            if re.search(r"\b(?:principal|distinguished|enterprise\s+architect)\b", role_lower):
                return AudienceResult(
                    target_audience="Software Engineers & Architects",
                    experience_level="Principal / Enterprise Architect",
                    confidence=0.95,
                    detected_markers=["explicit_principal_role_hint"],
                    pedagogical_mode=is_learning,
                    explicit_self_seniority=True,
                )
            if re.search(r"\b(?:senior|lead|staff|architect|expert|director|head)\b", role_lower):
                return AudienceResult(
                    target_audience="Software Engineers & Architects",
                    experience_level="Advanced / Senior",
                    confidence=0.95,
                    detected_markers=["explicit_senior_role_hint"],
                    pedagogical_mode=is_learning,
                    explicit_self_seniority=True,
                )

        # -------------------------------------------------------------
        # TIER C: Action = learn -> default to Beginner unless (a) or (b) contradicts it
        # HARD RULE: A learn-intent input NEVER resolves to Senior or Expert
        # -------------------------------------------------------------
        if is_learning:
            return AudienceResult(
                target_audience="Students & Learners",
                experience_level="Novice / Beginner",
                confidence=0.90,
                detected_markers=["learning_action_default"],
                pedagogical_mode=True,
                explicit_self_seniority=False,
            )

        # -------------------------------------------------------------
        # TIER D: Technical vocabulary is WEAK evidence (for non-learning only)
        # -------------------------------------------------------------
        # Vague input check -> Beginner
        for pat in self.VAGUE_PATTERNS:
            if re.search(pat, text_lower, re.I):
                return AudienceResult(
                    target_audience="General End-Users & Consumers",
                    experience_level="Novice / Beginner",
                    confidence=0.85,
                    detected_markers=["vague_input"],
                    pedagogical_mode=False,
                    explicit_self_seniority=False,
                )

        # Audience archetype matching
        combined = f"{role_hint} {text} {domain_hint}".lower()
        detected_audience = "General Stakeholders & Practitioners"
        max_audience_score = 0
        detected_markers: list[str] = []

        for aud_label, patterns in self.AUDIENCE_PATTERNS.items():
            matches = 0
            for pat in patterns:
                found = re.findall(pat, combined)
                if found:
                    matches += len(found)
                    detected_markers.extend(found[:2])
            if matches > max_audience_score:
                max_audience_score = matches
                detected_audience = aud_label

        if max_audience_score == 0:
            if any(k in combined for k in ["code", "software", "api", "website", "database", "python"]):
                detected_audience = "Software Engineers & Architects"
            elif any(k in combined for k in ["health", "hospital", "patient", "clinical", "medical"]):
                detected_audience = "Medical & Healthcare Clinicians"
            elif any(k in combined for k in ["market", "campaign", "ad", "growth", "seo"]):
                detected_audience = "Marketing & Growth Practitioners"
            elif any(k in combined for k in ["legal", "contract", "law", "court"]):
                detected_audience = "Legal & Regulatory Counsel"

        # Advanced technical vocabulary check for non-learning requests
        for pat in self.ADVANCED_TECH_PATTERNS:
            if re.search(pat, combined, re.I):
                return AudienceResult(
                    target_audience=detected_audience,
                    experience_level="Advanced / Senior",
                    confidence=0.85,
                    detected_markers=list(set(detected_markers))[:5],
                    pedagogical_mode=False,
                    explicit_self_seniority=False,
                )

        return AudienceResult(
            target_audience=detected_audience,
            experience_level="Intermediate / Practitioner",
            confidence=0.80,
            detected_markers=list(set(detected_markers))[:5],
            pedagogical_mode=False,
            explicit_self_seniority=False,
        )
