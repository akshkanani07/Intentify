# Intentify — Platform Roadmap & Deferred Items

**Status**: Active  
**Version**: 4.0.0  
**Updated**: 2026-10-27

---

## 1. Current Phase Scope (100% Implemented & Verified)

All 11 primary modules defined in `docs/PRODUCT.md` are actively implemented in code and verified with unit tests and golden benchmarks:

1. **Language Processing Module**: Fully implemented in `app.engine.normalizer` and `app.nlp.language_detector`.
2. **Intent Understanding Module**: Implemented with neural Adam classifier (`ml-engine/models/intent_model`) and fallback semantic extraction in `app.nlp.goal_extractor`.
3. **Domain Detection Module**: Implemented with neural Adam classifier (`ml-engine/models/domain_model`) and rule-based resolver in `app.knowledge.domain_resolver`.
4. **Requirement Analysis Module**: Implemented in `app.nlp.requirement_extractor` and `app.nlp.entity_extractor`.
5. **Smart Assumption Module**: Implemented in `app.engine.planner` and `app.knowledge.dynamic_assumptions`.
6. **AI Role Selection Module**: Implemented with neural Adam classifier (`ml-engine/models/role_model`) and `app.nlp.role_alignment_engine`.
7. **Prompt Compilation Module**: Implemented in `app.engine.composer` and `app.engine.planner`.
8. **Prompt Optimization Module**: Implemented in `app.engine.reranker`.
9. **Prompt Quality Evaluation Module**: Implemented in `app.engine.quality_engine`.
10. **Knowledge Base Module**: Implemented in `app.knowledge.knowledge_manager` with 21 concept graphs and lexicons.
11. **Learning Module (Feedback Loop)**: Implemented in `app.engine.memory_gate`, `ml-engine/memory/learning_store.json`, and API feedback routes.

---

## 2. Explicitly Deferred Features & Architectural Rationale

The following items mentioned in earlier conceptual discussions or exploratory drafts are explicitly deferred to future releases, with explicit architectural rationale provided:

| Feature / Capability | Status | Target Milestone | Architectural Rationale for Deferral |
| :--- | :--- | :--- | :--- |
| **Distributed Redis Caching** | Deferred | v5.0 | In-process LRU memory caching and JSON loading is currently 100x faster than network Redis for single-node offline deployments and eliminates an external daemon requirement. |
| **ChromaDB / Milvus Vector DB** | Deferred | v5.0 | A dedicated C++ vector database daemon adds external shared library complexity on Windows without performance gains for <= 10,000 exemplars. NumPy vectorized cosine distance executes sub-millisecond in-process. |
| **On-device Quantized SLM (GGUF / Llama.cpp)** | Deferred | v5.0 | Running a 7B-parameter SLM requires 6GB+ VRAM or heavy CPU quantization, which degrades response time on standard laptop environments. The modular cognitive planner compiles higher-structure prompts deterministically in < 200ms. |
| **Multi-User RBAC & Auth System** | Deferred | v5.1 | Intentify is presently scoped as an autonomous developer and workstation compiler engine. Multi-tenancy and JWT auth add unnecessary barrier-to-entry for local offline CLI and single-tenant web UI use. |
| **Prompt Marketplace & Cloud Sync** | Deferred | v5.2 | Violates the current strict requirement of "100% offline local inference without network calls". Will be introduced in an enterprise cloud tier. |
| **Voice / Speech-to-Text Input** | Deferred | v5.2 | Local Whisper transcription models require substantial PyTorch CUDA dependencies incompatible with the lightweight Python 3.15 runtime. |
