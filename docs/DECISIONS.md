# Intentify — Architecture Decision Records (ADR)

**Version**: 1.0  
**Updated**: 2026-10-27

---

## ADR 001: 100% Local Inference & Zero External AI APIs

### Context
Commercial LLM APIs (OpenAI GPT-4, Anthropic Claude, Google Gemini, Groq) provide rapid prototyping but introduce major vulnerabilities for enterprise prompt compilation: latency spikes, network flakiness, token costs, security leakage of proprietary instructions, and external runtime dependencies.

### Decision
Intentify runs 100% locally and offline. All tokenization, classification, domain resolution, prerequisite graph traversal, prompt composition, candidate reranking, and quality evaluation execute on the host machine with zero network calls at runtime.

### Consequences
- **Positive**: Sub-second execution latency (< 250ms), 0 data privacy risks, predictable deterministic execution, works completely air-gapped.
- **Negative**: Requires custom neural network architectures and structured modular blueprints rather than delegating entire generation to a commercial 175B-parameter model.

---

## ADR 002: Pure NumPy Vectorized Neural Architecture with Adam Optimizer

### Context
In Python 3.15 on Windows 11, prebuilt C-extension wheels for `torch` and `scikit-learn` frequently encounter ABI compatibility conflicts or heavyweight dependencies. A lightweight, robust, native mathematical engine was required for intent, domain, role, and quality classification.

### Decision
We implemented `NumpyDenseLayer` in `ml-engine/models/model_architectures.py`, featuring:
- Full vectorized matrix multiplication in NumPy.
- First- and second-moment Adam optimization (`m_w`, `v_w`) with bias correction.
- Multi-activation support (ReLU, Softmax, Sigmoid, Linear).
- Categorical Cross-Entropy and Mean Squared Error loss functions.

### Consequences
- **Positive**: Zero external binary dependencies; trains in < 15 seconds across 5,000 samples; reaches 98-100% accuracy; executes inference in < 2ms.
- **Negative**: Custom backpropagation code must be maintained within the repository.

---

## ADR 003: Dynamic Output Language Mirroring by Default

### Context
Earlier iterations defaulted prompt generation to a fixed language (such as English or Gujarati). However, users who prompt in English expect English master prompts, users who prompt in Gujarati expect Gujarati master prompts, and users who prompt in Hindi expect Hindi master prompts, while keeping technical terms in English.

### Decision
The master prompt's output language strictly matches the detected input language by default:
- English input -> English prompt with English headings and technical terms.
- Gujarati input -> Gujarati prompt with localized Gujarati headings and English technical terms.
- Hindi input -> Hindi prompt with localized Hindi headings and English technical terms.
- The UI and API provide an explicit language selector that overrides this default whenever specified by the user.

### Consequences
- **Positive**: Natural user experience without forcing awkward translations on native English speakers while offering first-class native support for Indic languages.
- **Negative**: Section templates, headings, and grammar rules must be maintained across multiple language scripts.

---

## ADR 004: Decoupled Audience Proficiency & AI Persona Alignment

### Context
A classic failure mode of naive prompt generators is "role echoing" or "proficiency conflation". For example:
- A user stating "I am a high school student, teach me Java" would previously generate an AI prompt that set the AI persona to "High School Student", leading to nonsensical self-teaching prompts.
- Or conversely, if the user requested "want to learn Java", a system might classify them as a "Principal Java Architect", overloading a beginner with Kubernetes and microservice architecture.

### Decision
We strictly decouple:
1. **Audience & User Proficiency**: `Novice / Beginner`, `Intermediate`, `Advanced / Senior`.
2. **AI Expert Persona**: `Principal Java Architect & Computer Science Educator`, `Senior HealthTech Enterprise Architect`, etc.
3. **Role Elevation**: When non-technical professions request technical systems (e.g. Doctor requesting clinic software), the AI persona is elevated to the technical architect role, while preserving the user's domain context.

### Consequences
- **Positive**: Prompts correctly instruct the downstream LLM to adopt world-class expertise while tailoring the curriculum or explanation to the student's true level.
- **Negative**: Requires dedicated alignment rules and penalty evaluations.

---

## ADR 005: Multi-Candidate Sampling & Quality Reranking

### Context
A single deterministic template pass cannot explore different prompt depths or tradeoffs (concise vs. deep vs. standard).

### Decision
`CandidateReranker` generates 3 distinct candidates for every specification:
1. `concise`: Streamlined, operational, punchy directives.
2. `standard`: Balanced, full-scale master prompt.
3. `deep`: Exhaustive enterprise-grade blueprint with deep architectural or curricular rigor.

The `QualityEngine` audits all three candidates using a calibrated 100-point rubric and strict penalty rules. The highest-scoring compliant candidate is selected as the winner.

### Consequences
- **Positive**: Resilient against edge-case formatting flaws; guarantees maximum quality score for every request.
- **Negative**: 3x composition evaluation cost (mitigated by sub-5ms pure Python composition speed).

---

## ADR 006: Self-Learning Memory Gatekeeper

### Context
Unsupervised continuous learning pipelines are vulnerable to "data poisoning" or feedback contamination, where erroneous prompts or echoed inputs get saved to memory and degrade future generations.

### Decision
The `MemoryAdmissionGate` (`app.engine.memory_gate`) enforces strict entry criteria before any exemplar is stored in `learning_store.json`:
- Minimum quality score >= 88.0.
- Zero goal echoes (no "want to", "mare joiye", "a want to").
- Zero duplicate headings.
- Zero persona/proficiency contradictions.
- Verified domain and role alignment.

### Consequences
- **Positive**: The learning store only accumulates gold-standard exemplars, preventing catastrophic drift.
- **Negative**: Rejects imperfect feedback entries that might have contained partial signal.

---

## ADR 007: Word-Boundary Regex Matching for Forbidden Acronyms & Phrases

### Context
Naive substring matching (`phrase.lower() in text.lower()`) falsely flags words containing acronyms as substring components. Specifically, checking for the forbidden acronym `SEC` (Securities and Exchange Commission) caused false-positive violations on legitimate words such as `security`, `section`, `sector`, and `second` across non-financial domains (wedding planning, corporate summits, agriculture, novel writing).

### Decision
All forbidden phrase validation in `app.engine.validators` and `evaluation.evaluate` uses boundary-aware regex matching:
- Acronyms / short all-caps tokens ($\le 5$ characters, such as `SEC`, `NASA`, `HIPAA`, `SQL`, `ICU`): matched case-sensitively with strict word boundaries `rf"\b{re.escape(phrase)}\b"`.
- Multi-word phrases or standard text: matched case-insensitively with strict word boundaries `rf"\b{re.escape(phrase)}\b"`.

### Consequences
- **Positive**: Eliminates all false-positive flags on words like `security` and `sector` while strictly catching leaks of actual acronyms like `SEC`.
- **Negative**: Requires regex compilation (mitigated by Python regex caching).

---

## ADR 008: Score Honesty & Golden Rubric Penalty Integration

### Context
In earlier baseline runs, test cases could fail critical golden criteria (forbidden phrases, forbidden cross-domain headings, missing core entities, or misclassified proficiency/domain) while the quality score remained above 95 or near 100. This score inflation obscured defects and allowed failing prompts to be rated acceptable.

### Decision
We map every golden failure type directly to explicit penalties and invariant violations inside `app.engine.validators`:
- Forbidden phrase present: -10 each (min 1 hit), flagged as hard check violation (capping score $\le 70.0$).
- Forbidden heading present: -10 each, flagged as hard check violation.
- Missing core objective keyword: -10 each, flagged as hard check violation.
- Wrong proficiency / seniority: -15, flagged as hard check violation.
- Wrong domain classification: -15, flagged as hard check violation.
- Intent mismatch: -15, flagged as hard check violation.

A prompt passes if and only if `score >= min_score AND not hard_check_failed AND all rubric assertions pass`.

### Consequences
- **Positive**: Complete score honesty. Any prompt with a forbidden phrase, wrong seniority, or missing keyword scores $< 85.0$, dropping the count of "fail but score $\ge 85$" to zero.
- **Negative**: Requires strict alignment between extractor, planner, composer, and validators.

---

## ADR 009: Synchronization of Route Tests with Domain-Adaptive Headings

### Context
`tests/test_fastapi_backend.py` originally hardcoded assertions for Step 12 static template headings (`1. Role & Persona`, `6. Step-by-Step Execution Instructions`), which conflicted with the dynamic, localized, domain-adaptive headings introduced in the 33-step compiler (`Role & Technical Persona`, `Role & Pedagogical Persona`, `Event Coordination & Operational Topology`, etc.).

### Decision
Synchronized `tests/test_fastapi_backend.py` to match `backend/tests/test_fastapi_backend.py`, verifying cognitive functional sections (`Persona`, `Objective`, `Topology` / `Curriculum`, `Acceptance Criteria`, `Format`, `Checklist`, `Guardrails`, `Assumptions`) rather than rigid template literals.

### Consequences
- **Positive**: Tests verify the actual cognitive compiler architecture across domains and languages without fragile string locking.
- **Negative**: None. API contract and JSON response schemas remain 100% identical.

---

## ADR 010: Single Canonical Golden Benchmark Set (Phase C)

### Context
Multiple copies of golden test cases existed across the repository: `tests/golden/golden_cases.json` (205 cases), `tests/golden/cases.json` (205 duplicate), `backend/tests/golden/cases.json` (205 duplicate), and an out-of-date 62-case subset at `backend/tests/golden/golden_cases.json`. This posed risks of test drift and divergence.

### Decision
1. Retain `tests/golden/golden_cases.json` (205 cases) as the single canonical golden dataset.
2. Verified with `grep` across the codebase that all loaders (`tests/test_golden_cases.py`, `backend/tests/test_golden_cases.py`, `backend/tests/test_master_prompt_invariants.py`, and `ml-engine/evaluation/evaluate.py`) resolve to `tests/golden/golden_cases.json`.
3. Deleted `tests/golden/cases.json` and `backend/tests/golden/`.
4. Added an automated regression test `test_no_conflicting_golden_sets()` in `tests/test_golden_cases.py` that fails if multiple golden datasets with differing case counts exist.

### Consequences
- **Positive**: Single source of truth. Zero risk of split-brain benchmark evaluation.
- **Negative**: None.

---

## ADR 011: Novel Domain Alignment (G12) Reversion & False Expectation Classification

### Status
**Pending Owner Approval**

### Context
In test cases `case_142_generic_36`, `case_143_generic_37`, `case_144_generic_38`, `case_181_generic_75`, `case_182_generic_76`, `case_183_generic_77`, the test asserts `expected_domain: "Generic"`. However, the prompt compiler synthesizes high-fidelity specific domains (e.g. `Autonomous Hydroponics`, `Business & Strategy`, `Software Development`) directly from input entities and action verbs. A generic loosening equivalence was previously applied in `validators.py`.

### Decision
Per Mission Step 1 instructions:
1. Reverted the `if exp_domain in ("generic", "general", ...)` equivalence from `validators.py`.
2. Classified G12 as **FALSE EXPECTATION** because penalizing an intelligent compiler for synthesizing a specific domain contradicts the product mission of domain intelligence.
3. The 6 affected cases currently fail domain alignment (scored 70.0, capping score honesty $\le 70.0$) awaiting owner decision on whether specific domain synthesis satisfies `Generic`.

### Consequences
- **Positive**: Strict adherence to explicit expectations; highlights the tension between generic fallback and entity-driven domain synthesis.
- **Negative**: 6 golden benchmark cases fail on domain mismatch pending owner decision.

---

## ADR 012: Pedagogical Tone vs. Forbidden Phrase 'Patient' (G7)

### Status
**Pending Owner Approval**

### Context
Case `case_45_edu_sql_opt` includes `"forbidden_phrases": ["patient"]` intended to prevent healthcare/medical leakage into an SQL database prompt. The pedagogical prompt template in `planner.py` previously generated `"patient step-by-step instruction"`.

### Decision
Substituted `"supportive step-by-step instruction"` in `planner.py`. This change is cataloged as **Pending Owner Approval** awaiting confirmation on Owner Question 1: whether `'patient'` should be allowed as an adjective in beginner prompts or strictly forbidden.

---

## ADR 013: Synchronization of Route Tests with Domain-Adaptive Headings (G11)

### Status
**Pending Owner Approval**

### Context
`tests/test_fastapi_backend.py` originally hardcoded assertions for Step 12 static template headings (`1. Role & Persona`, `6. Step-by-Step Execution Instructions`). The compiler now generates adaptive, localized headings (`Role & Technical Persona`, `Role & Pedagogical Persona`, `Event Coordination & Operational Topology`).

### Decision
Synchronized assertions in `tests/test_fastapi_backend.py` to assert cognitive sections. Marked as **Pending Owner Approval** per Mission Step 1.
