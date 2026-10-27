# Held-Out Evaluation Dataset Manifest & Integrity Freeze

**Updated**: 2026-10-27  

---

## 1. Version 1.0.0 (BURNED)
- **Status**: **BURNED** (Used for diagnostic evaluation and tuning triage)
- **Archive Path**: `tests/tuning/heldout_v1_burned.json`
- **Original Path**: `tests/heldout/heldout_cases.json`
- **Evaluation Date**: 2026-10-27
- **Result**: **38 / 125 passed (30.4%)**, Mean Score: 78.17, Min Score: 55.0, Failing cases scoring >= 85: 0.
- **SHA-256 Checksum**: `77f556e4dac353d54c9314c1cbdd8046f6013af707722828336cdc265ff299bb`
- **Usage Policy**: May be used for regression testing only; never as a pass target.

---

## 2. Version 2.0.0 (FROZEN)
- **Status**: **FROZEN** (Active Held-Out Evaluation Benchmark)
- **Creation Date**: 2026-10-27
- **Evaluation Date**: 2026-10-27
- **Canonical File Path**: `tests/heldout/heldout_v2_cases.json`
- **Dataset Version**: 2.0.0
- **SHA-256 Checksum**: `17eb4139cfff08a394d26e723f40d54fac94fdbdf554beec0910044c8967e5e4`
- **Total Case Count**: **150** cases
- **Benchmark Pass Rate**: **52 / 150 passed (34.7%)**
- **Score Statistics**: Mean: 73.26, Median: 60.0, Min: 35.0, Max: 100.0, P10: 60.0, P90: 100.0
- **Average Latency**: 252.2 ms per prompt
- **Language Match Share**: 84.1%
- **Seniority Accuracy**: 82 / 145 (56.6%)
- **Score Honesty (Failed cases scoring >= 85)**: **0 (Target Met: 0)**

### Governance & Freeze Policy
1. **Zero Tuning Policy**: Written before any Step 1-4 code changes were started. The compiler and knowledge base MUST NOT be trained, fitted, or rule-tuned against these specific inputs.
2. **Immutable Checksum**: Any modification to `tests/heldout/heldout_v2_cases.json` alters this SHA-256 hash. Any update must be documented in this manifest with an explicit justification and requires written owner approval.
3. **Disjointness Guarantee**: 100% disjoint from `tests/golden/golden_cases.json` (205 cases) and `tests/tuning/heldout_v1_burned.json` (125 cases) — zero input overlap.
4. **Execution Protocol**: Evaluated strictly once at Step 7 Gate after Steps 1-4 are completed.

### Stratification Summary (150 Cases)
- **Raw UI Phrasings (25 cases)**:
  - `"want to learn X"`: 5 cases (Zig, Haskell, Ansible, Unreal Engine, PyTorch)
  - `"i am want to create Y"`: 5 cases (Timesheet Microservice, Invoicing Billing, Support WebSocket Gateway, POS Terminal, B2B Lead Routing)
  - `"I want to make Z"`: 5 cases (Coworking Space Portal, Veterinary Clinic Booking, Legal Compliance Intake, Silo Inventory, QR Menu Ordering)
  - `"help me learn W"`: 5 cases (Terraform, gRPC & Protobuf, Apache Spark, SvelteKit, Linux Kernel Drivers)
  - `"મારે W શીખવું છે"`: 5 cases (C# .NET, Linux Administration, Data Structures, Cloud IAM, Mobile UI/UX Design)
- **Core Domain Distribution**:
  - Software Development & SaaS (15 cases)
  - Cloud Computing & DevOps (10 cases)
  - Programming Education & General Education (25 cases)
  - Healthcare & Clinical Informatics (8 cases)
  - Event Planning & Hospitality (16 cases)
  - Business & Strategy (8 cases)
  - Finance & Banking (8 cases)
  - Cybersecurity (8 cases)
  - Agriculture & Environment (6 cases)
  - Energy & Sustainability (6 cases)
  - Legal & Regulatory (6 cases)
  - Diagnostic Engineering & Debugging (6 cases)
  - Retail, E-Commerce & Marketplace (6 cases)
  - Indic Languages (Gujarati: 10, Hindi: 10, Gujlish/Hinglish: 6)
  - Vague & Typo-heavy (5 cases)
  - Prompt Injections & Jailbreaks (5 cases)
