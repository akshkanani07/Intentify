# Baseline Audit Telemetry & Defect Identification

**Date**: 2026-10-27

## Pytest Summary Line
`python -m pytest tests/ -q --tb=line`
- **Result**: `50 failed, 373 passed, 2 warnings in 10.40s`

## Golden Benchmark Summary
`python -m evaluation.evaluate` (205 test cases)
- **Passed Cases**: 164 / 205 (80.0%)
- **Failed Cases**: 41 / 205 (20.0%)
- **Mean Score**: 99.56 / 100.0
- **Min Score**: 90.0 / 100.0
- **Max Score**: 100.0 / 100.0
- **Cases that fail while still scoring >= 85.0**: **41 / 41 (100% of failures)**

## Score-Honesty Defect Analysis
Cases fail external rubric criteria (forbidden phrases, forbidden cross-domain headings, missing domain keywords, wrong seniority, or wrong domain) while the internal scoring engine returned 90.0 or 100.0 because the quality engine did not incorporate penalties for:
1. Forbidden phrases (-10 each)
2. Forbidden cross-domain headings (-10 each)
3. Expected objective keywords missing (-10)
4. Seniority / proficiency mismatch (-15)
5. Domain mismatch (-15)

## Golden Set Duplication & Diff
- `tests/golden/golden_cases.json`: 205 cases (canonical)
- `tests/golden/cases.json`: 205 cases (identical copy of canonical)
- `backend/tests/golden/cases.json`: 205 cases (identical copy of canonical)
- `backend/tests/golden/golden_cases.json`: 62 cases (legacy subset, missing 143 cases from canonical set)
- Case ID diff between canonical (205) and legacy (62): 143 cases absent in `backend/tests/golden/golden_cases.json`.
