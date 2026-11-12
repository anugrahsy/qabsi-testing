# API Delete Testing

## Overview
Menguji penghapusan resource (`DELETE /resources/{id}`), baik hard delete maupun soft delete. Risiko utama: data yang seharusnya hanya ditandai terhapus benar-benar hilang, record terhapus masih muncul di list, dan penghapusan meninggalkan data anak yatim atau merusak integritas relasi.

## When to Apply
Setiap aksi hapus: hapus pegawai, hapus dokumen, batalkan pengajuan. Pasangkan dengan `data-soft-delete` (kebijakan visibilitas) dan `auth-object-access` (kepemilikan). Untuk penghapusan massal, tambahkan skenario parsial.

## Testing Principles
1. **Kebijakan hapus harus eksplisit**: hard delete (baris hilang) atau soft delete (flag + tetap ada). Perilaku yang diuji mengikuti kontrak, bukan asumsi.
2. **Delete idempoten menurut RFC 9110**: delete kedua boleh `404` atau `204`, tetapi tidak boleh `500`.
3. **Integritas relasi dijaga**: cascade, restrict, atau set-null — pilih satu dan konsisten.
4. **Data terhapus tidak terlihat oleh pihak yang tidak berhak**, termasuk lewat endpoint lain (list, search, export).
5. **Penghapusan tercatat** (audit) bila domain membutuhkannya.

## Test Design Techniques
- **State Transition** — aktif → terhapus; terhapus → lookup; terhapus → hapus lagi.
- **Decision Table** — peran × kepemilikan × status resource × ada/tidak anak.
- **Boundary Value Analysis** — ID terakhir, resource dengan banyak anak.
- **Equivalence Partitioning** — ID valid/invalid/tidak ada.

## Test Scenarios

### Positive Testing
- DELETE resource milik sendiri → `204` (atau `200` sesuai kontrak).
- Setelah delete, GET detail → `404`.
- Setelah delete, resource tidak muncul di collection, filter, search, maupun export.
- Soft delete: baris tetap ada dengan penanda hapus dan `deleted_at` terisi.
- Hard delete: baris benar-benar hilang dari sumber data.
- Audit trail mencatat siapa menghapus dan kapan.

### Negative Testing
- DELETE ID tidak ada → `404` (atau `204` bila kontrak idempoten), bukan `500`.
- DELETE dua kali → kode konsisten dengan kontrak, bukan exception.
- Tanpa autentikasi → `401`; tanpa izin → `403`; resource milik orang lain → `403`/`404`.
- Resource yang masih direferensikan dan kebijakan restrict → `409` dengan pesan jelas.
- DELETE pada endpoint koleksi tanpa izin → `403` (bukan menghapus semua).
- Body/parameter tambahan yang tidak dikenal → diabaikan, tidak mengubah target.

### Boundary Testing
- Menghapus record terakhir → collection menjadi kosong dengan `200` + array kosong.
- Resource dengan tepat satu anak, banyak anak, dan tanpa anak.
- ID 0 / negatif / terlalu panjang → ditolak rapi.
- Penghapusan massal di batas jumlah maksimum; di atas batas → ditolak.
- Penghapusan resource yang sedang diproses (status transisi) → sesuai aturan bisnis.

### Integration Testing
- Delete + list/filter/search: record hilang dari semua jalur baca.
- Soft delete + restore (bila ada) → record kembali muncul dengan data utuh.
- Delete parent + anak: cascade terhapus semua, atau restrict menolak dengan `409` — tidak boleh separuh.
- Delete + cache: cache detail diinvalidasi sehingga tidak menyajikan data terhapus.
- Delete + proses turunan (notifikasi, sync): terpicu sekali dan tidak error karena data sudah tiada.
- Delete bersamaan dua request → satu berhasil, lainnya `404`/`204`, tidak ada `500` (lihat `api-concurrency`).

## Test Data
- Resource aktif tanpa relasi, dengan satu anak, dengan banyak anak.
- Resource yang sudah soft-deleted dan yang sudah hard-deleted.
- Resource milik user A dan user B (uji kepemilikan).
- Resource yang direferensikan tabel lain (uji restrict/cascade).
- Fixture terakhir di koleksi (uji empty state setelah delete).

## Expected Results
- `204 No Content` tanpa body (atau `200` + body status bila kontrak menyatakan).
- GET setelah delete → `404`; list → record tidak ada; `count` berkurang tepat satu.
- Soft delete: `deleted_at`/`is_deleted` terisi, data lain tidak berubah.
- Hard delete: tidak ada baris tersisa; tidak ada anak yatim.
- `409 Conflict` bila resource masih direferensikan dan kebijakan restrict.
- Delete kedua menghasilkan kode yang sama seperti delete pertama atau `404`, tidak pernah `500`.
- Audit trail mencatat `deleted_by`, waktu, dan ID resource.

## Common Defects
- Soft delete diimplementasikan sebagai hard delete (data hilang permanen).
- Record terhapus tetap muncul di list/search karena query tidak memfilter `deleted_at`.
- `500` saat delete karena foreign key constraint tidak ditangani.
- Cascade menghapus anak tetapi meninggalkan cucu (orphan).
- Delete kedua `500` karena record sudah tidak ada.
- Respons `200`/`204` tetapi record tidak benar-benar terhapus (silent no-op).
- Tidak ada pengecekan kepemilikan → user dapat menghapus data orang lain.
- Cache masih menyajikan resource yang sudah dihapus.
- Audit tidak tercatat sehingga penghapusan tidak dapat ditelusuri.

## Security Considerations
- **BOLA/IDOR**: hapus harus memverifikasi kepemilikan, bukan hanya autentikasi.
- Endpoint delete massal wajib dibatasi role dan dicatat auditnya.
- Konfirmasi/CSRF: bila delete dapat dipicu via GET atau link, rawan CSRF.
- Jangan membocorkan keberadaan resource lewat perbedaan `403` vs `404`.
- Soft delete menyimpan data sensitif — pastikan retensi dan aksesnya terkendali.

## References
- RFC 9110 — HTTP Semantics, §9.3.5 DELETE (idempotent).
- Google AIP-135 (Delete) — semantik standard method Delete.
- OpenAPI Specification — response `204`, `404`, `409`.
- OWASP Web Security Testing Guide — WSTG-ATHZ, business logic.
