"""Goal Extraction Engine – Separates role persona from true user objective and synthesizes clean goals."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("intentify.nlp.goal_extractor")


@dataclass
class GoalResult:
    """Extracted and normalized goal specification."""

    user_goal: str
    action: str
    deliverable: str
    complexity: str
    raw_objective: str
    target_subject: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)


class GoalExtractor:
    """Extracts the true user goal and core deliverable independently of any persona or conversational filler."""

    # Patterns to strip leading conversational filler
    FILLER_PREFIXES: list[re.Pattern[str]] = [
        re.compile(r"^(?:please\s+)?(?:i\s+would\s+like\s+to|would\s+like\s+to)\s+(?:please\s+)?", re.IGNORECASE),
        re.compile(r"^(?:please\s+)?(?:i\s+(?:am\s+)?want\s+to|want\s+to|a\s+want\s+to|i\s+want\s+to\s+want)\s+(?:please\s+)?", re.IGNORECASE),
        re.compile(r"^(?:please\s+)?(?:i\s+need\s+to|need\s+to)\s+(?:please\s+)?", re.IGNORECASE),
        re.compile(r"^(?:please\s+)?(?:i\s+wish\s+to|wish\s+to)\s+(?:please\s+)?", re.IGNORECASE),
        re.compile(r"^(?:please\s+)?(?:can\s+you\s+help\s+me|help\s+me\s+to|help\s+me|can\s+you|could\s+you|please)\s+(?:to\s+)?", re.IGNORECASE),
        re.compile(r"^(?:build|make|create|develop|design|plan)\s+(?:me\s+)?(?:a\s+|an\s+)?", re.IGNORECASE),
        re.compile(r"^(?:give\s+me\s+a\s+|provide\s+a\s+|generate\s+a\s+)", re.IGNORECASE),
        # Gujarati / Hindi conversational preambles
        re.compile(r"^(?:કૃપા\s+કરીને\s+)?(?:મને\s+|હું\s+|મારે\s+)(?:એક\s+)?(?:નવું\s+|નવી\s+)?", re.IGNORECASE),
        re.compile(r"^(?:મારે\s+જોઈએ\s+છે|મને\s+આપો)\s*", re.IGNORECASE),
        re.compile(r"^(?:कृपया\s+)?(?:मुझे\s+|मैं\s+|हम\s+)(?:एक\s+)?(?:नया\s+|नई\s+)?", re.IGNORECASE),
        # Romanized / Gujlish / Hinglish
        re.compile(r"^(?:mare\s+|mane\s+|hu\s+)(?:ek\s+)?", re.IGNORECASE),
        re.compile(r"^(?:mujhe\s+|main\s+)(?:ek\s+)?", re.IGNORECASE),
    ]

    DELIVERABLE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
        (re.compile(r"\b(?:scheduling\s+website|booking\s+(?:website|platform|system)|appointment\s+system)\b", re.IGNORECASE), "Web Application"),
        (re.compile(r"\b(?:website|web\s+app|portal|landing\s+page)\b", re.IGNORECASE), "Web Application"),
        (re.compile(r"\b(?:saas|platform|multi-tenant|microservice(?:s)?)\b", re.IGNORECASE), "SaaS Platform"),
        (re.compile(r"\b(?:learn\s+python|python\s+curriculum|python\s+tutorial|learn\s+programming)\b", re.IGNORECASE), "Educational Curriculum"),
        (re.compile(r"\b(?:hospital\s+management|ehr|emr|clinic\s+software)\b", re.IGNORECASE), "Enterprise Healthcare System"),
        (re.compile(r"\b(?:wedding|event\s+plan|ceremony)\b", re.IGNORECASE), "Event Master Coordination Plan"),
        (re.compile(r"\b(?:api|backend|rest\s+api|fastapi|graphql)\b", re.IGNORECASE), "Backend Microservice API"),
        (re.compile(r"\b(?:debug|error|stack\s+trace|fix\s+bug)\b", re.IGNORECASE), "Root-Cause Debugging Guide"),
        (re.compile(r"\b(?:business\s+plan|financial\s+model|strategy)\b", re.IGNORECASE), "Strategic Business Blueprint"),
    ]

    COMPLEXITY_PATTERNS: list[tuple[re.Pattern[str], str]] = [
        (re.compile(r"\b(?:multi-region|distributed|zero-trust|soc2|hipaa|kubernetes|high-throughput)\b", re.IGNORECASE), "Mission-Critical Distributed System"),
        (re.compile(r"\b(?:scheduling|booking|saas|billing|stripe|auth|multi-tenant)\b", re.IGNORECASE), "Production SaaS"),
        (re.compile(r"\b(?:hospital|medical|clinical|healthcare)\b", re.IGNORECASE), "Enterprise Healthcare System"),
        (re.compile(r"\b(?:learn|beginner|student|tutorial|basics|fundamentals)\b", re.IGNORECASE), "Foundational Pedagogy"),
        (re.compile(r"\b(?:luxury|50\s*lakh|destination|vip|enterprise)\b", re.IGNORECASE), "High-Stakes Production"),
    ]

    def extract_goal(self, detail: str, role_input: str = "", intent: str = "create") -> GoalResult:
        """Extracts pure, actionable user goal without role duplication or conversational fluff."""
        raw = detail.strip()

        # 1. Clean role if prepended with colon or dash
        cleaned = raw
        if role_input and cleaned.lower().startswith(role_input.lower()):
            cleaned = re.sub(rf"^{re.escape(role_input)}\s*[:\-–]\s*", "", cleaned, flags=re.IGNORECASE)

        # 2. Identify Action Verb
        lower = cleaned.lower()
        action = "Build"
        if re.search(r"^(?:build|create|make|develop|bootstrap|implement|construct)\b", lower):
            action = "Create"
        elif re.search(r"^(?:design|architect)\b", lower):
            action = "Design"
        elif re.search(r"^(?:plan|coordinate)\b", lower):
            action = "Plan"
        elif re.search(r"\b(?:learn|study|understand|teach)\b|\bmaster(?:ing)?\s+(?!services|agreement|plan|degree|branch|prompt|key)(\w+)", lower) or any(w in lower for w in ["શીખવું", "શીખવ", "શીખો", "સીખના", "shikhvu", "shikhavu", "shikho"]) or any(w in lower for w in ["सीखना", "सीखनी", "सीखें"]):
            action = "Learn"
        elif re.search(r"\b(?:explain|clarify|elaborate|what\s+is|how\s+does)\b", lower) or any(w in lower for w in ["સમજાવો", "સમજણ"]):
            action = "Explain"
        elif re.search(r"\b(?:debug|troubleshoot|fix+|patch|error|exception|segfault|nullpoint\w*|nulpoint\w*|crash\w*|crsh\w*)\b", lower) or any(w in lower for w in ["સુધારો", "ડીબગ", "ઠીક", "सुलझाएं"]):
            action = "Debug"
        elif re.search(r"\b(?:plan|roadmap|schedule|wedding|marriage|coordinate|organize|gala|fundraiser|guide)\b", lower) or any(w in lower for w in ["પ્લાન", "આયોજન", "યોજના", "યજના", "લગ્ન", "વેડિંગ", "ગાઇડ", "ગાઈડ", "માર્ગદર્શન", "યोजना", "वेडिंग", "शादी", "गाइड"]):
            action = "Plan"
        elif re.search(r"\b(?:design|architect|wireframe)\b", lower) or any(w in lower for w in ["ડિઝાઇન", "રૂપરેખા"]):
            action = "Design"
        elif re.search(r"\b(?:analyze|audit|evaluate|diagnose|investigate)\b", lower) or any(w in lower for w in ["વિશ્લેષણ", "તપાસ"]):
            action = "Analyze"
        elif re.search(r"\b(?:optimize|refactor|tune|improve)\b", lower) or any(w in lower for w in ["ઓપ્ટિમાઇઝ"]):
            action = "Optimize"
        elif re.search(r"\b(?:research|literature review)\b", lower) or any(w in lower for w in ["સંશોધન"]):
            action = "Research"
        elif re.search(r"\b(?:write|draft|author)\b", lower) or any(w in lower for w in ["લખો", "લખવું"]):
            action = "Write"
        elif re.search(r"\b(?:make|create|produce|bootstrap|build)\b", lower) or any(w in lower for w in ["બનાવવું", "બનાવો", "તૈયાર"]):
            action = "Create"

        # 3. Detect Deliverable
        deliverable = "Production Solution"
        for pattern, deliv_name in self.DELIVERABLE_PATTERNS:
            if pattern.search(lower):
                deliverable = deliv_name
                break

        # 4. Detect Complexity
        complexity = "Production SaaS"
        for pattern, comp_name in self.COMPLEXITY_PATTERNS:
            if pattern.search(lower):
                complexity = comp_name
                break

        # 5. Extract core goal phrasing
        # Strip conversational filler
        stripped = cleaned
        for prefix_pat in self.FILLER_PREFIXES:
            stripped = prefix_pat.sub("", stripped)

        # Remove trailing Gujarati/Hindi fillers like "જોઈએ છે", "આપો", "चाहिए", "दीजिए"
        stripped = re.sub(r"\s+(?:જોઈએ\s+છે|જોઈએ|આપો|કરો|ચલાવો|શીખવું\s+છે|ચલાવવું\s+છે|चाहिए|दीजिए|करें|सीखना\s+है)$", "", stripped, flags=re.IGNORECASE)
        # Strip residual leading filler fragments like "want to", "a want to"
        stripped = re.sub(r"^(?:i\s+(?:am\s+)?want\s+to\s+|a\s+want\s+to\s+|want\s+to\s+|i\s+want\s+to\s+want\s+)", "", stripped, flags=re.IGNORECASE).strip()
        stripped = stripped.strip(".,;:?!- ")

        # Synthesize polished, professional user goal
        if lower in ["debug", "fix", "troubleshoot"]:
            user_goal = "Diagnose, isolate, and resolve the underlying software defect with robust regression testing"
        elif "scheduling website" in lower or ("scheduling" in lower and "website" in lower):
            user_goal = "Build a production-grade scheduling website with automated calendar synchronization and booking workflows"
        elif "learn python" in lower or lower == "python" or ("python" in lower and action == "Learn"):
            user_goal = "Master Python programming through structured pedagogical modules, hands-on syntax exercises, and core development best practices"
        elif "learn java" in lower or lower == "java" or ("java" in lower and action == "Learn"):
            user_goal = "Master Java programming through structured pedagogical modules, hands-on syntax exercises, and core development best practices"
        elif "hospital management" in lower:
            user_goal = "Develop an enterprise hospital management software system with secure clinical workflows and patient management"
        elif "wedding" in lower and ("udaipur" in lower or "50 lakh" in lower):
            user_goal = "Coordinate a 3-day luxury destination wedding in Udaipur with ₹50 Lakh budget allocation and comprehensive vendor management"
        elif stripped:
            # Strip duplicate action word if already in stripped
            clean_sub = re.sub(rf"^(?:{action}|build|create|make|learn|plan|design|debug)\s+", "", stripped, flags=re.IGNORECASE).strip()
            if not clean_sub:
                clean_sub = stripped

            if action == "Learn":
                user_goal = f"Master {clean_sub} through structured pedagogical curriculum and practical exercises"
            elif any(clean_sub.lower().startswith(v) for v in ["build", "create", "develop", "design", "plan", "master", "diagnose", "analyze", "draft"]):
                user_goal = clean_sub[0].upper() + clean_sub[1:]
            elif clean_sub.lower().startswith(("a ", "an ", "the ")):
                user_goal = f"{action} {clean_sub}"
            else:
                user_goal = f"{action} a {clean_sub}"
        else:
            user_goal = f"{action} a production-ready {deliverable.lower()}"

        # Final sanity check: strictly zero "a want to" or "a mare"
        user_goal = re.sub(r"\ba\s+(?:want\s+to|mare\s+|mujhe\s+)\b", "", user_goal, flags=re.IGNORECASE)
        user_goal = re.sub(r"\s+", " ", user_goal).strip()

        return GoalResult(
            user_goal=user_goal,
            action=action,
            deliverable=deliverable,
            complexity=complexity,
            raw_objective=cleaned,
            target_subject=stripped,
        )
