# Professional PRD Standard

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

## Required sections

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
