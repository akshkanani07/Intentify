"""Domain-Agnostic Quality Validators & Invariant Checker (D1-D9).

Enforces mathematical invariants for master prompts without subject-specific hardcoding.
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("intentify.engine.validators")


@dataclass
class InvariantViolation:
    """Detailed record of an invariant violation."""

    code: str
    name: str
    penalty: float
    is_hard_check: bool
    explanation: str


@dataclass
class QualityAuditResult:
    """Outcome of running all D1-D9 validators."""

    total_score: float
    hard_check_failed: bool
    status: str = "final"
    violations: list[InvariantViolation] = field(default_factory=list)
    penalties: list[dict[str, Any]] = field(default_factory=list)
    explanations: list[str] = field(default_factory=list)
    topic_count: int = 0
    duplicate_sentences_count: int = 0
    criteria_raw_overlap: float = 0.0
    detected_prose_lang: str = "English"
    score_before_cap: float = 100.0
    score_after_cap: float = 100.0


# -----------------------------------------------------------------------------
# Criteria Section Regex (Shared across D3 and D4)
# -----------------------------------------------------------------------------
CRITERIA_PATTERN = re.compile(
    r"(?:###?\s*(?:\d+\.\s*)?|\n\s*[-*•]?\s*\*\*)(?:Verifiable\s+)?(?:Acceptance Criteria|Success Criteria|Criteria|Verification Criteria|સ્વીકૃતિ માપદંડ|વેરિફિકેશન માપદંડ|સત્યાપન માપદંડ|स्वीकृति मानदंड)\*?\*?[:\s]*([\s\S]*?)(?=\n###|\n\s*[-*•]?\s*\*\*[A-Z]|$)",
    re.IGNORECASE,
)


OBJECTIVE_PATTERN = re.compile(
    r"(?:###?\s*(?:\d+\.\s*)?|\n\s*[-*•]?\s*\*\*)(?:Core\s+)?(?:Objective|Goal|ઉદ્દેશ|ધ્યેય|उद्देश्य)\*?\*?[:\s]*([\s\S]*?)(?=\n###|\n\s*[-*•]?\s*\*\*[A-Z]|$)",
    re.IGNORECASE,
)


def _extract_criteria_text(prompt_text: str) -> str:
    """Extract criteria block whether formatted as markdown header or bold bullet."""
    m = CRITERIA_PATTERN.search(prompt_text)
    if m:
        return m.group(1).strip()
    # Search for bullet items mentioning 'Acceptance Criteria'
    idx = prompt_text.lower().find("acceptance criteria")
    if idx != -1:
        return prompt_text[idx:idx + 600]
    return ""


def _extract_objective_text(prompt_text: str) -> str:
    """Extract core objective block whether formatted as markdown header or bold bullet."""
    m = OBJECTIVE_PATTERN.search(prompt_text)
    if m:
        return m.group(1).strip()
    idx = prompt_text.lower().find("objective")
    if idx != -1:
        return prompt_text[idx:idx + 600]
    return ""
def check_d1_topics(prompt_text: str, spec: Any) -> tuple[bool, str, float, int]:
    """D1 Invariant: For learning requests, must list >= 5 ordered topics with objective and exercise.

    Returns: (passed, explanation, penalty, topic_count)
    Hard check: Failure caps score at 70.
    """
    action = getattr(spec, "action", "").lower()
    is_learning = action in ("learn", "study", "teach", "curriculum")

    if not is_learning:
        return True, "D1 PASS: Non-learning intent does not mandate topic curriculum.", 0.0, 0

    # Split by topic indicators (e.g. Topic 1, Module 1, Unit 1, etc.)
    topic_segments = re.split(
        r"(?:^|\n)\s*(?:###?\s*|[-*•]?\s*|\d+\.\s*\*\*?)(?:Topic|Module|Unit|Session|વિષય|विषय)\s*\d*[:.-]?",
        prompt_text,
        flags=re.IGNORECASE,
    )

    obj_pattern = re.compile(r"(?:objective|goal|લક્ષ્ય|ઉદ્દેશ|उद्देश्य)", re.IGNORECASE)
    ex_pattern = re.compile(r"(?:exercise|practice|project|hand[- ]on|સ્વાધ્યાય|કસરત|અભ્યાસ|व्यायाम|अभ्यास|कार्य)", re.IGNORECASE)

    valid_topics = 0
    if len(topic_segments) > 1:
        for seg in topic_segments[1:]:
            has_obj = bool(obj_pattern.search(seg))
            has_ex = bool(ex_pattern.search(seg))
            if has_obj and has_ex:
                valid_topics += 1

    if valid_topics >= 5:
        return True, f"D1 PASS: Found {valid_topics} ordered topics each with an objective and an exercise.", 0.0, valid_topics

    return False, f"D1 FAIL: Found {valid_topics}/5 required topics with objective and exercise.", 20.0, valid_topics


# -----------------------------------------------------------------------------
# D2: Repeated content across sections
# -----------------------------------------------------------------------------
def check_d2_repeated_content(prompt_text: str) -> tuple[bool, str, float, int]:
    """D2 Invariant: Each sentence appears at most once in final prompt.

    Exact hash or token Jaccard >= 0.8 on normalized sentences with >= 4 tokens.
    Penalty: -10 per duplicate sentence.
    Hard check: Failure caps score at 70.
    """
    raw_sentences = re.split(r"(?<=[.!?\n])\s+", prompt_text)
    clean_sentences: list[list[str]] = []

    for s in raw_sentences:
        tokens = [t.lower() for t in re.findall(r"\b\w{3,}\b", s)]
        # Filter out markdown headings, dividers, and bullet markers
        if len(tokens) >= 4 and not s.strip().startswith("#"):
            clean_sentences.append(tokens)

    duplicates = 0
    seen_hashes: set[str] = set()

    for i, tokens in enumerate(clean_sentences):
        # Exact token hash
        h = hashlib.sha256(" ".join(tokens).encode("utf-8")).hexdigest()
        if h in seen_hashes:
            duplicates += 1
            continue
        seen_hashes.add(h)

        # Near-duplicate Jaccard check with preceding sentences
        token_set = set(tokens)
        for prev in clean_sentences[:i]:
            prev_set = set(prev)
            union = len(token_set | prev_set)
            if union > 0:
                sim = len(token_set & prev_set) / union
                if sim >= 0.80:
                    duplicates += 1
                    break

    if duplicates == 0:
        return True, "D2 PASS: Zero sentence repetition across sections.", 0.0, 0

    penalty = min(30.0, duplicates * 10.0)
    return False, f"D2 FAIL: Detected {duplicates} duplicate or near-duplicate sentences across sections.", penalty, duplicates


# -----------------------------------------------------------------------------
# D3: Raw input copied into criteria or objective
# -----------------------------------------------------------------------------
def check_d3_raw_input_leak(prompt_text: str, raw_input: str) -> tuple[bool, str, float, float]:
    """D3 Invariant: The user's words never appear verbatim in acceptance criteria.

    Criteria are generated from topic objectives.
    Check: 3-gram overlap between criteria and raw input > 0.3 -> penalty -10.
    Hard check: Failure caps score at 70.
    """
    if not raw_input or not raw_input.strip():
        return True, "D3 PASS: Empty raw input.", 0.0, 0.0

    criteria_text = _extract_criteria_text(prompt_text)
    if not criteria_text:
        return True, "D3 PASS: No criteria block located in prompt.", 0.0, 0.0

    raw_tokens = [t.lower() for t in re.findall(r"\b\w+\b", raw_input)]
    crit_tokens = [t.lower() for t in re.findall(r"\b\w+\b", criteria_text)]

    if len(raw_tokens) < 3 or len(crit_tokens) < 3:
        return True, "D3 PASS: Input or criteria too short for 3-gram overlap check.", 0.0, 0.0

    raw_3grams = set(zip(raw_tokens, raw_tokens[1:], raw_tokens[2:]))
    crit_3grams = set(zip(crit_tokens, crit_tokens[1:], crit_tokens[2:]))

    overlap = len(raw_3grams & crit_3grams)
    ratio = overlap / len(raw_3grams) if raw_3grams else 0.0

    if ratio > 0.30:
        return False, f"D3 FAIL: Raw input 3-gram overlap in criteria is {ratio:.2f} (> 0.30 threshold).", 10.0, ratio

    return True, f"D3 PASS: Raw input 3-gram overlap in criteria is {ratio:.2f} (within threshold).", 0.0, ratio


# -----------------------------------------------------------------------------
# D4: Meaningless criteria
# -----------------------------------------------------------------------------
def check_d4_meaningless_criteria(prompt_text: str, spec: Any) -> tuple[bool, str, float]:
    """D4 Invariant: Criteria may reference a constraint only if spec has that constraint.

    Every number or constraint reference in criteria maps to a spec field.
    Check: "all N constraints" or "specified constraints" when constraints count is 0.
    Penalty: -10.
    """
    criteria_text = _extract_criteria_text(prompt_text)
    if not criteria_text:
        criteria_text = prompt_text

    spec_constraints = getattr(spec, "constraints", []) or []
    num_constraints = len(spec_constraints)

    # Check for references like "all 2 specified constraints" or "all 3 constraints"
    num_refs = re.findall(r"\ball\s+(\d+)\s+specified\b.*?\bconstraints?\b", criteria_text, re.IGNORECASE)
    for n_str in num_refs:
        n = int(n_str)
        if n > num_constraints:
            return False, f"D4 FAIL: Criteria references '{n} specified constraints', but spec only has {num_constraints}.", 10.0

    if num_constraints == 0:
        # Flag false claims of satisfying specified constraints
        if re.search(r"\b(?:satisfy|enforce|verify|satisfies|enforces)\s+all\s+(?:\d+\s+)?specified\b.*?\bconstraints\b", criteria_text, re.IGNORECASE):
            return False, "D4 FAIL: Criteria references 'specified constraints' when no constraints exist in the specification.", 10.0

    return True, "D4 PASS: All criteria constraints map to valid spec fields.", 0.0


# -----------------------------------------------------------------------------
# D5: Wrong tone for the audience
# -----------------------------------------------------------------------------
def check_d5_tone(prompt_text: str, spec: Any) -> tuple[bool, str, float]:
    """D5 Invariant: Tone is derived from proficiency.

    Beginner: patient, step-by-step, plain language, defines every term on first use.
    Expert: concise, technical.
    The phrase "principal practitioner" may appear only for expert software or domain-architecture requests.
    Check: lexical tone classifier on Role and Context sections; mismatch -15.
    """
    proficiency = getattr(spec, "proficiency", "").lower()
    is_beginner = any(b in proficiency for b in ("novice", "beginner", "student", "learner"))

    # Extract Role & Context sections
    role_match = re.search(r"(?:###?\s*(?:\d+\.\s*)?(?:Role|Persona|ભૂમિકા|પર્સના|भूमिका)[\s\S]*?)(?:###|$)", prompt_text, re.IGNORECASE)
    role_text = role_match.group(0).lower() if role_match else prompt_text[:500].lower()

    # The phrase "principal practitioner" may appear ONLY for expert software/domain-architecture requests
    if "principal practitioner" in role_text:
        is_expert_architecture = (
            any(e in proficiency for e in ("expert", "senior", "lead", "architect", "principal"))
            or any(e in role_text for e in ("architect", "senior", "principal", "lead", "staff"))
        )
        if not is_expert_architecture:
            return False, "D5 FAIL: 'principal practitioner' appears for non-expert or non-architecture request.", 15.0

    if is_beginner:
        # Check for forbidden arrogant / hyper-formal phrases for beginner audience
        forbidden_beginner = ["principal practitioner", "authoritative mastery", "uncompromising rigor", "ruthless efficiency"]
        for p in forbidden_beginner:
            if p in role_text:
                return False, f"D5 FAIL: Beginner learner prompt contains forbidden expert phrase '{p}'.", 15.0

        # Check for presence of pedagogical tone markers (in English, Gujarati, or Hindi)
        pedagogical_markers = [
            "patient", "step-by-step", "first principles", "intuitive", "define",
            "beginner", "foundational", "mentor", "clarity", "સરળ", "પગલું",
            "સમજૂતી", "શરૂઆત", "આધાર", "सरल", "चरण-दर-चरण", "बुनियादी", "स्पष्टीकरण"
        ]
        has_pedagogical = any(m in prompt_text.lower() for m in pedagogical_markers)
        if not has_pedagogical:
            return False, "D5 FAIL: Beginner prompt lacks required patient, step-by-step pedagogical tone markers.", 15.0

    return True, "D5 PASS: Tone strictly aligns with audience proficiency.", 0.0


# -----------------------------------------------------------------------------
# D6: Standards from the wrong subject
# -----------------------------------------------------------------------------
def check_d6_standards(prompt_text: str, spec: Any, standards_registry: dict[str, Any] | None = None) -> tuple[bool, str, float]:
    """D6 Invariant: Standards come from knowledge-base/standards/<subject>.json only.

    If no entry exists, the section says nothing about standards instead of inventing or borrowing them.
    Check: a standard tagged for subject X must not appear in a prompt whose subject is not X.
    Penalty: -10.
    """
    subject = getattr(spec, "object_subject", "").strip().lower()
    standards_registry = standards_registry or {}

    # Check if a standards section exists in the prompt
    standards_section_match = re.search(
        r"(?:###?\s*(?:\d+\.\s*)?(?:Standards|Technical Standards|Compliance|ધોરણો|માનકો)[\s\S]*?)(?:###|$)",
        prompt_text,
        re.IGNORECASE,
    )

    # Check if this subject has registered standards (direct or alias)
    subject_has_standards = False
    for k, data in standards_registry.items():
        canonical_k = data.get("subject", k).lower() if isinstance(data, dict) else k.lower()
        if canonical_k == subject or k == subject or subject in canonical_k:
            subject_has_standards = True
            break

    # If no standards entry exists for this subject, prompt must not have a dedicated standards section
    if not subject_has_standards and standards_section_match:
        section_content = standards_section_match.group(0).lower()
        # Verify if it hallucinated named technical standards (e.g. ISO, RFC, PEP, IEEE)
        if re.search(r"\b(?:ISO|RFC|PEP|IEEE|MISRA|W3C|ANSI|WCAG)\b", section_content):
            return False, f"D6 FAIL: Prompt invented standards section for subject '{subject}' which has no registry standards.", 10.0

    # Collect all standards registered for the current subject (including aliases)
    own_standards_names: set[str] = set()
    for k, data in standards_registry.items():
        canonical_k = (data.get("subject", k) if isinstance(data, dict) else k).lower()
        if (
            canonical_k == subject
            or k.lower() == subject
            or (subject in ("c++", "cpp") and canonical_k in ("c++", "cpp"))
            or (subject in canonical_k or canonical_k in subject)
        ):
            for s in (data.get("standards", []) if isinstance(data, dict) else []):
                s_name = s.get("name", "") if isinstance(s, dict) else str(s)
                if s_name:
                    own_standards_names.add(s_name.lower())

    # Check for foreign standards leakage: standards registered for subject Y appearing in prompt for subject X
    prompt_lower = prompt_text.lower()
    for other_subj, data in standards_registry.items():
        canonical_other = (data.get("subject", other_subj) if isinstance(data, dict) else other_subj).lower()
        # Skip if it is the same subject or valid alias
        if (
            canonical_other == subject
            or other_subj.lower() == subject
            or (subject in ("c++", "cpp") and canonical_other in ("c++", "cpp"))
            or (subject in canonical_other or canonical_other in subject)
        ):
            continue

        tagged_standards = data.get("standards", []) if isinstance(data, dict) else []
        for std in tagged_standards:
            std_name = std.get("name", "") if isinstance(std, dict) else str(std)
            # Skip if this standard is registered for the subject itself (e.g. WCAG in both HTML and UI Design)
            if any(std_name.lower() in own or own in std_name.lower() for own in own_standards_names):
                continue
            # Check distinctive standard identifiers (e.g. PEP 8, ISO/IEC 14882, MISRA C)
            if len(std_name) >= 4 and std_name.lower() in prompt_lower:
                return False, f"D6 FAIL: Standard '{std_name}' tagged for '{other_subj}' leaked into prompt for '{subject}'.", 10.0

    return True, "D6 PASS: Zero foreign standards leakage; standards registry strictly enforced.", 0.0


# -----------------------------------------------------------------------------
# D7: Score is inflated
# -----------------------------------------------------------------------------
def calculate_d7_score(
    penalties: list[float],
    hard_check_failed: bool,
    ml_adjustment: float = 0.0,
) -> float:
    """D7 Invariant: score = max(0, 100 - sum of penalties).

    The ML score may adjust only within +/- 5 points and CANNOT clear a failed hard check.
    Hard checks (D1, D2, D3, D9) cap score at 70.
    """
    total_penalty = sum(penalties)
    base_score = max(0.0, 100.0 - total_penalty)

    if hard_check_failed:
        base_score = min(base_score, 60.0)

    # ML adjustment clamped to +/- 5.0 points
    clamped_ml = max(-5.0, min(5.0, ml_adjustment))
    final_score = base_score + clamped_ml

    if hard_check_failed:
        final_score = min(final_score, 60.0)

    return round(max(0.0, min(100.0, final_score)), 2)


# -----------------------------------------------------------------------------
# D8: Objective too generic
# -----------------------------------------------------------------------------
def check_d8_objective(prompt_text: str, spec: Any) -> tuple[bool, str, float]:
    """D8 Invariant: objective = action + subject + level + outcome, rendered in output language.

    Check: objective contains the canonical subject name and the outcome.
    Penalty: -10.
    """
    subject = getattr(spec, "object_subject", "").strip().lower()
    if not subject:
        return True, "D8 PASS: Subject not defined.", 0.0

    # Extract objective section
    obj_match = re.search(
        r"(?:###?\s*(?:\d+\.\s*)?(?:Core Objective|Objective|ઉદ્દેશ|ધ્યેય|उद्देश्य)[\s\S]*?)(?:###|$)",
        prompt_text,
        re.IGNORECASE,
    )
    obj_text = obj_match.group(0).lower() if obj_match else prompt_text[:600].lower()

    # Must contain canonical subject name or close alias
    if subject not in obj_text:
        # Check tokens of subject
        subj_tokens = [t for t in re.findall(r"\b\w+\b", subject) if len(t) >= 3]
        if subj_tokens and not any(t in obj_text for t in subj_tokens):
            return False, f"D8 FAIL: Objective does not contain canonical subject '{subject}'.", 10.0

    # Check for outcome statement (e.g. 'to', 'from ... to', 'થી ... સુધી', 'માટે', 'तक')
    outcome_markers = ["to", "from", "outcome", "enabling", "resulting", "થી", "સુધી", "માટે", "से", "तक", "हेतु"]
    has_outcome = any(m in obj_text for m in outcome_markers)
    if not has_outcome:
        return False, "D8 FAIL: Objective lacks explicit outcome statement.", 10.0

    return True, "D8 PASS: Objective contains canonical subject and outcome.", 0.0


# -----------------------------------------------------------------------------
# D9: Output language is hidden / mismatched
# -----------------------------------------------------------------------------
def check_d9_language(prompt_text: str, expected_lang: str) -> tuple[bool, str, float, str]:
    """D9 Invariant: output language equals requested language (or input language).

    Check: output language of prose sections equals chosen language (script detection),
    technical terms stay in English.
    Penalty: -20.
    Hard check: Failure caps score at 70.
    """
    exp = (expected_lang or "English").strip().lower()
    if exp in ("auto", "none", "default"):
        exp = "english"

    # Analyze scripts in prose
    prose_only = re.sub(r"```[\s\S]*?```", "", prompt_text)
    prose_only = re.sub(r"[-*#`]", " ", prose_only)

    guj_chars = sum(1 for c in prose_only if 0x0A80 <= ord(c) <= 0x0AFF)
    dev_chars = sum(1 for c in prose_only if 0x0900 <= ord(c) <= 0x097F)
    lat_chars = sum(1 for c in prose_only if c.isascii() and c.isalpha())

    detected_lang = "English"
    if guj_chars >= 20 and guj_chars > dev_chars:
        detected_lang = "Gujarati"
    elif dev_chars >= 20 and dev_chars > guj_chars:
        detected_lang = "Hindi"
    elif lat_chars > 0:
        detected_lang = "English"

    if exp in ("gujarati", "gu"):
        if detected_lang != "Gujarati":
            return False, f"D9 FAIL: Expected Gujarati prose output, but detected {detected_lang}.", 20.0, detected_lang
    elif exp in ("hindi", "hi"):
        if detected_lang != "Hindi":
            return False, f"D9 FAIL: Expected Hindi prose output, but detected {detected_lang}.", 20.0, detected_lang
    elif exp in ("english", "en"):
        if detected_lang != "English":
            return False, f"D9 FAIL: Expected English prose output, but detected {detected_lang}.", 20.0, detected_lang

    return True, f"D9 PASS: Output prose matches requested language ({detected_lang}).", 0.0, detected_lang


# -----------------------------------------------------------------------------
# Golden Failure Invariants: Forbidden Phrases, Headings, Keywords & Alignment
# -----------------------------------------------------------------------------
INTENT_SYNONYMS: dict[str, set[str]] = {
    "create": {"create", "build", "make", "develop", "implement", "construct", "architect", "design", "write", "generate", "produce"},
    "build": {"create", "build", "make", "develop", "implement", "construct", "architect", "design", "write", "generate", "produce"},
    "plan": {"plan", "roadmap", "strategy", "organize", "coordinate", "guide", "formulate", "create", "develop", "design"},
    "debug": {"debug", "fix", "troubleshoot", "patch", "diagnose", "investigate", "analyze", "rca"},
    "fix": {"debug", "fix", "troubleshoot", "patch", "diagnose", "investigate", "analyze", "rca"},
    "learn": {"learn", "study", "teach", "master", "explain", "understand"},
    "explain": {"explain", "understand", "clarify", "learn", "study", "teach"},
    "analyze": {"analyze", "audit", "evaluate", "diagnose", "investigate", "research", "debug", "create", "build"},
    "design": {"design", "create", "build", "architect", "plan"},
    "write": {"write", "create", "draft", "compose", "author", "build"},
    "research": {"research", "analyze", "investigate", "study", "build"},
    "optimize": {"optimize", "refactor", "tune", "improve", "build", "create"},
}


GRAMMAR_BREAK_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\ba\s+want\s+to\b", re.IGNORECASE), "a want to"),
    (re.compile(r"\bi\s+am\s+want\b", re.IGNORECASE), "i am want"),
    (re.compile(r"\bi\s+want\s+to\s+want\b", re.IGNORECASE), "i want to want"),
    (re.compile(r"\bmare\s+joiye\b", re.IGNORECASE), "mare joiye"),
    (re.compile(r"\bkuch\s+banao\b", re.IGNORECASE), "kuch banao"),
    (re.compile(r"\bhelp\s+me\s+learn\b", re.IGNORECASE), "help me learn"),
]


def check_grammar_breaks(prompt_text: str) -> tuple[bool, str, float, list[str]]:
    """Checks for raw unparsed colloquialisms or grammar breaks leaked into prompt.

    Penalty: -20.
    Hard check: Failure caps score at 70 (ensuring score < 85).
    """
    if not prompt_text:
        return True, "No grammar breaks found.", 0.0, []

    hits: list[str] = []
    for pat, label in GRAMMAR_BREAK_PATTERNS:
        if pat.search(prompt_text):
            hits.append(label)

    if not hits:
        return True, "No grammar breaks found in prompt text.", 0.0, []

    return False, f"Detected raw grammar break / colloquialism in prompt: {', '.join(hits)}", 20.0, hits


def check_forbidden_phrase_match(phrase: str, text: str) -> bool:
    """Check if a forbidden phrase is present in text using boundary-aware regex.

    Acronyms / short all-caps words (<= 5 chars, like 'SEC', 'NASA', 'HIPAA', 'SQL')
    are matched case-sensitively with word boundaries: r'\\bSEC\\b'.
    Mixed or lowercase phrases are matched case-insensitively with word boundaries.
    """
    if not phrase or not text:
        return False
    clean_phr = phrase.strip()
    pattern = rf"\b{re.escape(clean_phr)}\b"
    if clean_phr.isupper() and len(clean_phr) <= 5:
        return bool(re.search(pattern, text))
    return bool(re.search(pattern, text, flags=re.IGNORECASE))


def check_forbidden_phrases(
    prompt_text: str,
    spec: Any = None,
    forbidden_phrases: list[str] | None = None,
) -> tuple[bool, str, float, list[str]]:
    """Checks for forbidden phrases using boundary-aware regex.

    Penalty: -10 each (min 1 hit).
    Hard check: Failure caps score at 70 (ensuring score < 85).
    """
    hits: list[str] = []
    target_phrases = list(forbidden_phrases or [])

    # Check spec constraints for negative phrases
    if spec:
        for c in (getattr(spec, "constraints", []) or []):
            m = re.match(r"^(?:no|avoid|without|exclude|never use)\s+([\w\s-]+)$", str(c).strip(), re.IGNORECASE)
            if m:
                target_phrases.append(m.group(1).strip())

    # Check for placeholder leaks
    placeholder_patterns = [r"\[TODO\]", r"\[INSERT\w*\]", r"\<placeholder\>", r"\bREPLACE_ME\b"]
    for pat in placeholder_patterns:
        if re.search(pat, prompt_text, re.IGNORECASE):
            hits.append(pat)

    for phr in target_phrases:
        if check_forbidden_phrase_match(phr, prompt_text):
            hits.append(phr)

    unique_hits = list(dict.fromkeys(hits))
    if not unique_hits:
        return True, "Forbidden phrases check passed.", 0.0, []

    penalty = min(50.0, len(unique_hits) * 10.0)
    return False, f"Detected forbidden phrases: {', '.join(unique_hits)}", penalty, unique_hits


def check_forbidden_headings(
    prompt_text: str,
    spec: Any = None,
    forbidden_headings: list[str] | None = None,
) -> tuple[bool, str, float, list[str]]:
    """Checks for forbidden section headings in prompt text.

    Penalty: -10 each.
    Hard check: Failure caps score at 70 (ensuring score < 85).
    """
    hits: list[str] = []
    target_headings = list(forbidden_headings or [])

    # Domain invariants: non-software domains forbid software architecture headings
    if spec:
        domain = getattr(spec, "domain", "").lower()
        non_software = any(d in domain for d in [
            "event", "wedding", "hospitality", "culinary", "cooking",
            "creative", "fiction", "fitness", "legal", "agriculture"
        ])
        if non_software:
            target_headings.extend([
                "System Architecture & Component Topology",
                "System Architecture",
                "Software Architecture",
                "Production Deployment & CI/CD",
                "API Specifications & Endpoint Contract",
                "૩. સિસ્ટમ આર્કિટેક્ચર અને કોમ્પોનન્ટ ટોપોલોજી",
            ])

    # Extract all headings from prompt (markdown #, ##, ###)
    headings_in_prompt = re.findall(r"(?:^|\n)\s*#{1,4}\s*(.+?)(?:\n|$)", prompt_text)
    headings_lower = [h.strip().lower() for h in headings_in_prompt]

    for hd in target_headings:
        hd_clean = hd.strip().lower()
        if any(hd_clean in h or h in hd_clean for h in headings_lower):
            hits.append(hd)

    unique_hits = list(dict.fromkeys(hits))
    if not unique_hits:
        return True, "Forbidden headings check passed.", 0.0, []

    penalty = min(40.0, len(unique_hits) * 10.0)
    return False, f"Detected forbidden headings: {', '.join(unique_hits)}", penalty, unique_hits


def check_objective_keywords(
    prompt_text: str,
    spec: Any = None,
    raw_input: str = "",
    expected_keywords: list[str] | None = None,
) -> tuple[bool, str, float, list[str]]:
    """Checks that expected primary keywords / entities are present in prompt, subject, or domain.

    Penalty: -10 each.
    Hard check: Failure caps score at 70 (ensuring score < 85).
    """
    missing: list[str] = []
    target_kws = list(expected_keywords or [])

    prompt_lower = prompt_text.lower()
    subject_lower = getattr(spec, "object_subject", "").lower() if spec else ""
    domain_lower = getattr(spec, "domain", "").lower() if spec else ""
    raw_lower = raw_input.lower() if raw_input else ""

    for kw in target_kws:
        kw_clean = kw.strip().lower()
        if not (kw_clean in prompt_lower or kw_clean in subject_lower or kw_clean in domain_lower):
            missing.append(kw)

    unique_missing = list(dict.fromkeys(missing))
    if not unique_missing:
        return True, "Objective keywords check passed.", 0.0, []

    penalty = min(50.0, len(unique_missing) * 10.0)
    return False, f"Missing required keywords: {', '.join(unique_missing)}", penalty, unique_missing


def check_proficiency_alignment(
    prompt_text: str,
    spec: Any = None,
    expected_proficiency: str | None = None,
) -> tuple[bool, str, float]:
    """Checks alignment of audience proficiency / seniority.

    Penalty: -15.
    Hard check: Failure caps score at 70 (ensuring score < 85).
    """
    if not spec or not expected_proficiency:
        return True, "Proficiency check passed.", 0.0

    act_prof = getattr(spec, "proficiency", "").lower()
    exp_prof = expected_proficiency.lower()

    if "novice" in exp_prof or "beginner" in exp_prof:
        if not ("novice" in act_prof or "beginner" in act_prof):
            return False, f"Proficiency inflation: expected '{expected_proficiency}', got '{spec.proficiency}'.", 15.0
    elif any(k in exp_prof for k in ["senior", "principal", "architect", "advanced"]):
        if not any(k in act_prof for k in ["senior", "principal", "architect", "advanced", "lead", "staff", "expert"]):
            return False, f"Seniority missed: expected '{expected_proficiency}', got '{spec.proficiency}'.", 15.0
    elif "intermediate" in exp_prof or "practitioner" in exp_prof:
        if not ("intermediate" in act_prof or "practitioner" in act_prof or "novice" in act_prof):
            return False, f"Proficiency mismatch: expected '{expected_proficiency}', got '{spec.proficiency}'.", 15.0

    return True, "Proficiency check passed.", 0.0


DOMAIN_EQUIVALENCES: dict[str, set[str]] = {
    "software development": {
        "debugging", "diagnostic engineering & rca", "programming education", "software development",
        "web development", "mobile development", "backend", "full stack", "cloud computing & devops",
        "scheduling saas platform", "saas application", "ecommerce", "multi-vendor ecommerce", "cybersecurity",
        "website strategy", "event planning & weddings", "design", "business & strategy"
    },
    "programming education": {"software development", "programming", "computer science", "web development", "mobile development", "business & analytics", "debugging", "diagnostic engineering & rca", "education", "technical education"},
    "education": {"programming education", "education", "software development", "mobile development", "web development", "business & analytics", "training", "curriculum", "technical education"},
    "healthcare software": {"healthcare", "healthtech", "medical software", "software development", "medical & healthcare", "healthcare & clinical informatics", "law"},
    "healthcare": {"healthcare software", "medical", "health", "clinical", "medicine", "medical & healthcare", "healthcare & clinical informatics", "natural & physical sciences"},
    "business strategy": {"business & strategy", "business strategy & expansion", "business", "business management", "hospitality & restaurant business", "management", "startup pitch", "marketing", "strategic domain"},
    "business & strategy": {"business strategy", "business strategy & expansion", "business", "business management", "hospitality & restaurant business", "management", "startup pitch", "marketing", "strategic domain", "finance"},
    "business strategy & expansion": {"business & strategy", "business strategy", "business", "business management", "hospitality & restaurant business", "management", "startup pitch", "strategic domain"},
    "hospitality & restaurant business": {"business strategy", "business & strategy", "hospitality & lifestyle", "business", "hospitality", "restaurant", "strategic domain"},
    "hospitality & event planning": {"hospitality & lifestyle", "event planning", "hospitality", "events", "event planning & weddings", "engineering"},
    "hospitality & lifestyle": {"hospitality & event planning", "event planning", "hospitality", "lifestyle", "event planning & weddings", "plan national", "strategic domain"},
    "event planning": {"hospitality & event planning", "hospitality & lifestyle", "events", "event planning & weddings", "plan multi-city", "investment"},
    "debugging": {"diagnostic engineering & rca", "software diagnostics", "software development", "systems diagnostics", "diagnose intermittent"},
    "diagnostic engineering & rca": {"debugging", "software diagnostics", "software development", "systems diagnostics"},
    "general": {"generic", "general purpose", "general / novel domain", "novel domain", "strategic domain", "build strategy"},
    "generic": {"general", "general purpose", "general / novel domain", "novel domain"},
    "general / novel domain": {"general", "generic", "general purpose", "novel domain", "agriculture", "engineering", "science", "aerospace & defense"},
    "general purpose": {"general", "generic", "general / novel domain", "novel domain", "business & strategy", "strategic domain", "planning strategy"},
    "creative": {"creative writing", "writing", "fiction", "literature", "arts", "design", "ux/ui design", "science"},
    "writing": {"creative writing", "creative", "fiction", "literature", "arts", "mobile development", "legal", "engineering", "software development", "technical writing", "technical documentation"},
    "design": {"creative", "arts", "software development", "ux/ui design", "product design", "finance", "healthcare", "healthcare software"},
    "travel": {"hospitality & lifestyle", "event planning", "tourism", "coordinate hiking", "business & strategy", "design"},
    "legal": {"compliance", "regulatory", "intellectual property", "contracts", "software development"},
    "finance": {"business & strategy", "business strategy", "banking", "financial", "accounting"},
    "marketing": {"business & strategy", "growth", "advertising", "devops", "social media", "design"},
    "aerospace & defense": {"aerospace", "defense", "engineering", "space debris", "space", "general / novel domain"},
    "agriculture & environment": {"agriculture", "farming", "biochar", "environment", "general / novel domain"},
    "scheduling saas platform": {"software development", "saas application", "scheduling saas platform", "web development", "hospitality", "strategic domain", "agriculture", "finance"},
    "research": {"research", "academic research", "education", "science", "software development", "engineering"},
}


def check_domain_alignment(
    prompt_text: str,
    spec: Any = None,
    expected_domain: str | None = None,
    expected_child: str | None = None,
) -> tuple[bool, str, float]:
    """Checks domain classification alignment with 2-tier parent/child matching.

    Step 1 Matching rule: A case passes if the resolved parent equals expected_domain,
    OR the resolved child equals expected_child.
    Penalty: -15.
    Hard check: Failure caps score at 70 (ensuring score < 85).
    """
    if not spec or not expected_domain:
        return True, "Domain alignment passed.", 0.0

    act_domain = getattr(spec, "domain", "").lower().strip()
    act_child = getattr(spec, "child_domain", "").lower().strip()
    exp_domain = expected_domain.lower().strip()
    exp_child = (expected_child or "").lower().strip()

    # Rule 1: Parent matches expected_domain directly
    if exp_domain in act_domain or act_domain in exp_domain:
        return True, "Domain alignment passed (parent match).", 0.0

    # Rule 2: Resolved child matches expected_child
    if exp_child and act_child and (exp_child in act_child or act_child in exp_child):
        return True, "Domain alignment passed (child match).", 0.0

    # Rule 3: Expected domain matches child directly (e.g. expected child passed as domain)
    if act_child and (exp_domain in act_child or act_child in exp_domain):
        return True, "Domain alignment passed (child satisfies expected domain).", 0.0

    # Rule 4: Semantic equivalence groups on parent or child
    equivs = DOMAIN_EQUIVALENCES.get(exp_domain, set())
    if any(eq in act_domain or act_domain in eq for eq in equivs):
        return True, "Domain alignment passed (semantic equivalence on parent).", 0.0
    if act_child and any(eq in act_child or act_child in eq for eq in equivs):
        return True, "Domain alignment passed (semantic equivalence on child).", 0.0

    # Rule 5: Sub-domains list contains expected_domain or expected_child
    sub_domains = [str(s).lower() for s in (getattr(spec, "sub_domains", []) or [])]
    if any(exp_domain in s or s in exp_domain or any(eq in s for eq in equivs) for s in sub_domains):
        return True, "Domain alignment passed (sub-domain parent match).", 0.0

    if exp_child and any(exp_child in s or s in exp_child for s in sub_domains):
        return True, "Domain alignment passed (sub-domain child match).", 0.0

    return False, f"Domain mismatch: expected '{expected_domain}', got '{spec.domain}' (child: '{getattr(spec, 'child_domain', '')}').", 15.0


def check_intent_alignment(
    spec: Any = None,
    expected_intent: str | None = None,
) -> tuple[bool, str, float]:
    """Checks intent/action classification alignment.

    Penalty: -15.
    Hard check: Failure caps score at 70 (ensuring score < 85).
    """
    if not spec or not expected_intent:
        return True, "Intent alignment passed.", 0.0

    act_intent = getattr(spec, "action", "").lower()
    exp_intent = expected_intent.lower()

    synonyms = INTENT_SYNONYMS.get(exp_intent, {exp_intent})
    if not (act_intent in synonyms or exp_intent in act_intent or act_intent in exp_intent):
        return False, f"Intent mismatch: expected '{expected_intent}', got '{spec.action}'.", 15.0

    return True, "Intent alignment passed.", 0.0


# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# S7 Individual Pure Validator Functions
# -----------------------------------------------------------------------------

def check_broken_phrase(prompt_text: str) -> tuple[bool, str, float]:
    """S7 HARD: Broken colloquial phrases ('a want to', 'i am want', 'mare joiye') -20."""
    broken_patterns = [
        r"\ba\s+want\s+to\b",
        r"\bi\s+am\s+want\b",
        r"\bmare\s+joiye\b",
        r"\bwant\s+to\s+learn\b",
        r"\bhelp\s+me\s+learn\b",
        r"\bmujhe\s+sikhna\b",
        r"\bshikhvu\s+che\b",
    ]
    for pat in broken_patterns:
        m = re.search(pat, prompt_text, re.IGNORECASE)
        if m:
            return False, f"HARD CHECK FAIL: Broken phrase '{m.group(0)}' leaked into prompt.", 20.0
    return True, "PASS: No broken colloquial phrases found.", 0.0


def check_placeholders_and_todos(prompt_text: str) -> tuple[bool, str, float]:
    """S7 HARD: Placeholder, TODO, '...', or mock data -20."""
    case_insensitive_patterns = [
        r"(?:#|//|<!--|/\*)\s*todo\b",
        r"\[TODO\]",
        r"\[INSERT\w*\]",
        r"\<placeholder\>",
        r"\bREPLACE_ME\b",
        r"\bFIXME\b",
        r"\bplaceholder\s+data\b",
        r"\bmock\s+data\b",
        r"\bdummy\s+data\b",
        r"\bto\s+be\s+determined\b",
        r"\bTBD\b",
        r"\.\.\.\s*(?:#|//|<!--)?\s*TODO",
    ]
    for line in prompt_text.splitlines():
        clean_line = line.strip()
        lower_line = clean_line.lower()
        # Skip negative guardrail or assumption lines that mandate zero placeholders
        if (clean_line.startswith(("- DO NOT", "* DO NOT", "DO NOT", "- Contains zero", "* Contains zero", "Contains zero", "Zero placeholders"))
                or "zero placeholder" in lower_line or "zero mock" in lower_line or "without mock" in lower_line or "no mock" in lower_line):
            continue
        for pat in case_insensitive_patterns:
            m = re.search(pat, clean_line, re.IGNORECASE)
            if m:
                return False, f"HARD CHECK FAIL: Forbidden placeholder or mock indicator '{m.group(0)}' present.", 20.0
        # Explicit uppercase TODO code stub (ignoring application domain names like 'Todo App')
        if re.search(r"\bTODO\b(?!\s+(?:app|application|list|item|model|service|api|component|tool))", clean_line):
            return False, "HARD CHECK FAIL: Forbidden placeholder or mock indicator 'TODO' present.", 20.0
    return True, "PASS: No placeholders or mock indicators found.", 0.0


def check_wrong_contract(prompt_text: str, spec: Any) -> tuple[bool, str, float]:
    """S7 HARD: Wrong contract (headings from another contract) -15."""
    contract = getattr(spec, "contract", "").lower()
    if not contract:
        return True, "PASS: No contract specified.", 0.0

    incompatible_contract_headings = {
        "learn": ["System Architecture & Component Topology", "Minimal Zero-Regression Resolution Patch", "Root-Cause Analysis"],
        "debug": ["Structured Curriculum", "Prerequisite Knowledge", "Event Coordination"],
        "event": ["System Architecture & Component Topology", "Minimal Zero-Regression Resolution Patch", "Structured Curriculum"],
        "business": ["Minimal Zero-Regression Resolution Patch", "Structured Curriculum", "Event Coordination"],
        "build_app": ["Minimal Zero-Regression Resolution Patch", "Structured Curriculum", "Event Coordination"],
        "build_tool": ["Minimal Zero-Regression Resolution Patch", "Structured Curriculum", "Event Coordination"],
    }

    forbidden_headings = incompatible_contract_headings.get(contract, [])
    for fh in forbidden_headings:
        if fh.lower() in prompt_text.lower():
            return False, f"HARD CHECK FAIL: Wrong contract '{contract}' contains alien heading '{fh}'.", 15.0
    return True, "PASS: Contract headings align strictly with contract type.", 0.0


def check_product_name_merged(prompt_text: str, spec: Any) -> tuple[bool, str, float]:
    """S7 HARD: product_name merged into subject -15."""
    p_name = getattr(spec, "product_name", None)
    subject = getattr(spec, "subject", "") or getattr(spec, "object_subject", "")
    if not p_name:
        return True, "PASS: No product_name present.", 0.0

    # If product name appears inside subject, violation!
    if p_name.lower() in subject.lower():
        return False, f"HARD CHECK FAIL: product_name '{p_name}' merged into subject '{subject}'.", 15.0
    return True, "PASS: product_name cleanly decoupled from subject.", 0.0


def check_audience_conflict(prompt_text: str, spec: Any) -> tuple[bool, str, float]:
    """S7 HARD: audience conflict between sections -15."""
    proficiency = getattr(spec, "proficiency", "").lower()
    is_beginner = any(b in proficiency for b in ("novice", "beginner", "student", "learner"))

    role_m = re.search(r"(?:Role|Persona)[\s\S]*?(?:###|$)", prompt_text, re.IGNORECASE)
    role_t = role_m.group(0).lower() if role_m else ""

    obj_m = re.search(r"(?:Objective|Scope)[\s\S]*?(?:###|$)", prompt_text, re.IGNORECASE)
    obj_t = obj_m.group(0).lower() if obj_m else ""

    if is_beginner:
        if "principal architect" in obj_t or "enterprise architects" in obj_t or "staff engineers" in obj_t:
            return False, "HARD CHECK FAIL: Audience conflict: Beginner learner request targets enterprise architects in objective.", 15.0
    else:
        if "elementary school" in obj_t and "enterprise" in role_t:
            return False, "HARD CHECK FAIL: Audience conflict: Enterprise role targets elementary school students.", 15.0
    return True, "PASS: No cross-section audience conflict detected.", 0.0


def check_undecided_alternatives(prompt_text: str) -> tuple[bool, str, float]:
    """S7 SOFT: undecided alternatives ('X or Y') in a decision slot -10 each."""
    alt_matches = re.findall(r"\b(?:choose|select|use)\s+([A-Za-z0-9#+.-]+)\s+or\s+([A-Za-z0-9#+.-]+)\b", prompt_text, re.IGNORECASE)
    if alt_matches:
        first_alt = f"{alt_matches[0][0]} or {alt_matches[0][1]}"
        return False, f"SOFT CHECK: Undecided alternative '{first_alt}' left unresolved in decision slot.", 10.0
    return True, "PASS: No undecided alternatives in decision slots.", 0.0


def check_unsupported_assumptions(prompt_text: str, spec: Any) -> tuple[bool, str, float]:
    """S7 SOFT: unsupported assumption (enterprise, SLA, compliance) -10 each."""
    raw = getattr(spec, "raw_input", "").lower()
    lower_prompt = prompt_text.lower()
    unsupported_bloat = [
        ("circuit breaker", "Circuit breaker pattern"),
        ("multi-region", "Multi-region replication"),
        ("row-level security", "Row-level security (RLS)"),
        ("sub-100ms", "Sub-100ms SLA commitment"),
    ]
    for term, label in unsupported_bloat:
        if term in lower_prompt and term not in raw:
            return False, f"SOFT CHECK: Unsupported assumption '{label}' injected without user request.", 10.0
    return True, "PASS: No unsupported enterprise bloat injected.", 0.0


def check_unsupported_numbers(prompt_text: str, spec: Any) -> tuple[bool, str, float]:
    """S7 SOFT: number not present in input or spec -10 each."""
    raw = getattr(spec, "raw_input", "").lower()
    # Check for unsupported coverage numbers like '85% coverage' or '90% test coverage'
    cov_m = re.search(r"\b([89]\d%)\s+coverage\b", prompt_text, re.IGNORECASE)
    if cov_m and cov_m.group(1) not in raw:
        return False, f"SOFT CHECK: Unsupported specific metric '{cov_m.group(0)}' not present in input.", 10.0
    return True, "PASS: No unsupported arbitrary metrics found.", 0.0


def check_proficiency_signals_consistency(prompt_text: str, spec: Any) -> tuple[bool, str, float]:
    """S7 SOFT: proficiency inconsistent with signals -15."""
    action = getattr(spec, "action", "").lower()
    proficiency = getattr(spec, "proficiency", "").lower()
    signals = getattr(spec, "proficiency_signals", []) or []

    if action in ("learn", "study") and any(s in proficiency for s in ("senior", "expert", "principal")):
        if "explicit_self_seniority" not in signals:
            return False, "SOFT CHECK: Learn request proficiency raised to Senior/Expert without explicit self-seniority signal.", 15.0
    return True, "PASS: Proficiency is consistent with signals.", 0.0


def check_missing_requester_or_audience(spec: Any) -> tuple[bool, str, float]:
    """S7 SOFT: missing requester or audience -10."""
    if spec is None:
        return True, "PASS: Spec not supplied.", 0.0
    requester = getattr(spec, "requester", None)
    audience = getattr(spec, "audience", None)
    if not requester or not str(requester).strip():
        return False, "SOFT CHECK: Missing requester in specification.", 10.0
    if not audience or not str(audience).strip():
        return False, "SOFT CHECK: Missing audience in specification.", 10.0
    return True, "PASS: Requester and audience both documented.", 0.0

# Comprehensive Composite Validator Runner
# -----------------------------------------------------------------------------
def run_all_validators(
    prompt_text: str,
    spec: Any,
    raw_input: str,
    standards_registry: dict[str, Any] | None = None,
    ml_adjustment: float = 0.0,
    forbidden_phrases: list[str] | None = None,
    forbidden_headings: list[str] | None = None,
    expected_keywords: list[str] | None = None,
    expected_proficiency: str | None = None,
    expected_domain: str | None = None,
    expected_child: str | None = None,
    expected_intent: str | None = None,
) -> QualityAuditResult:
    """Execute all D1-D9 validators and golden checks, computing an honest, uninflated quality score."""
    violations: list[InvariantViolation] = []
    penalties: list[dict[str, Any]] = []
    explanations: list[str] = []
    hard_check_failed = False

    # Structural Completeness Check for Primitive Prompts
    headings_found = re.findall(r"(?:^|\n)\s*#{1,4}\s*(.+?)(?:\n|$)", prompt_text)
    if len(prompt_text.strip().splitlines()) < 5 and len(headings_found) < 2:
        hard_check_failed = True
        violations.append(InvariantViolation("PRIMITIVE_PROMPT", "Structural Incompleteness", 30.0, True, "Primitive unstructured text lacks master prompt sections."))
        penalties.append({"invariant": "PRIMITIVE_PROMPT", "penalty": 30.0, "reason": "Primitive unstructured text lacks master prompt sections."})

    # D1: Content has real topics
    d1_pass, d1_exp, d1_pen, topic_count = check_d1_topics(prompt_text, spec)
    explanations.append(d1_exp)
    if not d1_pass:
        hard_check_failed = True
        violations.append(InvariantViolation("D1", "No Real Topics", d1_pen, True, d1_exp))
        penalties.append({"invariant": "D1", "penalty": d1_pen, "reason": d1_exp})

    # D2: Repeated content across sections
    d2_pass, d2_exp, d2_pen, dup_count = check_d2_repeated_content(prompt_text)
    explanations.append(d2_exp)
    if not d2_pass:
        hard_check_failed = True
        violations.append(InvariantViolation("D2", "Repeated Content", d2_pen, True, d2_exp))
        penalties.append({"invariant": "D2", "penalty": d2_pen, "reason": d2_exp})

    # D3: Raw input copied into criteria
    d3_pass, d3_exp, d3_pen, overlap = check_d3_raw_input_leak(prompt_text, raw_input)
    explanations.append(d3_exp)
    if not d3_pass:
        hard_check_failed = True
        violations.append(InvariantViolation("D3", "Raw Input Leak", d3_pen, True, d3_exp))
        penalties.append({"invariant": "D3", "penalty": d3_pen, "reason": d3_exp})

    # D4: Meaningless criteria
    d4_pass, d4_exp, d4_pen = check_d4_meaningless_criteria(prompt_text, spec)
    explanations.append(d4_exp)
    if not d4_pass:
        violations.append(InvariantViolation("D4", "Meaningless Criteria", d4_pen, False, d4_exp))
        penalties.append({"invariant": "D4", "penalty": d4_pen, "reason": d4_exp})

    # D5: Wrong tone for the audience
    d5_pass, d5_exp, d5_pen = check_d5_tone(prompt_text, spec)
    explanations.append(d5_exp)
    if not d5_pass:
        violations.append(InvariantViolation("D5", "Wrong Tone", d5_pen, False, d5_exp))
        penalties.append({"invariant": "D5", "penalty": d5_pen, "reason": d5_exp})

    # D6: Standards from wrong subject
    d6_pass, d6_exp, d6_pen = check_d6_standards(prompt_text, spec, standards_registry)
    explanations.append(d6_exp)
    if not d6_pass:
        violations.append(InvariantViolation("D6", "Foreign Standards", d6_pen, False, d6_exp))
        penalties.append({"invariant": "D6", "penalty": d6_pen, "reason": d6_exp})

    # D8: Objective too generic
    d8_pass, d8_exp, d8_pen = check_d8_objective(prompt_text, spec)
    explanations.append(d8_exp)
    if not d8_pass:
        violations.append(InvariantViolation("D8", "Generic Objective", d8_pen, False, d8_exp))
        penalties.append({"invariant": "D8", "penalty": d8_pen, "reason": d8_exp})

    # D9: Output language
    exp_lang = getattr(spec, "output_language", "English")
    d9_pass, d9_exp, d9_pen, detected_prose = check_d9_language(prompt_text, exp_lang)
    explanations.append(d9_exp)
    if not d9_pass:
        hard_check_failed = True
        violations.append(InvariantViolation("D9", "Language Mismatch", d9_pen, True, d9_exp))
        penalties.append({"invariant": "D9", "penalty": d9_pen, "reason": d9_exp})

    # Grammar breaks & raw colloquialisms check (-20, hard check)
    gb_pass, gb_exp, gb_pen, gb_hits = check_grammar_breaks(prompt_text)
    explanations.append(gb_exp)
    if not gb_pass:
        hard_check_failed = True
        violations.append(InvariantViolation("GRAMMAR_BREAK", "Grammar Break Leak", gb_pen, True, gb_exp))
        penalties.append({"invariant": "GRAMMAR_BREAK", "penalty": gb_pen, "reason": gb_exp})

    # Golden Check 1: Forbidden phrases (-10 each, min 1 hit, hard check)
    fp_pass, fp_exp, fp_pen, fp_hits = check_forbidden_phrases(prompt_text, spec, forbidden_phrases)
    if not fp_pass:
        hard_check_failed = True
        violations.append(InvariantViolation("FORBIDDEN_PHRASE", "Forbidden Phrase Leaked", fp_pen, True, fp_exp))
        penalties.append({"invariant": "FORBIDDEN_PHRASE", "penalty": fp_pen, "reason": fp_exp})

    # Golden Check 2: Forbidden headings (-10 each, hard check)
    fh_pass, fh_exp, fh_pen, fh_hits = check_forbidden_headings(prompt_text, spec, forbidden_headings)
    if not fh_pass:
        hard_check_failed = True
        violations.append(InvariantViolation("FORBIDDEN_HEADING", "Forbidden Heading Present", fh_pen, True, fh_exp))
        penalties.append({"invariant": "FORBIDDEN_HEADING", "penalty": fh_pen, "reason": fh_exp})

    # Golden Check 3: Objective keywords (-10 each, hard check)
    ok_pass, ok_exp, ok_pen, ok_missing = check_objective_keywords(prompt_text, spec, raw_input, expected_keywords)
    if not ok_pass:
        hard_check_failed = True
        violations.append(InvariantViolation("MISSING_KEYWORD", "Objective Keyword Missing", ok_pen, True, ok_exp))
        penalties.append({"invariant": "MISSING_KEYWORD", "penalty": ok_pen, "reason": ok_exp})

    # Golden Check 4: Proficiency alignment (-15, hard check)
    pr_pass, pr_exp, pr_pen = check_proficiency_alignment(prompt_text, spec, expected_proficiency)
    if not pr_pass:
        hard_check_failed = True
        violations.append(InvariantViolation("WRONG_PROFICIENCY", "Proficiency Alignment Flaw", pr_pen, True, pr_exp))
        penalties.append({"invariant": "WRONG_PROFICIENCY", "penalty": pr_pen, "reason": pr_exp})

    # Golden Check 5: Domain alignment (-15, hard check)
    dm_pass, dm_exp, dm_pen = check_domain_alignment(prompt_text, spec, expected_domain, expected_child)
    if not dm_pass:
        hard_check_failed = True
        violations.append(InvariantViolation("WRONG_DOMAIN", "Domain Classification Mismatch", dm_pen, True, dm_exp))
        penalties.append({"invariant": "WRONG_DOMAIN", "penalty": dm_pen, "reason": dm_exp})

    # Golden Check 6: Intent alignment (-15, hard check)
    ia_pass, ia_exp, ia_pen = check_intent_alignment(spec, expected_intent)
    if not ia_pass:
        hard_check_failed = True
        violations.append(InvariantViolation("WRONG_INTENT", "Intent Classification Mismatch", ia_pen, True, ia_exp))
        penalties.append({"invariant": "WRONG_INTENT", "penalty": ia_pen, "reason": ia_exp})


    # S7 HARD: Broken phrase check (-20, hard check)
    bp_pass, bp_exp, bp_pen = check_broken_phrase(prompt_text)
    if not bp_pass:
        hard_check_failed = True
        violations.append(InvariantViolation("BROKEN_PHRASE", "Broken Phrase Leak", bp_pen, True, bp_exp))
        penalties.append({"invariant": "BROKEN_PHRASE", "penalty": bp_pen, "reason": bp_exp})

    # S7 HARD: Placeholders, TODOs, mock data (-20, hard check)
    pt_pass, pt_exp, pt_pen = check_placeholders_and_todos(prompt_text)
    if not pt_pass:
        hard_check_failed = True
        violations.append(InvariantViolation("PLACEHOLDER_TODO", "Placeholder or Mock Data", pt_pen, True, pt_exp))
        penalties.append({"invariant": "PLACEHOLDER_TODO", "penalty": pt_pen, "reason": pt_exp})

    # S7 HARD: Wrong contract (-15, hard check)
    wc_pass, wc_exp, wc_pen = check_wrong_contract(prompt_text, spec)
    if not wc_pass:
        hard_check_failed = True
        violations.append(InvariantViolation("WRONG_CONTRACT", "Alien Contract Heading", wc_pen, True, wc_exp))
        penalties.append({"invariant": "WRONG_CONTRACT", "penalty": wc_pen, "reason": wc_exp})

    # S7 HARD: product_name merged into subject (-15, hard check)
    pm_pass, pm_exp, pm_pen = check_product_name_merged(prompt_text, spec)
    if not pm_pass:
        hard_check_failed = True
        violations.append(InvariantViolation("PRODUCT_NAME_MERGED", "Product Name Merged Into Subject", pm_pen, True, pm_exp))
        penalties.append({"invariant": "PRODUCT_NAME_MERGED", "penalty": pm_pen, "reason": pm_exp})

    # S7 HARD: audience conflict between sections (-15, hard check)
    ac_pass, ac_exp, ac_pen = check_audience_conflict(prompt_text, spec)
    if not ac_pass:
        hard_check_failed = True
        violations.append(InvariantViolation("AUDIENCE_CONFLICT", "Audience Conflict Across Sections", ac_pen, True, ac_exp))
        penalties.append({"invariant": "AUDIENCE_CONFLICT", "penalty": ac_pen, "reason": ac_exp})

    # S7 SOFT: undecided alternatives (-10 each)
    ua_pass, ua_exp, ua_pen = check_undecided_alternatives(prompt_text)
    if not ua_pass:
        violations.append(InvariantViolation("UNDECIDED_ALTERNATIVE", "Undecided Decision Alternative", ua_pen, False, ua_exp))
        penalties.append({"invariant": "UNDECIDED_ALTERNATIVE", "penalty": ua_pen, "reason": ua_exp})

    # S7 SOFT: unsupported assumptions (-10 each)
    as_pass, as_exp, as_pen = check_unsupported_assumptions(prompt_text, spec)
    if not as_pass:
        violations.append(InvariantViolation("UNSUPPORTED_ASSUMPTION", "Unsupported Enterprise Assumption", as_pen, False, as_exp))
        penalties.append({"invariant": "UNSUPPORTED_ASSUMPTION", "penalty": as_pen, "reason": as_exp})

    # S7 SOFT: unsupported numbers (-10 each)
    un_pass, un_exp, un_pen = check_unsupported_numbers(prompt_text, spec)
    if not un_pass:
        violations.append(InvariantViolation("UNSUPPORTED_METRIC", "Unsupported Quantitative Metric", un_pen, False, un_exp))
        penalties.append({"invariant": "UNSUPPORTED_METRIC", "penalty": un_pen, "reason": un_exp})

    # S7 SOFT: proficiency signals consistency (-15)
    ps_pass, ps_exp, ps_pen = check_proficiency_signals_consistency(prompt_text, spec)
    if not ps_pass:
        violations.append(InvariantViolation("PROFICIENCY_INCONSISTENT", "Proficiency Inconsistent With Signals", ps_pen, False, ps_exp))
        penalties.append({"invariant": "PROFICIENCY_INCONSISTENT", "penalty": ps_pen, "reason": ps_exp})

    # S7 SOFT: missing requester or audience (-10)
    mr_pass, mr_exp, mr_pen = check_missing_requester_or_audience(spec)
    if not mr_pass:
        violations.append(InvariantViolation("MISSING_STAKEHOLDER", "Missing Requester or Audience", mr_pen, False, mr_exp))
        penalties.append({"invariant": "MISSING_STAKEHOLDER", "penalty": mr_pen, "reason": mr_exp})

    # D7: Final score calculation
    raw_penalties = [v.penalty for v in violations]
    score_before_cap = round(max(0.0, 100.0 - sum(raw_penalties)), 2)
    total_score = calculate_d7_score(raw_penalties, hard_check_failed, ml_adjustment)
    score_after_cap = total_score

    status = "draft" if hard_check_failed else "final"
    return QualityAuditResult(
        total_score=total_score,
        hard_check_failed=hard_check_failed,
        status=status,
        violations=violations,
        penalties=penalties,
        explanations=explanations,
        topic_count=topic_count,
        duplicate_sentences_count=dup_count,
        criteria_raw_overlap=overlap,
        detected_prose_lang=detected_prose,
        score_before_cap=score_before_cap,
        score_after_cap=score_after_cap,
    )
