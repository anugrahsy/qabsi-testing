# Design Doc — QABSI (Skill QA Testing BSI UII)

Tanggal: 2026-11-12
Status: draft — menunggu review

## 1. Intent & Why

QA engineer butuh cara testing aplikasi web UII yang profesional dan otomatis: dari kondisi **tanpa PRD/test case sama sekali** (aplikasi lama) sampai kondisi **PRD + test case sudah ada**. Proses manual (clone repo, baca code, susun skenario, jalankan test, rekam bug, tulis report, bikin ticket) lambat dan tidak konsisten.

QABSI membungkus seluruh alur itu jadi skill Claude Code, meniru pola `superpowers` (skill utama + sub-skill + references + progressive disclosure).

## 2. Goals / Non-goals / Anti-goals

**Goals**
- Satu perintah QA bisa menjalankan full flow: baca ticket → analisa → PRD → test case → testing → report → bug ticket.
- Skill bersifat **kondisional**: pilih flow berdasarkan apa yang sudah ada (PRD/test case ada atau tidak).
- Knowledge base QA (standar ISTQB, validasi input, API contract, security) terpisah dan bisa dipakai lintas project.
- Skill ter-install lewat repo khusus, bisa di-push ke GitHub, dipakai orang lain.

**Non-goals**
- Bukan CI/CD test runner. Tidak menggantikan framework automation (Playwright/JUnit/dsb).
- Tidak menulis product code. Output hanya artefak QA (PRD, test case, report, bug ticket).
- Tidak commit/push ke repo product kecuali user suruh.

**Anti-goals (gagal walau teknis jalan)**
- Mengarang hasil test (claim pass/fail tanpa benar-benar menjalankan).
- Menebak gender/identitas assignee dari nama.
- Menulis langsung ke DB prod.
- Satu dokumen raksasa campur semua aturan (brief eksplisit melarang).

## 3. Constraints

- MCP tersedia & diprioritaskan: **Chrome DevTools, ClickUp, Confluence** (pasti) + Playwright, Atlassian/Jira, Postman (sesuai kondisi).
- Repo: user kasih URL, **sudah login GitLab mandiri**. Skill tinggal `git clone`.
- Login app UII lewat **UII Gateway SSO** (`gateway-dev.uii.ac.id`) → skill `uii-gateway-login`.
- ClickUp workspace: **tidak ada task type "Bug"** → fallback prefix `[BUG]` + label.
- ClickUp storage attachment bisa penuh (`GBUSED_005`) → skill harus deteksi & fallback (simpan lokal + link).
- Screencast: `navigate` dulu baru `screencast_start`, kalau page tertutup saat rekam hasil 0-byte.
- Assignee bug: resolve dari **contract Consumer/Maintainer**, bukan infer gender.

## 4. Skill Tree (struktur repo)

Meniru superpowers: namespace `qabsi`, skill utama + sub-skill + `references/`.
Katalog knowledge domain-based — detail di `qabsi-knowledge-taxonomy-v1.md`.

```
qabsi/                                  # repo root — push GitHub, installable
├── skills/                             # flat namespace (nama skill)
│   ├── qabsi/            SKILL.md       # dispatcher utama
│   ├── analyze-testing/  SKILL.md
│   ├── qa-flow/          SKILL.md
│   ├── create-prd/       SKILL.md
│   └── create-test-case/ SKILL.md
├── references/                         # referensi (boleh hierarkis per domain)
│   ├── rules.md
│   ├── flow.md
│   ├── skill-tree.md
│   ├── setup.md                        # konfigurasi destinasi (ClickUp/Jira/Confluence)
│   ├── testing-module-input.md
│   ├── testing-module-api.md
│   ├── testing-module-ui.md
│   ├── testing-module-security.md
│   ├── testing-module-business.md
│   ├── testing-module-data.md
│   ├── testing-module-non-functional.md
│   ├── testing-module-output.md        # format report + bug ticket (fleksibel)
│   └── knowledge/                      # domain-based knowledge modules
│       ├── input/          # input-email, input-password, input-number, ... (15)
│       ├── api/            # api-get-collection, api-pagination, api-filtering, ... (24)
│       ├── ui/             # ui-form, ui-table, ui-loading, ui-behavior, ... (15)
│       ├── security/       # auth-*, nft-security (dipetakan)
│       ├── business/       # business-rules, business-workflow, ... (11)
│       ├── data/           # data-crud, data-integrity, ... (10)
│       └── non-functional/ # nft-performance, nft-load, ... (10)
├── scripts/                            # tool reusable (kalau ada)
└── README.md                           # install + setup
```

## 5. Flow per Skill

### 5.1 `qabsi` (dispatcher)
1. Baca ticket ClickUp parent (atau input user).
2. Tentukan kondisi:
   - Tidak ada PRD + tidak ada test case → `analyze-testing`.
   - PRD + test case sudah ada → `qa-flow`.
   - User minta PRD saja → `create-prd`.
   - User minta test case saja → `create-test-case`.
3. Cek destinasi (report/bug) — kalau tidak ditentukan → tanya user; kalau ditentukan → eksekusi.

### 5.2 `analyze-testing` (dari nol)
Input ticket berisi: repo BE, repo FE, link Confluence API contract, user testing (1/2/3), deskripsi target web.
1. `git clone` repo BE & FE (URL dari ticket).
2. Analisa code → pahami alur, logika, aturan, cara kerja.
3. Buat PRD (kalau belum ada) dari hasil analisa.
4. Buat test case (.md) pakai teknik ISTQB (EP/BVA/decision table/state transition).
5. Buat child ticket test case (opsional).
6. Jalankan testing: Chrome DevTools (prioritas) + Playwright.
7. Enrich test case pakai knowledge module (input validation, ui-behavior, api, security).
8. Rekam video kalau ada bug (screencast).
9. Susun report → Confluence (format bebas dulu).
10. Buat bug ticket → ClickUp, assign berdasar contract Consumer/Maintainer.

### 5.3 `qa-flow` (PRD + test case sudah ada)
1. Baca ticket berisi: link contract API, target web (`gateway-dev.uii.ac.id`), PRD/test case.
2. Testing detail sesuai test case.
3. Rekam bug (video), report → Confluence, bug ticket → ClickUp + assign.

### 5.4 `create-prd` / `create-test-case`
- Fragmen dari 5.2: cuma output PRD atau test case saja.

## 6. Knowledge Base

Knowledge base = **modul pengetahuan pengujian berbasis domain** (bukan cuma validasi input). Katalog lengkap, cakupan, referensi, dan relasi antar-modul ada di **`qabsi-knowledge-taxonomy-v1.md`**.

7 domain:
1. **Input & Data Validation** — email, password, username, phone, number, date, text, url, file, image, array, object, enum, currency, identifier.
2. **API & Integration** — contract, get-resource, get-collection, filtering, pagination, sorting, search, combination, post/put/patch/delete, http-status, header, auth, idempotency, rate-limit, timeout, versioning, concurrency, error, file-upload, integration.
3. **UI & Interaction** — form, button, modal, dropdown, table, loading, empty/error state, navigation, responsive, accessibility, behavior (double-click guard, debounce), file-upload, notification, state.
4. **Authentication & Authorization** — login, logout, registration, password reset/change, token, session, rbac, abac, object-access (IDOR), mfa.
5. **Business Logic & Workflow** — rules, workflow, approval, transaction, calculation, status-transition, duplicate, scheduling, inventory, payment, audit.
6. **Data & Persistence** — crud, integrity, relationship, transaction, soft-delete, duplicate, migration, consistency, concurrency, seeding.
7. **Non-functional** — performance, load, stress, endurance, security, accessibility, compatibility, reliability, scalability, usability.

**Cara QABSI pakai knowledge** (context-driven): feature discovery → knowledge selection (load modul relevan saja) → test design → execution & report. Bukan baca semua modul.

**Struktur tiap modul**: Overview, When to Apply, Testing Principles, Test Design Techniques, Test Scenarios (positive/negative/boundary/integration), Test Data, Expected Results, Common Defects, Security Considerations, References.

**Referensi fondasi**: ISTQB CTFL v4.0.1 (teknik), OWASP WSTG (security), OpenAPI (kontrak), Google AIP-132/AIP-158 (collection/pagination).

`testing-module-*.md` = ringkasan per domain (index). `knowledge/<domain>/*.md` = detail per modul.

## 7. Keputusan yang Sudah Ditetapkan (dari user)

- Bug ticket → **ClickUp default**; Jira via setup.
- Report → **Confluence**; destinasi tidak ditentukan → tanya user.
- Tooling: **Chrome DevTools + ClickUp + Confluence** prioritas utama, MCP lain sesuai kondisi.
- Repo: user kasih URL, sudah login GitLab.
- Skill disimpan **repo khusus**, installable, push GitHub.
- Format report: **bebas sekarang**, template menyusul, fleksibel per kondisi.

## 8. Keputusan yang Diserahkan ke Builder (mark as my call)

- Nama namespace: `qabsi`.
- Layout repo persis (folder `skills/` + `references/`).
- Penomoran/prefix test case & bug ticket.
- Detail prompt tiap SKILL.md (progressive disclosure: SKILL.md ringkas, detail di references).

## 9. Next Steps

1. Review & approve design doc ini.
2. `superpowers:writing-plans` → rencana implementasi.
3. Bangun repo skill (SKILL.md + references + sub-skill).
4. Uji smoke: jalankan `qa-flow` di ticket `[QA-123] PAK Testing`.
