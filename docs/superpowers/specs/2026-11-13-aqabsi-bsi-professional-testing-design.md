# AQABSI BSI Professional Testing Expansion

**Official name:** AQABSI — AI QA BSI

**Status:** Approved and implemented locally through package forward-test; live BSI connectors and active scans remain separately authorized

**Date:** 2026-11-13

**Target:** AQABSI skill package for BSI-wide GitLab, Confluence, ClickUp, web, API, service, data, and multi-stack engineering workflows

## 1. Intent

Upgrade AQABSI from a broad testing knowledge pack into a professional, evidence-backed QA operating system for teams across BSI. It must produce review-ready PRDs and test cases, detect and select the right testing modules for different frontend, backend, API, data, and integration stacks, execute web testing through a bounded adapter, and support defensive or active security assessment without confusing generated content with verified evidence.

The system is intended for FE, BE, QA, security, data, platform, and product collaborators across BSI UII who work from BSI-managed GitLab repositories and publish approved results to BSI-managed Confluence and ClickUp destinations. No team, application, framework, or architecture is treated as the organizational default.

## 2. Success criteria

1. Every PRD claim is traceable to a source, explicitly classified as verified, inferred, assumed, open, or recommended, and checked for contradiction.
2. Every functional requirement is atomic, testable, prioritized, and has observable acceptance criteria plus negative/error behavior where relevant.
3. Every test case maps to requirement and risk IDs, has deterministic preconditions, safe test data, atomic steps, an observable oracle, cleanup needs, and an honest initial status.
4. Coverage is reported by requirement, risk, role, state, and selected test layer rather than by test-case count alone.
5. Framework detection routes Angular, React, Vue, Laravel, Lumen, Go, Java, .NET, Node, Python, and unknown/custom stacks to appropriate profiles without loading the entire knowledge base.
6. E2E execution is web-only for AQABSI's first delivery, reproducible, telemetry-disabled, and isolated from each target application's dependency tree.
7. Security findings distinguish confirmed, needs-validation, rejected, hardening recommendation, and untested coverage.
8. GitLab, Confluence, and ClickUp integration remains draft-first, idempotent, sanitized, and unable to guess assignees.
9. All new schemas, generators, validators, module registries, and example outputs pass automated package tests.

## 3. Non-goals and anti-goals

- Do not promise a “perfect” PRD when business intent or approval is missing; produce a professional draft with visible gaps.
- Do not turn current implementation defects into approved requirements.
- Do not install test dependencies into any target repository automatically.
- Do not execute Strix, pentests, load tests, destructive tests, production writes, Confluence publication, ClickUp task creation, assignment, commit, or push without the corresponding explicit authorization.
- Do not send BSI source, credentials, test data, or findings to managed external security services by default.
- Do not treat scanner output, an agent assertion, or exit code zero as proof of complete coverage.
- Do not copy entire third-party repositories into AQABSI. Install selected skills separately and keep a pinned-source registry.

## 4. Constraints and project calls

### 4.1 BSI integration assumptions

- GitLab and Confluence use BSI UII-managed domains and may require VPN or internal network access.
- GitLab must be treated as self-managed until its API version and base URL are verified.
- Confluence must be treated as deployment-variant-neutral until Cloud versus Data Center and authentication method are verified.
- ClickUp remains an external SaaS integration.
- Draft generation works without network access; live publication is a separate authorized step.

### 4.2 Third-party source pins

Initial review pins the following upstream commits. Implementation records the exact installed commit and license in a machine-readable provenance file.

| Source | Commit reviewed | License | Decision |
|---|---|---|---|
| `cloudflare/security-audit-skill` | `c1c8a8c1471069fb0e188eeaff69b8e8db6564a8` | MIT | Install `skills/security-audit` for source-first defensive audits and evidence discipline. |
| `obra/superpowers` | `22f0b463e7a5e579904dd6211a520321035526f7` | MIT | Superpowers is already installed. Back up current copies and synchronize only the five skills that differ after reviewing their diffs; leave matching skills untouched. |
| `e2e-inc/e2e` | `79f70ae419adb0f4c2df8d374c1b7d9e3851726d` | Apache-2.0 | Install the official `skills/e2e` package; AQABSI invokes only the web engine. |
| `usestrix/strix` | `928b1ca66ea5a00e7fe83f0fce84c7d557ff8091` | Apache-2.0 | Install the selected local/CI security skills below; managed-cloud execution remains disabled by default. |

Selected Strix skills:

- `application-security-testing`
- `api-security-testing`
- `find-security-vulnerabilities-in-code`
- `owasp-top-10-testing`
- `penetration-testing-with-strix`
- `web-app-penetration-testing`
- `ci-security-scanning-with-strix`
- `fix-security-vulnerabilities-with-strix`

`managed-pentesting-with-strix` is intentionally excluded from the default installation because it can upload BSI source or run scans on third-party infrastructure. It can be evaluated later with information-security and data-governance approval.

### 4.3 E2E compatibility call

The official E2E web engine requires a modern Node runtime, while target applications may use older or non-Node runtimes. AQABSI therefore provides an isolated web-test harness or GitLab job using a compatible Node runtime and targets a local/staging URL. It does not modify the application's dependency tree unless a project owner separately approves that change. Compatibility is resolved from the selected project profile rather than an organization-wide framework assumption.

Set `E2E_TELEMETRY_DISABLED=1` in local and CI examples. Agentic model steps are optional; exact locator tests must work without a model. Credentials use the framework's opaque credential/secret facilities and never enter committed test code or artifacts.

### 4.4 First-delivery boundary and fail-closed defaults

The first delivery is limited to global skill installation/synchronization plus local AQABSI package work through the forward-test phase. It may add reusable templates, schemas, registries, validators, and synthetic examples. It does **not** modify any target repository; run Strix or another active security scan; configure a live pipeline; call an external model with BSI material; upload source; or publish/assign through Confluence or ClickUp.

Until BSI supplies organization-specific policy, use these safe defaults:

- BSI source, prompts containing source, runtime evidence, findings, identities, and internal URLs have `internal_restricted` classification and cannot leave BSI-managed infrastructure. ClickUp drafts may contain sanitized metadata only.
- Managed Strix and remote agentic E2E model calls are disabled. Local exact-locator E2E remains available; a later approved internal model endpoint may enable agentic steps.
- An authorization record requires approver identity, authority reference, target allowlist, environment, techniques, accounts/roles, rate ceiling, data/cleanup rules, start/expiry, and revocation/stop contact. With no approved authority registry, adapters fail closed.
- Existing AQABSI v1 manifests, CLI arguments, and artifact columns remain input-compatible during the AQABSI migration. New fields are optional in v1-compatible input; breaking changes require a new schema version and migration fixture.
- A PRD field that is irrelevant is explicitly `not_applicable` with rationale and reviewer, never silently omitted by the quality engine.
- Security output records CVSS 4.0 vector/score when enough evidence exists, plus a separate configurable BSI business-impact priority. Until BSI supplies its matrix and SLAs, the latter remains `unmapped` and does not fabricate a due date.
- The CRUD pilot uses a sanitized synthetic BSI-style service/endpoint resource, not private source excerpts or business data. A real module can replace it only when an approved public-safe source is selected.
- Accessibility uses WCAG 2.2 AA as a recommendation baseline. Browser versions, latency budgets, availability, error rate, recovery objectives, and other organizational thresholds remain open/configurable and cannot be presented as approved requirements.

### 4.5 Canonical name and organizational configuration

- The canonical installed skill name becomes `aqabsi-testing`, the display name becomes **AQABSI**, and the Claude/plugin namespace becomes `aqabsi:`.
- AQABSI is the official abbreviation of **AI QA BSI**. Use that expansion consistently in public documentation and interface metadata.
- The pre-migration installation is backed up and retired after the canonical package passes validation, preventing two auto-invoked copies from competing. Existing v1 input files remain supported by AQABSI.
- Configuration has three explicit layers: organization policy → team profile → project profile. Lower layers may supply concrete routes, commands, owners, and thresholds but cannot weaken organization safety or data-egress policy.
- Project-specific conventions live only in selected project profiles. They are never embedded as defaults in the core router.

## 5. Architecture

```text
BSI evidence sources
  GitLab MR/commit + Confluence requirement + code/contracts + approved clarifications
        |
        v
Evidence ledger and contradiction register
        |
        +--> Professional PRD engine --> PRD quality gate --> PRD draft / review package
        |
        +--> Risk and module selector --> Test design engine --> Test-case quality gate
                                             |
                                             v
                                  Coverage and execution plan
                                             |
                    +------------------------+-----------------------+
                    |                        |                       |
              Native project tests       E2E web adapter      Security adapter
              unit/api/contract          isolated runner      guidance/local/active
                    |                        |                       |
                    +------------------------+-----------------------+
                                             |
                                             v
                          Evidence manifest and triage classification
                                             |
                          Spreadsheet + QA report + dry-run payloads
                                             |
                           authorized Confluence / ClickUp publication
```

### 5.1 Evidence ledger

Add a structured ledger for every source:

- source ID, type, title, URI/path, revision, owner, and approval state;
- exact location such as file/line, route, ticket section, contract operation, or runtime evidence ID;
- classification: verified, inferred, assumption, open question, recommendation;
- confidence and freshness;
- contradictions and the decision owner needed to resolve them;
- sensitivity and allowed artifact destinations.

Generated PRDs and test cases reference source IDs rather than copying sensitive source content.

### 5.2 Professional PRD engine

Use adaptive composition with deterministic gates. The list below is a professional section library, not one mandatory order or identical template for every product. A profile selects relevant sections from evidence, change type, actors, interfaces, and risk; teams may add domain sections. Mandatory quality outcomes remain evidence-backed/testable requirements, scope boundaries, relevant authorization, observable acceptance/error behavior, risks/decisions, release evidence, and traceability. Irrelevant sections are `not_applicable` with rationale and reviewer.

1. **Document control:** version, status, business owner, technical owner, QA owner, reviewers, source refs, environment, change history.
2. **Problem and outcome:** current pain, users, business value, measurable success, baseline gaps.
3. **Scope:** in, out, non-goals, constraints, dependencies, affected systems.
4. **Actors and authorization:** actor-resource-action matrix and unresolved permission risks.
5. **Journeys and states:** happy, alternative, error, recovery, cancellation, timeout, concurrency, and state transitions.
6. **Requirements:** stable IDs, priority, rationale, source IDs, observable acceptance criteria, error behavior, data and authorization rules.
7. **Contracts:** UI state, API request/response/error, integration, retries, idempotency, audit events, and version compatibility.
8. **NFRs:** security, privacy, accessibility, performance, reliability, observability, compatibility, scalability, localization, and maintainability only where relevant.
9. **Risks and decisions:** likelihood, impact, mitigation, detection, owner, due date, assumptions, questions, and decisions.
10. **Release gates:** acceptance, rollback, cleanup, evidence, residual risk, and sign-off.

Quality verdicts are `review_ready`, `needs_business_input`, `needs_technical_evidence`, or `draft_incomplete`. A numeric completeness score may support triage but never overrides a failed mandatory gate.

### 5.3 Professional test-design engine

Each test case requires:

- stable ID and title describing one observable behavior;
- requirement IDs, risk IDs, source IDs, module IDs, role, and state;
- layer and technique: equivalence, boundary, decision table, state transition, pairwise, scenario, exploratory charter, abuse case, or contract;
- priority rationale and severity only after a reproduced failure;
- environment and authorization prerequisites;
- synthetic or approved test data with sensitivity classification;
- atomic arrange-act-assert steps;
- observable expected result including status, response/UI state, persistence/audit effect, and prohibited side effects when relevant;
- cleanup/rollback and evidence requirements;
- automation suitability and target adapter;
- honest status starting at `not_run`.

The validator rejects ambiguous or untestable phrases, missing traceability, duplicate case intent, unsupported pass/fail, secret-like test data, destructive steps without a safety gate, and defect drafts without confirmed failure evidence.

### 5.4 Coverage model

Generate these matrices:

- requirement × risk × case × result;
- role × action × resource × authorization case;
- state transition × positive/negative/recovery path;
- endpoint × method × validation/auth/error/idempotency/concurrency coverage;
- UI route × form/state/accessibility/compatibility coverage;
- untested risk and blocked-evidence register.

Coverage claims are qualitative and evidence-bound. A missing source or blocked environment remains visible rather than being converted into a synthetic test result.

## 6. Module catalog

Create a machine-readable module registry. Each module defines detection cues, evidence to inspect, common requirements, risks, test dimensions, negative/boundary/security cases, preferred test layers, oracles, data needs, cleanup, and related modules.

### 6.1 Authentication and authorization

- login and failed-login behavior;
- SSO callback and redirect handling;
- MFA/OTP enrollment and verification;
- password reset and password change;
- logout, token invalidation, timeout, refresh, and concurrent sessions;
- RBAC, ABAC, BOLA/IDOR, function-level authorization, tenant isolation;
- brute-force/rate limits, enumeration resistance, audit events, and recovery abuse.

### 6.2 REST/API operations

- `GET` collection: pagination, filtering, search, sort, field exposure, empty/error states;
- `GET` detail: identifier/UUID validation, not found, ownership, soft-deleted state;
- `POST`: required/optional fields, duplicate behavior, transactionality, idempotency, created contract;
- `PUT`: full replacement semantics, omitted fields, versioning, authorization;
- `PATCH`: partial update, field allowlist, mass assignment, concurrency;
- `DELETE`: soft/hard delete, dependency rules, repeat behavior, rollback/audit;
- cross-cutting headers, content types, status codes, error envelope, versioning, rate limits, timeouts/retries, uploads, integrations, and schema compatibility.

### 6.3 Frontend web profiles

The universal web module covers routing, authorization gates, forms, HTTP behavior, rendering states, state synchronization, double submission, stale data, keyboard access, accessible names/errors/focus, responsive behavior, and browser compatibility. Framework profiles add evidence locations and native test commands without changing the universal requirements:

- **Angular:** router/guards, reactive and template forms, services/interceptors, RxJS lifecycle, components, pipes/directives, TestBed, and version-compatible runners;
- **React/Next.js:** routes/server boundaries, hooks, context/state, server/client components, data fetching, hydration, Testing Library, and framework-native E2E hooks;
- **Vue/Nuxt:** router/guards, composables/stores, component emits/props, async state, SSR/hydration, Vue Test Utils, and native runners;
- **unknown/custom web:** DOM/accessibility/API-contract evidence and black-box web testing without inventing a framework.

A project profile supplies verified paths, commands, response conventions, and compatibility constraints only after the actual repository is inspected.

### 6.4 Backend and service profiles

The universal backend flow is entry point/route → middleware/policy → validation → business/service logic → data/integration boundary → serialization/error/audit result. Framework profiles locate those responsibilities without forcing one architecture:

- **PHP Laravel:** routes, controllers, Form Requests, policies/gates, services/actions, Eloquent/query builder, resources, jobs/events, transactions, Pest/PHPUnit, and framework security defaults;
- **PHP Lumen:** bootstrap-enabled features, routes, controllers, custom/BaseRequest validation, middleware, services, repositories, models/query builder, resources/response helpers, transactions, and PHPUnit without assuming full Laravel facilities;
- **Go:** router and handler (`net/http`, Gin, Echo, Fiber, or detected framework), middleware, request binding/validation, service/use-case, repository/SQL/ORM, `context` cancellation, error mapping, goroutine/race behavior, table-driven tests, fuzzing, and `go test`/`-race` evidence;
- **Java/Spring:** controllers, filters/security, Bean Validation, services, repositories/JPA, transaction boundaries, serialization, MockMvc/WebTestClient, integration containers, and Maven/Gradle tests;
- **.NET:** endpoints/controllers, middleware/filters, model validation, authorization policies, services, EF/data access, transactions, problem details, xUnit/NUnit/MSTest, and ASP.NET integration factories;
- **Node.js:** Express/Nest/Fastify routing, middleware/guards/pipes, services, ORM/query layer, async error and transaction handling, Jest/Vitest/native tests, and contract/E2E runners;
- **Python:** FastAPI/Django/Flask routing, dependency/middleware/auth, Pydantic/forms/serializers, service/domain logic, ORM/query layer, transaction behavior, pytest, and framework test clients;
- **unknown/custom service:** derive the actual call graph and test commands from source, then apply universal API, security, data, and observability modules without inventing framework conventions.

Across profiles, inspect validation, authorization, duplicate rules, idempotency, transactions, parameter binding, filtering, pagination, concurrency, soft delete, sensitive-field exposure, rollback, auditability, standardized errors, timeout/cancellation, and cleanup.

### 6.5 Supporting domains

- business workflow, approval, status transition, calculation, scheduling, payment/inventory where present;
- data CRUD, relationships, transactions, migration, seeding, integrity, and reconciliation;
- contract/integration failure, retry, idempotency, queue/event, and third-party sandboxing;
- accessibility, compatibility, performance, resilience, reliability, observability, localization, and usability.

## 7. Security integration

Security has four explicit operating levels:

| Level | Default authority | Engine | Output |
|---|---|---|---|
| Guidance/source triage | Read-only repository scope | Cloudflare security-audit guidance | Candidate, recommendation, or needs-validation |
| Full source audit | Explicit comprehensive audit request and isolated sandbox | Cloudflare six-phase workflow | Independently verified structured findings |
| Local Strix code scan | Explicit scan authorization, clean disposable checkout, Docker/LLM budget | Strix OSS CLI | Validated/local findings with run completeness |
| Staging active pentest | Written target/technique/account/rate/data authorization | Strix web/API skills | Reproduced findings and bounded PoCs |

Production active testing is prohibited by default. Managed Strix cloud is out of scope by default. AQABSI normalizes third-party results into `confirmed`, `needs_validation`, `rejected`, or `hardening_recommendation`; only confirmed findings receive severity and ClickUp defect drafts.

GitLab CI support starts as an opt-in template. It resolves the actual merge-request target branch, uses diff scope, checks completion/budget to avoid fail-open, stores sanitized reports as protected artifacts, and never hardcodes credentials.

## 8. External integration contracts

### 8.1 GitLab BSI UII

- Capture project path, MR IID, source/target SHA, pipeline ID, job ID, environment, and artifact links.
- Prefer GitLab-provided CI variables and project access tokens stored as masked/protected variables.
- Generate CI templates only; adding a pipeline job to a target repository is separately authorized.
- Support internal TLS/CA configuration without disabling certificate verification.

### 8.2 Confluence BSI UII

- Adapter configuration records base URL, deployment type, space key, parent page, authentication mode, and allowed attachment classification.
- Search by AQABSI run ID/content property before create; update idempotently.
- Publish only sanitized content and links recipients can access.
- The default remains a local dry-run JSON payload.

### 8.3 ClickUp

- Create a task only for a confirmed product failure or explicitly classified investigation/work item.
- Deduplicate by root-cause fingerprint and append new evidence to the existing task when appropriate.
- Resolve assignee through approved platform user IDs; unresolved ownership stays unassigned.
- Link the GitLab revision, Confluence page, test case, environment, and sanitized evidence.

## 9. Planned repository changes

1. Add a module-registry reference and a machine-readable registry/schema.
2. Add stack detection plus organization/team/project profiles, including a generic project example and reusable frontend/backend families.
3. Strengthen `references/prd-standard.md`, `references/rules.md`, and quality validators.
4. Extend PRD, test-case, and test-run schemas for source IDs, quality verdicts, technique, oracle, data classification, cleanup, and adapter.
5. Add a deterministic PRD/test-case lint command with human-readable and JSON output.
6. Add isolated E2E web and GitLab CI templates with telemetry disabled.
7. Add a security adapter contract for Cloudflare and Strix findings.
8. Add `third-party-skills.lock.json` with repository, commit, path, license, install date, and local name.
9. Add professional examples for login and one complete CRUD family covering GET collection/detail, POST, PUT/PATCH, and DELETE.
10. Add regression tests for traceability, contradiction handling, secret redaction, duplicate cases, unsupported results, and security authorization gates.

## 10. Delivery phases

1. **Supply-chain and installation:** verify pinned contents and licenses, back up conflicting installed skills, install selected packages, record provenance, and validate each skill.
2. **Professional document gates:** implement evidence ledger, PRD/test-case schema extensions, linting, templates, and quality reports.
3. **Module registry:** convert existing knowledge into universal auth, REST, business, data, integration, and NFR packs, then add lightweight framework profiles for Angular, React, Vue, Laravel, Lumen, Go, Java, .NET, Node, Python, and unknown/custom stacks.
4. **Execution adapters:** add web-only E2E guidance/templates and security result normalization; no live target execution yet.
5. **Forward tests:** regenerate the login pilot and add a source-backed CRUD pilot, ensuring blocked information remains explicit.
6. **BSI integrations:** finalize GitLab/Confluence/ClickUp adapters after deployment/auth details are provided, then test against non-production destinations.

## 11. Verification

- Package unit tests and validators pass from both source and installed skill locations.
- Every third-party skill passes its applicable structure validation and is pinned in provenance.
- No example contains a credential, session, personal data, internal hostname, or private BSI source excerpt.
- Generated XLSX/CSV/JSON/Markdown contain identical case IDs and verdicts.
- PRD and test-case lints fail on deliberately malformed fixtures.
- E2E templates are web-only and telemetry-disabled; they do not mutate any target application's dependencies.
- Security adapters reject active execution without the required authorization contract.
- Login and CRUD examples demonstrate traceability and honest `not_run`/`blocked` behavior.

## 12. Builder discretion

The builder may choose internal Python module names, registry file splitting, and lint implementation details as long as outputs remain deterministic, dependency-light, and compatible with the current package. The builder may consolidate redundant existing knowledge files but must preserve discoverability and avoid loading the full catalog for every request.

## 13. Information needed before live integrations

These items do not block the local skill/package work, but they block live connector validation:

- GitLab BSI UII base URL, API version constraints, and runner capabilities;
- Confluence base URL, Cloud/Data Center type, authentication method, target space, and attachment policy;
- ClickUp workspace/space/list IDs and approved ownership registry;
- approved staging targets, test identities/roles, rate limits, data fixtures, cleanup, and security techniques;
- whether BSI permits any source or result data to leave its managed infrastructure.
