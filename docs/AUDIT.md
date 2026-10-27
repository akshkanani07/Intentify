# Intentify Codebase Audit & Architectural Mapping

**Date**: 2026-10-27  
**Platform**: Windows 11 (PowerShell / CMD)  
**Python Runtime**: Python 3.15.1  
**Repository Root**: `C:\intentify`

---

## 1. Executive Summary

Intentify is a 100% offline, local-first AI Cognitive Prompt Compiler Platform. The system converts raw, unstructured human thoughts (in English, Gujarati, Hindi, or mixed scripts) into structured, professional, high-fidelity Master Prompts without making any external API calls (zero runtime dependency on OpenAI, Claude, Gemini, Groq, or Hugging Face Hosted).

The engine operates across a multi-stage cognitive pipeline:
```
Raw Human Input (Any Language / Mixed / Typos / Vague)
   ↓
[S1: Normalizer] Unicode NFC, Per-token Script Identification, Preamble Stripping, Lexicon Canonicalization
   ↓
[S2: Spec Extractor] Intent Classification, Product Name Extraction, Requester vs Audience Decoupling, Proficiency Signals
   ↓
[S3: Contract Selector] Contract JSON Schema Routing (build_tool | build_app | learn | debug | plan | business | event | write | analyze)
   ↓
[S4: Retrieval Engine] FAISS Index & 2-Tier Taxonomy Resolver (Parent Domain & Child Specialization)
   ↓
[S5: Generation Engine] Grammar-Constrained JSON Generation (Local Model / Rules Fallback)
   ↓
[S6: Renderer Engine] Script-Aware Markdown Generation in Contract-Defined Section Order
   ↓
[S7: Quality & Validators] Pure Validator Functions (Hard & Soft Penalties, Caps, Status: Final | Draft)
   ↓
[S8/S9: Regeneration & Reranker] Multi-Candidate Sampling & Targeted Single-Attempt Regeneration
   ↓
[S10: Self-Learning Gate] Quality Filtering & Learning Store Admission Gatekeeper
   ↓
Master Prompt Output
```

---

## 2. Directory & Module Topology

### 2.1 Backend (`backend/app`)

| Path | Primary Module / Class | Responsibilities & Usages | Test Suite |
| :--- | :--- | :--- | :--- |
| `main.py` | `create_app()`, `lifespan` | FastAPI entrypoint, CORS configuration, centralized exception handlers, startup knowledge and model caching. | `test_fastapi_backend.py` |
| `api/v1/routes/prompt.py` | `generate_prompt()` | HTTP POST endpoints for prompt compilation; handles validation, injection detection, quality exceptions. | `test_fastapi_backend.py` |
| `api/v1/schemas/prompt.py` | `PromptGenerationRequest`, `PromptGenerationResponse`, `PenaltyItem` | Pydantic v2 schemas for request input and response payload with cognitive metadata. | `test_fastapi_backend.py` |
| `engine/normalizer.py` | `InputNormalizer`, `NormalizedInput` | Unicode NFC normalization, script detection (Latin, Gujarati, Devanagari), preamble stripping without object loss, multi-domain lexicon mapping. | `test_engine_normalizer.py` |
| `engine/spec_extractor.py` | `SpecExtractor`, `PromptSpec` | Core specification extractor. Enforces proficiency decoupling, product_name extraction, requester vs audience separation. | `test_engine_spec_extractor.py` |
| `engine/planner.py` | `KnowledgePlanner`, `PromptPlan`, `PlanSection` | Contract-aligned blueprint routing. Enforces deduplication and prerequisite concept structures. | `test_cognitive_compiler_engine.py` |
| `engine/composer.py` | `PromptComposer` | Generates clean Markdown Master Prompts with script-appropriate localized headers and clean bullet directives. | `test_cognitive_compiler_engine.py` |
| `engine/reranker.py` | `CandidateReranker`, `RerankWinner` | Generates 3 candidate prompts (`concise`, `standard`, `deep`) and selects optimal candidate using `QualityEngine`. | `test_cognitive_compiler_engine.py` |
| `engine/quality_engine.py` | `QualityEngine`, `QualityAudit` | 100-point rubric, 12-dimensional cognitive breakdown, structured rule penalties. Single evaluator across platform. | `test_quality_evaluator.py`, `test_live_api_benchmark_parity.py` |
| `engine/validators.py` | Pure validator functions | Pure check functions for D1-D9 invariants, forbidden phrases, language fidelity, domain tree match, tone check. | `test_quality_evaluator.py` |
| `engine/memory_gate.py` | `MemoryAdmissionGate` | Gatekeeper preventing contaminated, echoed, or low-scoring entries from entering learning memory. | `test_engine_memory_gate.py` |
| `services/orchestrator.py` | `PromptOrchestrator` | End-to-end synchronization coordinating normalization, extraction, planning, composition, reranking, and self-learning loop. | `test_v4_self_learning_engine.py` |
| `nlp/language_detector.py` | `LanguageDetector` | Heuristic + Unicode-based language and script identification. | `test_language_intelligence.py` |
| `nlp/goal_extractor.py` | `GoalExtractor` | Dissects raw user input into primary action verbs and core target subjects. | `test_requirement_extraction.py` |
| `nlp/audience_detector.py` | `AudienceDetector` | Detects audience persona and proficiency level without contaminating learner profiles. | `test_audience_seniority.py` |
| `nlp/role_alignment_engine.py` | `RoleAlignmentEngine` | Aligns user-provided or inferred roles with true task requirements. | `test_role_intelligence_upgrade.py` |
| `core/security.py` | `PromptSafetyChecker` | Detects prompt injection, system prompt extraction, jailbreaks, and destructive instructions. | `test_golden_cases.py` |

---

## 3. P0 Baseline Audit Telemetry

### 3.1 Test Suite Status
- Command: `python -m pytest tests/ -q --tb=line`
- **Result**: `441 passed, 2 warnings in 71.98s (100% green)`

### 3.2 Golden Benchmark Evaluation
- Command: `python -m evaluation.evaluate --set golden` (205 cases)
- **Result**: `183 / 205 passed (89.3%)`
- **Mean Score**: `97.32` | **Median**: `100.0` | **Min**: `70.0` | **Max**: `100.0`
- **Latency**: `188.2 ms` avg
- **Language Match**: `100.0%`
- **Seniority Accuracy**: `193 / 199 (97.0%)`
- **Fail-but-score>=85**: `6 cases` (reduced from 41; remaining are 6 borderline seniority test assertions)

### 3.3 Live Inputs Baseline Audit
Saved to [`docs/audit/baseline/live_inputs_baseline.md`](file:///C:/intentify/docs/audit/baseline/live_inputs_baseline.md) and [`docs/audit/baseline/live_inputs_baseline.json`](file:///C:/intentify/docs/audit/baseline/live_inputs_baseline.json).
Identified baseline gaps:
1. **Product Name Separation**: On `i want to make project management tool, which name is "taskflow"`, `"taskflow"` was embedded in the subject rather than separated into `product_name`.
2. **Generic Enterprise Bloat**: Unrequested enterprise headings (production CI/CD, high-availability multi-region) appear in basic app/tool requests.
3. **Preamble Stripping**: Raw colloquial phrases ("want to learn", "help me learn") occasionally echoed in objective statements.
4. **Contract Routing**: Section layout needs to adhere strictly to declarative Contract JSON definitions (`knowledge-base/contracts/<contract>.json`).
5. **Tone Invariant**: Replace legacy `"patient"` references with `"supportive"` across all learner pipelines.

---

## 4. Phase Execution Plan

- **P0 Audit and Baseline**: COMPLETE (Recorded baseline, created `tests/live/live_inputs.json`, updated `docs/AUDIT.md`).
- **P1 Spec Extractor & Product Name Separation**: S1 normalizer upgrades, S2 PromptSpec with explicit `product_name`, `requester` vs `audience`, `contract` enum, 40 unit tests.
- **P2 Contracts and Taxonomy**: S3 declarative contract schemas (`knowledge-base/contracts/*.json`), S4 FAISS retrieval and 2-tier taxonomy.
- **P3 Validators & Score Honesty**: Pure validator functions with unit tests, hard vs soft check penalties, status `final` vs `draft`, score capped at 60 on hard fail.
- **P4 Generation and Renderer**: S5 grammar-constrained JSON generation with `rules_fallback` mode, S6 deterministic renderer, S8 single-attempt regeneration, S9 multi-candidate selection.
- **P5 Knowledge Expansion**: Schema validation for 29 drafted concept graphs with `reviewed: false`, `content_share` telemetry.
- **P6 API, UI & Cleanup**: Schema updates on `/api/v1/generate-prompt`, frontend badge alignment, deletion of duplicate golden sets.
- **P7 Single Held-Out Measurement**: Single execution on frozen Held-Out v2 (`tests/heldout/heldout_v2_cases.json`).
