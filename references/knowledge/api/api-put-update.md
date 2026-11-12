# API Put Update Testing

## Overview
Menguji update dengan semantik **full replacement** (`PUT /resources/{id}`): seluruh representasi resource dikirim, field yang tidak dikirim kehilangan nilai lamanya. Risiko utama: PUT diperlakukan seperti PATCH sehingga data lama tertinggal, atau sebaliknya field yang tidak dikirim terhapus tanpa disadari. Keduanya adalah defect kontrak, bukan sekadar preferensi.

## When to Apply
Endpoint edit yang secara eksplisit memakai `PUT` dan mendokumentasikan replacement penuh: form edit lengkap, sinkronisasi record dari sumber eksternal. Bila API hanya mengubah sebagian field, gunakan `api-patch-update`.

## Testing Principles
1. **PUT = replace.** Nilai default untuk field yang tidak dikirim harus mengikuti kontrak (reset ke default atau `null`), bukan mempertahankan nilai lama secara diam-diam.
2. **PUT idempoten.** Request yang sama dua kali menghasilkan state akhir yang sama.
3. **Identifier tidak berubah.** `id` di path adalah otoritas; `id` di body tidak boleh memindahkan resource.
4. **Validasi sama ketatnya dengan create**, karena hasil akhirnya harus resource yang valid.
5. **Concurrency harus aman** — gunakan precondition (`If-Match`/version) bila kontrak menyediakannya.

## Test Design Techniques
- **Equivalence Partitioning** — payload lengkap valid / lengkap invalid / tidak lengkap.
- **Decision Table** — field dikirim × field required × nilai valid × versi cocok.
- **Boundary Value Analysis** — panjang, angka, ukuran payload.
- **State Transition** — nilai lama → nilai baru; update gagal → state lama utuh.

## Test Scenarios

### Positive Testing
- Payload lengkap valid → `200` + representasi resource setelah update.
- Semua field berubah sesuai payload; tidak ada field yang "tertinggal" nilai lama secara tak terdokumentasi.
- `updated_at` berubah, `created_at` dan `id` tidak berubah.
- Request identik dikirim dua kali → state akhir sama (idempoten).
- Field opsional yang dikirim `null` menjadi `null` bila nullable.
- Setelah PUT, GET detail menampilkan hasil yang sama dengan response PUT.

### Negative Testing
- Required field dihapus dari payload → `422`, state lama tidak berubah.
- Nilai invalid → `422` dengan field yang jelas.
- ID tidak ada → `404`, bukan pembuatan resource baru (no silent upsert).
- ID di body berbeda dari ID di path → `400`/`409` sesuai kontrak, bukan memindahkan resource.
- Field read-only diubah (`id`, `created_at`, `owner_id`) → diabaikan atau ditolak.
- Tanpa izin update → `403`; tanpa autentikasi → `401`; resource milik orang lain → `403`/`404`.
- Body kosong `{}` → `422` (karena required hilang), bukan `200` tanpa perubahan.

### Boundary Testing
- Field opsional yang **tidak dikirim** → diverifikasi apakah di-reset atau dipertahankan sesuai kontrak.
- String tepat panjang maksimum; maksimum + 1 ditolak.
- Angka min/max domain; nol dan negatif bila relevan.
- Array kosong `[]` menggantikan array lama (replace, bukan append).
- Payload tepat di batas ukuran body; di atas batas → `413`.
- Update nilai menjadi nilai yang sama (no-op) → `200`, `updated_at` mengikuti kebijakan kontrak.

### Integration Testing
- PUT bersamaan dari dua client → salah satu menang, lainnya `409`/`412` bila ada precondition (lihat `api-concurrency`).
- PUT pada resource yang sudah dihapus → `404`.
- PUT mengubah field yang memicu proses turunan (status, relasi) → proses terpicu sesuai aturan.
- Audit trail mencatat nilai sebelum dan sesudah untuk seluruh field yang berubah.
- PUT + `If-Match`/ETag: ETag lama → `412`; ETag terbaru → `200`.

## Test Data
- Representasi resource lengkap yang valid (semua field).
- Payload yang menghilangkan satu field opsional, satu per satu.
- Payload dengan nilai `null` pada field nullable dan non-nullable.
- Nilai batas untuk setiap field bertipe teks/angka.
- Dua versi resource (sebelum/sesudah) untuk membandingkan state akhir.

## Expected Results
- `200` dengan representasi resource hasil update (atau `204` bila kontrak menyatakan tanpa body).
- Field yang tidak dikirim berperilaku **sesuai kontrak replacement**, dan perilaku itu konsisten untuk semua field.
- `id` tetap sama; `created_at` tidak berubah; `updated_at` diperbarui.
- Respons gagal tidak mengubah state apa pun (diverifikasi lewat GET setelahnya).
- `412 Precondition Failed` saat ETag/version tidak cocok (bila didukung).
- Error `422` menyebut field dan alasan, bukan pesan generik.

## Common Defects
- PUT berperilaku seperti PATCH: field yang tidak dikirim tetap mempertahankan nilai lama padahal kontrak menyatakan replace.
- Sebaliknya, field opsional ter-reset menjadi `null` tanpa didokumentasikan sehingga data hilang.
- PUT dengan ID tidak ditemukan justru membuat record baru (upsert diam-diam).
- `id` di body dapat mengubah identifier resource.
- `updated_at` tidak berubah padahal data berubah (atau berubah walau no-op).
- Update berhasil sebagian: beberapa field tersimpan, sebagian gagal, respons `500`.
- Field read-only dapat ditimpa lewat PUT.
- Body kosong diterima sebagai "tidak ada perubahan" padahal required field hilang.

## Security Considerations
- Cek kepemilikan resource sebelum replace (BOLA/IDOR).
- Mass assignment pada replace lebih berbahaya karena seluruh objek ditulis: whitelist field.
- Jangan izinkan perubahan field otorisasi (`role`, `organization_id`, `owner_id`) lewat body.
- Precondition (`If-Match`) mencegah overwrite data orang lain pada edit bersamaan.

## References
- RFC 9110 — HTTP Semantics, §9.3.4 PUT (idempotent, full replacement).
- OpenAPI Specification — requestBody, `200`, `412`.
- Google AIP-134 (Update) — semantik standard method Update.
- ISTQB CTFL v4.0.1 — decision table, state transition.
