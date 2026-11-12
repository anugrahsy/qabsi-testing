# QABSI — Evidence-Backed Vibe Testing

QABSI membantu QA engineer mengubah ticket, kontrak, source code, dan aplikasi ter-deploy menjadi PRD profesional, test case berbasis risiko, eksekusi manual/otomatis yang dapat dibuktikan, spreadsheet, laporan, serta draft defect yang aman dan anti-duplikasi.

## Kapabilitas

- Rekonstruksi PRD dari bukti dengan pemisahan fakta, inferensi, asumsi, pertanyaan terbuka, dan rekomendasi.
- Traceability requirement → risk → test case → evidence → defect.
- Pemilihan layer static, unit, component, integration, contract, API, E2E, exploratory, regression, security, accessibility, compatibility, data/migration, resilience, observability, performance, load, stress, endurance, scalability, reliability, usability, dan localization sesuai risiko.
- Generator deterministik untuk Markdown, CSV, XLSX, draft Confluence, dan draft ClickUp.
- Safety gate untuk production, security, load, destructive test, credential, PII, publication, dan assignment.
- GitLab CI blueprint yang menghubungkan runner project dengan report QABSI.

## Skill

Root `SKILL.md` adalah entrypoint Codex. Plugin Claude tetap menyediakan:

| Skill | Fungsi |
|---|---|
| `qabsi:analyze-testing` | Dari evidence discovery sampai draft report |
| `qabsi:testing` | Eksekusi PRD dan test case yang tersedia |
| `qabsi:prd-generate` | PRD profesional berbasis bukti |
| `qabsi:test-case-generate` | Test case profesional tanpa eksekusi |
| `qabsi:security-testing` | Security assessment yang terotorisasi |

## Install

### Codex

Install seluruh root repository sebagai satu skill `qabsi-testing` agar semua references, schemas, assets, dan scripts ikut tersedia. Jangan menginstal `skills/*` satu per satu.

### Claude Code plugin

Daftarkan repository sebagai plugin sesuai mekanisme plugin Claude Code yang berlaku, kemudian gunakan namespace `qabsi:`. Folder `.claude-plugin/`, `skills/`, dan `references/` dipertahankan untuk kompatibilitas.

## Artifact generator

```bash
python3 scripts/generate_artifacts.py tests/fixtures/sample-run.json .qabsi-output
```

Output lokal selalu draft dan tersanitasi. Script tidak memanggil Confluence atau ClickUp API.

## Forward-tested example

Folder [`examples/login-pilot/`](examples/login-pilot/) berisi pilot nyata berbasis pembacaan source FE/BE tim: PRD *as-is*, manifest 34 test case login/SSO/2FA/recovery/accessibility, spreadsheet XLSX, laporan QA, serta payload draft Confluence dan ClickUp. Seluruh status tetap `not_run` karena target runtime, akun uji, dan kontrak auth belum tersedia; akibatnya generator tidak membuat defect palsu maupun task ClickUp.

## Verification

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_package.py .
```

## Prinsip keselamatan

- Tidak ada pass/fail tanpa eksekusi dan evidence.
- Tidak ada pentest/load/destructive/production mutation tanpa otorisasi spesifik.
- Tidak ada publish, task creation, assignment, commit, atau push secara implisit.
- Tidak ada credential, token, session, atau PII yang tidak diperlukan di artifact.
- Tidak ada assignee hasil tebakan; gunakan ownership registry dan platform ID.
