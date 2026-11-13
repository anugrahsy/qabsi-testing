# AQABSI Professional PRD Standard

Use this standard when a PRD is missing, incomplete, contradicted by implementation, or explicitly requested. A PRD derived from code is an **as-is technical reconstruction**, not automatic proof of intended business behavior.

## Evidence hierarchy

Prefer approved business requirements and contracts over implementation. Record disagreements instead of silently choosing one source.

1. Approved ticket, policy, or signed-off PRD.
2. Current API/data/interface contract.
3. Confirmed stakeholder clarification.
4. Executed runtime evidence.
5. Source code and tests.
6. Inference or industry recommendation.

For every material requirement, record `evidence_type`, `source`, and confidence (`high`, `medium`, `low`). Never fabricate missing actors, fields, limits, roles, metrics, status codes, or business rules.

## Adaptive composition, mandatory quality

AQABSI does not force every team or feature into one fixed PRD layout. Select a `prd_profile` and compose sections from the evidence, change type, risk, interfaces, actors, and review needs. A UI-only change, API contract change, data migration, authentication flow, and cross-service initiative should not have identical section weight or order.

What is mandatory is the professional quality contract: document control, evidence-backed and testable requirements, explicit scope boundary, relevant actors/authorization, observable acceptance/error behavior, risks/decisions, release evidence, and end-to-end traceability. A section may be `not_applicable` only with rationale and reviewer. Teams may add domain sections through `adaptive_sections`; the validator evaluates their claims and traceability rather than their position in a template.

## Professional section library

Choose relevant sections; preserve the mandatory quality outcomes above.

1. **Document control** — title, version, status, owner, reviewers, date, source commits, target environment.
2. **Executive summary** — problem, users, value, and measurable outcome.
3. **Context and problem statement** — current behavior, pain, trigger, and system boundary.
4. **Goals and success measures** — measurable outcomes; label unavailable baselines as open questions.
5. **Scope** — in-scope, out-of-scope, non-goals, dependencies, and constraints.
6. **Stakeholders and actors** — role, responsibility, need, and authorization boundary.
7. **User journeys/workflows** — happy path, alternatives, failures, recovery, and state transitions.
8. **Functional requirements** — stable IDs such as `FR-AUTH-001`, priority, rationale, source, and acceptance criteria.
9. **Business rules** — stable IDs, decisions, calculations, duplicate rules, lifecycle, and exceptions.
10. **Roles and permissions** — actor × resource × action matrix; flag unverified authorization as a risk.
11. **Data requirements** — entities, fields, validation, classification, retention, ownership, and relationships; do not invent schema.
12. **Interface contracts** — UI states, API request/response/error behavior, events, integrations, timeouts, retry, and idempotency.
13. **Non-functional requirements** — security, privacy, accessibility, performance, reliability, compatibility, observability, scalability, localization, and maintainability where relevant.
14. **Audit and observability** — events, actor/time/context, correlation IDs, alerts, dashboards, and privacy restrictions.
15. **Risks and failure modes** — impact, likelihood, mitigation, detection, and owner.
16. **Assumptions, open questions, and decisions** — owner and due date when known.
17. **Acceptance and release criteria** — objective gates, rollback/cleanup, and residual risks.
18. **Traceability matrix** — requirement → source → risk → test case → result/evidence → defect.

## Requirement quality gate

Each requirement must be necessary, unambiguous, feasible, testable, atomic enough to verify, and consistent with its source. Use `shall` only for actual requirements. Do not encode an implementation choice unless it is a verified constraint.

Acceptance criteria must describe observable outcomes, including relevant invalid states and authorization rules. Avoid phrases such as “works normally”, “user friendly”, “fast”, or “secure” without a measurable definition.

## Code-derived PRD workflow

1. Pin repository and commit; preserve local changes and avoid reading secrets.
2. Inventory entry points, routes, controllers/components, validations, services, repositories, models, migrations/contracts, feature flags, roles, errors, and existing tests.
3. Reconstruct workflows and states with source citations.
4. Compare frontend, backend, contract, and runtime behavior; list discrepancies.
5. Mark facts as verified/inferred/assumed/open.
6. Draft requirements and acceptance criteria from verified evidence only.
7. Put unresolved business intent into open questions rather than requirements.
8. Run the traceability and contradiction checks before delivery.

Use `assets/templates/prd-template.md` as the output skeleton and `schemas/prd.schema.json` when a machine-readable PRD is required.

## Deterministic review gate

Run `python3 scripts/validate_quality.py prd.json --kind prd` before calling a draft review-ready. The gate checks source linkage, observable acceptance criteria, and requirement traceability. Its verdicts are:

- `review_ready`: deterministic gates pass; human business, technical, and QA review is still required.
- `needs_business_input`: intent, owner, policy, or approval is unresolved.
- `needs_technical_evidence`: a requirement lacks a reliable contract/source.
- `draft_incomplete`: structural or testability gates fail.

A field that is irrelevant is recorded as `not_applicable` with rationale and reviewer. Never omit it silently or use a numeric score to override a failed mandatory gate.
