---
name: aqabsi-testing
description: Plan and execute evidence-backed QA for web apps, APIs, services, and data systems, including professional source-derived PRDs, traceable test cases, authorized testing, security and non-functional scope, spreadsheets, reports, and draft defect tickets. Use for AQABSI or AI QA BSI workflows; do not publish, assign, pentest, load-test, deploy, or mutate production without explicit authorization.
metadata:
  version: "2.0.0"
  organization: "BSI UII"
---

# AQABSI — AI QA BSI

AQABSI (AI QA BSI) is a BSI-wide, risk-based QA orchestrator. It discovers facts, separates them from inference, chooses relevant testing layers for the detected stack, records reproducible evidence, and prepares sanitized artifacts. It never treats generated text as proof that a test ran.

## Choose one mode

| Situation | Mode | Read |
|---|---|---|
| No trustworthy PRD or test cases | Analyze and test | `skills/analyze-testing/SKILL.md` |
| PRD and test cases already exist | Execute tests | `skills/testing/SKILL.md` |
| Only a PRD is requested | Generate PRD | `skills/prd-generate/SKILL.md` |
| Only test cases are requested | Generate test cases | `skills/test-case-generate/SKILL.md` |
| An authorized security assessment is requested | Security assessment | `skills/security-testing/SKILL.md` |

For every mode, read `references/execution-safety.md` first. Then read only the referenced domain modules needed for the feature. Do not load the whole knowledge base.

## Mandatory preflight

Before execution, establish:

1. Objective, feature/module, acceptance source, and explicit out-of-scope items.
2. Repositories/commits, target URL/API, environment class, and allowed test identities.
3. Available tools and runners; never claim a tool or connector exists without checking.
4. Authorization boundary for login, data mutation, security probes, load, cleanup, evidence capture, publication, assignment, commit, and push.
5. Evidence location, redaction requirements, ownership registry, and stop conditions.

Read-only code and document analysis may proceed within the supplied scope. If execution needs a missing credential or would create meaningful external state, stop before that action and request the missing authority.

## Evidence model

Label every statement as one of:

- **Verified:** directly supported by source code, contract, ticket, observed runtime behavior, or executed test evidence.
- **Inferred:** likely behavior derived from implementation; include source and confidence.
- **Assumption:** temporary decision required to continue; make it visible.
- **Open question:** missing information that can change requirements or verdicts.
- **Recommendation:** desired industry behavior, never silently substituted for the application contract.

Only executed, observed checks may receive `pass` or `fail`. Use `blocked`, `skipped`, `not_run`, `flaky`, or `environment_error` when appropriate. A failed check becomes a defect only after reproduction or strong deterministic evidence.

## Core workflow

1. Build a source inventory: ticket, PRD, API contract, repository paths, routes, validation, services, data model, UI, roles, and deployed target.
2. Create or reconcile the PRD using `references/prd-standard.md`; do not turn implementation defects into requirements.
3. Select testing layers with `references/test-strategy.md` and the indexes in `references/testing-module-*.md`.
4. Create traceable test cases following `references/rules.md`; map requirement ID → risk → test case ID → evidence → defect fingerprint.
5. Execute with the narrowest reliable tool: native unit/integration runner, API/contract runner, browser automation, or manual exploration with captured evidence.
6. Triage failures: product defect, test defect, flaky behavior, environment failure, requirement ambiguity, or accepted limitation.
7. Create a test-run manifest following `schemas/test-run.schema.json` and generate artifacts with:

   ```bash
   python3 scripts/generate_artifacts.py run.json artifacts/
   ```

8. Review sanitized drafts. Publish to Confluence or create/update ClickUp tasks only after explicit authorization for those mutations and resolved platform IDs.

## Testing breadth

Consider static analysis, unit, component, integration, contract, API, E2E, exploratory, regression, smoke, security, accessibility, localization, compatibility, data/migration, resilience, observability, performance, load, stress, endurance, scalability, reliability, and usability testing. “Consider” is not “run”: select by risk, change impact, environment, authorization, time, and available evidence.

Never run destructive, exploitative, high-volume, chaos, endurance, or production tests merely to maximize the number of test types.

## External systems

- Generated Confluence and ClickUp payloads are drafts and `dry_run: true`.
- Use stable run IDs and defect fingerprints to update rather than duplicate.
- Resolve assignees through an approved ownership registry containing platform user IDs. A team name, code author, Consumer/Maintainer label, or inferred identity is not an assignee ID.
- Never place secrets, full session material, private source, or unnecessary personal data in reports or attachments.

Read `references/integrations.md` immediately before any publication workflow.

## Completion gate

Before declaring completion:

- Every verdict has evidence or an explicit non-executed status.
- Requirements and test cases are traceable.
- Secrets and unnecessary personal data are absent from artifacts.
- Flaky/environment failures are not misreported as confirmed product defects.
- Scope, limitations, untested risks, and cleanup state are visible.
- External mutations performed are listed with links/IDs; drafts are not described as published.
- Package changes pass `python3 -m unittest discover -s tests -v` and `python3 scripts/validate_package.py .`.
