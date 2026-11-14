# Changelog

Semua perubahan penting AQABSI, terbaru di atas.

## 2.3.2 — 2026-11-14
- **Dashboard** — `scripts/generate_dashboard.py` di-redesign jadi nav-menu minimalis-elegan
  (halaman Ringkasan / PRD / Hasil Test) + drawer detail per test case + dark/light mode +
  palette status ter-validasi CVD-safe (dataviz). Interface CLI (`input output [--prd] [--prd-json]`)
  dan sanitasi (`validate_manifest` + `sanitize`) tetap.
- **Docs** — `references/onboarding.md`: dashboard kini otomatis, tanpa koreksi desain manual.
- **Tests** — `test_dashboard_executor_tools.py` di-update ke marker dashboard baru (83/83 pass).

## 2.3.0 — 2026-11-14
- Bundel skill desain `awwwards` + `jury` (MIT) + mode "Design & visual QA".
- `generate_artifacts.py`: draft Confluence & ClickUp dibuat defects-only (hanya status `fail`).
- Baseline: preflight integrasi, mode analyze/testing + PRD/test-case/security, executor
  deterministik, publish draft (dry-run), validate quality/package.
