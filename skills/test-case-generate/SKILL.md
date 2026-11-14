---
name: test-case-generate
description: Use when professional risk-based test cases are requested from a PRD, contract, ticket, or source evidence without executing them.
---

# Generate Test Cases

0. Read `../../references/onboarding.md` dan **TANYAKAN preflight dulu** (jangan asumsikan): target & environment, akun uji (username/password), Confluence (base URL/email/token/space), ClickUp (token/workspace/list), scope BE/FE, akses browser FE. Pakai default dari memory `aqabsi-qa-workflow` bila tersedia. Kredensial dipakai in-session saja (inject env var), jangan disimpan ke file/PRD/report/memory.
1. Establish the authoritative requirement sources and label gaps or contradictions; do not invent expected behavior.
2. Read `../../references/rules.md` and select layers with `../../references/test-strategy.md`.
3. Load only relevant indexes/modules through `../../references/skill-tree.md`.
4. Apply equivalence partitioning, boundaries, decision tables, state transitions, pairwise, risk-based, and exploratory heuristics where they add coverage.
5. Give each test a stable ID and map requirement IDs, risk IDs, preconditions, data, steps, verifiable expected result, layer, priority, owner team, and evidence expectation.
6. Include positive, negative, boundary, permission, state, concurrency, recovery, and observability cases only when applicable.
7. Default unexecuted cases to `not_run`; severity remains null until a defect exists.
8. Validate against `../../schemas/test-case.schema.json` or prepare the columns defined in `../../references/testing-module-output.md`.

Do not mark generated cases pass/fail or create external tickets without execution and authorization.
