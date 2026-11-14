# AQABSI Preflight Onboarding

Baca dulu memory `aqabsi-qa-workflow` (jika tersedia di memori proyek), lalu **TANYAKAN** (jangan asumsikan) hal **non-secret** berikut sebelum mulai eksekusi: mode, target/modul, scope BE/FE, dan environment. **Nilai secret (token/password/email akun uji) tidak ditanya ulang** — sudah disimpan di file `.env` lokal (gitignored) di root skill dan di-source otomatis saat preflight. Pakai nilai default dari memory/`.env` bila user tidak memberikan nilai baru.

1. **Target & environment** — URL gateway/API + dev / staging / prod.
2. **Akun uji** — username + password.
3. **Confluence** — base URL + email + API token + space key/id + parent page id (opsional).
4. **ClickUp** — API token + workspace id + list id.
5. **Scope** — BE (backend/API) / FE (frontend/UI) / keduanya.
6. **Akses browser FE/UI** — apakah target FE/UI bisa dibuka via browser untuk runtime exploration? Kalau tidak bisa → runtime exploration = `blocked` (fallback ke baca kode).

> **Cara pakai kredensial (secret):** simpan di `$AQABSI_SKILL_ROOT/.env` (gitignored, diisi sekali). Preflight meng-`source` file itu otomatis (`set -a; . ./.env; set +a`), jadi script membaca dari environment tanpa token muncul di chat. JANGAN tulis token/password ke PRD/manifest/report/memory/file yang ter-commit, dan jangan commit `.env`. Template nama variabel: `assets/templates/integrations.env.example`.

## Output yang SELALU dibuat setelah eksekusi

- **Web report HTML visual** — dashboard interaktif (summary card, tabel test case yang bisa difilter/search per status & modul, temuan/banner, log) yang di-`serve` via `localhost` (`python3 -m http.server <port>`), supaya mudah dicek.
- **PRD** — markdown (template `prd-template.md`).
- **Test case** — CSV + XLSX (dari manifest `run.json`).
- **Draft Confluence/ClickUp** — dry-run, hanya publish setelah otorisasi eksplisit.

## Desain web report

Gunakan skill `antislop` (plugin `antislop@anti-slop`) agar desain web report profesional — bukan generik/AI-slop: spacing, kontras, tipografi, dan warna yang rapi dan konsisten. Naikkan standar visual ke quality-bar skill desain bawaan AQABSI (`skills/awwwards/references/quality-bar.md`) dan nilai hasil akhirnya dengan skill juri bawaan (`skills/jury/SKILL.md`) untuk daftar perbaikan ter-ranking. Dashboard self-contained tetap dibuat langsung dengan `scripts/generate_dashboard.py`.

## Autentikasi target aplikasi

Untuk login target aplikasi (form/API, Basic, bearer, atau SSO/SAML/OIDC dengan cert self-signed), ikuti `references/auth-adapter.md`. Helper `scripts/auth_login.py` menyimpan session cookie ke file tanpa menampilkan password/token.
