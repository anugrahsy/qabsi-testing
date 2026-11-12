# Risk-Based Test Strategy

Maximum QA quality comes from selecting the right evidence at the cheapest reliable layer, not from executing every possible test against every change.

## Selection inputs

- Changed code, dependency and configuration impact.
- Business criticality, transaction value, data sensitivity, and user reach.
- Authentication/authorization boundaries and external integrations.
- Historical defects, complexity, concurrency, irreversible actions, and migration risk.
- Environment capability, test data, observability, time budget, and authorization.

## Testing layers

| Layer | Best evidence | Typical use |
|---|---|---|
| Static analysis | Lint/type/security findings | Syntax, types, unsafe patterns, dependency/config issues |
| Unit | Isolated deterministic assertions | Calculations, validation, transformations, state rules |
| Component | Render/behavior assertions | UI states, accessibility semantics, local interaction |
| Integration | Real boundary behavior | Database, filesystem, queue, service adapter |
| Contract | Schema/consumer-provider verification | API/message compatibility and breaking changes |
| API functional | Request/response evidence | Validation, errors, auth, CRUD, filtering, concurrency |
| E2E | User-visible workflow evidence | Critical cross-system journeys; keep narrow |
| Exploratory/manual | Session notes and recordings | Unknown risks, UX, visual and emergent behavior |
| Regression/smoke | Stable suite deltas | Release confidence and critical health |
| Security | Authorized validated findings | Authentication, authorization, injection, session, file handling |
| Accessibility | Automated plus keyboard/screen-reader checks | WCAG-relevant semantics and interaction |
| Compatibility | Browser/device/platform matrix | Supported client and layout differences |
| Data/migration | Before/after reconciliation | Integrity, rollback, transformation, retention |
| Resilience | Controlled fault evidence | Timeout, retry, idempotency, degradation, recovery |
| Performance family | Baseline and workload metrics | Response, throughput, load, stress, endurance, scalability |
| Reliability/observability | Recovery and telemetry evidence | SLO, alert, correlation, audit and failure diagnosis |
| Usability/localization | Task and content evidence | Clarity, error recovery, locale, timezone, formatting |

## Decision rules

1. Prefer unit/component/contract checks for broad combinations; reserve E2E for critical integrated journeys.
2. Map every high/critical risk to at least one preventive or detective test.
3. Test positive, negative, boundary, permission, state transition, concurrency, recovery, and observability behavior when relevant.
4. Separate product defects from test defects, environment failures, contract ambiguity, flaky behavior, and expected limitations.
5. Re-run deterministic failures once only when repetition adds diagnostic value; do not hide flakiness through unlimited retries.
6. Security, load, stress, endurance, chaos, migration, and destructive tests require their specific safety gate in `execution-safety.md`.

## Change-impact mapping

Create a small matrix before execution:

| Change | Direct consumers | Data/permission impact | Selected layers | Regression set | Residual risk |
|---|---|---|---|---|---|

Do not infer “unchanged means safe” when shared middleware, schemas, libraries, permissions, or configuration changed.

## Exit criteria

- Critical paths executed or explicitly blocked with owner/action.
- No unresolved critical/high confirmed defect unless accepted by the authorized owner.
- Flaky and environment failures have separate disposition.
- Coverage and limitations are visible by requirement and risk, not only by test count.
- Evidence is reproducible and sanitized.
