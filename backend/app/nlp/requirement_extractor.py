"""Requirement Extraction Engine extracting all 11 core prompt dimensions with deep NLP parsing."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field, asdict
from typing import Any

from app.nlp.entity_extractor import Entity, EntityExtractor

logger = logging.getLogger("intentify.nlp.requirement_extractor")


@dataclass
class Requirements:
    """Structured requirements extracted from user text across all 11 dimensions."""

    goal: str = ""
    audience: str = "general audience"
    tone: str = "professional"
    format: str = "Detailed Technical Response"
    constraints: list[str] = field(default_factory=list)
    deadline: str = ""
    budget: str = ""
    platform: str = ""
    location: str = ""
    entities: list[dict[str, Any]] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RequirementExtractor:
    """Extracts all 11 requirement dimensions:

    1. Goal               - Primary intended objective or assignment deliverable
    2. Audience           - Intended recipients, stakeholders, or user persona
    3. Tone               - Linguistic register, style, and voice
    4. Format             - Deliverable output structure (mapped to catalog templates)
    5. Constraints        - Technical, operational, and negative boundaries
    6. Deadline           - Target timeframe, completion schedule, or SLA
    7. Budget             - Financial parameters or cost ceilings
    8. Platform           - Deployment environment, OS, runtime, or cloud ecosystem
    9. Location           - Geographic venue, city, or physical/cloud deployment region
   10. Entities           - Structured named entities (technologies, metrics, organizations)
   11. Success Criteria   - Explicit, verifiable validation metrics and acceptance conditions
    """

    AUDIENCE_PATTERNS: dict[str, list[str]] = {
        "beginners": [
            r"\b(?:beginners?|novices?|starters?|dummies|laymen|non-technical|students?)\b",
            r"\b(?:shuruat|navsikhya|વિદ્યાર્થી)\b",
        ],
        "executives": [
            r"\b(?:executives?|c-suite|c-level|ceo|cto|cfo|coo|board|investors?|leadership|management|stakeholders)\b",
            r"\b(?:leadership team|venture capital|decision-makers?)\b",
        ],
        "developers": [
            r"\b(?:developers?|programmers?|engineers?|devs?|architects?|coders?|technical leads?)\b",
        ],
        "wedding_guests": [
            r"\b(?:wedding guests?|bride and groom|family|attendees|baratis?|parivar|mehmaan|મહેમાન|લગ્ન ના મહેમાન)\b",
        ],
        "medical_professionals": [
            r"\b(?:doctors?|physicians?|surgeons?|nurses?|clinical staff|practitioners?|patients?)\b",
        ],
        "legal_clients": [
            r"\b(?:clients?|legal counsel|compliance officers?|court|arbitrators?)\b",
        ],
        "b2b_clients": [
            r"\b(?:clients?|customers?|buyers?|prospects?|enterprise customers?|b2b users?)\b",
        ],
    }

    TONE_PATTERNS: dict[str, list[str]] = {
        "authoritative": [
            r"\b(?:authoritative|decisive|rigorous|expert-level|uncompromising|firm)\b",
        ],
        "concise": [
            r"\b(?:concise|short|brief|bullet-points|quick|terse|compact|summary-only|tl;?dr)\b",
            r"\b(?:tunkma|sankshipt|ટૂંકમાં|संक्षिप्त)\b",
        ],
        "conversational": [
            r"\b(?:conversational|friendly|casual|engaging|warm|approachable|informal)\b",
        ],
        "technical": [
            r"\b(?:technical|in-depth|deep-dive|architectural|exhaustive|rigorous|low-level)\b",
        ],
        "persuasive": [
            r"\b(?:persuasive|pitch|sales|compelling|convincing|high-converting|influence)\b",
        ],
        "academic": [
            r"\b(?:academic|scholarly|formal|scientific|peer-reviewed|methodological)\b",
        ],
        "professional": [
            r"\b(?:professional|business|enterprise|corporate|executive|formal)\b",
        ],
    }

    FORMAT_PATTERNS: dict[str, list[str]] = {
        "Comparison Matrix Table": [
            r"\b(?:table|matrix|comparison grid|spreadsheet|side-by-side table|tabular)\b",
            r"\b(?:tulna table|સરખામણી કોષ્ટક)\b",
        ],
        "Step-by-Step Implementation Guide": [
            r"\b(?:step-by-step|guide|walkthrough|tutorial|steps|procedure|how-to)\b",
            r"\b(?:ek pachi ek pagla|चरण-दर-चरण)\b",
        ],
        "Production Code with Inline Architectural Annotations": [
            r"\b(?:code|code snippet|implementation|script|repository|full code|runnable code)\b",
        ],
        "Strict JSON Schema & Payload": [
            r"\b(?:json|schema|api response|payload|json format|structured data)\b",
        ],
        "Executive Brief": [
            r"\b(?:executive brief|memo|whitepaper|executive summary|1-pager|one-pager)\b",
        ],
        "Event Master Coordination Plan": [
            r"\b(?:event master coordination plan|coordination plan|event plan|wedding plan|itinerary|run of show|coordination schedule|wedding schedule)\b",
            r"\b(?:lagan no karyakram|આયોજન પ્લાન)\b",
        ],
        "Concise Bulleted Summary": [
            r"\b(?:bullet points?|bulleted|list|checklist|bullet list|quick list)\b",
        ],
        "Architectural Decision Record (ADR)": [
            r"\b(?:adr|architectural decision record|design doc|rfc)\b",
        ],
        "Detailed Technical Response": [
            r"\b(?:detailed response|comprehensive report|in-depth document|specification)\b",
        ],
    }

    CONSTRAINT_TRIGGERS: list[str] = [
        "must not", "do not", "avoid", "never", "limit to", "limit", "maximum of", "minimum of",
        "under", "without", "strictly", "no external", "cannot", "only use", "should not",
        "excluding", "zero", "keep under", "restrict to", "restrict", "neither", "prohibit", "cap at"
    ]

    GOAL_PREAMBLE_PATTERNS: list[str] = [
        r"^(?:i am want to|a want to|want to|i want to|i need to|please|can you|could you|help me(?: learn)?|the goal is to|objective is to|prompt for|prompt mate|prompt chahiye for)\s+",
        r"^(?:mare\s+[a-zA-Z\s]+?\s+mate prompt joiye|mujhe\s+[a-zA-Z\s]+?\s+ke liye prompt chahiye)\s*",
        r"^(?:act as a?|you are a?)\s+[a-zA-Z\s]+?(?:to|for)\s+",
    ]

    def __init__(self, entity_extractor: EntityExtractor | None = None) -> None:
        self._entity_extractor = entity_extractor or EntityExtractor()

    def extract(self, text: str, entities: list[Entity] | None = None) -> Requirements:
        """Extract all 11 requirement dimensions from text."""
        if not text or not text.strip():
            return Requirements(
                goal="Execute user directive with principal-grade precision.",
                audience="general audience",
                tone="professional",
                format="Detailed Technical Response",
                constraints=["Maintain production-ready standards", "Zero placeholders"],
                deadline="",
                budget="",
                platform="",
                location="",
                entities=[],
                success_criteria=[
                    "Fulfills the core objective completely",
                    "Contains zero ambiguity or unverified claims",
                    "Adheres strictly to professional standards",
                ],
            )

        clean_text = text.strip()
        text_lower = clean_text.lower()

        # Extract entities if not passed in
        if entities is None:
            entities = self._entity_extractor.extract(clean_text)

        # 1. Goal Extraction
        goal = self._extract_goal(clean_text)

        # 2. Audience Detection
        detected_audience = "general audience"
        for aud, pats in self.AUDIENCE_PATTERNS.items():
            if any(re.search(p, text_lower) for p in pats):
                detected_audience = aud
                break

        # 3. Tone Detection
        detected_tone = "professional"
        for tone_name, pats in self.TONE_PATTERNS.items():
            if any(re.search(p, text_lower) for p in pats):
                detected_tone = tone_name
                break

        # 4. Format Detection (mapped to catalog formats)
        detected_format = "Detailed Technical Response"
        explicit_fmt = re.search(r"format\s*:\s*([^\n\.;]+)", clean_text, re.IGNORECASE)
        if explicit_fmt:
            cand = explicit_fmt.group(1).strip().lower()
            for fmt_name in self.FORMAT_PATTERNS.keys():
                if cand in fmt_name.lower() or fmt_name.lower() in cand:
                    detected_format = fmt_name
                    break

        if detected_format == "Detailed Technical Response":
            for fmt_name, pats in self.FORMAT_PATTERNS.items():
                if any(re.search(p, text_lower) for p in pats):
                    detected_format = fmt_name
                    break

        # 5. Constraints Extraction
        constraints = self._extract_constraints(clean_text)

        # 6. Deadline Extraction
        deadline = self._extract_deadline(clean_text, entities)

        # 7. Budget Extraction
        budget = self._extract_budget(clean_text, entities)

        # 8. Platform Extraction
        platform = self._extract_platform(clean_text, entities)

        # 9. Location Extraction
        location = self._extract_location(clean_text, entities)

        # 10. Entities formatting
        entities_dicts = [e.to_dict() for e in entities]

        # 11. Success Criteria Formulation
        success_criteria = self._formulate_success_criteria(
            goal=goal,
            format_name=detected_format,
            tone=detected_tone,
            constraints=constraints,
            deadline=deadline,
            budget=budget,
        )

        return Requirements(
            goal=goal,
            audience=detected_audience,
            tone=detected_tone,
            format=detected_format,
            constraints=constraints,
            deadline=deadline,
            budget=budget,
            platform=platform,
            location=location,
            entities=entities_dicts,
            success_criteria=success_criteria,
        )

    def _extract_goal(self, text: str) -> str:
        """Extract the core objective, stripping conversational preambles."""
        # Check for explicit 'Goal:' or 'Objective:' header
        explicit_match = re.search(r"(?:goal|objective|purpose)\s*:\s*([^\n\.;]+)", text, re.IGNORECASE)
        if explicit_match:
            candidate = explicit_match.group(1).strip()
            if len(candidate) > 5:
                return candidate.rstrip(".,")

        # Take first sentence or line
        first_clause = re.split(r"[\n\.]+", text)[0].strip()

        # Strip common conversational preambles
        cleaned = first_clause
        for pat in self.GOAL_PREAMBLE_PATTERNS:
            cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE).strip()

        if len(cleaned) >= 6:
            # Capitalize first letter
            return cleaned[0].upper() + cleaned[1:].rstrip(".,")
        return first_clause.rstrip(".,") or "Accomplish user directive with high precision."

    def _extract_constraints(self, text: str) -> list[str]:
        """Extract technical and negative constraints across sentences and bullet points."""
        constraints: list[str] = []
        seen = set()

        # Split by sentences, newlines, and semicolons
        segments = re.split(r"[\n;\.]+", text)
        for seg in segments:
            seg_clean = seg.strip().lstrip("-*• ")
            seg_lower = seg_clean.lower()
            if any(trig in seg_lower for trig in self.CONSTRAINT_TRIGGERS):
                if len(seg_clean) > 8 and seg_lower not in seen:
                    seen.add(seg_lower)
                    constraints.append(seg_clean)

        # Ensure default constraints if none were explicitly stated
        if not constraints:
            constraints = [
                "Production-ready execution with verified schemas and complete implementations",
                "Strict alignment with industry standards and best practices",
            ]

        return constraints

    def _extract_deadline(self, text: str, entities: list[Entity]) -> str:
        """Extract deadline timeframe."""
        # 1. From entities
        for ent in entities:
            if ent.label == "TIMEFRAME":
                return ent.text

        # 2. Regex fallback
        match = re.search(
            r"\b(?:within\s+\d+\s+(?:days?|weeks?|months?|hours?)|by\s+[A-Za-z]+\s+\d{1,2}|by\s+tomorrow|in\s+\d+\s+days?|deadline\s*:\s*[^\n,.]+)\b",
            text,
            re.IGNORECASE,
        )
        return match.group(0).strip() if match else ""

    def _extract_budget(self, text: str, entities: list[Entity]) -> str:
        """Extract financial budget parameter."""
        # 1. From entities
        for ent in entities:
            if ent.label == "BUDGET":
                return ent.text

        # 2. Regex fallback
        match = re.search(
            r"(?:\$\s*\d+(?:,\d+)*(?:\.\d+)?|\b\d+\s*(?:usd|eur|inr|dollars?|lakh|crore)\b|budget\s*:\s*[^\n,.]+)",
            text,
            re.IGNORECASE,
        )
        return match.group(0).strip() if match else ""

    def _extract_platform(self, text: str, entities: list[Entity]) -> str:
        """Extract deployment target platform or environment."""
        platforms: list[str] = []
        for ent in entities:
            if ent.label == "PLATFORM":
                platforms.append(ent.text)
            elif ent.label == "TECHNOLOGY" and ent.text in ["AWS", "GCP", "Azure", "Kubernetes", "Docker"]:
                platforms.append(ent.text)

        if platforms:
            return ", ".join(list(dict.fromkeys(platforms)))

        match = re.search(r"\b(?:iOS|Android|Web|Linux|Windows|macOS|Cloud|AWS|GCP|Azure|Serverless|Kubernetes)\b", text, re.IGNORECASE)
        return match.group(0).strip() if match else ""

    def _extract_location(self, text: str, entities: list[Entity]) -> str:
        """Extract geographic location or physical venue."""
        locations = [ent.text for ent in entities if ent.label == "LOCATION"]
        if locations:
            return ", ".join(list(dict.fromkeys(locations)))

        match = re.search(
            r"\b(?:in|at|near|location\s*:)\s+([A-Z][a-zA-Z\s]{2,20}?)(?=[,\.\n\(\)]|\bto\b|\bfor\b|\bwith\b|$)",
            text,
        )
        return match.group(1).strip() if match else ""

    def _formulate_success_criteria(
        self,
        goal: str,
        format_name: str,
        tone: str,
        constraints: list[str],
        deadline: str = "",
        budget: str = "",
    ) -> list[str]:
        """Synthesize concrete, verifiable acceptance criteria across all extracted dimensions."""
        criteria: list[str] = [
            "Fulfills the core objective comprehensively with verifiable outcomes",
            f"Delivered strictly formatted as: {format_name}",
            f"Adheres to a {tone} communication register and standards",
        ]

        if constraints:
            criteria.append(f"Satisfies all {len(constraints)} specified operational & negative constraints")

        if deadline:
            criteria.append(f"Deliverable milestone completed within stated timeframe: {deadline}")

        if budget:
            criteria.append(f"Execution adheres strictly to the budget ceiling: {budget}")

        criteria.append("Contains zero placeholders, TODOs, or unverified approximations")
        return criteria
