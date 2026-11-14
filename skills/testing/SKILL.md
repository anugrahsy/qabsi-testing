---
name: testing
description: Use when a PRD and test cases already exist and QA must reconcile them, execute an authorized evidence-backed test scope, triage outcomes, and prepare sanitized report and defect drafts.
---

# Execute Testing

0. Read `../../references/onboarding.md` dan **TANYAKAN preflight dulu** (jangan asumsikan): target & environment, akun uji (username/password), Confluence (base URL/email/token/space), ClickUp (token/workspace/list), scope BE/FE, akses browser FE. Pakai default dari memory `aqabsi-qa-workflow` bila tersedia. Kredensial dipakai in-session saja (inject env var), jangan disimpan ke file/PRD/report/memory.
1. Read `../../references/execution-safety.md`; pin requirements, source commit/MR, target, environment, identities, scope, cleanup, evidence policy, and stop conditions.
2. Reconcile PRD, contract, and test cases. Record ambiguity instead of silently choosing an expected result.
3. Use `../../references/test-strategy.md` and `../../references/skill-tree.md` to identify missing high-risk coverage without expanding beyond authorization.
4. Execute each case with a real runner/tool and record actual results and evidence. Use only `pass`, `fail`, `blocked`, `skipped`, `not_run`, `flaky`, or `environment_error`.
5. Reproduce safe deterministic failures and classify them before calling them product defects.
6. Generate sanitized report/spreadsheet and external-system drafts from the run manifest using `../../scripts/generate_artifacts.py`.
7. Read `../../references/integrations.md`; publish or assign only after explicit authorization, deduplication, and identity resolution.

Never turn unexecuted cases into pass/fail, retry until a flaky result disappears, or describe drafts as published artifacts.
