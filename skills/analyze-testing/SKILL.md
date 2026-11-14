---
name: analyze-testing
description: Use when an authorized application has no trustworthy PRD or test cases and QA must reconstruct current behavior from evidence, create traceable requirements and tests, execute the approved scope, and prepare sanitized draft reports.
---

# Analyze Testing

Use this end-to-end mode only when requirements or test cases are missing or unreliable.

0. Read `../../references/onboarding.md` dan **TANYAKAN preflight dulu** (jangan asumsikan): target & environment, akun uji (username/password), Confluence (base URL/email/token/space), ClickUp (token/workspace/list), scope BE/FE, akses browser FE. Pakai default dari memory `aqabsi-qa-workflow` bila tersedia. Kredensial ditulis ke `.env` gitignored via `scripts/configure_env.py`; jangan disimpan ke PRD/report/memory/commit.
1. Read `../../references/execution-safety.md`; establish repositories/commits, target, environment, accounts/roles, scope, prohibited actions, cleanup, publication authority, and stop conditions.
2. Reuse an existing checkout when supplied. If cloning is needed, clone only the authorized URLs into a safe workspace. Preserve dirty work and never inspect secret files unless explicitly required and authorized.
3. Run `../../references/runtime-exploration.md` when the target UI is browser-accessible, then inventory ticket/contract/code/runtime evidence. Label each finding verified, inferred, assumed, open, or recommended.
4. Build an as-is PRD with `../../references/prd-standard.md` from observed runtime evidence plus code. Do not convert implementation defects or missing behavior into intended requirements.
5. Select relevant layers with `../../references/test-strategy.md` and `../../references/skill-tree.md`.
6. Generate requirement- and risk-linked test cases using `../../references/rules.md`.
7. Execute only authorized checks with real runners/tools. Record commands, versions, timestamps, actual results, and evidence. Never fabricate a pass/fail.
8. Reproduce failures when safe and classify product defect, test defect, flaky, environment failure, ambiguity, or limitation.
9. Create a run manifest and generate sanitized Markdown, CSV, XLSX, Confluence, and ClickUp drafts with `../../scripts/generate_artifacts.py`.
10. Read `../../references/integrations.md`; publish or assign only after explicit authorization and resolved platform identities.

Do not write production data, perform unapproved security/load/destructive tests, or commit/push product code merely because this mode is end-to-end.
