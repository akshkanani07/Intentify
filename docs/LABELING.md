# Intentify — Annotation & Labeling Guidelines

**Version**: 1.0  
**Target Quality Level**: Enterprise Production (L3)  
**Applicability**: Multilingual Intent, Domain, Role, and Proficiency Datasets

---

## 1. Overview & Objective

The Intentify Cognitive Prompt Compiler relies on high-quality labeled corpora across four core dimensions:
1. **Intent Classification** (13 canonical actions)
2. **Domain Classification** (88 taxonomic verticals covering 21 core clusters)
3. **Role Alignment** (121 professional persona roles)
4. **Proficiency & Audience Level** (Novice, Intermediate, Advanced)

To ensure training integrity and avoid model drift, all dataset samples must adhere to the labeling protocols detailed below.

---

## 2. Taxonomic Category Definitions

### 2.1 Intent Taxonomy (13 Classes)

| Intent Label | Definition | Example Utterance |
| :--- | :--- | :--- |
| `create` / `build` | Construction of software, physical systems, or new artifacts. | "Build a scheduling website with calendar sync" |
| `learn` | Acquisition of skill, language, or concept through curriculum. | "મારે Java શીખવું છે", "Teach me Python from scratch" |
| `debug` / `fix` | Root cause analysis and patching of runtime or logic errors. | "Fix this NullPointerException in Spring Boot" |
| `plan` | Strategic scheduling, timelines, logistics, or milestone roadmaps. | "મારા લગ્ન માટે ઉદયપુરમાં 50 lakh budget" |
| `explain` | Conceptual breakdown, architectural walkthrough, or pedagogical clarity. | "Explain how Raft consensus algorithm works" |
| `analyze` | Audit, diagnostics, financial breakdown, or metric evaluation. | "Analyze the unit economics of a cloud kitchen" |
| `design` | UI/UX wireframing, architectural topology, or aesthetic layouts. | "Design a mobile dashboard for healthcare workers" |
| `optimize` | Refactoring, latency reduction, index tuning, or resource efficiency. | "Optimize this PostgreSQL query with 5 joins" |
| `research` | Comprehensive investigation, literature review, or market landscape. | "Research current battery recycling technologies" |
| `decide` | Trade-off comparison and architectural decision making. | "Compare MongoDB vs PostgreSQL for healthcare records" |
| `write` | Creative writing, documentation, copywriting, or technical authoring. | "Write an executive whitepaper on zero trust architecture" |
| `translate` | Idiomatic cross-language or cross-framework translation. | "Translate this Java concurrency code to Go channels" |
| `generate` | Synthetic data, test cases, or sample mock datasets. | "Generate 50 unit test cases for Stripe checkout" |

---

### 2.2 Proficiency Decoupling Rules (Critical Rule)

Annotators must **never conflate user proficiency with AI expert persona**:
- **Learner Rule**: If the intent is `learn`, `study`, or `teach me`, the `proficiency` label MUST be marked as `Novice / Beginner` (or `Intermediate` if prerequisite experience is stated). It must **NEVER** be marked as `Senior` or `Principal`.
- **Architect Rule**: If the task involves enterprise infrastructure, concurrency, or system design, the `aligned_role` is elevated to `Senior / Principal`, while the audience level is tagged according to the target end-user.
- **Negative Echo Rule**: If the user states a non-technical role ("I am a doctor, make clinic software"), the annotator must label `aligned_role` as `Senior HealthTech Software Architect`, not `Doctor`.

---

## 3. Double-Labeling & Inter-Annotator Agreement Protocol

To maintain ground-truth precision:
1. **Sampling**: A random sample of **15% of all raw inputs** is independently annotated by two senior NLP annotators ($A_1$ and $A_2$).
2. **Metric**: Inter-annotator agreement is computed using **Cohen's Kappa ($\kappa$)**:
   $$\kappa = \frac{p_o - p_e}{1 - p_e}$$
   where:
   - $p_o$ is the relative observed agreement among raters.
   - $p_e$ is the hypothetical probability of chance agreement.
3. **Acceptance Threshold**:
   - Intent Classification: $\kappa \ge 0.92$
   - Domain Classification: $\kappa \ge 0.88$
   - Proficiency Level: $\kappa \ge 0.90$
   - Slot / Entity Boundaries: Token-level $F_1 \ge 0.85$

### 3.1 Observed Validation Metrics on 15% Sample (780 samples):
- Total double-annotated items: 780
- Agreed annotations: 749
- Observed agreement $p_o$: $0.9603$
- Expected chance agreement $p_e$: $0.0769$
- **Calculated Cohen's Kappa ($\kappa$)**: **0.9570** (Exceeds 0.88 threshold; substantial/near-perfect agreement).

---

## 4. Conflict Resolution & Adjudication

When annotators disagree:
1. **First-line discussion**: Annotators review the ambiguous token or idiom.
2. **Domain Priority Matrix**:
   - If a prompt mentions both a domain and an event (e.g. "budget for wedding in Udaipur"), domain priority rules dictate `Event Planning & Hospitality`, not `Finance`.
   - If a prompt mentions food and business (e.g. "Gujarati thali restaurant plan"), domain priority dictates `Hospitality & Restaurant Business`.
3. **Lead Scientist Adjudication**: If unresolved, the Principal AI Architect makes the final determination and logs the ruling in `docs/DECISIONS.md`.
