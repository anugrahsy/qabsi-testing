# Skill Tree — Struktur AQABSI

Codex memakai root `aqabsi-testing`; plugin Claude memakai skill ter-prefix `aqabsi:`. Keduanya berbagi references, schemas, assets, config, dan scripts yang sama.

## Skill (5)

| Skill | Fungsi | Trigger |
|---|---|---|
| `aqabsi:analyze-testing` | Flow penuh dari nol | Tanpa PRD + tanpa test case |
| `aqabsi:testing` | Testing + report + bug | PRD + test case ada |
| `aqabsi:prd-generate` | PRD adaptif | Butuh PRD profesional berbasis evidence |
| `aqabsi:test-case-generate` | Test case saja | Butuh test case traceable |
| `aqabsi:security-testing` | Security assessment | Minta cek keamanan yang sesuai authority |

Root router memilih salah satu mode di atas dan selalu menerapkan `execution-safety.md`.

## References (heavy — di-load on demand)

| File | Isi |
|---|---|
| `rules.md` | Standar QA, teknik test design, struktur test case |
| `flow.md` | Langkah detail tiap skill + routing |
| `skill-tree.md` | Peta ini |
| `setup.md` | Konfigurasi destinasi (ClickUp/Jira/Confluence) |
| `testing-module-input.md` | Index domain Input & Data Validation |
| `testing-module-api.md` | Index domain API & Integration |
| `testing-module-ui.md` | Index domain UI & Interaction |
| `testing-module-security.md` | Index domain Auth & Security |
| `testing-module-business.md` | Index domain Business Logic |
| `testing-module-data.md` | Index domain Data & Persistence |
| `testing-module-non-functional.md` | Index domain Non-functional |
| `testing-module-output.md` | Format report + bug ticket |
| `prd-standard.md` | PRD profesional berbasis bukti + traceability |
| `test-strategy.md` | Pemilihan layer testing berbasis risiko |
| `execution-safety.md` | Otorisasi, environment, destructive/load/security gate |
| `evidence-and-privacy.md` | Evidence, redaction, dan data pribadi |
| `integrations.md` | Draft/publish Confluence dan ClickUp anti-duplikasi |
| `gitlab-ci.md` | Orkestrasi runner dan artifacts melalui GitLab CI |

## Knowledge Modules (detail — `references/knowledge/<domain>/`)

- `input/` (15) · `api/` (24) · `ui/` (15) · `security/` (11) · `business/` (11) · `data/` (10) · `non-functional/` (10).

Katalog lengkap + cakupan + relasi: `../qabsi-knowledge-taxonomy-v1.md`.

## Cara Pakai Knowledge (context-driven)

Feature discovery → knowledge selection → test design → execution & report.
Contoh fitur tabel pegawai → load `api-get-collection`, `api-filtering`, `api-pagination`, `api-sorting`, `ui-table`.
