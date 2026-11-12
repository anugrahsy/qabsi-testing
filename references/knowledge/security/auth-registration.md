# Authentication Registration Testing

## Overview
Menguji proses **pendaftaran akun** (self-registration): pembuatan akun, validasi data, dan deteksi **akun duplikat**. Risiko utama: akun duplikat lolos, enumerasi akun lewat respons pendaftaran, dan validasi password/email tidak konsisten.

## When to Apply
Fitur pendaftaran pengguna mandiri (form register, API register), termasuk alur verifikasi email. Aplikasikan bersama `input-email`, `input-password`, `input-username`, dan `data-duplicate`.

## Testing Principles
1. Duplikasi (email/username) harus **dicek dan ditolak** — jangan sampai ada dua akun dengan identitas sama.
2. Pendaftaran tidak boleh membocorkan akun yang sudah ada (enumerasi akun).
3. Kebijakan password/email diterapkan konsisten dengan modul input terkait.
4. Akun baru belum bisa dipakai sebelum statusnya terverifikasi (sesuai kontrak).
5. Penanganan duplikasi harus tahan race condition (concurrent).

## Test Design Techniques
- Equivalence Partitioning — data valid vs invalid per field.
- Boundary Value Analysis — batas panjang/format field.
- Decision Table — kombinasi status verifikasi × duplikasi × validasi.
- Combinatorial — kombinasi field (email + username + password).

## Test Scenarios

### Positive Testing
- Pendaftaran dengan data valid → akun dibuat sesuai kontrak.
- Akun berstatus sesuai alur (mis. menunggu verifikasi email).
- Email verifikasi terkirim dan tautan berfungsi (bila ada).
- Verifikasi selesai → akun aktif dan bisa login.

### Negative Testing
- Email/username sudah terdaftar → ditolak (tanpa membocorkan akun yang ada).
- Format email/username/password tidak valid → ditolak validasi.
- Field wajib kosong → ditolak.
- Password tidak memenuhi kebijakan → ditolak.
- Pendaftaran duplikat persis (data sama) → ditolak idempoten/konsisten.
- Token verifikasi invalid/expired → verifikasi ditolak.

### Boundary Testing
- Panjang field (email/username/password) di batas min/max.
- Karakter khusus / Unicode pada username → sesuai aturan kontrak.
- Verifikasi tautan dipakai lebih dari sekali → hanya berlaku sekali (sesuai kontrak).

### Integration Testing
- Registrasi + verifikasi email + login pertama (alur end-to-end).
- Registrasi + `data-duplicate` — constraint unik di DB dijamin.
- Registrasi bersamaan (concurrent) dengan data sama → hanya satu akun dibuat.

## Test Data
- Data registrasi valid dan invalid per field.
- Akun yang sudah ada (untuk uji duplikat).
- Token verifikasi valid/invalid/expired.
- Dua request registrasi identik (untuk uji race condition).

## Expected Results
- Registrasi valid → akun dibuat dengan status benar.
- Duplikat → ditolak (`400`/`409`) tanpa membocorkan data akun yang ada.
- Akun baru tidak bisa dipakai sebelum verifikasi (sesuai kontrak).
- Tidak ada akun duplikat yang tersimpan di DB.

## Common Defects
- Respons duplikat membocorkan akun ("email sudah terdaftar" → enumerasi).
- Race condition: dua pendaftaran identik sama-sama lolos.
- Kebijakan password/email tidak diterapkan sama seperti modul input.
- Akun tanpa verifikasi sudah bisa login.
- Data akun baru tidak lengkap/inkonsisten (field wajib kosong tersimpan).

## Security Considerations
- Enumerasi akun lewat respons/verifikasi pendaftaran.
- Mass registration / bot (perlu CAPTCHA/rate limit).
- Verifikasi email yang bisa dipalsukan (token tebak-duga).
- Penyimpanan data pribadi berlebihan (data minimization).

## References
- OWASP WSTG — Testing for Account Enumeration and Guessable User Account (WSTG-IDENT)
- OWASP ASVS — V2 Authentication
- ISTQB CTFL v4.0.1 — teknik test design
