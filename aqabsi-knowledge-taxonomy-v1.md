# AQABSI Knowledge Taxonomy v1

Dokumen induk (master) — katalog taksonomi knowledge base AQABSI.
Tanggal: 2026-11-12
Status: v1 — draft untuk review

## 0. Status & Tujuan

Dokumen ini mendefinisikan **AQABSI Knowledge Base**: kumpulan modul pengetahuan pengujian software yang reusable, berbasis domain, mengacu standar dan praktik industri.

Tujuan:
- Menjadi **index/taksonomi induk** sebelum modul ditulis satu per satu.
- Menentukan cakupan, referensi, dan relasi antar-modul.
- Menjadi acuan `design-aqabsi.md` dan `references/knowledge/`.

Bukan sekadar daftar validasi input. Cakupan = seluruh jenis perilaku sistem yang perlu diuji.

## 1. Prinsip Desain Knowledge Base

1. **Context-driven, bukan checklist buta.** Agent identifikasi fitur dulu → load modul relevan saja (progressive disclosure), bukan baca 100 modul.
2. **Knowledge ≠ test case.** Knowledge = metode + skenario yang perlu dipertimbangkan. Test case = hasil penerapannya pada aplikasi tertentu.
3. **Jangan asumsi semua fitur dukung semua perilaku.** API tanpa sorting → jangan buat expected result seolah sorting wajib.
4. **Pisahkan expected behavior vs recommended behavior.** Kontrak aplikasi menentukan expected result; standar industri membantu menemukan risiko/desain kurang.
5. **Tiap modul wajib punya sumber referensi.** Jangan klaim aturan sebagai kewajiban ISTQB/OWASP tanpa dasar.
6. **Prioritas berbasis risiko.** Tidak semua skenario diuji intensitas sama.
7. **Progressive disclosure.** Dispatcher baca index + modul yang perlu saja.

## 2. Referensi Fondasi

| Referensi | Fokus | Dipakai untuk |
|---|---|---|
| ISTQB CTFL v4.0.1 | Metodologi testing (EP, BVA, decision table, state transition, exploratory, defect management, coverage) | Teknik desain test case |
| OWASP WSTG | Security testing (authn, authz, session, input, business logic, error handling, API, client-side) | Security modules |
| OpenAPI Specification | Kontrak API (methods, parameters, body, schema, response, status, headers) | API contract modules |
| Google AIP-132 / AIP-158 | Desain collection API (List, pagination, filtering, ordering) | API GET collection modules |

Catatan: keempatnya beda fungsi. ISTQB = teknik, OWASP = security, OpenAPI = kontrak, AIP = pedoman desain API. Tidak semuanya wajib di tiap aplikasi.

## 3. Model Domain (7 Domain)

| Domain | Fokus |
|---|---|
| Input & Data Validation | Validasi data dan batas nilai |
| API & Integration | HTTP methods, contract, pagination, filtering |
| UI & Interaction | Komponen, interaksi, state, feedback |
| Authentication & Authorization | Identitas, akses, permission |
| Business Logic | Aturan bisnis, transaksi, workflow |
| Data & Persistence | Database, konsistensi, relasi, integritas |
| Non-functional | Performance, accessibility, compatibility, reliability |

## 4. Katalog Modul per Domain

Setiap modul = satu file `.md` di `references/knowledge/<domain>/`.

### A. Input & Data Validation

| Module | Cakupan |
|---|---|
| `input-email.md` | Format, domain, uniqueness, normalization |
| `input-password.md` | Min/max length, complexity, whitespace |
| `input-username.md` | Allowed characters, uniqueness, reserved words |
| `input-phone.md` | E.164, country code, NIK, KTP, passport |
| `input-number.md` | Integer, decimal, precision, min/max, overflow |
| `input-date.md` | Date format, leap year, date range, timezone |
| `input-text.md` | Length, whitespace, Unicode, special characters |
| `input-url.md` | URL syntax, protocol, domain, malformed URL |
| `input-file.md` | MIME type, extension, size, corrupted file |
| `input-image.md` | Dimensions, resolution, format, metadata |
| `input-array.md` | Empty array, duplicate items, item limits |
| `input-object.md` | Required properties, nested schema, unexpected fields |
| `input-enum.md` | Allowed values, invalid values, case sensitivity |
| `input-currency.md` | Decimal precision, currency, rounding |
| `input-identifier.md` | UUID, numeric ID, format, existence |

Tiap modul jelaskan positive, negative, boundary, equivalence partitioning, kasus khusus — sesuai karakteristik input. Tidak semua teknik dipaksakan.

### B. API & Integration  *(prioritas tinggi)*

| Module | Cakupan |
|---|---|
| `api-contract.md` | Request/response schema, required fields, type |
| `api-get-resource.md` | Get by ID, not found, invalid ID |
| `api-get-collection.md` | List data, empty collection, response structure |
| `api-filtering.md` | Exact, partial, multiple filters, AND/OR |
| `api-pagination.md` | Page, limit, offset, cursor, next page |
| `api-sorting.md` | Ascending, descending, multiple sort fields |
| `api-search.md` | Keyword, partial match, case sensitivity |
| `api-combination.md` | Filter + sort + pagination + search |
| `api-post-create.md` | Required fields, creation, duplicate data |
| `api-put-update.md` | Full replacement, missing fields |
| `api-patch-update.md` | Partial update, null, unchanged fields |
| `api-delete.md` | Delete, soft delete, repeated delete |
| `api-http-status.md` | HTTP status codes dan error responses |
| `api-header.md` | Content-Type, Accept, Authorization |
| `api-authentication.md` | Token, expiration, invalid credentials |
| `api-authorization.md` | Role, permission, resource ownership |
| `api-idempotency.md` | Repeated requests, idempotency keys |
| `api-rate-limit.md` | Rate limiting, throttling, retry |
| `api-timeout-retry.md` | Timeout, retry, transient failures |
| `api-versioning.md` | Version compatibility, deprecated endpoints |
| `api-concurrency.md` | Concurrent requests, race conditions |
| `api-error-handling.md` | Error schema, messages, unexpected exceptions |
| `api-file-upload.md` | Multipart, upload limits, invalid files |
| `api-integration.md` | Third-party service, external dependency |

### C. UI & Interaction

| Module | Cakupan |
|---|---|
| `ui-form.md` | Form submission, validation, reset |
| `ui-button.md` | Click, disabled, repeated click |
| `ui-modal.md` | Open, close, backdrop, escape |
| `ui-dropdown.md` | Select, keyboard navigation |
| `ui-table.md` | Rendering, sorting, filtering, pagination |
| `ui-loading.md` | Spinner, skeleton, loading state |
| `ui-empty-state.md` | Empty data, no search results |
| `ui-error-state.md` | Error feedback, retry |
| `ui-navigation.md` | Routing, redirects, back navigation |
| `ui-responsive.md` | Mobile, tablet, desktop |
| `ui-accessibility.md` | Keyboard, focus, labels, contrast |
| `ui-behavior.md` | Debounce, double-click guard, race conditions |
| `ui-file-upload.md` | Upload progress, preview, removal |
| `ui-notification.md` | Toast, alert, notification state |
| `ui-state.md` | State persistence, refresh, stale state |

### D. Authentication & Authorization

| Module | Cakupan |
|---|---|
| `auth-login.md` | Valid/invalid login, account lockout |
| `auth-logout.md` | Session invalidation |
| `auth-registration.md` | Account creation, duplicate account |
| `auth-password-reset.md` | Reset token, expiration, reuse |
| `auth-password-change.md` | Current password, new password |
| `auth-token.md` | JWT, expiration, tampering |
| `auth-session.md` | Session timeout, concurrent sessions |
| `auth-rbac.md` | Role-based access control |
| `auth-abac.md` | Attribute-based access control |
| `auth-object-access.md` | Ownership, IDOR, cross-user access |
| `auth-mfa.md` | OTP, recovery code, expiration |

### E. Business Logic & Workflow

| Module | Cakupan |
|---|---|
| `business-rules.md` | Validasi aturan bisnis |
| `business-workflow.md` | Workflow dan tahapan proses |
| `business-approval.md` | Approval, rejection, delegation |
| `business-transaction.md` | Transaction consistency |
| `business-calculation.md` | Formula, rounding, totals |
| `business-status-transition.md` | Perubahan status yang diperbolehkan |
| `business-duplicate.md` | Duplicate submission |
| `business-scheduling.md` | Jadwal, deadline, cut-off |
| `business-inventory.md` | Stock, reservation, availability |
| `business-payment.md` | Payment, refund, partial payment |
| `business-audit.md` | Audit trail dan perubahan data |

### F. Data & Persistence

| Module | Cakupan |
|---|---|
| `data-crud.md` | Create, read, update, delete |
| `data-integrity.md` | Constraints, nullability, consistency |
| `data-relationship.md` | Foreign keys, parent-child |
| `data-transaction.md` | Commit, rollback, atomicity |
| `data-soft-delete.md` | Deleted records dan visibility |
| `data-duplicate.md` | Unique constraints |
| `data-migration.md` | Schema/data migration |
| `data-consistency.md` | API vs database consistency |
| `data-concurrency.md` | Concurrent updates |
| `data-seeding.md` | Test fixtures dan test data |

### G. Non-functional

| Module | Cakupan |
|---|---|
| `nft-performance.md` | Response time, throughput |
| `nft-load.md` | Expected concurrent load |
| `nft-stress.md` | Beyond expected capacity |
| `nft-endurance.md` | Sustained load |
| `nft-security.md` | Security assessment |
| `nft-accessibility.md` | WCAG accessibility |
| `nft-compatibility.md` | Browser, OS, device |
| `nft-reliability.md` | Recovery, failure handling |
| `nft-scalability.md` | Resource scaling |
| `nft-usability.md` | Usability evaluation |

## 5. Struktur Standar Tiap Modul

Tiap file pakai struktur konsisten (boleh disesuaikan per kebutuhan domain):

```markdown
# <Judul Module>

## Overview
Tujuan dan risiko yang diuji.

## When to Apply
Kapan modul dipakai.

## Testing Principles
Prinsip pengujian.

## Test Design Techniques
- Equivalence Partitioning
- Boundary Value Analysis
- State Transition (jika relevan)
- Combinatorial Testing

## Test Scenarios
### Positive Testing
### Negative Testing
### Boundary Testing
### Integration Testing

## Test Data
Data yang diperlukan.

## Expected Results
Kriteria hasil benar.

## Common Defects
Kesalahan implementasi yang sering terjadi.

## Security Considerations
Risiko terkait.

## References
Referensi standar.
```

Tidak semua modul harus persis sama (accessibility, auth, DB transaction punya kebutuhan berbeda).

## 6. Cara AQABSI Memilih Module (context-driven)

```
Application / Repository / PRD
        ↓
Feature Discovery  (identifikasi form, API, tabel, workflow, role, business rules)
        ↓
Knowledge Selection  (load modul relevan saja)
        ↓
Test Design  (test conditions, test data, test scenarios)
        ↓
Test Execution & Reporting  (pass / fail / blocked / evidence / defect report)
```

Contoh — fitur Employee Management:

| Fitur ditemukan | Knowledge yang di-load |
|---|---|
| Form tambah pegawai | input validation, api-post-create |
| Tabel pegawai | api-get-collection, api-filtering, api-pagination, api-sorting, ui-table |
| Detail pegawai | api-get-resource, auth-object-access |
| Edit pegawai | api-patch-update / api-put-update, data-integrity |
| Hapus pegawai | api-delete, data-soft-delete |
| Approval pegawai | business-workflow, business-status-transition |
| Hak akses berdasarkan jabatan | auth-rbac, auth-object-access |

## 7. Relasi Antar Module

- `api-get-collection` ⇄ `api-filtering`, `api-pagination`, `api-sorting`, `api-search` → digabung di `api-combination`.
- `ui-table` ⇄ `api-get-collection` (UI mencerminkan collection API).
- `business-status-transition` ⇄ `business-audit`, `data-consistency`.
- `api-post-create` ⇄ `input-*` (validasi request), `data-duplicate`, `api-idempotency`.
- `api-delete` ⇄ `data-soft-delete`, `auth-object-access`.
- `auth-*` ⇄ `api-authentication`, `api-authorization`, `nft-security`.
- `business-transaction` ⇄ `data-transaction`, `data-concurrency`.

## 8. Konvensi Penamaan & Folder

- Prefix file = domain: `input-`, `api-`, `ui-`, `auth-`, `business-`, `data-`, `nft-`.
- kebab-case, verb/kategori-first.
- Flat namespace hanya untuk **nama skill** (`skills/<name>/SKILL.md`), bukan untuk file referensi. File referensi boleh hierarkis per domain.

```
references/
├── rules.md
├── flow.md
├── skill-tree.md
├── testing-module-input.md
├── testing-module-api.md
├── testing-module-ui.md
├── testing-module-security.md
├── testing-module-business.md
├── testing-module-data.md
├── testing-module-non-functional.md
└── knowledge/
    ├── input/
    ├── api/
    ├── ui/
    ├── security/          # dipetakan ke module auth-* & nft-security
    ├── business/
    ├── data/
    └── non-functional/
```

## 9. Roadmap / Prioritas Build

Jangan langsung buat semua file. Urutan:

1. **Taxonomy + index** (dokumen ini) — selesai.
2. **Domain API & Integration** dulu (prioritas tertinggi, paling banyak kombinasi terlewat): mulai `api-get-collection`, `api-pagination`, `api-filtering`, `api-sorting`, `api-search`, `api-combination`.
3. **Input & Data Validation** (dasar form).
4. **UI & Interaction**.
5. **Authentication & Authorization** + `nft-security`.
6. **Business Logic & Workflow**.
7. **Data & Persistence**.
8. **Non-functional** (load, performance, accessibility, dst).

Setiap modul dikembangkan dari: dokumentasi resmi + contoh konkret + test design techniques + expected behavior.

## 10. Catatan Penutup

- Knowledge = metode & skenario, bukan test case.
- Kontrak aplikasi > standar industri untuk menentukan expected result.
- Standar industri dipakai untuk menemukan risiko/kekurangan desain.
- Prioritas berbasis risiko.
- Progressive disclosure wajib.

## 11. Referensi

1. ISTQB CTFL v4.0.1 — metodologi & teknik test design.
2. OWASP Web Security Testing Guide — security testing.
3. OpenAPI Specification — kontrak API.
4. Google AIP-132 — List methods.
5. Google AIP-158 — Pagination.
