# AQABSI QA and Test Design Rules

AQABSI applies risk-based testing and established black-box techniques. Testing can demonstrate defects but cannot prove their absence; exhaustive testing is not a realistic goal.

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
| Title | One observable behavior, not a collection of unrelated assertions |
| Requirement/Risk IDs | Trace to intent and reason for testing |
| Source/Module IDs | Trace to evidence and the selected machine-readable module |
| Role/State | Identify actor authorization and starting state where relevant |
| Technique | Equivalence, boundary, decision table, state transition, pairwise, scenario, exploratory charter, abuse case, or contract |
| Module/Feature/Layer | Identify scope and evidence level |
| Scenario | One clear condition/outcome |
| Preconditions | Observable starting state and role |
| Test data | Synthetic/minimized; secrets never embedded |
| Data classification | Synthetic, public, internal, internal restricted, or confidential |
| Steps | Reproducible actions, not implementation narration |
| Expected result | Specific and verifiable from an authoritative source |
| Actual result | Recorded only after execution |
| Status | `pass`, `fail`, `blocked`, `skipped`, `not_run`, `flaky`, `environment_error` |
| Priority | Test execution importance: critical/high/medium/low |
| Severity | Defect impact; null until a defect exists |
| Evidence | Sanitized path/link plus capture context |
| Cleanup | Explicit rollback/cleanup for mutating or destructive execution |
| Adapter | Native/API/web/security executor selected for the case |
| Owner team | Approved ownership key, not guessed person |

Generated cases start as `not_run`. A test is `pass` only when its expected result was observed, and `fail` only when a reproducible mismatch was observed. Use `environment_error` for unavailable dependencies/configuration and `flaky` for inconsistent repeat behavior.

## Coverage expectations

Select relevant positive, negative, boundary, permission, state, concurrency, idempotency, timeout/retry, recovery, audit/observability, accessibility, compatibility, privacy, and security cases. Do not multiply irrelevant cases to inflate coverage.

## Defect standard

Record one observable defect per ticket unless multiple symptoms share one root behavior and owner. Include concise impact, exact reproduction, expected/actual, environment, source commit/MR, sanitized evidence, severity rationale, owner team, test case/run IDs, and stable fingerprint.

Severity reflects impact; priority reflects scheduling. A failed test is not automatically a new defect: check duplication, requirement ambiguity, environment, test correctness, and flakiness first.

## Traceability quality gate

For every critical/high risk, show requirement/source → risk → test case → execution result/evidence → defect or accepted residual risk. Explicitly list untested requirements and why.

Run `python3 scripts/validate_quality.py run.json --kind test-run` before artifact generation. The validator rejects missing traceability, ambiguous expected results, duplicate intent, unsupported executed verdicts, embedded secrets, and destructive steps without authorization and cleanup. Generated cases begin at `not_run`; quality validation does not execute them.
