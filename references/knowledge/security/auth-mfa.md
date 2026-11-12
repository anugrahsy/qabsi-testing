# Authentication Multi-Factor Authentication (MFA) Testing

## Overview
Menguji **Multi-Factor Authentication**: verifikasi **OTP**, **recovery code**, dan **expiration** faktor kedua. Risiko utama: OTP bisa ditebak/dipakai ulang, brute force OTP tanpa pembatasan, dan mekanisme pemulihan (recovery code) bisa menyalahi MFA itu sendiri.

## When to Apply
Fitur yang menambah faktor kedua setelah login: TOTP/HOTP, OTP via SMS/email, atau recovery code. Aplikasikan bersama `auth-login` (langkah kedua) dan `auth-token`/`auth-session` (penerbitan sesi setelah MFA).

## Testing Principles
1. MFA harus **diverifikasi server-side**; langkah pertama tidak boleh menerbitkan sesi penuh sebelum MFA lolos.
2. OTP harus **acak, sekali pakai, dan berumur pendek** dengan batas percobaan.
3. Recovery code harus **acak, sekali pakai**, dan tidak melemahkan MFA (tidak bisa jadi pengganti tanpa kontrol).
4. Percobaan OTP gagal berulang harus dibatasi (rate limit/lockout).
5. Alur MFA tidak boleh bisa di-bypass (skip step, langsung panggil endpoint pasca-MFA).

## Test Design Techniques
- Equivalence Partitioning — OTP benar/salah/expired/reused.
- Boundary Value Analysis — masa berlaku OTP dan batas percobaan.
- State Transition — status MFA (pending → verified → failed/locked).
- Decision Table — kombinasi OTP × recovery code × percobaan.

## Test Scenarios

### Positive Testing
- OTP benar → verifikasi lolos, sesi penuh diterbitkan.
- OTP dalam masa berlaku → diterima.
- Recovery code valid (bila OTP tak tersedia) → akses dipulihkan sekali pakai.
- Resend OTP → OTP baru terbit, OTP lama tidak berlaku (sesuai kontrak).

### Negative Testing
- OTP salah → ditolak, sesi tidak diterbitkan.
- OTP expired → ditolak.
- OTP dipakai ulang → ditolak.
- OTP untuk user/sesi berbeda → ditolak.
- Recovery code dipakai ulang → ditolak.
- Bypass MFA: langsung panggil endpoint pasca-MFA tanpa verifikasi → ditolak.
- Percobaan OTP berulang melebihi batas → lockout/rate limit.

### Boundary Testing
- OTP dipakai tepat sebelum expire → diterima; tepat setelah → ditolak.
- Percobaan OTP tepat di batas maksimum vs melebihi.
- Recovery code terakhir habis → kebijakan regenerasi sesuai kontrak.

### Integration Testing
- MFA + `auth-login` — sesi hanya terbit setelah faktor kedua lolos.
- MFA + `auth-session`/`auth-token` — revoke/logout tetap menutup akses pasca-MFA.
- MFA + notifikasi (SMS/email) — OTP sampai tanpa bocor di log.

## Test Data
- OTP: valid, expired, reused, salah-user.
- Recovery code: valid, reused, habis.
- Konfigurasi: masa berlaku OTP, batas percobaan, jumlah recovery code.
- Sesi pada tahap sebelum dan sesudah MFA.

## Expected Results
- MFA lolos hanya dengan OTP valid dalam masa berlaku.
- OTP expired/reused/salah → ditolak, sesi tidak terbit.
- Recovery code berlaku sekali pakai.
- Percobaan berlebih → lockout/rate limit.
- Endpoint pasca-MFA tidak bisa diakses tanpa verifikasi MFA.

## Common Defects
- Sesi penuh sudah diterbitkan sebelum MFA lolos (MFA bypassable).
- OTP tidak ber-umur pendek atau bisa dipakai ulang.
- Brute force OTP tidak dibatasi.
- Recovery code melemahkan MFA (bisa dipakai terus, atau reset OTP tanpa verifikasi).
- Algoritma OTP lemah / seed bocor → OTP bisa diprediksi.
- MFA hanya di client (langkah bisa di-skip via API).

## Security Considerations
- Bypass MFA (skip step, endpoint tidak diproteksi).
- OTP brute force / prediction (entropy rendah, seed bocor).
- Recovery code sebagai jalur bypass MFA.
- OTP via SMS rawan SIM swap / interception.

## References
- OWASP WSTG — Testing for Multi-Factor Authentication (WSTG-ATHN-09)
- OWASP ASVS — V2 Authentication (MFA)
- RFC 6238 (TOTP), RFC 4226 (HOTP)
- ISTQB CTFL v4.0.1 — teknik test design
