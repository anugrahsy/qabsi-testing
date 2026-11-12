# Authentication Logout Testing

## Overview
Menguji proses **logout** dan **invalidasi sesi/token**. Risiko utama: sesi tidak benar-benar berakhir server-side, token lama masih bisa dipakai setelah logout, dan logout satu perangkat tidak menghapus sesi lain sesuai kebijakan.

## When to Apply
Setiap fitur logout, baik UI (tombol logout) maupun API (endpoint logout), pada sistem berbasis sesi maupun token. Aplikasikan bersama `auth-session` dan `auth-token`.

## Testing Principles
1. Logout harus **invalidasi server-side** — bukan hanya menghapus token/sesi di client.
2. Setelah logout, kredensial/sesi lama **tidak boleh** dipakai ulang untuk akses.
3. Kebijakan logout harus jelas: single session vs semua perangkat.
4. Logout tidak boleh bergantung semata pada penghapusan cookie/token di sisi pengguna.

## Test Design Techniques
- State Transition — transisi authenticated → unauthenticated.
- Negative Testing — akses dengan sesi/token yang sudah di-logout.
- Combinatorial — logout × jenis sesi (single/multi-device).

## Test Scenarios

### Positive Testing
- Logout dari sesi aktif → sesi/token tidak lagi valid.
- Setelah logout, request dengan token lama → `401`/ditolak.
- Logout menghapus cookie/refresh token sesuai kontrak.
- Logout dari semua perangkat (bila didukung) → semua sesi berakhir.

### Negative Testing
- Akses endpoint terlindungi dengan token pasca-logout → ditolak.
- Refresh token dipakai setelah logout → ditolak.
- Logout ganda (logout lagi saat sudah logout) → ditangani tanpa error tak terduga.
- Logout dengan token/sesi yang sudah invalid → respons idempoten.

### Boundary Testing
- Logout sesaat sebelum sesi idle timeout → tetap invalidasi bersih.
- Banyak sesi paralel: logout satu sesi → perilaku sesi lain sesuai kebijakan kontrak.

### Integration Testing
- Logout + `auth-session` — invalidasinya konsisten dengan session timeout/concurrent session.
- Logout + `auth-token` — refresh token juga di-revoke (bila ada blacklist).
- Logout + audit log — kejadian logout tercatat.

## Test Data
- Sesi aktif (cookie session ID / JWT access + refresh token).
- Sesi paralel di beberapa perangkat.
- Token yang sudah/baru saja di-logout.

## Expected Results
- Setelah logout, akses dengan sesi/token lama → `401`/`403`.
- Tidak ada state authenticated yang tersisa server-side.
- Perilaku single vs multi-device sesuai kontrak.
- Logout idempoten — tidak menghasilkan error tak terduga.

## Common Defects
- Logout hanya menghapus cookie client, sesi server tetap aktif.
- Refresh token tidak di-revoke → sesi bisa diperpanjang pasca-logout.
- Logout tidak menutup semua sesi padahal kebijakan "logout all devices".
- Endpoint logout bisa dipanggil tanpa autentikasi (membuang sesi orang lain).

## Security Considerations
- Sesi yatim (orphaned session) yang tetap valid setelah logout.
- CSRF pada endpoint logout berbasis cookie.
- Logout lintas perangkat yang tidak menutup sesi → sesi bocor dipakai orang lain.

## References
- OWASP WSTG — Testing for Session Management (WSTG-SESS)
- OWASP ASVS — V2 Authentication, V3 Session Management
- ISTQB CTFL v4.0.1 — state transition testing
