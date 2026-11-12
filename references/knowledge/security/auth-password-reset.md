# Authentication Password Reset Testing

## Overview
Menguji alur **lupa/reset password**: permintaan token reset, pengiriman token, dan pemakaian token untuk menetapkan password baru. Risiko utama: token tebak-duga/tamper, token kadaluarsa tapi tetap diterima, token dipakai ulang, dan enumerasi akun lewat respons reset.

## When to Apply
Fitur "lupa password" / forgot password / reset password, baik via email/OTP. Aplikasikan bersama `auth-password-change`, `input-password`, dan `auth-mfa` (bila reset lewat OTP).

## Testing Principles
1. Token reset harus **acak, sekali pakai (single-use), dan berumur pendek**.
2. Respons reset tidak boleh membocorkan apakah akun ada (enumerasi akun).
3. Token invalid/expired/tampered harus ditolak tanpa menetapkan password.
4. Setelah reset, sesi/token lama akun harus diinvalidasi.
5. Password baru tetap tunduk kebijakan password.

## Test Design Techniques
- Equivalence Partitioning — token valid vs invalid/expired/reused.
- Boundary Value Analysis — masa berlaku token (tepat sebelum/sesudah expire).
- State Transition — status token (unused → used → invalid).
- Decision Table — kombinasi status token × validitas password baru.

## Test Scenarios

### Positive Testing
- Permintaan reset untuk akun valid → token terbit dan terkirim via kanal aman.
- Token valid + password baru valid → password berubah, token tidak berlaku lagi.
- Setelah reset sukses → login dengan password baru berhasil.
- Notifikasi keamanan terkirim (sesuai kontrak).

### Negative Testing
- Token invalid / asal → ditolak.
- Token expired → ditolak.
- Token dipakai ulang (kedua kali) → ditolak.
- Token hasil tamper/modifikasi → ditolak.
- Password baru tidak memenuhi kebijakan → ditolak.
- Permintaan reset untuk akun tidak terdaftar → respons generik (tidak membocorkan).

### Boundary Testing
- Token dipakai tepat sebelum expire → diterima.
- Token dipakai tepat setelah expire → ditolak.
- Token dengan masa berlaku sangat panjang → sesuai kontrak (wajib ada batas).
- Password baru di batas panjang min/max → sesuai kebijakan.

### Integration Testing
- Reset + `auth-session`/`auth-token` — sesi lama diinvalidasi setelah reset.
- Reset + email service — token sampai tanpa bocor di log/URL.
- Reset + `auth-password-change` — konsistensi kebijakan password.

## Test Data
- Akun valid dan akun tidak terdaftar.
- Token reset: valid, expired, reused, tampered.
- Password baru valid/invalid sesuai kebijakan.
- Konfigurasi masa berlaku token.

## Expected Results
- Token valid sekali pakai → sukses satu kali, selanjutnya ditolak.
- Token invalid/expired/tampered → ditolak (`400`/`422`/`401`).
- Respons reset tidak membocorkan keberadaan akun.
- Sesi/token lama akun tidak lagi valid setelah reset.
- Password baru memenuhi kebijakan dan berhasil dipakai login.

## Common Defects
- Token reset tidak ber-umur pendek (tidak ada expiration).
- Token dapat dipakai ulang (tidak single-use).
- Token bisa ditebak (random lemah / predictable).
- Enumerasi akun lewat pesan "email tidak terdaftar".
- Sesi lama tidak diinvalidasi setelah reset (akun tetap bisa diakses penyerang).
- Token bocor di URL/referer/log.

## Security Considerations
- Token prediction / brute force (entropy rendah).
- Account takeover via token reset yang bocor.
- Enumerasi akun via respons/duur reset.
- Reuse token lintas akun (token tidak terikat ke akun).

## References
- OWASP WSTG — Testing for Weak Password Reset / Change (WSTG-ATHN-07)
- OWASP ASVS — V2 Authentication (credential recovery)
- ISTQB CTFL v4.0.1 — teknik test design
