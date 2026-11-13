# AQABSI — AI QA BSI

**AQABSI adalah singkatan resmi dari AI QA BSI.** AQABSI merupakan skill QA berbasis bukti untuk membantu tim di lingkungan BSI mengubah ticket, PRD, kontrak, source code, merge request, dan perilaku aplikasi menjadi dokumen kebutuhan profesional, test case berbasis risiko, eksekusi testing yang dapat dibuktikan, laporan, spreadsheet, serta draft defect yang aman dan anti-duplikasi.

AQABSI dirancang untuk seluruh lingkungan BSI UII. Core-nya stack-agnostic dan dapat digunakan oleh tim frontend, backend, QA, security, data, platform, serta product tanpa mengutamakan unit, aplikasi, framework, atau pola arsitektur tertentu.

> Status package lokal: identitas kanonis sudah `aqabsi-testing` dengan namespace plugin `aqabsi:`. Input dan kolom artifact AQABSI v1 tetap kompatibel. Live connector BSI tetap membutuhkan URL, deployment type, credential, ID destination, ownership registry, dan otorisasi yang benar.

## Quick install

Prasyarat untuk installer publik: Node.js `>=22.20.0`. Core AQABSI sendiri menggunakan Python 3 standard library dan dapat dipasang manual tanpa Node.

```bash
DISABLE_TELEMETRY=1 npx skills add anugrahsy/qabsi-testing
```

Pilih root skill `aqabsi-testing`. Untuk instalasi global tambahkan `-g`; untuk melihat skill yang ditemukan tanpa memasang gunakan `--list`.

## Tersedia sekarang dan batasannya

| Tersedia di package | Memerlukan konfigurasi/otorisasi lanjutan |
|---|---|
| PRD adaptif berbasis evidence dengan deterministic quality gate | Klarifikasi dan approval business owner untuk mengubah draft menjadi requirement resmi |
| Registry modul login, authorization, GET/POST/PUT/PATCH/DELETE, data, web, security, dan non-functional | Detection terhadap repository nyata dan pemilihan command/path yang sudah diverifikasi |
| Profil Angular, React/Next, Vue/Nuxt, Laravel, Lumen, Go, Java/Spring, .NET, Node, Python, dan custom | Runner/dependency masing-masing project atau isolated harness |
| Test-run validator, redaction, CSV, workbook tiga sheet, Markdown, Confluence draft, dan ClickUp draft | Live publication/assignment ke Confluence BSI dan ClickUp |
| Security finding schema, access-control matrix, Cloudflare/Strix contracts, dan CI dry-run template | Scan aktif, pentest, Docker/model budget, target/account/rate/window yang diotorisasi |
| Login design pilot dan synthetic CRUD forward-test pilot | Runtime target dan akun uji agar kasus dapat berubah dari `not_run` |

## Tujuan

AQABSI dibangun untuk menghasilkan QA yang:

- profesional dan layak direview oleh product, developer, QA, dan security;
- dapat ditelusuri dari sumber kebutuhan sampai evidence dan defect;
- jujur mengenai hal yang sudah diverifikasi, masih berupa inferensi, belum diketahui, atau belum dijalankan;
- fleksibel untuk berbagai framework dan pola arsitektur;
- aman untuk lingkungan enterprise BSI;
- dapat diintegrasikan dengan GitLab, Confluence, dan ClickUp tanpa melakukan mutasi eksternal secara diam-diam.

## Prinsip utama

1. **Evidence before verdict.** Tidak ada status `pass` atau `fail` tanpa eksekusi dan evidence.
2. **Requirement before test count.** Kualitas dinilai dari risiko dan requirement yang terliput, bukan banyaknya test case.
3. **Stack-aware, framework-neutral.** AQABSI memahami pola framework tanpa memaksakan satu arsitektur untuk semua tim.
4. **Draft before publish.** Spreadsheet, Confluence, dan ClickUp selalu dibuat sebagai draft terlebih dahulu.
5. **Security fails closed.** Pentest, load test, destructive test, production write, dan data egress membutuhkan otorisasi khusus.
6. **No invented business rules.** Kekurangan informasi menjadi pertanyaan terbuka, bukan requirement buatan AI.

## Alur kerja

```text
GitLab / Confluence / ticket / source code / API contract / runtime evidence
                              |
                              v
             Evidence ledger + contradiction register
                              |
              +---------------+---------------+
              |                               |
              v                               v
      Professional PRD                Risk and module selection
              |                               |
              +---------------+---------------+
                              v
                    Professional test cases
                              |
                              v
        Unit / component / API / contract / E2E / security
                              |
                              v
              Evidence manifest + failure triage
                              |
                              v
      XLSX / CSV / QA report / Confluence draft / ClickUp draft
                              |
                              v
             Authorized publication and assignment
```

## PRD profesional

PRD AQABSI bukan sekadar ringkasan source code. Setiap PRD membedakan:

- **Verified:** didukung langsung oleh ticket, kontrak, source, atau runtime evidence.
- **Inferred:** disimpulkan dari implementasi dengan sumber dan confidence yang jelas.
- **Assumption:** keputusan sementara agar analisis dapat dilanjutkan.
- **Open question:** informasi yang masih dapat mengubah requirement atau test plan.
- **Recommendation:** perilaku industri yang disarankan, bukan kontrak aplikasi saat ini.

PRD AQABSI **tidak memakai format baku yang sama untuk semua fitur**. UI change, API contract, migrasi data, login/security, dan cross-service initiative boleh memiliki susunan serta bobot bagian yang berbeda. Yang wajib adalah aturan kualitas profesionalnya: document control, evidence, requirement yang atomic dan testable, scope boundary, actor/authorization yang relevan, acceptance/error behavior yang observable, risiko/keputusan, release evidence, dan traceability.

Section library mencakup problem statement, tujuan terukur, scope, actor, journey, state transition, functional requirement, business rule, role/permission, data, interface contract, NFR, observability, risk, decision, dan release gate. Generator memilih bagian yang relevan; bagian yang tidak relevan dapat ditandai `not_applicable` dengan alasan dan reviewer. Tim juga dapat menambahkan `adaptive_sections` khusus domain tanpa merusak quality gate.

Quality verdict PRD dirancang menjadi:

- `review_ready`
- `needs_business_input`
- `needs_technical_evidence`
- `draft_incomplete`

Field yang tidak relevan harus ditandai `not_applicable` beserta alasan, bukan dihilangkan tanpa penjelasan.

## Test case profesional

Setiap test case AQABSI dirancang memiliki:

- test case ID, requirement ID, risk ID, source ID, dan module ID;
- satu perilaku yang dapat diamati;
- role, state, layer testing, dan teknik test design;
- priority beserta alasan;
- environment dan authorization prerequisite;
- test data sintetis atau data uji yang telah disetujui;
- langkah arrange–act–assert yang atomik;
- expected result yang mencakup UI/response, persistence, audit, dan prohibited side effect jika relevan;
- cleanup atau rollback;
- evidence yang dibutuhkan;
- automation suitability dan target adapter;
- status awal `not_run`.

Teknik yang dapat dipilih meliputi equivalence partitioning, boundary value, decision table, state transition, pairwise, scenario, exploratory charter, abuse case, dan contract testing.

## Modul testing

### Authentication dan authorization

- login dan failed login;
- SSO dan callback/redirect;
- MFA/OTP;
- password reset dan password change;
- logout, token, timeout, refresh, dan concurrent session;
- RBAC, ABAC, BOLA/IDOR, function-level authorization, dan tenant isolation;
- rate limit, enumeration resistance, audit event, dan recovery abuse.

### REST dan API

- `GET` collection dan detail;
- `POST` create;
- `PUT` full update;
- `PATCH` partial update;
- `DELETE` soft/hard delete;
- pagination, filtering, search, sorting, headers, content type, status code, error envelope, idempotency, concurrency, timeout/retry, rate limit, file upload, dan versioning;
- REST, GraphQL, gRPC, event/message, dan third-party integration sesuai evidence project.

### Business dan data

- workflow, approval, duplicate rule, status transition, calculation, scheduling, inventory, dan payment jika ada;
- CRUD, relationship, transaction, migration, seeding, soft delete, integrity, reconciliation, retention, dan auditability.

### Non-functional

- security dan privacy;
- accessibility;
- browser/platform compatibility;
- performance, load, stress, endurance, dan scalability;
- resilience, reliability, recovery, dan observability;
- usability, localization, timezone, dan formatting.

## Stack dan framework

AQABSI memakai universal testing core lalu memuat profil framework hanya ketika terdeteksi atau dipilih.

### Frontend

| Profil | Area yang dikenali |
|---|---|
| Angular | Router/guard, reactive/template form, service/interceptor, RxJS, component, TestBed, dan runner yang kompatibel dengan versi project |
| React/Next.js | Routing, hooks, context/state, server/client boundary, data fetching, hydration, Testing Library, dan E2E |
| Vue/Nuxt | Router/guard, composable/store, props/emits, SSR/hydration, Vue Test Utils, dan E2E |
| Custom web | DOM, accessibility, network/API contract, state, dan black-box web testing tanpa menebak framework |

### Backend

| Profil | Area yang dikenali |
|---|---|
| Laravel | Route, controller, Form Request, policy/gate, service/action, Eloquent/query builder, resource, job/event, transaction, Pest/PHPUnit |
| Lumen | Route, bootstrap capability, controller, request validation, middleware, service, repository, model/query builder, resource/response helper, transaction, PHPUnit |
| Go | `net/http`, Gin, Echo, Fiber, handler, middleware, validation, service/use-case, repository/SQL/ORM, context cancellation, goroutine/race, table test, fuzzing |
| Java/Spring | Controller, security/filter, Bean Validation, service, JPA/repository, transaction, serialization, MockMvc/WebTestClient, Maven/Gradle |
| .NET | Endpoint/controller, middleware/filter, validation, authorization policy, service, EF/data access, transaction, problem details, xUnit/NUnit/MSTest |
| Node.js | Express, Nest, Fastify, middleware/guard/pipe, service, ORM/query, async error, transaction, Jest/Vitest |
| Python | FastAPI, Django, Flask, dependency/middleware/auth, serializer/schema, service/domain, ORM, transaction, pytest |
| Custom service | Call graph, command, contract, security boundary, dan test layer diturunkan dari evidence source |

Konfigurasi menggunakan tiga lapisan:

```text
BSI organization policy
  -> team profile
    -> project profile
```

Project dapat menambahkan command, lokasi file, convention, owner, dan threshold, tetapi tidak dapat melemahkan kebijakan keamanan dan data-egress organisasi.

## Security

AQABSI memisahkan security guidance dari pengujian aktif:

| Level | Contoh | Otorisasi |
|---|---|---|
| Source guidance | Review trust boundary dan candidate finding | Read-only repository scope |
| Full source audit | Audit defensif dengan coverage ledger dan independent verification | Permintaan audit komprehensif dan sandbox terisolasi |
| Local security scan | Strix terhadap disposable clean checkout | Otorisasi scan, Docker, model/budget, dan batas data |
| Staging pentest | Pengujian web/API dengan payload aktif | Target, teknik, akun, rate, data, cleanup, dan window yang disetujui |

Komponen security yang dikunci dan dikontrak oleh package:

- Cloudflare `security-audit` untuk source-first defensive audit;
- Strix untuk code, API, OWASP, web, CI, dan fix verification;
- temuan dinormalisasi menjadi `confirmed`, `needs_validation`, `rejected`, atau `hardening_recommendation`;
- hanya temuan `confirmed` yang boleh memiliki severity dan menghasilkan draft defect.

Untuk test hak akses, AQABSI membangun matrix `role × action × resource × expected × actual × status × test case × error location`. Hasilnya ditampilkan pada QA report/Confluence draft, sheet **Security Findings**, dan coverage summary. ClickUp draft dibuat hanya saat finding berstatus `confirmed`, evidence tersedia, dan `clickup_eligible=true`; task menyertakan lokasi boundary/error yang teridentifikasi, bukan menebak sumber masalah.

Managed security cloud dan upload source BSI dinonaktifkan secara default.

## Web E2E

AQABSI menggunakan integrasi E2E web pada runner terpisah agar tidak memaksa dependency Node modern masuk ke aplikasi lama atau aplikasi non-Node.

- Web-only pada delivery pertama.
- Chromium/Firefox/WebKit dipilih sesuai support matrix project.
- Exact locator assertion dapat berjalan tanpa model.
- Agentic action bersifat opsional dan tidak boleh mengirim material BSI ke model eksternal tanpa persetujuan.
- Telemetry dinonaktifkan dengan `E2E_TELEMETRY_DISABLED=1`.
- Credentials dan secret menggunakan fasilitas opaque secret, bukan literal di test code.

## GitLab, Confluence, dan ClickUp

### GitLab BSI

- Mengambil project, merge request, source/target SHA, pipeline, job, environment, dan artifact link.
- Mendukung self-managed GitLab dan internal CA tanpa mematikan TLS verification.
- Pipeline template bersifat opt-in dan tidak otomatis ditambahkan ke repository project.

### Confluence BSI

- Output default adalah payload lokal `dry_run`.
- Publication mencari AQABSI run ID terlebih dahulu agar create/update idempotent.
- Hanya content dan attachment yang telah disanitasi yang dapat dipublikasikan.

### ClickUp

- Hanya confirmed product failure yang menghasilkan draft bug.
- Fingerprint digunakan untuk mencegah task duplikat.
- Assignee harus berasal dari ownership registry berisi platform user ID.
- `blocked`, `not_run`, `flaky`, dan `environment_error` tidak disamarkan sebagai product defect.

## Skill dan mode

Nama kanonis root skill setelah migrasi adalah `aqabsi-testing`. Namespace plugin menjadi:

| Skill | Fungsi |
|---|---|
| `aqabsi:analyze-testing` | Evidence discovery, PRD, test design, execution plan, dan draft report |
| `aqabsi:testing` | Eksekusi PRD dan test case yang sudah tersedia |
| `aqabsi:prd-generate` | PRD profesional berbasis bukti |
| `aqabsi:test-case-generate` | Test case profesional tanpa mengarang hasil eksekusi |
| `aqabsi:security-testing` | Security guidance atau assessment yang terotorisasi |

## Artifact generator

```bash
python3 scripts/generate_artifacts.py tests/fixtures/sample-run.json .aqabsi-output
```

Generator menghasilkan:

- `sanitized-run.json`
- `qa-report.md`
- `test-cases.csv`
- `test-cases.xlsx`
- `confluence-draft.json`
- `clickup-drafts.json`

Workbook `test-cases.xlsx` berisi:

- **Test Cases** — seluruh functional, API, UI, data, security, dan non-functional case yang dipilih;
- **Security Findings** — finding terkonfirmasi/needs-validation berikut target, expected/actual, evidence, owner team, dan error location;
- **Coverage Summary** — total case, status, requirement/risk coverage, access-control checks, dan security findings.

Output lokal selalu draft dan tersanitasi. Generator tidak memanggil API Confluence atau ClickUp.

## Contoh desain dan forward-test generator

Folder [`examples/login-pilot/`](examples/login-pilot/) berisi pilot autentikasi yang sudah disanitasi: PRD *as-is*, 34 test case login/SSO/2FA/recovery/accessibility, XLSX, QA report, serta draft Confluence dan ClickUp.

Seluruh test tetap `not_run` karena target runtime, akun uji, dan kontrak auth belum tersedia. Generator tidak membuat defect atau task ClickUp palsu. Contoh tersebut menunjukkan cara AQABSI mempertahankan evidence honesty; ini bukan klaim bahwa login aplikasi sudah dieksekusi.

Folder [`examples/crud-pilot/`](examples/crud-pilot/) berisi PRD adaptif dan 13 kasus sintetis untuk GET collection/detail, POST, PUT, PATCH, DELETE, validation, duplicate, transaction, UUID, concurrency, audit, dan authorization. Pilot lulus quality validation dan artifact generation, tetapi semua kasus tetap `not_run` karena tidak memakai target/data BSI nyata.

## Instalasi

### Installer publik terperinci

Untuk pengguna umum dengan Node.js `>=22.20.0`, jalankan:

```bash
npx skills add anugrahsy/qabsi-testing
```

Installer akan mendeteksi skill di repository, lalu meminta pengguna memilih skill, AI agent, scope project/global, dan metode instalasi. Pilih `aqabsi-testing` sebagai root skill; jangan memilih folder internal AQABSI satu per satu.

Untuk memasang secara global agar tersedia di semua project:

```bash
npx skills add anugrahsy/qabsi-testing -g
```

Untuk memeriksa isi repository sebelum instalasi:

```bash
npx skills add anugrahsy/qabsi-testing --list
```

### Privacy-first install

`skills` CLI mengumpulkan telemetry instalasi anonim secara default. Untuk lingkungan BSI atau pengguna yang tidak ingin mengirim telemetry installer, gunakan:

```bash
DISABLE_TELEMETRY=1 npx skills add anugrahsy/qabsi-testing
```

### Instal versi yang dipin

Untuk penggunaan tim atau CI, pin release tag atau full commit yang sudah direview:

```bash
npx skills add anugrahsy/qabsi-testing@<release-tag-or-full-commit>
```

### Update instalasi

```bash
npx skills check
npx skills update aqabsi-testing
```

Periksa release note dan perubahan schema sebelum melakukan update pada workflow tim.

### Instal dari repository privat atau GitLab

CLI yang sama mendukung GitLab, SSH, dan repository privat menggunakan credential Git yang sudah dikonfigurasi:

```bash
npx skills add https://gitlab.example.com/group/aqabsi.git
npx skills add git@gitlab.example.com:group/aqabsi.git
```

Ganti URL contoh dengan repository resmi yang telah disetujui organisasi. Jangan memasukkan token ke command atau README.

Panduan `npx skills` dapat dibaca di [Skills CLI documentation](https://www.skills.sh/docs/cli).

### Instalasi manual lanjutan

Metode berikut digunakan jika `npx` tidak tersedia atau tim membutuhkan instalasi Codex yang dikontrol secara manual. Install seluruh root repository sebagai satu skill `aqabsi-testing` agar references, schemas, assets, scripts, dan profil tetap konsisten.

### Prasyarat instalasi manual

- Git
- Python 3
- Codex dengan system skill installer
- `uv` dan PyYAML hanya diperlukan untuk validator tambahan; generator artifact memakai Python standard library

Node.js, browser engine, Docker, Strix, dan credential model **bukan** prasyarat instalasi core. Komponen tersebut hanya diperlukan saat adapter E2E atau security yang relevan diaktifkan.

### Installer bawaan Codex

Gunakan tag atau commit AQABSI yang sudah direview agar instalasi dapat direproduksi. Ganti nilai `AQABSI_REF` dengan release tag atau commit yang disetujui tim.

```bash
AQABSI_REF="<approved-commit-or-tag>"

python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo anugrahsy/qabsi-testing \
  --path . \
  --ref "$AQABSI_REF" \
  --name aqabsi-testing
```

Installer akan berhenti jika folder tujuan sudah ada. Perilaku ini mencegah instalasi lama tertimpa secara tidak sengaja.

### Instal dari checkout lokal

Gunakan metode ini untuk pengembangan atau ketika repository hanya dapat diakses melalui GitLab/internal network. Isi `AQABSI_SOURCE` dengan path absolut checkout yang sudah diverifikasi.

```bash
AQABSI_SOURCE="/absolute/path/to/aqabsi-repository"
AQABSI_SKILLS_DIR="${CODEX_HOME:-$HOME/.codex}/skills"
AQABSI_DEST="$AQABSI_SKILLS_DIR/aqabsi-testing"

test ! -e "$AQABSI_DEST" || {
  echo "Destination already exists: $AQABSI_DEST" >&2
  exit 1
}

mkdir -p "$AQABSI_DEST"
rsync -a \
  --exclude '.git/' \
  --exclude '__pycache__/' \
  --exclude '.DS_Store' \
  "$AQABSI_SOURCE/" "$AQABSI_DEST/"
```

### Verifikasi instalasi manual

```bash
AQABSI_DEST="${CODEX_HOME:-$HOME/.codex}/skills/aqabsi-testing"

cd "$AQABSI_DEST"
python3 -m unittest discover -s tests -v
python3 scripts/validate_package.py .
```

Jika `uv` tersedia, jalankan validator struktur skill tambahan:

```bash
uv run --with pyyaml python \
  "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  "${CODEX_HOME:-$HOME/.codex}/skills/aqabsi-testing"
```

Buka chat/turn baru setelah instalasi agar Codex memuat daftar skill terbaru.

### Upgrade manual yang aman

Jangan menimpa instalasi aktif secara langsung. Pindahkan instalasi lama menjadi backup, install versi baru, jalankan verifikasi, lalu pertahankan backup sampai forward test selesai.

```bash
AQABSI_SKILLS_DIR="${CODEX_HOME:-$HOME/.codex}/skills"
AQABSI_DEST="$AQABSI_SKILLS_DIR/aqabsi-testing"
AQABSI_BACKUP="$AQABSI_SKILLS_DIR/aqabsi-testing.backup-$(date +%Y%m%d-%H%M%S)"

mv "$AQABSI_DEST" "$AQABSI_BACKUP"
```

Setelah backup dibuat, jalankan kembali langkah instalasi dan verifikasi. Saat migrasi dari instalasi versi pra-AQABSI, jangan menonaktifkan instalasi lama sebelum `aqabsi-testing` lulus seluruh validator dan pilot.

### Claude Code/plugin manual

Daftarkan root repository menggunakan mekanisme plugin yang disetujui tim, lalu gunakan namespace `aqabsi:`. Folder `.claude-plugin/`, `skills/`, dan `references/` harus dipasang sebagai satu package agar router dan knowledge module tetap konsisten.

Skill pihak ketiga dipasang terpisah dan dikunci ke repository, commit, path, serta license yang telah direview. AQABSI tidak menyalin seluruh source pihak ketiga ke dalam package.

## Verification

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_package.py .
```

Package dianggap siap ketika source dan instalasi skill sama-sama lulus test, schema validation, link validation, redaction check, dan forward test.

## Prinsip keselamatan

- Tidak ada pass/fail tanpa eksekusi dan evidence.
- Tidak ada pentest, load, destructive, atau production mutation tanpa otorisasi spesifik.
- Tidak ada source, prompt, evidence, credential, token, session, internal URL, atau PII BSI yang keluar dari batas yang disetujui.
- Tidak ada publish, task creation, assignment, commit, atau push secara implisit.
- Tidak ada assignee hasil tebakan; gunakan ownership registry dan platform ID.
- Tidak ada klaim “semua aman” dari exit code nol atau test suite yang terpotong budget.

## Status implementasi

Tersedia dan tervalidasi di package lokal:

- evidence classification dan traceability;
- PRD/test strategy references;
- deterministic artifact generator;
- CSV/XLSX/Markdown dan dry-run payload;
- secret redaction;
- package validator dan automated tests;
- login forward-test pilot.
- identitas AQABSI 2.0.0 dan invariant metadata;
- adaptive professional PRD/test-case quality engine;
- machine-readable module registry dan layered BSI profiles;
- web-only E2E contract dan GitLab CI dry-run template;
- Cloudflare/Strix provenance lock dan security adapter contract;
- access-control/security reporting ke workbook, Confluence draft, dan eligible ClickUp draft;
- synthetic CRUD pilot.

Masih memerlukan akses/configuration organisasi:

- verifikasi base URL, deployment type, auth mode, internal CA, space/list/folder IDs, dan ownership registry;
- live GitLab/Confluence/ClickUp connector pada destination non-production;
- runtime execution dengan target, akun, data, cleanup, dan authority yang disetujui;
- active security scan atau pentest dalam sandbox/target yang diotorisasi;
- release/tag resmi dan publish ke remote repository.

Desain lengkap tersedia di [AQABSI BSI Professional Testing Expansion](docs/superpowers/specs/2026-11-13-aqabsi-bsi-professional-testing-design.md).
