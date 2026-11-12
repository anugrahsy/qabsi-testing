---
name: security-testing
description: Use when a security assessment of a web app or API is requested — OWASP-style checks for authentication, authorization, input validation, business logic, error handling, and client-side security.
---

# Security Testing

## Overview
Testing keamanan aplikasi/API mengacu OWASP. Berdiri sendiri atau bagian flow testing.

## When to Use
- Minta security assessment.
- Perlu cek XSS, SQLi, IDOR, mass assignment, token, brute-force, file upload, CSRF, SSRF.

## Core Pattern
1. Tentukan scope: endpoint/URL + role + kontrak.
2. Load knowledge `../../references/knowledge/security/*` (auth-*) + `../../references/knowledge/non-functional/nft-security.md`.
3. Jalankan checklist OWASP WSTG/ASVS.
4. Report temuan → bug ticket (severity = dampak keamanan).

## Common Mistakes
- Anggap security testing = cuma scan tool.
- Lapor XSS/SQLi tanpa bukti reproduce.

Detail: `../../references/rules.md`, `../../references/testing-module-security.md`, `../../references/flow.md`.
