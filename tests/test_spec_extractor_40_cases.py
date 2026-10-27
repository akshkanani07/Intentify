"""Comprehensive 40-case unit test suite for P1 SpecExtractor Gate (S1 & S2)."""

import pytest
from app.engine.spec_extractor import PromptSpec, SpecExtractor


@pytest.fixture(scope="module")
def extractor():
    return SpecExtractor()


SPEC_40_CASES = [
    # 1-10: Product Name Extraction & Separation
    (
        'i want to make project management tool, which name is "taskflow"',
        {"product_name": "taskflow", "contract": "build_app", "no_product_in_subject": True},
    ),
    (
        'build a todo app called "ListMaster"',
        {"product_name": "ListMaster", "contract": "build_app", "no_product_in_subject": True},
    ),
    (
        'create a retail marketplace named "ShopEase" for local artisans',
        {"product_name": "ShopEase", "contract": "build_app", "audience_source": "stated"},
    ),
    (
        'mara app nu naam "KhedutMitra" che for organic farmers',
        {"product_name": "KhedutMitra", "contract": "build_app", "audience_source": "stated"},
    ),
    (
        'hamare naye tool ka naam "DataSync" hai',
        {"product_name": "DataSync", "contract": "build_tool"},
    ),
    (
        'Build a scheduling website with calendar sync',
        {"product_name": None, "contract": "build_app"},
    ),
    (
        'I want to make a todo app',
        {"product_name": None, "contract": "build_app"},
    ),
    (
        'design a microservice tool called "MetricPusher" for devops engineers',
        {"product_name": "MetricPusher", "contract": "build_tool", "audience_source": "stated"},
    ),
    (
        'create an accounting platform with name is "LedgerPro"',
        {"product_name": "LedgerPro", "contract": "build_app"},
    ),
    (
        'write a CLI utility called "log-stripper"',
        {"product_name": "log-stripper", "contract": "build_tool"},
    ),

    # 11-20: Preamble Stripping & Multi-Script Normalization
    (
        'want to learn html',
        {"action": "Learn", "subject_contains": "HTML", "contract": "learn"},
    ),
    (
        'want to learn c++',
        {"action": "Learn", "subject_contains": "C++", "contract": "learn"},
    ),
    (
        'help me learn python',
        {"action": "Learn", "subject_contains": "Python", "contract": "learn"},
    ),
    (
        'મારે Java શીખવું છે',
        {"action": "Learn", "subject_contains": "Java", "input_language": "Gujarati", "contract": "learn"},
    ),
    (
        'mujhe docker sikhna hai',
        {"action": "Learn", "subject_contains": "Docker", "contract": "learn"},
    ),
    (
        'i am want to create a blog platform',
        {"action": "Build", "subject_contains": "Blog", "contract": "build_app"},
    ),
    (
        'please give me a roadmap for machine learning',
        {"action": "Plan", "contract": "learn"},
    ),
    (
        'kuch banao',
        {"proficiency": "Novice / Beginner", "contract": "build_app"},
    ),
    (
        'કૃપા કરીને મને એક વેચાણ વેબસાઇટ આપો',
        {"input_language": "Gujarati", "contract": "build_app"},
    ),
    (
        'mere liye ek inventory management app banao',
        {"contract": "build_app"},
    ),

    # 21-30: Requester vs Audience Separation & Stated Audiences
    (
        'I want to make a learning portal for elementary school kids',
        {"requester": "Software Developer", "audience_contains": "Elementary School Kids", "audience_source": "stated"},
    ),
    (
        'Develop an EHR portal for hospital doctors',
        {"requester": "Software Developer", "audience_contains": "Hospital Doctors", "audience_source": "stated"},
    ),
    (
        'As a junior developer, I want to build a rest api',
        {"requester": "Junior Developer", "audience_source": "assumed"},
    ),
    (
        'I am a teacher, help me create a classroom quiz app',
        {"requester": "Teacher", "contract": "build_app"},
    ),
    (
        'I want to make a destination wedding plan in Udaipur for family guests',
        {"contract": "event", "audience_source": "stated"},
    ),
    (
        'Build a financial valuation model for angel investors',
        {"contract": "business", "audience_source": "stated"},
    ),
    (
        'Design a mobile fitness tracker',
        {"requester": "Software Developer", "audience_source": "assumed"},
    ),
    (
        'Audit cloud infrastructure compliance for enterprise regulators',
        {"contract": "analyze", "audience_source": "stated"},
    ),
    (
        'Write a sci-fi cyberpunk novel chapter for young adult readers',
        {"contract": "write", "audience_source": "stated"},
    ),
    (
        'Create a customer loyalty rewards platform',
        {"audience_source": "assumed"},
    ),

    # 31-40: Proficiency Signals & Invariants
    (
        'want to learn advanced distributed systems architecture',
        # Learn request with architecture vocabulary raises to Intermediate, NEVER Senior alone!
        {"contract": "learn", "proficiency": "Intermediate / Practitioner", "signal": "architecture_vocabulary_learning"},
    ),
    (
        'want to learn zero-trust security networking',
        {"contract": "learn", "proficiency": "Intermediate / Practitioner", "signal": "architecture_vocabulary_learning"},
    ),
    (
        'help me learn javascript basics',
        {"contract": "learn", "proficiency": "Novice / Beginner", "signal": "action_learn_default"},
    ),
    (
        'I am a Senior Solutions Architect wanting to design high-throughput Kafka streaming',
        {"proficiency": "Advanced / Senior", "signal": "explicit_self_seniority"},
    ),
    (
        'fix this critical kernel segfault and memory leak in production',
        {"contract": "debug", "proficiency": "Advanced / Senior", "signal": "critical_fault_complexity"},
    ),
    (
        'fix this NullPointerException',
        {"contract": "debug"},
    ),
    (
        'Design a Raft consensus distributed state machine',
        {"proficiency": "Advanced / Senior", "signal": "distributed_systems_lexicon"},
    ),
    (
        'organic farming app',
        {"proficiency": "Intermediate / Practitioner"},
    ),
    (
        'Build an API gateway with choice of REST or GraphQL',
        {"has_decision_needed": True},
    ),
    (
        'want to learn rust',
        {"contract": "learn", "proficiency": "Novice / Beginner", "tone_contains": "supportive"},
    ),
]


@pytest.mark.parametrize("query,expected", SPEC_40_CASES)
def test_spec_extractor_40_cases(extractor, query, expected):
    spec = extractor.extract(query)
    assert isinstance(spec, PromptSpec)

    if "product_name" in expected:
        assert spec.product_name == expected["product_name"]

    if expected.get("no_product_in_subject"):
        if spec.product_name:
            assert spec.product_name.lower() not in spec.subject.lower()

    if "contract" in expected:
        assert spec.contract == expected["contract"]

    if "action" in expected:
        assert spec.action.lower() == expected["action"].lower()

    if "subject_contains" in expected:
        assert expected["subject_contains"].lower() in spec.subject.lower()

    if "input_language" in expected:
        assert spec.input_language == expected["input_language"]

    if "audience_source" in expected:
        assert spec.audience_source == expected["audience_source"]

    if "audience_contains" in expected:
        assert expected["audience_contains"].lower() in spec.audience.lower()

    if "requester" in expected:
        assert expected["requester"].lower() in spec.requester.lower()

    if "proficiency" in expected:
        assert spec.proficiency == expected["proficiency"]

    if "signal" in expected:
        assert expected["signal"] in spec.proficiency_signals

    if expected.get("has_decision_needed"):
        assert len(spec.decisions_needed) > 0

    if "tone_contains" in expected:
        assert expected["tone_contains"] in spec.tone.lower()
