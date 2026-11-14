# AQABSI Preflight Onboarding

Baca dulu memory `aqabsi-qa-workflow` (jika tersedia di memori proyek), lalu **KUMPULKAN SEMUA DATA PREFLIGHT DARI AWAL — jangan asumsikan dan jangan lewati satu pun**. Yang wajib dikumpulkan/ditanyakan:

- mode, target/modul, scope BE/FE, environment (non-secret, via AskUserQuestion)
- **akun uji gateway** (`AQABSI_TEST_USERNAME` + `AQABSI_TEST_PASSWORD`)
- **Confluence** (`AQABSI_CONFLUENCE_EMAIL`, `AQABSI_CONFLUENCE_API_TOKEN`, `AQABSI_CONFLUENCE_SPACE_ID`; base URL/space key sesuai mode cloud/data-center)
- **ClickUp** (`AQABSI_CLICKUP_API_TOKEN`, `AQABSI_CLICKUP_WORKSPACE_ID`, `AQABSI_CLICKUP_LIST_ID`)

**Alur wajib (jangan lanjut diam-diam):**
1. Jalankan `python3 scripts/check_integrations.py --json`.
2. Untuk **setiap** variabel yang `missing`/kosong, **TANYAKAN ke user nilainya** (AskUserQuestion), lalu tulis ke `.env` (gitignored) via `scripts/configure_env.py`. Jangan pernah bilang "lanjut analisis lokal saja" tanpa menawarkan user mengisi data yang kosong.
3. Pakai nilai default dari memory/`.env` HANYA bila sudah terisi; kalau kosong, wajib tanya dulu.

1. **Target & environment** — URL gateway/API + dev / staging / prod.
2. **Akun uji** — username + password.
3. **Confluence** — base URL + email + API token + space key/id + parent page id (opsional).
4. **ClickUp** — API token + workspace id + list id.
5. **Scope** — BE (backend/API) / FE (frontend/UI) / keduanya.
6. **Akses browser FE/UI** — apakah target FE/UI bisa dibuka via browser untuk runtime exploration? Kalau tidak bisa → runtime exploration = `blocked` (fallback ke baca kode).

> **Cara pakai kredensial (secret):** simpan di `$AQABSI_SKILL_ROOT/.env` (gitignored). Kumpulkan nilainya saat preflight lalu tulis via `python3 scripts/configure_env.py '{"AQABSI_TEST_USERNAME":"...", ...}'` (hanya nama key yang dicetak, nilai tidak pernah di-echo). Preflight meng-`source` file itu otomatis (`set -a; . ./.env; set +a`). JANGAN tulis token/password ke PRD/manifest/report/memory/file yang ter-commit, dan jangan commit `.env`. Template nama variabel: `assets/templates/integrations.env.example`.

## Output yang SELALU dibuat setelah eksekusi

- **Web report HTML visual** — dashboard interaktif (summary card, tabel test case yang bisa difilter/search per status & modul, temuan/banner, log) yang di-`serve` via `localhost` (`python3 -m http.server <port>`), supaya mudah dicek.
- **PRD** — markdown (template `prd-template.md`).
- **Test case** — CSV + XLSX (dari manifest `run.json`).
- **Draft Confluence/ClickUp** — dry-run, hanya publish setelah otorisasi eksplisit.

## Desain web report

Dashboard web report **sudah otomatis**: `scripts/generate_dashboard.py` menghasilkan dashboard **nav-menu minimalis-elegan** (halaman Ringkasan / PRD / Hasil Test + drawer detail per test case + dark mode) dengan palette status ter-validasi CVD-safe (dataviz) — tidak perlu koreksi desain manual. Untuk kustomisasi lanjutan (mis. re-skin warna brand), gunakan quality-bar bawaan `skills/awwwards/references/quality-bar.md` sebagai rujukan.

## Autentikasi target aplikasi

Untuk login target aplikasi (form/API, Basic, bearer, atau SSO/SAML/OIDC dengan cert self-signed), ikuti `references/auth-adapter.md`. Helper `scripts/auth_login.py` menyimpan session cookie ke file tanpa menampilkan password/token.
