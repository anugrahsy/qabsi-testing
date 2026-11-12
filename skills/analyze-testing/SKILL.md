---
name: analyze-testing
description: Use when the app being tested has no PRD and no test cases — QA must read the source code to understand the flow and test immediately (typically legacy apps).
---

# Analyze Testing

## Overview
Flow penuh dari nol: clone repo → analisa code → PRD → test case → testing → report → bug ticket.

## When to Use
- Tidak ada PRD.
- Tidak ada test case.
- QA butuh paham alur dari kode lalu testing segera.

## Core Pattern
1. Baca ticket: repo BE, repo FE, link Confluence API contract, user testing, deskripsi target web.
2. `git clone` repo BE & FE (URL dari ticket; asumsi sudah login GitLab mandiri).
3. Analisa code → pahami alur, logika, aturan, cara kerja.
4. Buat PRD (kalau belum ada) dari hasil analisa.
5. Buat test case (.md) pakai teknik ISTQB — lihat `../../references/rules.md`.
6. Jalankan testing: Chrome DevTools (prioritas) + Playwright. Enrich pakai knowledge module relevan — lihat `../../references/skill-tree.md`.
7. Rekam video kalau bug (screencast: `navigate` dulu, baru `screencast_start`).
8. Report → Confluence; bug ticket → ClickUp, assign dari contract Consumer/Maintainer.

## Quick Reference
- Knowledge selection **context-driven**: identifikasi fitur dulu, load modul relevan saja.
- Knowledge ≠ test case. Kontrak aplikasi > standar industri.
- Format report bebas dulu (template menyusul).

## Common Mistakes
- Klaim pass/fail tanpa benar-benar jalankan.
- Tebak assignee dari gender.
- Langsung tulis DB prod.
- Screencast sebelum page stabil (hasil 0-byte).

Detail: `../../references/flow.md`, `../../references/rules.md`.
