# AQABSI v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a coherent, installable AQABSI (AI QA BSI) package with professional PRD/test-case quality gates, BSI-wide stack profiles, safe web/security adapter contracts, and forward-tested synthetic examples.

**Architecture:** Keep the root skill as the orchestration entry point, route work through machine-readable registries and layered organization/team/project profiles, and enforce document quality with deterministic Python validators. Preserve v1 manifest compatibility while adding optional professional fields and dry-run-only external integration contracts.

**Tech Stack:** Markdown skills, JSON/JSON Schema 2020-12, Python 3 standard library, `unittest`, GitLab CI YAML, Vercel `skills` CLI.

**Spec:** `docs/superpowers/specs/2026-11-13-aqabsi-bsi-professional-testing-design.md`

## Global Constraints

- Canonical skill name is `aqabsi-testing`; display name is `AQABSI — AI QA BSI`; Claude/plugin namespace is `aqabsi:`.
- Existing v1 manifests, CLI arguments, and artifact columns remain input-compatible.
- No target repository changes, live security scans, production writes, publication, assignment, commit, or push in this delivery.
- BSI material is `internal_restricted` by default and cannot be sent to managed external services.
- Web E2E uses an isolated compatible runtime with `E2E_TELEMETRY_DISABLED=1` and does not alter target dependencies.
- Organization policy cannot be weakened by team or project profiles.
- Generated Confluence and ClickUp payloads remain sanitized, idempotent drafts.

## Review Focus

- Legacy v1 manifests with missing new optional fields must still generate the same artifact columns.
- A `pass`/`fail` case without executable evidence must be rejected by the quality validator.
- Secret-like nested test data and string credentials must be rejected or redacted.
- A project profile attempting to weaken organization data-egress or authorization policy must fail validation.
- Public installation instructions must match discoverable skill and plugin metadata exactly.

---

### Task 1: Canonical AQABSI identity and package invariants

**Files:**
- Modify: `SKILL.md`
- Modify: `agents/openai.yaml`
- Modify: `.claude-plugin/plugin.json`
- Modify: `.gitignore`
- Modify: `scripts/validate_package.py`
- Modify: `tests/test_validate_package.py`

**Interfaces:**
- Consumes: current package layout and public installation contract.
- Produces: `validate(root: Path) -> list[str]` enforcing canonical metadata and compatibility paths.

- [x] Add failing fixture-based tests for canonical name/display/prompt/plugin consistency and `.aqabsi-output/`.
- [x] Run `python3 -m unittest tests.test_validate_package -v`; expect the new invariant tests to fail.
- [x] Rename metadata atomically to AQABSI 2.0.0 and implement deterministic invariant checks.
- [x] Run `python3 -m unittest tests.test_validate_package -v`; expect all tests to pass.

### Task 2: Professional PRD and test-case quality engine

**Files:**
- Create: `scripts/validate_quality.py`
- Create: `tests/test_validate_quality.py`
- Create: `schemas/evidence-ledger.schema.json`
- Modify: `schemas/prd.schema.json`
- Modify: `schemas/test-case.schema.json`
- Modify: `schemas/test-run.schema.json`
- Modify: `references/prd-standard.md`
- Modify: `references/rules.md`

**Interfaces:**
- Consumes: v1-compatible PRD/test-run JSON and evidence classifications.
- Produces: `validate_document(data: Any, kind: str) -> list[Finding]` and CLI human/JSON verdicts.

- [x] Add failing tests for missing traceability, ambiguous oracle, duplicate intent, unsupported executed verdict, secrets, destructive steps without authorization, and a review-ready fixture.
- [x] Run `python3 -m unittest tests.test_validate_quality -v`; expect failures because the validator does not exist.
- [x] Implement the standard-library quality validator and optional schema fields without breaking v1 generator inputs.
- [x] Run quality and artifact-generator tests; expect all to pass.

### Task 3: BSI-wide module registry and layered profiles

**Files:**
- Create: `schemas/module-registry.schema.json`
- Create: `schemas/profile.schema.json`
- Create: `config/module-registry.json`
- Create: `config/profiles/organization-bsi.json`
- Create: `config/profiles/team-default.json`
- Create: `config/profiles/project-example.json`
- Create: `references/stack-profiles.md`
- Modify: `scripts/validate_package.py`
- Modify: `tests/test_validate_package.py`

**Interfaces:**
- Consumes: canonical module IDs, stack cues, and organization safety policy.
- Produces: validated registry/profile JSON and fail-closed inheritance invariants.

- [x] Add failing tests for required login/CRUD/API modules, all specified stack families, unique IDs, valid cross-references, and policy non-weakening.
- [x] Run package validator tests; expect the new registry/profile tests to fail.
- [x] Implement the registry, stack profiles, and validator checks.
- [x] Run package validator tests; expect all to pass.

### Task 4: Safe web E2E, security, and integration contracts

**Files:**
- Create: `schemas/security-finding.schema.json`
- Create: `config/third-party-skills.lock.json`
- Create: `assets/templates/e2e-web/README.md`
- Create: `assets/templates/e2e-web/e2e.config.example.json`
- Create: `assets/templates/gitlab-ci.aqabsi-web-security.example.yml`
- Create: `references/security-adapters.md`
- Modify: `references/integrations.md`
- Modify: `references/gitlab-ci.md`

**Interfaces:**
- Consumes: reviewed upstream pins and first-delivery safety boundary.
- Produces: provenance lock, dry-run adapter contracts, isolated E2E/CI templates.

- [x] Add failing package tests for exact pins, excluded managed Strix skill, disabled telemetry, no insecure TLS bypass, and dry-run defaults.
- [x] Run package validator tests; expect failures before files exist.
- [x] Implement templates/contracts and provenance lock with exact reviewed commits/licenses.
- [x] Run package validator tests; expect all to pass.

### Task 5: Forward-tested CRUD pilot and public documentation

**Files:**
- Create: `examples/crud-pilot/prd-crud.json`
- Create: `examples/crud-pilot/test-run.json`
- Create: `examples/crud-pilot/README.md`
- Modify: `README.md`
- Modify: `scripts/generate_artifacts.py`
- Modify: `tests/test_generate_artifacts.py`
- Modify: `schemas/prd.schema.json`
- Modify: `schemas/test-run.schema.json`
- Modify: `references/prd-standard.md`
- Modify: `docs/superpowers/specs/2026-11-13-aqabsi-bsi-professional-testing-design.md`

**Interfaces:**
- Consumes: quality engine, registry, schemas, and deterministic artifact generator.
- Produces: adaptive professional PRDs, a synthetic GET collection/detail, POST, PUT/PATCH, DELETE example, and complete security/coverage reporting for spreadsheet, Confluence drafts, and ClickUp drafts.

- [x] Add failing tests that adaptive/custom PRD sections are accepted when professional quality rules pass; the pilot covers all CRUD methods and starts `not_run`; and authorization/security errors appear in workbook, Confluence, and eligible ClickUp drafts.
- [x] Run generator/quality tests; expect failure before pilot exists.
- [x] Add adaptive PRD guidance, the synthetic pilot, access-control/security normalization, a multi-sheet workbook (all test cases, security findings, coverage), AQABSI copy/output strings, Node `>=22.20.0`, and clear available-vs-planned status.
- [x] Generate pilot artifacts in a temporary directory and run the full unit suite; expect all checks to pass.

### Task 6: Installed-package and public-discovery verification

**Files:**
- Modify: source package only if installed-location tests expose defects.

**Interfaces:**
- Consumes: completed AQABSI source package and exact third-party pins.
- Produces: validated global `aqabsi-testing` installation and evidence that public discovery matches documentation.

- [x] Run `python3 scripts/validate_package.py .`, full unittests, JSON parsing, and whitespace checks.
- [x] Run `DISABLE_TELEMETRY=1 npx --yes skills add . --list`; expect exactly `aqabsi-testing`.
- [x] Back up any legacy global QABSI installation, install AQABSI and approved pinned third-party skills without modifying target repositories, then validate installed paths.
- [x] Stage only intended package files and run one final whole-change review; do not commit or push.
