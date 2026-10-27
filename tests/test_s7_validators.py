"""Unit tests for S7 Validators & Score Honesty (Phase P3 Gate)."""

import pytest
from app.engine.spec_extractor import PromptSpec
from app.engine.validators import (
    check_broken_phrase,
    check_placeholders_and_todos,
    check_wrong_contract,
    check_product_name_merged,
    check_audience_conflict,
    check_undecided_alternatives,
    check_unsupported_assumptions,
    check_unsupported_numbers,
    check_proficiency_signals_consistency,
    check_missing_requester_or_audience,
    calculate_d7_score,
    run_all_validators,
)


def _make_dummy_spec(**kwargs) -> PromptSpec:
    defaults = {
        "action": "Build",
        "subject": "Scheduling SaaS",
        "object_subject": "Scheduling SaaS",
        "requester": "Software Developer",
        "audience": "End Users & Platform Clients",
        "audience_source": "assumed",
        "proficiency": "Intermediate / Practitioner",
        "proficiency_signals": ["domain_baseline"],
        "contract": "build_app",
        "domain": "Software Development",
        "persona_role": "Principal Software Architect",
        "deliverable": "Production Architecture Specification",
        "format": "Markdown Document",
        "input_language": "English",
        "output_language": "English",
        "tone": "practical, structured",
        "raw_input": "Build a scheduling website with calendar sync",
    }
    defaults.update(kwargs)
    return PromptSpec(**defaults)


def test_check_broken_phrase():
    bad_prompt = "### 1. Role\nI am want to help you build a web app."
    passed, msg, penalty = check_broken_phrase(bad_prompt)
    assert not passed
    assert penalty == 20.0
    assert "i am want" in msg.lower()

    good_prompt = "### 1. Role\nAssume the persona of a world-class Software Architect."
    passed, msg, penalty = check_broken_phrase(good_prompt)
    assert passed
    assert penalty == 0.0


def test_check_placeholders_and_todos():
    bad_prompt = "### 3. Implementation\ndef handle():\n    # TODO: write implementation"
    passed, msg, penalty = check_placeholders_and_todos(bad_prompt)
    assert not passed
    assert penalty == 20.0
    assert "todo" in msg.lower()

    bad_mock = "### 4. Schema\nUse mock data for initial user accounts."
    passed, msg, penalty = check_placeholders_and_todos(bad_mock)
    assert not passed
    assert penalty == 20.0

    good_prompt = "### 4. Schema\nDefine strict PostgreSQL schema with UUID primary keys."
    passed, msg, penalty = check_placeholders_and_todos(good_prompt)
    assert passed
    assert penalty == 0.0


def test_check_wrong_contract():
    spec = _make_dummy_spec(contract="learn")
    bad_learn_prompt = "### 1. Role\nMentor\n### 2. Objective\nLearn Python\n### 3. System Architecture & Component Topology\nServices"
    passed, msg, penalty = check_wrong_contract(bad_learn_prompt, spec)
    assert not passed
    assert penalty == 15.0

    good_learn_prompt = "### 1. Role\nMentor\n### 2. Objective\nLearn Python\n### 3. Structured Curriculum & Hands-On Milestones\nTopics"
    passed, msg, penalty = check_wrong_contract(good_learn_prompt, spec)
    assert passed
    assert penalty == 0.0


def test_check_product_name_merged():
    bad_spec = _make_dummy_spec(product_name="taskflow", subject="taskflow project management tool")
    passed, msg, penalty = check_product_name_merged("### 2. Objective\nBuild taskflow", bad_spec)
    assert not passed
    assert penalty == 15.0

    good_spec = _make_dummy_spec(product_name="taskflow", subject="Project Management Tool")
    passed, msg, penalty = check_product_name_merged("### 2. Objective\nBuild Project Management Tool (taskflow)", good_spec)
    assert passed
    assert penalty == 0.0


def test_check_audience_conflict():
    beginner_spec = _make_dummy_spec(proficiency="Novice / Beginner")
    conflict_prompt = "### 1. Role\nPedagogical Mentor\n### 2. Objective\nArchitect enterprise solution for enterprise architects and staff engineers."
    passed, msg, penalty = check_audience_conflict(conflict_prompt, beginner_spec)
    assert not passed
    assert penalty == 15.0

    coherent_prompt = "### 1. Role\nPedagogical Mentor\n### 2. Objective\nTeach fundamentals to beginner students."
    passed, msg, penalty = check_audience_conflict(coherent_prompt, beginner_spec)
    assert passed
    assert penalty == 0.0


def test_check_undecided_alternatives():
    undecided_prompt = "### 3. Decisions\nPlease choose REST or GraphQL for the client communication layer."
    passed, msg, penalty = check_undecided_alternatives(undecided_prompt)
    assert not passed
    assert penalty == 10.0

    decided_prompt = "### 3. Decisions\nImplement REST APIs using OpenAPI 3.1 specifications."
    passed, msg, penalty = check_undecided_alternatives(decided_prompt)
    assert passed
    assert penalty == 0.0


def test_check_unsupported_assumptions():
    spec = _make_dummy_spec(raw_input="make a simple todo app")
    bloated_prompt = "### 5. Constraints\nImplement circuit breaker pattern and multi-region replication across clusters."
    passed, msg, penalty = check_unsupported_assumptions(bloated_prompt, spec)
    assert not passed
    assert penalty == 10.0

    requested_spec = _make_dummy_spec(raw_input="make a multi-region app with circuit breaker")
    passed, msg, penalty = check_unsupported_assumptions(bloated_prompt, requested_spec)
    assert passed
    assert penalty == 0.0


def test_check_unsupported_numbers():
    spec = _make_dummy_spec(raw_input="make a todo app")
    bloated_prompt = "### 4. Acceptance Criteria\nMust achieve 85% coverage across all test suites."
    passed, msg, penalty = check_unsupported_numbers(bloated_prompt, spec)
    assert not passed
    assert penalty == 10.0

    clean_prompt = "### 4. Acceptance Criteria\nAll unit tests must pass deterministically."
    passed, msg, penalty = check_unsupported_numbers(clean_prompt, spec)
    assert passed
    assert penalty == 0.0


def test_check_proficiency_signals_consistency():
    bad_spec = _make_dummy_spec(
        action="Learn",
        proficiency="Advanced / Senior",
        proficiency_signals=["action_learn_default"],
    )
    passed, msg, penalty = check_proficiency_signals_consistency("prompt text", bad_spec)
    assert not passed
    assert penalty == 15.0

    good_spec = _make_dummy_spec(
        action="Learn",
        proficiency="Novice / Beginner",
        proficiency_signals=["action_learn_default"],
    )
    passed, msg, penalty = check_proficiency_signals_consistency("prompt text", good_spec)
    assert passed
    assert penalty == 0.0


def test_check_missing_requester_or_audience():
    bad_spec = _make_dummy_spec(requester="")
    passed, msg, penalty = check_missing_requester_or_audience(bad_spec)
    assert not passed
    assert penalty == 10.0

    good_spec = _make_dummy_spec(requester="Software Engineer", audience="End Users")
    passed, msg, penalty = check_missing_requester_or_audience(good_spec)
    assert passed
    assert penalty == 0.0


def test_hard_check_caps_score_at_60_and_sets_status_draft():
    spec = _make_dummy_spec()
    prompt_with_placeholder = (
        "### 1. Role & Technical Persona\n- Expert Engineer\n"
        "### 2. Core Objective\n- Build app\n"
        "### 3. Architecture\n- TODO: complete subsystem\n"
        "### 4. Criteria\n- Complete\n"
        "### 5. Format\n- Markdown"
    )
    result = run_all_validators(
        prompt_text=prompt_with_placeholder,
        spec=spec,
        raw_input=spec.raw_input,
    )
    assert result.hard_check_failed is True
    assert result.status == "draft"
    assert result.total_score <= 60.0
    assert result.score_after_cap <= 60.0
    assert any(v.is_hard_check for v in result.violations)


def test_clean_prompt_passes_with_status_final():
    spec = _make_dummy_spec()
    clean_prompt = (
        "### 1. Role & Technical Persona\n- Assume persona of Principal Architect\n"
        "### 2. Core Objective & System Scope\n- Deliver scalable high-availability services\n"
        "### 3. System Architecture & Component Topology\n- Architecture layout\n"
        "### 4. Verifiable Acceptance Criteria\n- Enforces strict data integrity and schema validation\n"
        "### 5. Output Format Specification\n- Format response strictly as Markdown\n"
        "### 6. Documented Assumptions & Context\n- Baseline assumptions"
    )
    result = run_all_validators(
        prompt_text=clean_prompt,
        spec=spec,
        raw_input=spec.raw_input,
    )
    assert result.hard_check_failed is False
    assert result.status == "final"
    assert result.total_score >= 85.0
