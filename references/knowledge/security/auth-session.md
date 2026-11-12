# Authentication Session Management Testing

## Overview
Menguji pengelolaan **sesi**: **session timeout** (idle vs absolute), **concurrent sessions**, dan keamanan sesi (fixation, hijacking). Risiko utama: sesi tidak pernah berakhir, sesi bisa dipakai lintas perangkat tanpa batas, dan ID sesi bisa dibajak/difiksasi.

## When to Apply
Sistem berbasis sesi (cookie session ID) maupun token yang menyimpan state login. Aplikasikan bersama `auth-login`, `auth-logout`, dan `auth-token`.

## Testing Principles
1. Sesi harus punya **timeout**: idle timeout dan/atau absolute timeout sesuai kontrak.
2. Kebijakan **concurrent session** harus jelas: boleh berapa sesi aktif, perilaku saat melebihi.
3. ID sesi harus **acak, panjang, dan dirotasi saat login** (anti session fixation).
4. ID sesi tidak boleh lewat URL; cookie sesi wajib atribut aman (`HttpOnly`, `Secure`, `SameSite`).
5. Sesi harus bisa diakhiri server-side (logout/timeout).

## Test Design Techniques
- Boundary Value Analysis — batas waktu timeout (tepat sebelum/sesudah).
- State Transition — sesi active → idle → expired → terminated.
- Decision Table — kombinasi idle × absolute timeout × concurrent limit.
- Combinatorial — jumlah sesi × perangkat.

## Test Scenarios

### Positive Testing
- Aktivitas pengguna menjaga sesi tetap hidup (idle timeout reset).
- Sesuai idle timeout, sesi berakhir setelah periode tanpa aktivitas.
- Absolute timeout berlaku terlepas aktivitas.
- Concurrent session dalam batas yang diizinkan → semua aktif.

### Negative Testing
- Sesuai timeout, request dengan sesi expired → `401`/redirect login.
- Melebihi batas concurrent session → sesi lama diakhiri/ditolak sesuai kontrak.
- ID sesi di URL → ditolak/tidak diterima.
- Akses dengan ID sesi yang difiksasi (sebelum login) → tidak valid setelah login.
- Cookie sesi tanpa atribut aman → flag sesuai kontrak keamanan.

### Boundary Testing
- Aktivitas tepat sebelum idle timeout → sesi tetap hidup.
- Aktivitas tepat setelah idle timeout → sesi berakhir.
- Absolute timeout tercapai saat pengguna aktif → tetap berakhir.
- Concurrent session di batas N vs N+1.

### Integration Testing
- Sesi + `auth-login` — ID sesi baru setelah login (anti fixation).
- Sesi + `auth-logout` — logout mengakhiri sesi server-side.
- Sesi + `auth-token` — timeout/revoke konsisten antara cookie dan token.

## Test Data
- Sesi aktif, sesi idle (tanpa aktivitas), sesi expired.
- Beberapa sesi paralel dari perangkat berbeda.
- Cookie session ID dengan/ tanpa atribut `HttpOnly`/`Secure`/`SameSite`.

## Expected Results
- Sesi berakhir sesuai idle/absolute timeout.
- Concurrent session dibatasi sesuai kontrak.
- ID sesi dirotasi saat login; ID lama tidak valid.
- Cookie sesi punya atribut aman (`HttpOnly`, `Secure`, `SameSite`).
- Akses sesi expired → `401`/redirect login.

## Common Defects
- Session timeout tidak diterapkan (sesi tak pernah berakhir).
- Concurrent session tidak dibatasi.
- ID sesi tidak dirotasi saat login (session fixation).
- ID sesi di URL (bocor via referer/log).
- Cookie sesi tanpa `HttpOnly`/`Secure` (bisa dicuri via XSS/MITM).
- Logout tidak mengakhiri sesi server-side.

## Security Considerations
- Session fixation — penyerang menanam ID sesi lalu korban login.
- Session hijacking via ID sesi yang bocor (URL, log, XSS).
- Sesi tak berakhir → akses berlarut pada perangkat bersama/publik.
- Cookie tanpa `Secure` → bocor lewat koneksi tidak terenkripsi.

## References
- OWASP WSTG — Testing for Session Management (WSTG-SESS)
- OWASP ASVS — V3 Session Management
- ISTQB CTFL v4.0.1 — state transition testing
