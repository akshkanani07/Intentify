# Intentify — Universal AI Prompt Compiler Platform (Product Specification)

## 1. What is the Problem?

Artificial Intelligence adoption is accelerating rapidly, but the vast majority of users cannot communicate with AI effectively. Large language models and AI agents are powerful, but their output quality depends entirely on the precision, structure, domain context, and constraints of the instructions they receive.

The core issues are:
1. **Prompt Incompetence**: Users do not know how to construct comprehensive, production-grade AI prompts.
2. **Degraded Outputs**: Poor, vague, or naive prompts produce generic, inaccurate, or hallucinated AI outputs.
3. **High Cognitive Burden**: Prompt engineering has become an intricate technical discipline requiring deep understanding of personas, contextual framing, operational boundaries, edge cases, and output schemas.
4. **Intent Ambiguity**: Non-technical users struggle to articulate their true objectives clearly.
5. **Rigid Template Generators**: Existing prompt generators rely on naive slot-filling templates that fail across non-trivial or domain-specific use cases.
6. **Narrow Domain Scope**: Most existing tools support only a handful of software engineering or marketing tasks and crumble when presented with unfamiliar or multi-disciplinary tasks.
7. **Language Barriers**: Users communicating in Indic languages (Gujarati, Hindi) or mixed vernacular scripts face immense barriers when attempting to guide English-centric AI models.

---

## 2. How Intentify Solves the Problem

Intentify functions as an autonomous, local-first AI Cognitive Prompt Compiler that converts raw, unstructured human thoughts into bespoke, enterprise-grade AI instructions automatically.

Key capabilities:
- **Multilingual Understanding**: Accepts raw, natural input in any language, dialect, or mixed script (e.g. Gujarati, Hindi, English, Hinglish, Gujlish).
- **Cognitive Intent Understanding**: Decodes what the user actually wants to accomplish rather than blindly copying words or roles.
- **Domain & Sub-domain Detection**: Identifies the professional domain, sub-domain, and industry vertical without manual pre-configuration.
- **Requirement & Entity Extraction**: Dissects goals, core entities, technical parameters, constraints, and target deliverables.
- **Smart Proactive Assumptions**: Identifies informational gaps and automatically supplies domain-standard assumptions without burdening the user with redundant questions.
- **Audience & Proficiency Decoupling**: Separates the user's personal proficiency level from the AI expert persona, ensuring learners are never given unmanageable enterprise assumptions and senior architects are never treated as novices.
- **Dynamic Master Prompt Compilation**: Plans and compiles a structured, modular prompt using prerequisite concept graphs and blueprints.
- **Dynamic Output Language Rule**: **The final prompt is rendered in the user's input language by default** (English -> English, Gujarati -> Gujarati, Hindi -> Hindi). Technical terms (Java, API, JVM, RBAC) are strictly preserved in English. The UI or API may override the language.
- **Cognitive Quality Evaluation**: Audits and scores the compiled prompt against a 100-point rubric and 12 cognitive dimensions before presentation.
- **Continuous Feedback Learning Loop**: Learns from user acceptance, ratings, and edits, storing verified exemplars in a quality-gated learning store.

---

## 3. Scope & Absolute Architectural Rules

### Absolute Rules:
- **Zero Hosted AI APIs**: No runtime calls to OpenAI, Claude, Gemini, Groq, Hugging Face Hosted, or any remote AI endpoint.
- **100% Local Inference**: All neural networks, embeddings, classifiers, and rule engines run entirely on the host machine.
- **Bespoke Generation**: Every prompt is unique and dynamically synthesized from modular components. No static hardcoded templates as complete outputs.
- **Zero Hallucination / Mock Data**: Prompts must never contain unfinished placeholders (`TODO`, `...`, `lorem ipsum`, or unpopulated brackets).
- **Default Language Mirroring**: The output prompt language must match the input text language by default unless explicitly overridden by user request.

---

## 4. System Modules & Specifications

### Module 1: Language Processing Module
- **Purpose**: Prepare raw multilingual, multi-script input for downstream cognitive analysis.
- **Features**:
  - Script identification (Latin, Gujarati, Devanagari, Mixed).
  - Unicode NFC normalization.
  - Conversational preamble stripping (e.g. "I want to", "મારે જોઈએ છે", "help me") without losing target entities.
  - Multi-domain terminology normalization via curated lexicons.

### Module 2: Intent Understanding Module
- **Purpose**: Classify human intention into concrete cognitive actions.
- **Features**:
  - Multi-class classification (Learn, Build, Plan, Debug, Explain, Analyze, Optimize, Refactor, Evaluate, Design, Write, Research, Audit).
  - Action verb extraction and primary target subject identification.
  - Goal decoupling: Separates the user's desire from their persona.

### Module 3: Domain Detection Module
- **Purpose**: Detect the professional vertical across 21 core domains.
- **Features**:
  - Software Development (SaaS, Web, Backend, Cloud, APIs).
  - Programming Languages (C, C++, Java, Python, JavaScript/TypeScript, SQL).
  - Healthcare & Clinical Systems.
  - Hospitality & Event Planning (Weddings, Catering, Tourism).
  - Business Strategy & Restaurant Operations.
  - Marketing & Growth.
  - Education & Pedagogy.
  - Design & UI/UX.
  - Writing & Content Strategy.
  - Research & Analysis.
  - Finance & Unit Economics.
  - Travel & Tourism.
  - Legal & Compliance.
  - Creative & Multimedia.
  - Debugging & Diagnostics.
  - Open Domain / Generic handling.

### Module 4: Requirement Analysis Module
- **Purpose**: Extract structured parameters, entities, constraints, and deliverable targets.
- **Features**:
  - Named entity extraction (technologies, locations, budgets, timeframes).
  - Explicit constraint extraction (negative constraints, prohibited tools, budgets).
  - Deliverable type determination (Code, Curriculum, Execution Plan, Incident Patch, Financial Model).

### Module 5: Smart Assumption Module
- **Purpose**: Fill informational gaps autonomously using domain priors.
- **Features**:
  - Domain-specific operational defaults (e.g. PostgreSQL + Redis for SaaS, JUnit 5 for Java, local vendor networks for weddings).
  - Explicit documentation of assumptions in prompt section.
  - Avoids interrogating the user with endless clarification forms.

### Module 6: AI Role Selection Module
- **Purpose**: Select and configure the optimal AI expert persona.
- **Features**:
  - Prevents blind persona copying (e.g. "Doctor" asking for "Hospital Management Software" -> "Principal HealthTech Enterprise Architect").
  - Role elevation for technical and operational complexity.
  - Decoupling of user proficiency from persona expertise.

### Module 7: Prompt Compilation Module
- **Purpose**: Assemble the structured Master Prompt.
- **Features**:
  - 8-to-10 modular sections:
    1. Role & Persona Definition
    2. Core Objective & Scope
    3. Pedagogical Breakdown / System Architecture / Domain Framework
    4. Execution Roadmap / Curriculum / API Contract
    5. Hands-on Code / Schema / Logistics Matrix
    6. Traps, Anti-patterns & Security / Guardrails
    7. Output Format Specification
    8. Self-Verification Quality Checklist
    9. Operational Boundaries & Negative Constraints
    10. Documented Assumptions

### Module 8: Prompt Optimization Module
- **Purpose**: Optimize prompt structure and clarity before presentation.
- **Features**:
  - Multi-candidate sampling (Concise, Standard, Deep).
  - Heading deduplication.
  - Conversational echo elimination (ensuring no "a want to" or awkward phrasing).

### Module 9: Prompt Quality Evaluation Module
- **Purpose**: Evaluate prompt quality objectively using a calibrated rubric.
- **Features**:
  - 100-point scoring scale across 6 core criteria.
  - 12-dimensional cognitive breakdown (Clarity, Specificity, Context, Constraints, Format, Persona, Assumptions, Domain Depth, Anti-patterns, Actionability, Guardrails, Completeness).
  - Hard rule penalties (-20 for goal echo, -15 for persona/proficiency contradiction, -10 for duplicate heading, -15 for domain mismatch).

### Module 10: Knowledge Base Module
- **Purpose**: Provide structured ground-truth domain intelligence.
- **Features**:
  - 21 Prerequisite concept graphs with dependency trees.
  - Domain terminology lexicons.
  - Exemplar prompt blueprints and section patterns.

### Module 11: Learning Module (Feedback Loop)
- **Purpose**: Continuously improve compilation intelligence from user interactions.
- **Features**:
  - Feedback ingestion API (`POST /api/v1/feedback`).
  - Strict Memory Admission Gatekeeper: Disallows prompts with low scores, goal echoes, or contradictions.
  - Learning store persistence (`learning_store.json`).
  - Active exemplar lookup for future compilation context.

---

## 5. Technology Stack

- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS, Lucide React icons.
- **Backend**: Python 3.15, FastAPI, Uvicorn, Pydantic v2.
- **Machine Learning**: Pure NumPy vectorized neural architectures with Adam optimizer, TF-IDF + n-gram vectorization, Cosine similarity, kNN retrieval.
- **Storage & Knowledge**: File-based JSON schemas, concept graph representations, and structured learning stores.
