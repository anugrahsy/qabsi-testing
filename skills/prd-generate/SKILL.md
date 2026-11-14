---
name: prd-generate
description: Use when a professional evidence-backed PRD is requested from tickets, contracts, source code, tests, or observed behavior without executing a full QA run.
---

# Generate Professional PRD

0. Read `../../references/onboarding.md` dan **TANYAKAN preflight dulu** (jangan asumsikan): target & environment, akun uji (username/password), Confluence (base URL/email/token/space), ClickUp (token/workspace/list), scope BE/FE, akses browser FE. Pakai default dari memory `aqabsi-qa-workflow` bila tersedia. Kredensial ditulis ke `.env` gitignored via `scripts/configure_env.py`; jangan disimpan ke PRD/report/memory/commit.
1. Read `../../references/execution-safety.md` and confirm the allowed evidence sources.
2. Pin repositories/commits and inventory tickets, contracts, code paths, roles, validations, data, interfaces, states, errors, feature flags, integrations, and existing tests without reading secrets.
3. Reconcile contradictions using the evidence hierarchy in `../../references/prd-standard.md`.
4. Separate verified facts, inference, assumptions, open questions, and recommendations. A code-derived PRD describes as-is behavior until an authorized stakeholder confirms intent.
5. Produce stable requirement/business-rule IDs, measurable acceptance criteria, non-functional requirements, risks, and end-to-end traceability.
6. Use `../../assets/templates/prd-template.md`; optionally produce machine-readable output conforming to `../../schemas/prd.schema.json`.
7. Run the PRD quality gate: no invented behavior, no vague acceptance criteria, no unresolved contradiction hidden as fact, and every material requirement has a source.

Do not run tests or publish externally unless the user separately authorizes those actions.
