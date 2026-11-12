# Authentication Token Testing

## Overview
Menguji penggunaan **token** untuk autentikasi — utamanya **JWT** (header.payload.signature), **expiration**, dan ketahanan terhadap **tampering**. Risiko utama: token kedaluwarsa tetap diterima, signature bisa dibypass (algorithm confusion), klaim tidak divalidasi, dan token bocor/replay.

## When to Apply
Sistem yang memakai token (JWT, opaque token, refresh token) untuk mengautentikasi request API. Aplikasikan bersama `auth-login`, `auth-session`, dan `api-header` (header `Authorization`).

## Testing Principles
1. Token harus **diverifikasi signature** di server — jangan percaya payload.
2. **Expiration (`exp`), `nbf`, `iss`, `aud`** harus divalidasi sesuai kontrak.
3. Token tidak boleh diterima setelah revoked/expired (termasuk refresh token).
4. Token tidak boleh bocor di URL/log/referer; gunakan header `Authorization`.
5. Algoritma tanda tangan harus dibatasi (jangan terima `alg: none`/algorithm confusion).

## Test Design Techniques
- Equivalence Partitioning — token valid vs expired vs tampered vs salah-audience.
- Boundary Value Analysis — masa berlaku token (tepat sebelum/sesudah `exp`).
- State Transition — token issued → valid → expired/revoked.
- Decision Table — kombinasi klaim (iss/aud/sub) × signature.

## Test Scenarios

### Positive Testing
- Token valid + signature benar → request diterima.
- Klaim `iss`/`aud`/`sub` sesuai → diterima.
- Refresh token valid → access token baru diterbitkan (bila ada flow refresh).
- Token dalam header `Authorization` (bukan URL) → diterima.

### Negative Testing
- Token expired → ditolak (`401`).
- Token dengan signature diubah (tamper payload) → ditolak.
- Token `alg: none` / algorithm confusion → ditolak.
- Token untuk audience/issuer berbeda → ditolak.
- Token yang sudah di-revoke (logout) → ditolak.
- Token tanpa/malformed → ditolak.
- Token di-query-string/URL → kebijakan kontrak (harusnya ditolak/bocor).

### Boundary Testing
- Token dipakai tepat sebelum `exp` → diterima.
- Token dipakai tepat setelah `exp` → ditolak.
- Clock skew / perbedaan waktu server → perilaku sesuai toleransi kontrak.
- Refresh token expired vs access token expired (perilaku berbeda).

### Integration Testing
- Token + `auth-session` — revoke konsisten (logout invalidasi token).
- Token + `api-header` — token hanya lewat header yang benar.
- Token + refresh flow — perpanjangan sesi tidak menghasilkan token tak terbatas.

## Test Data
- Token valid dengan klaim lengkap dan benar.
- Token: expired, tampered (payload diubah), salah `aud`/`iss`, `alg` none, revoked.
- Access token dan refresh token dengan masa berlaku berbeda.

## Expected Results
- Token valid → diterima; klaim tervalidasi.
- Token expired/tampered/revoked → `401` dengan pesan aman (tanpa bocor detail).
- `alg` tidak sesuai kebijakan → ditolak.
- Refresh flow mematuhi batas masa berlaku (tidak memperpanjang tanpa batas).

## Common Defects
- Server tidak memverifikasi signature (hanya decode payload).
- `exp`/`nbf` tidak divalidasi → token kedaluwarsa diterima.
- Algorithm confusion (`none`, HS256 vs RS256) bisa dieksploitasi.
- Klaim `aud`/`iss` tidak dicek → token lintas sistem dipakai.
- Refresh token tidak di-revoke saat logout.
- Token bocor di URL/log.

## Security Considerations
- Token tampering / forgery bila signature lemah atau tidak diverifikasi.
- Token replay (dipakai ulang) bila tidak ada mekanisme revoke/expiration pendek.
- Secret key lemah → signature bisa ditebak.
- Token di log/URL → kebocoran kredensial.

## References
- OWASP WSTG — Testing JSON Web Tokens (WSTG-ATHN-06 / APIT)
- OWASP ASVS — V2 Authentication (token), V3 Session
- RFC 7519 (JWT)
- ISTQB CTFL v4.0.1 — teknik test design
