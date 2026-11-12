# API Patch Update Testing

## Overview
Menguji update parsial (`PATCH /resources/{id}`): hanya field yang dikirim yang berubah, field lain tetap. Risiko utama: ketidakjelasan **absent vs null** — field yang tidak dikirim ikut terhapus, atau field yang dikirim `null` justru diabaikan. Perbedaan ini adalah sumber bug data paling sering pada PATCH.

## When to Apply
Endpoint edit sebagian: ubah satu status, ganti satu field dari tabel inline, toggle aktif/nonaktif. Bila kontrak menyatakan replacement penuh, gunakan `api-put-update`.

## Testing Principles
1. **Field tidak dikirim = tidak disentuh.** Field dikirim `null` = dikosongkan (hanya bila nullable).
2. **PATCH tidak harus idempoten secara semantik**, tetapi hasilnya harus deterministik untuk payload yang sama.
3. **Semantik merge harus dinyatakan**: JSON Merge Patch (RFC 7396) atau JSON Patch (RFC 6902) — bukan campuran.
4. **Validasi tetap berlaku pada field yang dikirim**, dan hasil akhir harus resource yang valid.
5. **Perubahan sekecil apa pun tercatat** (audit, `updated_at`) sesuai kebijakan.

## Test Design Techniques
- **Equivalence Partitioning** — field dikirim / tidak dikirim / dikirim `null`.
- **Decision Table** — kombinasi nullability × kehadiran field × jenis operasi (set/clear).
- **Boundary Value Analysis** — nilai batas field yang diubah.
- **State Transition** — state sebelum → state sesudah untuk satu field.

## Test Scenarios

### Positive Testing
- Satu field diubah → `200`, field itu berubah, **semua field lain identik** dengan sebelumnya.
- Beberapa field diubah sekaligus → semua berubah, sisanya tetap.
- Field nullable dikirim `null` → nilainya menjadi `null`.
- `updated_at` diperbarui; `created_at` dan `id` tetap.
- Response mengembalikan state resource setelah merge.
- PATCH dengan nilai yang sama (no-op) → `200` dengan state tidak berubah.

### Negative Testing
- Field tak dikenal dikirim → diabaikan atau `422` sesuai kontrak, konsisten.
- Field read-only diubah → diabaikan/ditolak.
- Nilai invalid untuk field yang dikirim → `422`, tidak ada perubahan sebagian.
- Resource tidak ada → `404`; tanpa izin → `403`; tanpa autentikasi → `401`.
- Body bukan objek (`[]`, `"text"`) → `400`.
- Field non-nullable dikirim `null` → `422`, bukan diam-diam diabaikan.
- PATCH pada resource yang sudah dihapus → `404`.

### Boundary Testing
- `{}` (objek kosong) → no-op `200` atau `400` sesuai kontrak, konsisten.
- String tepat panjang maksimum / maksimum + 1.
- Array: `[]` mengosongkan vs tidak dikirim (tidak berubah).
- Objek nested: field tertentu diubah tanpa menghapus sibling-nya (merge dalam).
- Nilai `null` pada field yang sebelumnya `null` (idempoten).
- PATCH dengan banyak field (batas atas) → tetap `200`.

### Integration Testing
- PATCH bersamaan pada field berbeda → kedua perubahan dapat bertahan, atau konflik terdeteksi (`409`/`412`).
- PATCH bersamaan pada field yang sama → tidak ada lost update diam-diam.
- PATCH + audit trail: hanya field yang berubah yang dicatat, dengan nilai lama dan baru.
- PATCH memicu aturan bisnis (mis. status berubah → notifikasi) → terpicu satu kali.
- PATCH + ETag/`If-Match` → `412` bila resource sudah berubah.
- Setelah PATCH, GET detail dan item collection menampilkan nilai yang sama.

## Test Data
- Resource baseline dengan semua field terisi (termasuk field nullable).
- Payload satu field; payload beberapa field; payload dengan `null` eksplisit.
- Payload dengan field tak dikenal dan field read-only.
- Nilai batas untuk field yang diubah.
- Snapshot resource sebelum PATCH untuk membandingkan field yang tidak boleh berubah.

## Expected Results
- `200` (atau `204` sesuai kontrak) dengan state setelah merge.
- Field yang tidak dikirim **byte-identik** dengan nilai sebelum PATCH.
- Field yang dikirim `null` menjadi `null` hanya bila nullable; selain itu `422`.
- Tidak ada perubahan parsial saat respons error.
- Audit mencatat field yang berubah beserta nilai lama dan baru.
- `updated_at` berubah hanya bila ada perubahan nyata (sesuai kebijakan).

## Common Defects
- Field yang tidak dikirim ter-reset menjadi `null` (merge patch diimplementasikan sebagai replace).
- Field yang dikirim `null` diabaikan sehingga tidak bisa mengosongkan nilai.
- PATCH menimpa seluruh objek sehingga field lain hilang.
- No-op tetap mengubah `updated_at` dan memicu notifikasi/audit palsu.
- Validasi hanya dijalankan pada field yang dikirim, sehingga kombinasi antar-field menjadi invalid.
- Field `id`/`owner_id`/`role` dapat diubah lewat PATCH.
- Array selalu di-append, bukan diganti, saat kontrak menyatakan replace.
- Error pada satu field tetap menyimpan field lain (partial commit).

## Security Considerations
- Mass assignment field otorisasi (`role`, `is_admin`, `organization_id`) lewat PATCH adalah jalur eskalasi hak akses yang umum.
- IDOR: pastikan objek yang di-PATCH milik pemanggil.
- Null injection pada kolom yang dipakai logika bisnis dapat menyebabkan perilaku tak terduga di downstream.
- Batasi field yang boleh diubah per role (field-level authorization).

## References
- RFC 7396 — JSON Merge Patch.
- RFC 6902 — JSON Patch.
- RFC 9110 — HTTP Semantics, §9.3.5 PATCH (tidak idempoten secara default).
- OpenAPI Specification — requestBody partial, `422`.
- Google AIP-134 (Update) — field mask untuk update parsial.
