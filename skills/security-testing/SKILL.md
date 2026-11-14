---
name: security-testing
description: Use for an explicitly authorized security assessment of a web app or API covering authentication, authorization, input, business logic, session, file handling, and client risks; never use it for an unverified target or unapproved exploit scope.
---

# Security Testing

0. Read `../../references/onboarding.md` dan **TANYAKAN preflight dulu** (jangan asumsikan): target & environment, akun uji (username/password), Confluence (base URL/email/token/space), ClickUp (token/workspace/list), scope BE/FE, akses browser FE. Pakai default dari memory `aqabsi-qa-workflow` bila tersedia. Kredensial ditulis ke `.env` gitignored via `scripts/configure_env.py`; jangan disimpan ke PRD/report/memory/commit.
1. Read `../../references/execution-safety.md` and confirm ownership/authorization, exact allowlist, environment, roles, credentials source, permitted techniques, prohibited actions, rate/budget, test window, cleanup, evidence handling, contact, and stop conditions.
2. Read `../../references/evidence-and-privacy.md`. Never persist credentials, session material, private keys, or unnecessary personal data.
3. Build a threat- and contract-based scope. Load only relevant files from `../../references/knowledge/security/`, `../../references/knowledge/api/`, `../../references/knowledge/input/`, and `../../references/knowledge/non-functional/nft-security.md`.
4. Test with the least harmful method that can prove or disprove the risk. Production, destructive, brute-force, denial-of-service, SSRF-to-internal, file-write, high-volume, or data-access probes require explicit technique-level authorization.
5. Distinguish scanner suspicion from a validated finding. Record sanitized reproduction, affected role/resource, impact, likelihood, evidence, and remediation guidance.
6. Stop on scope drift, unexpected impact, sensitive-data exposure, rate breach, or failed cleanup.
7. Create defect drafts following `../../references/testing-module-output.md`; publish only after authorization and deduplicate by fingerprint.

A clean result means no validated findings in the tested scope, not proof of complete security.
