# AQABSI Integration Onboarding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add mandatory first-use integration readiness checks and a secure, idempotent, explicitly authorized Confluence/ClickUp publisher to AQABSI.

**Architecture:** Standard-library Python modules separate configuration/redaction, read-only preflight, provider-specific HTTP adapters, and publication orchestration. Local fake HTTP services prove network behavior without real credentials or external mutations; documentation routes every AQABSI workflow through the preflight before testing.

**Tech Stack:** Python 3 standard library, `unittest`, JSON, `urllib.request`, Markdown documentation.

**Spec:** `docs/superpowers/specs/2026-11-13-aqabsi-integration-onboarding-design.md`

## Global Constraints

- Keep runtime dependency-free and compatible with the package's existing Python standard-library tooling.
- Never read browser cookies or persist, print, serialize, or commit secret values.
- Require HTTPS for non-loopback endpoints and preserve TLS verification.
- Keep all destination and identity settings team-neutral; do not hardcode BSI team/account IDs.
- Default to offline preflight and dry-run publication; live mutation requires `--execute` plus `--authorization-reference`.
- Do not retry writes automatically or claim draft generation is publication.

## Review Focus

- A secret embedded in an HTTP error body must be redacted from CLI output and receipts.
- A provider redirect to another origin must fail closed without forwarding authorization headers.
- A partial Confluence/ClickUp run must preserve successful IDs and avoid blind replay.
- A malformed ownership registry or non-numeric ClickUp assignee must remain unassigned and produce an actionable error.
- A duplicate run/page/fingerprint must update or reuse the existing record instead of creating a second one.

---

### Task 1: Integration configuration and offline preflight

**Files:**
- Create: `scripts/integration_config.py`
- Create: `scripts/check_integrations.py`
- Create: `tests/test_integration_preflight.py`

**Interfaces:**
- Produces: `load_integration_config(environ: Mapping[str, str]) -> IntegrationConfig`, `redact(value: object, secrets: Iterable[str]) -> object`, `build_readiness(config: IntegrationConfig) -> dict`, and a CLI returning JSON or human guidance.

- [ ] Write failing tests for empty environment, deployment-specific required fields, invalid URL/auth mode, optional provider selection, and output that never contains supplied tokens.
- [ ] Run `python3 -m unittest tests.test_integration_preflight -v`; expect failures because the modules do not exist.
- [ ] Implement immutable configuration records, HTTPS/loopback validation, missing-variable diagnostics, and offline status classification.
- [ ] Implement `check_integrations.py` with `--json`, `--provider`, and exit codes that distinguish ready from setup-required and invalid configuration.
- [ ] Run the focused tests; expect all Task 1 tests to pass.

### Task 2: Read-only provider verification

**Files:**
- Create: `scripts/integration_http.py`
- Modify: `scripts/check_integrations.py`
- Modify: `tests/test_integration_preflight.py`

**Interfaces:**
- Consumes: `IntegrationConfig` from Task 1.
- Produces: `request_json(request: HttpRequest, secrets: Iterable[str]) -> HttpResponse`, `verify_confluence(config) -> ProviderVerification`, and `verify_clickup(config) -> ProviderVerification`.

- [ ] Add failing fake-server tests for verified identity/destination, `401`, `403`, timeout/network failure, secret-bearing error bodies, and cross-origin redirects.
- [ ] Run the focused tests; expect failures for missing verification functions.
- [ ] Implement bounded read-only requests for Confluence Cloud/Data Center and ClickUp with provider-specific authorization headers and redacted errors.
- [ ] Wire `--verify` into the preflight CLI without changing the offline default.
- [ ] Run the focused tests; expect all verification cases to pass.

### Task 3: Gated, idempotent artifact publisher

**Files:**
- Create: `scripts/publish_artifacts.py`
- Create: `tests/test_publish_artifacts.py`

**Interfaces:**
- Consumes: `confluence-draft.json`, `clickup-drafts.json`, `IntegrationConfig`, provider selection, `execute: bool`, and `authorization_reference: str | None`.
- Produces: `build_publication_plan(...) -> dict`, `publish_confluence(...) -> MutationResult`, `publish_clickup(...) -> list[MutationResult]`, and sanitized `publication-result.json` output.

- [ ] Write failing tests proving dry-run makes zero HTTP requests and live mode rejects missing authorization, non-draft inputs, unresolved destinations, and malformed assignees.
- [ ] Write failing fake-server tests for Confluence create/update, ClickUp task create/existing-fingerprint skip, and partial failure receipts.
- [ ] Run `python3 -m unittest tests.test_publish_artifacts -v`; expect failures because the publisher does not exist.
- [ ] Implement safe draft loading, deterministic Markdown-to-storage conversion, mutation planning, provider adapters, deduplication, and receipt generation without write retries.
- [ ] Run the focused tests; expect all publisher cases to pass.

### Task 4: Mandatory skill onboarding and package invariants

**Files:**
- Modify: `SKILL.md`
- Modify: `references/setup.md`
- Modify: `references/integrations.md`
- Modify: `references/execution-safety.md`
- Modify: `README.md`
- Create: `assets/templates/integrations.env.example`
- Modify: `scripts/validate_package.py`
- Modify: `tests/test_validate_package.py`
- Modify: `.claude-plugin/plugin.json`

**Interfaces:**
- Consumes: preflight and publisher CLIs from Tasks 1-3.
- Produces: first-use instructions, safe environment template, version `2.1.0`, and validator enforcement for no secret values or skipped preflight routing.

- [ ] Add failing package tests that execute the preflight, reject secret-valued templates, and validate the public package onboarding contract through observable CLI behavior.
- [ ] Run the focused package tests; expect failures until the documentation/template/version invariants are implemented.
- [ ] Update skill routing and documentation so preflight runs before testing and missing publication setup is explained without blocking local QA.
- [ ] Add a names-only environment template with empty values and official token setup links; never include example token-shaped strings.
- [ ] Update package metadata and validator rules to `2.1.0`.
- [ ] Run the focused package tests; expect all Task 4 cases to pass.

### Task 5: Whole-package forward verification

**Files:**
- Modify only files required by failures discovered in this task.

**Interfaces:**
- Consumes: completed integration workflow.
- Produces: verified package evidence and a clean, reviewable working tree; no commit or push unless separately requested.

- [ ] Run `python3 -m unittest discover -s tests -v`; expect zero failures.
- [ ] Run `python3 scripts/validate_package.py .`; expect `AQABSI package valid`.
- [ ] Run the skill quick validator with its required YAML runtime; expect `Skill is valid!`.
- [ ] Run `DISABLE_TELEMETRY=1 npx --yes skills add . --list`; expect exactly `aqabsi-testing`.
- [ ] Run offline preflight with an empty environment and verify it reports setup-required without revealing values.
- [ ] Run dry-run publication on the sanitized login pilot and verify no network mutation occurs.
- [ ] Scan changed files for secret patterns and run `git diff --check`.
