# QA and Test Design Rules

QABSI applies risk-based testing and established black-box techniques. Testing can demonstrate defects but cannot prove their absence; exhaustive testing is not a realistic goal.

## Test design techniques

- **Equivalence partitioning:** representative valid/invalid classes.
- **Boundary value analysis:** values below, at, and above meaningful limits.
- **Decision tables:** relevant combinations of conditions and outcomes.
- **State transitions:** allowed/forbidden transitions, repeated events, and recovery.
- **Pairwise/combinatorial:** reduce combinations without erasing high-risk interactions.
- **Error guessing/exploratory:** experience-based investigation with a charter and notes.
- **Risk-based selection:** prioritize impact × likelihood × detectability and change exposure.

## Test case contract

| Field | Rule |
|---|---|
| ID | Stable and unique |
| Requirement/Risk IDs | Trace to intent and reason for testing |
| Module/Feature/Layer | Identify scope and evidence level |
| Scenario | One clear condition/outcome |
| Preconditions | Observable starting state and role |
| Test data | Synthetic/minimized; secrets never embedded |
| Steps | Reproducible actions, not implementation narration |
| Expected result | Specific and verifiable from an authoritative source |
| Actual result | Recorded only after execution |
| Status | `pass`, `fail`, `blocked`, `skipped`, `not_run`, `flaky`, `environment_error` |
| Priority | Test execution importance: critical/high/medium/low |
| Severity | Defect impact; null until a defect exists |
| Evidence | Sanitized path/link plus capture context |
| Owner team | Approved ownership key, not guessed person |

Generated cases start as `not_run`. A test is `pass` only when its expected result was observed, and `fail` only when a reproducible mismatch was observed. Use `environment_error` for unavailable dependencies/configuration and `flaky` for inconsistent repeat behavior.

## Coverage expectations

Select relevant positive, negative, boundary, permission, state, concurrency, idempotency, timeout/retry, recovery, audit/observability, accessibility, compatibility, privacy, and security cases. Do not multiply irrelevant cases to inflate coverage.

## Defect standard

Record one observable defect per ticket unless multiple symptoms share one root behavior and owner. Include concise impact, exact reproduction, expected/actual, environment, source commit/MR, sanitized evidence, severity rationale, owner team, test case/run IDs, and stable fingerprint.

Severity reflects impact; priority reflects scheduling. A failed test is not automatically a new defect: check duplication, requirement ambiguity, environment, test correctness, and flakiness first.

## Traceability quality gate

For every critical/high risk, show requirement/source → risk → test case → execution result/evidence → defect or accepted residual risk. Explicitly list untested requirements and why.
