# QABSI Workflow

## Routing

1. Read the request/ticket and extract objective, evidence sources, repository/commit, target, environment, roles, and requested outputs.
2. Select exactly one primary mode:
   - Missing/untrusted PRD or tests → `analyze-testing`.
   - Trusted PRD and tests exist → `testing`.
   - PRD only → `prd-generate`.
   - Test cases only → `test-case-generate`.
   - Explicitly authorized security assessment → `security-testing`.
3. Read `execution-safety.md` before tool use. Tool availability does not imply permission.
4. Load only relevant references/knowledge modules.

## End-to-end analyze and test

1. Pin tickets/contracts/repos/commits and record unavailable sources.
2. Reuse supplied checkouts or safely clone authorized repositories; preserve dirty work and avoid secrets.
3. Inventory code, contracts, data, roles, states, errors, integrations, and existing tests.
4. Build an as-is evidence-backed PRD using `prd-standard.md`.
5. Select risk-based layers using `test-strategy.md`.
6. Generate traceable test cases using `rules.md`.
7. Execute authorized tests with real tools and capture sanitized evidence.
8. Triage failures into product, test, flaky, environment, ambiguity, or limitation.
9. Generate Markdown/CSV/XLSX and external-system drafts from the run manifest.
10. Publish/assign only after explicit mutation authorization and deduplication.

## PRD only

Stop after the professional PRD quality gate. Do not execute tests or publish merely because their likely next steps are visible.

## Test-case only

Stop with `not_run` cases, coverage/traceability, and open requirement gaps. Do not create fake actual results.

## Security

Confirm authorization and safety scope before any active probe. A clean result is scoped evidence, not a universal security guarantee.

## Cross-flow invariants

- Application contract and approved requirements define expected behavior; industry guidance remains a recommendation unless adopted.
- Every pass/fail requires executed evidence.
- Production writes, destructive/security/high-volume tests, publication, assignment, commit, and push require explicit authorization.
- Reports must disclose source commits, environment, limitations, untested risk, and cleanup state.
- Resolve platform assignees from approved IDs; never infer identity or ownership from gender or names.
