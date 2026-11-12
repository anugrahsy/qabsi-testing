# Authorization RBAC Testing

## Overview
Menguji **Role-Based Access Control (RBAC)**: pemetaan **role → permission**, dan penegakan akses berdasarkan role pengguna. Risiko utama: privilege escalation (vertikal/horizontal), default-allow (akses lolos tanpa role), dan role yang tidak konsisten setelah assignment/removal.

## When to Apply
Sistem dengan role/peran (admin, operator, reviewer, dst.) yang membatasi akses fitur/endpoint/aksi. Aplikasikan bersama `auth-object-access` (akses per resource) dan `api-authorization`.

## Testing Principles
1. Penegakan akses harus **server-side** — jangan hanya sembunyikan menu/button di UI.
2. Default harus **deny** — akses tanpa role yang memadai ditolak.
3. Setiap aksi/fitur/endpoint harus **dipetakan ke permission** yang jelas.
4. Perubahan role (grant/revoke) harus segera konsisten di seluruh request.
5. Uji **privilege escalation**: role rendah tidak boleh melakukan aksi role lebih tinggi.

## Test Design Techniques
- Equivalence Partitioning — role yang diizinkan vs tidak diizinkan per aksi.
- Decision Table — matriks role × aksi/fitur × permission.
- State Transition — perubahan status role (grant/revoke/expired).
- Combinatorial — kombinasi role × endpoint (prioritas berbasis risiko).

## Test Scenarios

### Positive Testing
- Role dengan permission → akses diizinkan.
- Setiap aksi/fitur hanya bisa diakses role yang dipetakan.
- Role bertingkat (hierarki) mewarisi permission sesuai kontrak.
- Perubahan role langsung berefek pada request berikutnya.

### Negative Testing
- Role tanpa permission → akses ditolak (`403`).
- User tanpa role / role kosong → ditolak (default deny).
- Role rendah mencoba aksi role tinggi (vertical escalation) → ditolak.
- User dengan satu role mengakses resource role lain (horizontal escalation) → ditolak.
- Akses endpoint tanpa autentikasi → `401`, bukan sekadar `403`.

### Boundary Testing
- Role dengan permission parsial (sebagian fitur) → hanya yang diizinkan lolos.
- Grant lalu revoke role → akses langsung ditolak.
- Multi-role (user dengan beberapa role) → gabungan permission sesuai kebijakan kontrak.

### Integration Testing
- RBAC + `auth-object-access` — permission role dikombinasikan dengan kepemilikan resource.
- RBAC + UI — tombol/menu yang disembunyikan tidak cukup; endpoint tetap diperiksa.
- RBAC + `api-authorization` — konsistensi enforcement di semua endpoint.

## Test Data
- Set role dan matriks permission-nya.
- User per role: admin, role terbatas, tanpa role.
- User dengan multi-role dan role yang baru di-revoke.
- Matriks aksi/fitur/endpoint yang dipetakan.

## Expected Results
- Role yang diizinkan → `200`; role tidak diizinkan → `403`.
- Tanpa autentikasi → `401`.
- Default deny: akses tanpa permission memadai ditolak.
- Revoke role langsung menutup akses.
- Tidak ada aksi role tinggi yang bisa dijalankan role rendah.

## Common Defects
- Enforcement hanya di client (UI) — endpoint bisa dipanggil langsung.
- Default allow — endpoint lupa diproteksi sehingga publik.
- Missing access control: endpoint tertentu tidak dicek role.
- Role assignment/removal tidak konsisten (cache/token stale).
- Hierarki role salah (role rendah mewarisi akses admin).

## Security Considerations
- Vertical privilege escalation (role rendah → admin).
- Horizontal privilege escalation (akses resource user/role lain).
- Broken function-level access control (endpoint tak diproteksi).
- Role stale pada token/sesi (perubahan role tidak langsung berlaku).

## References
- OWASP WSTG — Testing for Authorization (WSTG-ATHZ)
- OWASP ASVS — V4 Access Control
- OWASP Top 10 — A01 Broken Access Control
- ISTQB CTFL v4.0.1 — decision table testing
