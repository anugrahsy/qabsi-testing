# Authentication Login Testing

## Overview
Menguji proses **login** (autentikasi kredensial): validasi username/email + password, penerbitan sesi/token, dan mekanisme **account lockout**. Risiko utama: pesan error membocorkan identitas akun, brute force tanpa pembatasan, dan lockout tidak konsisten (kunci terlalu cepat/terlalu lama).

## When to Apply
Setiap fitur yang meminta kredensial untuk mengidentifikasi pengguna: login form, login SSO, login API (basic/digest), dan mekanisme lockout akun. Aplikasikan bersama `auth-session`, `auth-token`, dan `auth-mfa`.

## Testing Principles
1. Pesan error login harus **generik** — jangan bedakan "username tidak ditemukan" vs "password salah" (mencegah enumerasi akun).
2. Respons (status, body, waktu) tidak boleh membedakan akun valid vs tidak valid.
3. Lockout harus **deterministik**: ambang percobaan, durasi, dan reset counter jelas.
4. Setelah login sukses, kredensial lama/sesi lama harus dirotasi (jangan reuse sesi lama).
5. Transmisi kredensial wajib lewat kanal terenkripsi (HTTPS); kredensial tidak boleh masuk log/URL.

## Test Design Techniques
- Equivalence Partitioning — kelompok kredensial valid vs invalid.
- Boundary Value Analysis — ambang jumlah percobaan lockout.
- State Transition — status akun (active / locked / disabled / unverified) dan transisinya.
- Decision Table — kombinasi status akun × kredensial × lockout.

## Test Scenarios

### Positive Testing
- Kredensial valid → login sukses, sesi/token diterbitkan sesuai kontrak.
- Username/email diterima sesuai aturan kontrak (case-insensitive bila kontrak menyatakan).
- Akun dengan status aktif dapat login.
- Redirect/landing setelah login sesuai hak akses pengguna.

### Negative Testing
- Password salah → ditolak dengan pesan generik (tanpa membedakan username).
- Username/email tidak terdaftar → ditolak dengan pesan generik.
- Akun disabled / nonaktif / belum verifikasi → ditolak sesuai kontrak.
- Kredensial kosong / field kosong → ditolak validasi.
- Username dengan whitespace leading/trailing → ditangani sesuai kontrak.
- Login ulang dengan kredensial lama setelah password diubah → ditolak.

### Boundary Testing
- Percobaan gagal tepat di bawah ambang lockout → belum terkunci.
- Percobaan gagal mencapai ambang → terkunci.
- Setelah durasi lockout habis → dapat login kembali.
- Reset counter percobaan gagal setelah satu login sukses (sesuai kontrak).

### Integration Testing
- Login + lockout + notifikasi (email/audit) berjalan konsisten.
- Login + MFA (delegasi `auth-mfa`) — langkah kedua gagal → sesi tidak diterbitkan.
- Login + `auth-session` — kebijakan concurrent session diterapkan.
- Login SSO/gateway — pertukaran token/assertion valid.

## Test Data
- Akun valid (status aktif) dan akun invalid.
- Akun dengan status: disabled, locked, belum verifikasi.
- Set kredensial valid/invalid, password mendekati benar.
- Konfigurasi lockout (ambang N percobaan, durasi T).

## Expected Results
- Login valid → `200`/redirect sukses + sesi/token valid.
- Login gagal → `401` dengan pesan generik (atau status sesuai kontrak).
- Tidak ada informasi yang membedakan akun valid vs tidak valid.
- Lockout aktif setelah N gagal dan lepas setelah durasi T.
- Kredensial tidak terekspos di log, URL, atau response.

## Common Defects
- Pesan error membocorkan keberadaan akun ("email tidak terdaftar").
- Brute force tidak dibatasi (tanpa lockout/rate limit/CAPTCHA).
- Lockout counter reset tidak konsisten.
- Setelah login, sesi lama/token lama masih bisa dipakai.
- Kredensial tercatat di log server atau muncul di URL.
- Status akun (disabled/locked) tidak dicek saat login.

## Security Considerations
- Enumerasi akun via pesan error, timing, atau perbedaan status HTTP.
- Brute force / credential stuffing → wajib rate limit + lockout.
- Credential dalam teks terbuka (tanpa HTTPS) → MITM.
- Logging kredensial → kebocoran lewat log/aggregator.

## References
- OWASP WSTG — Testing for Authentication (WSTG-ATHN-01/02/03)
- OWASP ASVS — V2 Authentication Verification Requirements
- ISTQB CTFL v4.0.1 — teknik test design
