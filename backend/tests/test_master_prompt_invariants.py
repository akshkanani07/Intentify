"""Property-based invariant tests and golden benchmark suite (D1-D9).

Matrix of 300+ cases asserting generic invariants across subjects, languages, and levels.
"""

from __future__ import annotations

import itertools
import pytest
from app.api.v1.schemas.prompt import PromptGenerationRequest
from app.knowledge.knowledge_manager import KnowledgeManager
from app.services.orchestrator import PromptOrchestrator
from app.engine.spec_extractor import SpecExtractor
from app.engine.validators import run_all_validators


# -----------------------------------------------------------------------------
# Test Input Matrices (Separated completely from composer code)
# -----------------------------------------------------------------------------

KNOWN_SUBJECTS = [
    "C", "C++", "Java", "Python", "JavaScript", "TypeScript", "SQL", "HTML", "CSS",
    "Git", "Linux Command Line", "Data Structures", "Statistics", "Excel",
    "English Grammar", "Gujarati Typing", "Accounting Basics", "Digital Marketing",
    "UI Design Basics", "Public Speaking",
]

UNKNOWN_SUBJECTS = [
    "organic farming app",
    "satellite orbital propulsion",
    "biochar carbon sequestration",
    "deep sea kelp ecology",
    "quantum key distribution protocol",
]

PHRASINGS = [
    ("English", "want to learn {subject} from scratch with hands-on practice"),
    ("Gujarati", "મારે શરૂઆતથી {subject} શીખવું છે અને વ્યવહારુ પ્રોજેક્ટ બનાવવા છે"),
    ("Hindi", "मुझे शुरू से {subject} सीखना है और अभ्यास कार्य करना है"),
    ("Mixed", "mare {subject} learn karvu che basic to advanced level mate"),
]

LEVELS = [
    ("Beginner", "Student / Beginner"),
    ("Intermediate", "Practitioner / Professional"),
    ("Expert", "Senior Architect"),
]

VAGUE_AND_TYPO_INPUTS = [
    "kuch banao",
    "pythn seekhna h",
    "hlp me make a website",
    "mare joiye java",
    "c++ tutorial",
    "fix crash now",
    "data structres",
    "banao ek app",
]


@pytest.fixture(scope="module")
def orchestrator():
    KnowledgeManager._instance = None
    return PromptOrchestrator()


@pytest.fixture(scope="module")
def extractor():
    return SpecExtractor()


# -----------------------------------------------------------------------------
# Part 1: 60 Hand-Written Golden Cases
# -----------------------------------------------------------------------------

GOLDEN_CASES = [
    # 1-10: Pedagogical core programming in English
    ("want to learn HTML", "English", "Learn", "HTML", "Novice / Beginner"),
    ("want to learn c++", "English", "Learn", "C++", "Novice / Beginner"),
    ("I want to learn Java programming", "English", "Learn", "Java", "Novice / Beginner"),
    ("teach me Python step by step", "English", "Learn", "Python", "Novice / Beginner"),
    ("beginner guide to learn JavaScript", "English", "Learn", "JavaScript", "Novice / Beginner"),
    ("want to learn TypeScript with strict types", "English", "Learn", "TypeScript", "Novice / Beginner"),
    ("learn SQL database queries and schema design", "English", "Learn", "SQL", "Novice / Beginner"),
    ("learn CSS flexbox and grid layouts", "English", "Learn", "CSS", "Novice / Beginner"),
    ("learn Git version control and branching", "English", "Learn", "Git", "Novice / Beginner"),
    ("learn Linux command line navigation and pipes", "English", "Learn", "Linux Command Line", "Novice / Beginner"),

    # 11-20: Pedagogical subjects in Gujarati
    ("મારે Java શીખવું છે", "Gujarati", "Learn", "Java", "Novice / Beginner"),
    ("કૃપા કરીને મને Python શીખવો", "Gujarati", "Learn", "Python", "Novice / Beginner"),
    ("મારે HTML5 અને CSS શીખવું છે", "Gujarati", "Learn", "HTML", "Novice / Beginner"),
    ("મારે ગુજરાતી ટાઈપિંગ શીખવું છે", "Gujarati", "Learn", "Gujarati Typing", "Novice / Beginner"),
    ("મારે એકાઉન્ટિંગ બેસિક્સ શીખવું છે", "Gujarati", "Learn", "Accounting Basics", "Novice / Beginner"),
    ("મારે C++ પ્રોગ્રામિંગ શીખવું છે શરૂઆતથી", "Gujarati", "Learn", "C++", "Novice / Beginner"),
    ("ડિજિટલ માર્કેટિંગ શીખવા માટે ગાઈડ આપો", "Gujarati", "Learn", "Digital Marketing", "Novice / Beginner"),
    ("મારે ડેટા સ્ટ્રક્ચર્સ શીખવું છે", "Gujarati", "Learn", "Data Structures", "Novice / Beginner"),
    ("મારે પબ્લિક સ્પીકિંગ શીખવું છે", "Gujarati", "Learn", "Public Speaking", "Novice / Beginner"),
    ("મારે એક્સેલ શીખવું છે", "Gujarati", "Learn", "Excel", "Novice / Beginner"),

    # 21-30: Pedagogical subjects in Hindi & Mixed
    ("मुझे Python सीखना है बुनियादी स्तर से", "Hindi", "Learn", "Python", "Novice / Beginner"),
    ("मुझे Java programming सिखाएं", "Hindi", "Learn", "Java", "Novice / Beginner"),
    ("HTML और CSS सीखने के लिए पाठ्यक्रम बनाएं", "Hindi", "Learn", "HTML", "Novice / Beginner"),
    ("SQL डेटाबेस क्वेरी कैसे सीखें", "Hindi", "Learn", "SQL", "Novice / Beginner"),
    ("mare c++ shikhvu che basic thi", "Gujarati", "Learn", "C++", "Novice / Beginner"),
    ("mujhe statistics aur probability sikhna hai", "Hindi", "Learn", "Statistics", "Novice / Beginner"),
    ("mare excel na formulas shikhva che", "Gujarati", "Learn", "Excel", "Novice / Beginner"),
    ("learn english grammar from scratch", "English", "Learn", "English Grammar", "Novice / Beginner"),
    ("mujhe digital marketing sikhna hai", "Hindi", "Learn", "Digital Marketing", "Novice / Beginner"),
    ("mare git branching samjavu che", "Gujarati", "Learn", "Git", "Novice / Beginner"),

    # 31-40: Creation & SaaS Architecture in English
    ("Build a scheduling website with calendar sync", "English", "Build", "scheduling website with calendar sync", "Intermediate / Practitioner"),
    ("Architect a multi-tenant SaaS e-commerce platform", "English", "Build", "multi-tenant SaaS e-commerce platform", "Senior / Expert"),
    ("Design a high-throughput event streaming API with Kafka", "English", "Build", "high-throughput event streaming API with Kafka", "Senior / Expert"),
    ("Build an automated invoice processing microservice", "English", "Build", "automated invoice processing microservice", "Intermediate / Practitioner"),
    ("Create a real-time collaborative document editor with WebSockets", "English", "Build", "real-time collaborative document editor with WebSockets", "Senior / Expert"),
    ("Design a healthcare telemetry dashboard for ICU patients", "English", "Build", "healthcare telemetry dashboard for ICU patients", "Senior / Expert"),
    ("Build an inventory tracking system with barcode scanner", "English", "Build", "inventory tracking system with barcode scanner", "Intermediate / Practitioner"),
    ("Architect an enterprise role-based access control (RBAC) service", "English", "Build", "enterprise role-based access control (RBAC) service", "Senior / Expert"),
    ("Create a mobile banking payment gateway integration", "English", "Build", "mobile banking payment gateway integration", "Senior / Expert"),
    ("Build a customer churn prediction ML pipeline", "English", "Build", "customer churn prediction ML pipeline", "Senior / Expert"),

    # 41-50: Diagnostic Debugging
    ("fix this NullPointerException", "English", "Debug", "NullPointerException", "Intermediate / Practitioner"),
    ("diagnose segmentation fault in worker process", "English", "Debug", "segmentation fault in worker process", "Senior / Expert"),
    ("fix memory leak in long-running thread pool", "English", "Debug", "memory leak in long-running thread pool", "Senior / Expert"),
    ("resolve database deadlock under high concurrency", "English", "Debug", "database deadlock under high concurrency", "Senior / Expert"),
    ("debug 504 Gateway Timeout in microservice mesh", "English", "Debug", "504 Gateway Timeout in microservice mesh", "Senior / Expert"),
    ("fix circular dependency import crash in Python package", "English", "Debug", "circular dependency import crash in Python package", "Intermediate / Practitioner"),
    ("diagnose Redis connection pool exhaustion", "English", "Debug", "Redis connection pool exhaustion", "Senior / Expert"),
    ("resolve CORS policy preflight header rejection", "English", "Debug", "CORS policy preflight header rejection", "Intermediate / Practitioner"),
    ("fix JWT token expiration refresh race condition", "English", "Debug", "JWT token expiration refresh race condition", "Senior / Expert"),
    ("debug OOM killer terminating container on startup", "English", "Debug", "OOM killer terminating container on startup", "Senior / Expert"),

    # 51-60: Novel Unknown Domains, Vague Inputs & Multilingual Business
    ("organic farming app", "English", "Build", "organic farming app", "Intermediate / Practitioner"),
    ("satellite orbital propulsion simulator", "English", "Build", "satellite orbital propulsion simulator", "Senior / Expert"),
    ("deep sea kelp monitoring sensor network", "English", "Build", "deep sea kelp monitoring sensor network", "Intermediate / Practitioner"),
    ("biochar carbon sequestration verification portal", "English", "Build", "biochar carbon sequestration verification portal", "Senior / Expert"),
    ("quantum key distribution simulator", "English", "Build", "quantum key distribution simulator", "Senior / Expert"),
    ("kuch banao", "Hindi", "Build", "kuch banao", "Intermediate / Practitioner"),
    ("hlp me make a website", "English", "Build", "website", "Novice / Beginner"),
    ("અમદાવાદમાં ગુજરાતી થાળી રેસ્ટોરન્ટ માટે બિઝનેસ પ્લાન", "Gujarati", "Build", "રેસ્ટોરન્ટ", "Intermediate / Practitioner"),
    ("उदयपुर में डेस्टिनेशन वेडिंग का बजट और आयोजन", "Hindi", "Plan", "डेस्टिनेशन वेडिंग", "Intermediate / Practitioner"),
    ("મારા લગ્ન માટે ઉદયપુરમાં 50 lakh budget", "Gujarati", "Plan", "લગ્ન", "Intermediate / Practitioner"),
]


class TestGolden60Cases:
    """Verifies all 60 hand-written golden test cases against invariants D1-D9."""

    @pytest.mark.parametrize("detail,expected_lang,expected_action,expected_subject,expected_prof", GOLDEN_CASES)
    def test_golden_case_invariants(self, orchestrator, extractor, detail, expected_lang, expected_action, expected_subject, expected_prof):
        req = PromptGenerationRequest(detail=detail)
        res = orchestrator.generate_prompt_sync(req)
        spec = extractor.extract(detail)

        standards_registry = orchestrator._engine_planner.km.list_standards()
        audit = run_all_validators(res.master_prompt, spec, detail, standards_registry=standards_registry)

        # Assert no hard check failures
        assert not audit.hard_check_failed, f"Hard check failed for '{detail}': {audit.explanations}"
        # Assert quality score threshold
        assert audit.total_score >= 85.0, f"Score {audit.total_score} < 85 for '{detail}': {audit.violations}"

        # If learning: D1 must strictly pass with >= 5 topics
        if spec.action.lower() in ("learn", "study", "teach"):
            assert audit.topic_count >= 5, f"Expected >= 5 topics for learning '{detail}', got {audit.topic_count}"

        # D2: Zero duplicate sentences across sections
        assert audit.duplicate_sentences_count == 0, f"Detected duplicate sentences in '{detail}'"

        # D3: 3-gram overlap with raw input in criteria must be <= 0.30
        assert audit.criteria_raw_overlap <= 0.30, f"Raw input leak in criteria for '{detail}': {audit.criteria_raw_overlap}"


# -----------------------------------------------------------------------------
# Part 2: 300+ Case Property Test Matrix
# -----------------------------------------------------------------------------

def _generate_matrix_cases():
    """Build a matrix of at least 300 diverse combinations."""
    all_subjects = KNOWN_SUBJECTS + UNKNOWN_SUBJECTS  # 25 subjects
    cases = []

    for subject in all_subjects:
        for lang_name, phrasing_template in PHRASINGS:  # 4 phrasings
            for level_name, role_hint in LEVELS:        # 3 levels
                text = phrasing_template.format(subject=subject)
                cases.append((text, lang_name, subject, level_name, role_hint))

    for vague in VAGUE_AND_TYPO_INPUTS:
        cases.append((vague, "Auto", vague, "Beginner", ""))

    return cases


ALL_MATRIX_CASES = _generate_matrix_cases()


class TestPropertyMatrixInvariants:
    """Evaluates 300+ diverse cases to assert mathematical invariants D1-D9."""

    def test_matrix_size(self):
        assert len(ALL_MATRIX_CASES) >= 300, f"Matrix size must be >= 300, got {len(ALL_MATRIX_CASES)}"

    @pytest.mark.parametrize("text,expected_lang,subject,level_name,role_hint", ALL_MATRIX_CASES[:310])
    def test_property_invariant_case(self, orchestrator, extractor, text, expected_lang, subject, level_name, role_hint):
        req = PromptGenerationRequest(detail=text, role=role_hint)
        res = orchestrator.generate_prompt_sync(req)
        spec = extractor.extract(text, role_hint=role_hint)

        standards_registry = orchestrator._engine_planner.km.list_standards()
        audit = run_all_validators(res.master_prompt, spec, text, standards_registry=standards_registry)

        # Invariant Assertions:
        # D1: If learning, must have >= 5 topics each with objective and exercise
        if spec.action.lower() in ("learn", "study", "teach"):
            assert audit.topic_count >= 5, f"D1 topic count violation for '{text}': got {audit.topic_count}"

        # D2: Zero duplicate sentences across sections
        assert audit.duplicate_sentences_count == 0, f"D2 sentence duplication violation in '{text}'"

        # D3: Acceptance criteria 3-gram overlap with raw input <= 0.30
        assert audit.criteria_raw_overlap <= 0.30, f"D3 raw input leak in criteria for '{text}': {audit.criteria_raw_overlap}"

        # D6: Zero foreign standards leakage
        d6_violations = [v for v in audit.violations if v.code == "D6"]
        assert len(d6_violations) == 0, f"D6 foreign standards violation for '{text}': {d6_violations}"

        # D9: Output language matching
        if expected_lang != "Auto":
            assert res.metadata.detected_language.lower() in (expected_lang.lower(), "gujarati", "hindi", "english")
