# QABSI V1 Design

## Intent

QABSI turns application context, source code, requirements, and deployed behavior into a traceable QA workflow. It must help a QA engineer produce a professional evidence-backed PRD, design risk-based test cases, execute the appropriate testing layers, and prepare publication-ready artifacts without inventing requirements or mutating external systems implicitly.

## Goals

- Support five existing modes: analyze-and-test, execute existing tests, PRD only, test-case only, and security assessment.
- Add a root Codex-compatible skill while preserving the Claude plugin layout.
- Cover static, unit, component, integration, contract, API, E2E, exploratory, regression, security, accessibility, compatibility, data, resilience, performance, load, stress, endurance, scalability, reliability, and usability testing when relevant.
- Produce a professional PRD with provenance, confidence labels, numbered requirements, acceptance criteria, and traceability.
- Produce deterministic Markdown, CSV, XLSX, Confluence draft, and ClickUp draft artifacts from a machine-readable run manifest.
- Make external publication dry-run by default, idempotent, attributable, and safe for credentials and personal data.
- Provide GitLab CI guidance without pretending the skill itself replaces test runners.

## Non-goals

- QABSI does not claim exhaustive testing or zero defects.
- QABSI does not invent business intent from implementation details.
- QABSI does not publish, assign, push, deploy, attack, or run destructive/load tests without explicit authorization for the exact target and action.
- QABSI does not replace PHPUnit, Playwright, contract-test, security, accessibility, or performance tools.

## Architecture

The repository becomes one self-contained `qabsi-testing` skill for Codex. Its root `SKILL.md` routes to focused workflow and reference files. Existing `skills/*/SKILL.md` entrypoints remain for Claude plugin compatibility and use the same shared references. Standard-library Python scripts validate the package and convert a test-run JSON manifest into sanitized, deterministic reporting artifacts. JSON schemas and templates define stable contracts.

## Safety and authorization

- Read-only discovery is allowed within the user-provided scope.
- Production writes, destructive tests, security exploitation, high-volume traffic, external publication, task creation, assignment, repository mutation, and credential use require explicit authorization.
- Test evidence must redact secrets and avoid unnecessary personal data.
- A target allowlist, environment classification, test identities, cleanup policy, and stop conditions are required before risky execution.
- Unverified or flaky failures do not create definitive defect tickets.

## Professional PRD standard

Every generated PRD separates verified facts, inferred behavior, assumptions, and open questions. Requirements receive stable IDs and map to source evidence, business rules, acceptance criteria, risks, and test cases. The PRD documents system boundaries, roles, workflows, data, interfaces, non-functional requirements, observability, privacy, and exclusions without fabricating missing details.

## Reporting contract

A test run records source commit/MR, environment, tool evidence, timestamps, test status, severity, ownership reference, and limitations. Supported statuses are `pass`, `fail`, `blocked`, `skipped`, `not_run`, `flaky`, and `environment_error`. Defects use a stable fingerprint so repeat failures update an existing draft rather than create duplicates.

## Builder calls

- Use one root skill instead of duplicating the knowledge base across five Codex installations.
- Use Python standard library only for artifact generation and validation so the skill remains portable.
- Generate external-system drafts but never call Confluence or ClickUp APIs from helper scripts.
- Retain the current Indonesian-first voice and existing knowledge modules, correcting unsafe or misleading universal claims.
