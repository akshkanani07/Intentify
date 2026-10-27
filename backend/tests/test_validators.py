"""Unit tests for individual invariant validators D1-D9."""

import pytest
from app.engine.spec_extractor import PromptSpec
from app.engine.validators import (
    check_d1_topics,
    check_d2_repeated_content,
    check_d3_raw_input_leak,
    check_d4_meaningless_criteria,
    check_d5_tone,
    check_d6_standards,
    calculate_d7_score,
    check_d8_objective,
    check_d9_language,
    run_all_validators,
    check_forbidden_phrase_match,
    check_forbidden_phrases,
    check_forbidden_headings,
    check_objective_keywords,
    check_proficiency_alignment,
)


class TestD1Topics:
    def test_d1_passes_for_5_topics_with_objective_and_exercise(self):
        spec = PromptSpec(
            action="Learn",
            object_subject="C++",
            domain="Software Development",
            audience="Students & Learners",
            proficiency="Novice / Beginner",
            persona_role="C++ Mentor",
            deliverable="Curriculum",
            format="Markdown",
        )
        sample = """
### Topic 1: Variables and Basic Syntax
- Objective: Understand integer types and declaration syntax.
- Exercise: Write a program calculating area of a rectangle.

### Topic 2: Control Flow
- Objective: Master if-else branching and while loops.
- Exercise: Implement a number guessing game.

### Topic 3: Functions and Scope
- Objective: Comprehend parameters, return values, and call stack.
- Exercise: Create modular conversion utilities.

### Topic 4: Pointers and Memory
- Objective: Grasp memory addresses and dereferencing operators.
- Exercise: Implement swap function using pointer arguments.

### Topic 5: Object-Oriented Basics
- Objective: Construct classes with constructors and encapsulation.
- Exercise: Model a BankAccount class with deposit and withdraw methods.
"""
        passed, msg, penalty, count = check_d1_topics(sample, spec)
        assert passed is True
        assert count == 5
        assert penalty == 0.0

    def test_d1_fails_when_topics_missing_or_fewer_than_5(self):
        spec = PromptSpec(
            action="Learn",
            object_subject="HTML",
            domain="Software Development",
            audience="Students & Learners",
            proficiency="Novice / Beginner",
            persona_role="HTML Mentor",
            deliverable="Curriculum",
            format="Markdown",
        )
        sample = "Just learn HTML tags and have fun."
        passed, msg, penalty, count = check_d1_topics(sample, spec)
        assert passed is False
        assert penalty == 20.0
        assert count < 5


class TestD2RepeatedContent:
    def test_d2_passes_unique_content(self):
        sample = "This is the first sentence with unique tokens. And here is a second distinct thought. Finally a third concluding statement."
        passed, msg, penalty, dups = check_d2_repeated_content(sample)
        assert passed is True
        assert dups == 0

    def test_d2_fails_exact_and_near_duplicates(self):
        sample = (
            "Ensure every facet of this directive is thoroughly executed with zero ambiguity.\n"
            "Some intermediate content here.\n"
            "Ensure every facet of this directive is thoroughly executed with zero ambiguity."
        )
        passed, msg, penalty, dups = check_d2_repeated_content(sample)
        assert passed is False
        assert dups >= 1
        assert penalty >= 10.0


class TestD3RawInputLeak:
    def test_d3_passes_when_no_verbatim_leak(self):
        criteria = "The learner can build semantic HTML forms with accessible labels and input validation."
        raw_input = "want to learn html"
        passed, msg, penalty, ratio = check_d3_raw_input_leak(criteria, raw_input)
        assert passed is True
        assert ratio <= 0.30

    def test_d3_fails_when_verbatim_3gram_leak(self):
        criteria = "### Acceptance Criteria\n- Fulfills the core objective: want to learn html right now"
        raw_input = "want to learn html"
        passed, msg, penalty, ratio = check_d3_raw_input_leak(criteria, raw_input)
        assert passed is False
        assert ratio > 0.30
        assert penalty == 10.0


class TestD4MeaninglessCriteria:
    def test_d4_passes_valid_constraint_reference(self):
        spec = PromptSpec(
            action="Build",
            object_subject="SaaS",
            domain="Software Development",
            audience="Engineers",
            proficiency="Senior",
            persona_role="Architect",
            deliverable="Architecture",
            format="Markdown",
            constraints=["PostgreSQL strictly", "Kafka event streaming"],
        )
        criteria = "- Satisfies all 2 specified constraints: PostgreSQL strictly and Kafka event streaming."
        passed, msg, penalty = check_d4_meaningless_criteria(criteria, spec)
        assert passed is True

    def test_d4_fails_when_referencing_constraints_with_empty_spec(self):
        spec = PromptSpec(
            action="Build",
            object_subject="SaaS",
            domain="Software Development",
            audience="Engineers",
            proficiency="Senior",
            persona_role="Architect",
            deliverable="Architecture",
            format="Markdown",
            constraints=[],
        )
        criteria = "- Satisfies all 2 specified operational & negative constraints"
        passed, msg, penalty = check_d4_meaningless_criteria(criteria, spec)
        assert passed is False
        assert penalty == 10.0


class TestD5Tone:
    def test_d5_passes_for_patient_beginner_tone(self):
        spec = PromptSpec(
            action="Learn",
            object_subject="Python",
            domain="Software Development",
            audience="Students & Learners",
            proficiency="Novice / Beginner",
            persona_role="Python Mentor",
            deliverable="Curriculum",
            format="Markdown",
        )
        prompt = """### Role & Persona
Assume the persona of a patient, step-by-step programming mentor. Explain concepts from first principles using intuitive analogies, and define every term on first use.
"""
        passed, msg, penalty = check_d5_tone(prompt, spec)
        assert passed is True

    def test_d5_fails_when_beginner_prompt_uses_principal_practitioner(self):
        spec = PromptSpec(
            action="Learn",
            object_subject="Python",
            domain="Software Development",
            audience="Students & Learners",
            proficiency="Novice / Beginner",
            persona_role="Python Mentor",
            deliverable="Curriculum",
            format="Markdown",
        )
        prompt = "Approach this assignment with the ruthless efficiency of a principal practitioner."
        passed, msg, penalty = check_d5_tone(prompt, spec)
        assert passed is False
        assert penalty == 15.0


class TestD6Standards:
    def test_d6_passes_with_matching_standards(self):
        spec = PromptSpec(
            action="Build",
            object_subject="Python API",
            domain="Software Development",
            audience="Engineers",
            proficiency="Senior",
            persona_role="Architect",
            deliverable="API",
            format="Markdown",
        )
        standards = {"python": {"standards": ["PEP 8"]}}
        prompt = "Adhere strictly to PEP 8 conventions."
        passed, msg, penalty = check_d6_standards(prompt, spec, standards)
        assert passed is True

    def test_d6_fails_when_foreign_standard_leaked(self):
        spec = PromptSpec(
            action="Learn",
            object_subject="HTML",
            domain="Web Development",
            audience="Students",
            proficiency="Novice / Beginner",
            persona_role="Mentor",
            deliverable="Curriculum",
            format="Markdown",
        )
        standards = {"python": {"standards": ["PEP 8"]}}
        prompt = "For HTML, adhere to PEP 8 standards."
        passed, msg, penalty = check_d6_standards(prompt, spec, standards)
        assert passed is False
        assert penalty == 10.0


class TestD7ScoreFormula:
    def test_d7_caps_at_70_on_hard_check_failure(self):
        score = calculate_d7_score(penalties=[10.0], hard_check_failed=True, ml_adjustment=3.0)
        assert score <= 70.0

    def test_d7_honest_subtraction(self):
        score = calculate_d7_score(penalties=[15.0, 10.0], hard_check_failed=False, ml_adjustment=0.0)
        assert score == 75.0


class TestD8Objective:
    def test_d8_passes_when_subject_and_outcome_present(self):
        spec = PromptSpec(
            action="Learn",
            object_subject="Java",
            domain="Software Development",
            audience="Students",
            proficiency="Novice",
            persona_role="Mentor",
            deliverable="Curriculum",
            format="Markdown",
        )
        prompt = "### Core Objective\nMaster Java foundational syntax to build first console application."
        passed, msg, penalty = check_d8_objective(prompt, spec)
        assert passed is True

    def test_d8_fails_when_subject_missing(self):
        spec = PromptSpec(
            action="Learn",
            object_subject="Java",
            domain="Software Development",
            audience="Students",
            proficiency="Novice",
            persona_role="Mentor",
            deliverable="Curriculum",
            format="Markdown",
        )
        prompt = "### Core Objective\nStudy general programming concepts."
        passed, msg, penalty = check_d8_objective(prompt, spec)
        assert passed is False


class TestD9Language:
    def test_d9_passes_matching_gujarati(self):
        prompt = "### ભૂમિકા અને પર્સના\n- આ પ્રોમ્પ્ટ મુજબ નિષ્ણાત માર્ગદર્શન આપો અને દરેક વિષય સરળ ભાષામાં સમજાવો."
        passed, msg, penalty, detected = check_d9_language(prompt, "Gujarati")
        assert passed is True
        assert detected == "Gujarati"

    def test_d9_fails_when_english_expected_but_gujarati_rendered(self):
        prompt = "### ભૂમિકા અને પર્સના\n- આ પ્રોમ્પ્ટ મુજબ નિષ્ણાત માર્ગદર્શન આપો અને દરેક વિષય સરળ ભાષામાં સમજાવો."
        passed, msg, penalty, detected = check_d9_language(prompt, "English")
        assert passed is False
        assert penalty == 20.0


class TestForbiddenPhraseMatching:
    def test_sector_passes_no_sec_violation(self):
        text = "The energy SECTOR must follow strict compliance rules."
        assert check_forbidden_phrase_match("SEC", text) is False

    def test_security_passes_no_sec_violation(self):
        text = "SECURITY is critical for multi-tenant isolation."
        assert check_forbidden_phrase_match("SEC", text) is False

    def test_sec_caught_fails(self):
        text = "Report to the SEC immediately."
        assert check_forbidden_phrase_match("SEC", text) is True


class TestScoreHonesty:
    def test_prompt_with_forbidden_phrase_scores_below_85(self):
        spec = PromptSpec(
            action="Build",
            object_subject="Scheduling Website",
            domain="Software Engineering",
            audience="Software Engineers",
            proficiency="Senior",
            persona_role="Principal Architect",
            deliverable="Architecture Document",
            format="Markdown",
        )
        prompt = """### Role & Technical Persona
Assume the persona of an authoritative Principal Architect.

### Core Objective & System Scope
System Objective: Architect production-ready Scheduling Website for Software Engineers to deliver high-availability services.

### System Architecture & Component Topology
Subsystem 1: Calendar Sync Service
- Design Objective: Synchronize calendars.
- Implementation Requirement: Integrate APIs.
Subsystem 2: Notification Pipeline
- Design Objective: Deliver alerts.
- Implementation Requirement: Message queue.
Subsystem 3: Scheduling Engine
- Design Objective: Resolve booking slots.
- Implementation Requirement: Time slot algorithm.
Subsystem 4: Security and Auth
- Design Objective: OAuth authentication.
- Implementation Requirement: JWT verification.
Subsystem 5: Database Persistence
- Design Objective: Store user bookings.
- Implementation Requirement: Scalable relational storage.

### Verifiable Acceptance Criteria
- Fulfills all subsystem design objectives.
- Contains zero placeholders or unverified approximations.
- Report to the SEC immediately for regulatory filings.

### Output Format Specification
Format response strictly as Markdown.
"""
        # Audit with forbidden phrase 'SEC'
        audit = run_all_validators(
            prompt_text=prompt,
            spec=spec,
            raw_input="Build a scheduling website",
            forbidden_phrases=["SEC"],
        )
        # Score must be honest: cannot score >= 85 when forbidden phrase leaked!
        assert audit.hard_check_failed is True
        assert audit.total_score < 85.0
        assert audit.total_score <= 70.0

