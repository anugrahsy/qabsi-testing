# Authorization Object-Level Access Testing (IDOR)

## Overview
Menguji **akses objek** — kepemilikan resource dan **IDOR (Insecure Direct Object Reference)** / **cross-user access**. Risiko utama: pengguna bisa mengakses/memodifikasi resource milik pengguna lain dengan mengubah identifier (ID), dan akses resource tidak dicek kepemilikannya per request.

## When to Apply
Setiap endpoint/fitur yang beroperasi pada **resource spesifik** (`GET/PUT/PATCH/DELETE /resource/{id}`): dokumen, data pribadi, pengajuan, lampiran. Wajib digabung dengan `auth-rbac`/`auth-abac` untuk akses berbasis kepemilikan.

## Testing Principles
1. **Setiap** akses resource wajib dicek otorisasinya server-side per request — bukan hanya validasi ID.
2. ID resource tidak boleh jadi satu-satunya penentu akses; kepemilikan/scope harus diverifikasi.
3. Uji **horizontal escalation** (user A → resource user B) dan **vertical escalation** (role rendah → aksi role tinggi).
4. Identifier yang **tebak-duga** (auto-increment) lebih rawan daripada UUID — tapi UUID tetap wajib dicek kepemilikan.
5. Akses via referensi tidak langsung (indirect reference map) bila kontrak menerapkannya.

## Test Design Techniques
- Equivalence Partitioning — ID milik sendiri vs milik orang lain vs tidak ada.
- Boundary Value Analysis — ID di batas (0, negatif, sangat besar, format berbeda).
- Decision Table — kombinasi role × kepemilikan × aksi.
- Combinatorial — aksi (read/update/delete) × resource.

## Test Scenarios

### Positive Testing
- Akses resource milik sendiri → diizinkan.
- Akses resource milik sendiri dengan role yang memadai → diizinkan.
- Referensi tidak langsung (bila diterapkan) memetakan ke resource benar.

### Negative Testing
- **IDOR**: mengganti ID resource dengan milik user lain → `403`/`404` (bukan bocor).
- Akses resource yang tidak ada (ID tak valid) → `404`/`400` sesuai kontrak.
- Modifikasi (update/delete) resource milik orang lain → ditolak.
- Mengubah ID di body/parameter (bukan path) untuk akses resource lain → ditolak.
- Akses tanpa autentikasi ke resource terlindungi → `401`.

### Boundary Testing
- ID = 0 / negatif / sangat besar → ditolak/ditangani aman.
- ID dengan format berbeda (string vs numerik) → ditangani sesuai kontrak.
- Enumerasi ID berurutan (1,2,3,…) → tidak membocorkan resource orang lain.

### Integration Testing
- Object access + `auth-rbac` — role dan kepemilikan dikombinasikan.
- Object access + `auth-abac` — atribut objek (unit organisasi) sebagai scope.
- Object access + `data-soft-delete` — resource yang dihapus tidak bisa diakses oleh user lain.

## Test Data
- Resource milik user A dan user B (identik jenis).
- Resource yang sudah dihapus (soft-delete) milik user lain.
- ID valid/invalid: 0, negatif, UUID acak, ID berurutan.
- Dua user berbeda role (untuk vertical escalation).

## Expected Results
- Akses resource milik sendiri → `200`.
- Akses resource milik orang lain → `403` (atau `404` untuk mencegah enumerasi).
- Modifikasi resource orang lain → ditolak, data tidak berubah.
- ID invalid → `400`/`404` aman tanpa bocor data.
- Tidak ada data milik user lain yang ter-expose/ter-ubah.

## Common Defects
- Otorisasi kepemilikan tidak dicek — hanya validasi format ID.
- ID auto-increment memudahkan enumerasi + IDOR.
- Vertical escalation: role rendah bisa akses aksi admin dengan ID yang benar.
- Referensi tidak langsung tidak dipetakan (ID internal bocor ke client).
- Cek kepemilikan hanya di UI, bukan di API.

## Security Considerations
- **IDOR / cross-user access** — membaca/mengubah data orang lain via manipulasi ID.
- Horizontal & vertical privilege escalation.
- Enumerasi resource (ID berurutan) → eksfiltrasi data massal.
- Bocornya identifier internal yang bisa dipakai ulang.

## References
- OWASP WSTG — Testing for Insecure Direct Object References (WSTG-ATHZ-04)
- OWASP WSTG — Testing for Authorization (WSTG-ATHZ)
- OWASP ASVS — V4 Access Control (4.1.x object-level)
- OWASP Top 10 — A01 Broken Access Control
- ISTQB CTFL v4.0.1 — teknik test design
