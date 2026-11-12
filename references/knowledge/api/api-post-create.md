# API Post Create Testing

## Overview
Menguji endpoint pembuatan resource (`POST /resources`): validasi required field, pembentukan ID, penerapan default, penolakan duplikat, dan jaminan bahwa kegagalan tidak meninggalkan data setengah jadi. Risiko utama: record tercipta dua kali, record parsial tersimpan saat validasi gagal, dan field yang dikendalikan server (owner, role, timestamp) dapat diisi client.

## When to Apply
Setiap aksi "tambah/simpan baru": tambah pegawai, buat pengajuan, buat transaksi. Pasangkan dengan `input-*` (validasi per field) dan `data-duplicate` (unique constraint). Untuk pengulangan request yang aman, lihat `api-idempotency`.

## Testing Principles
1. **Create adalah all-or-nothing.** Gagal validasi = tidak ada baris baru, tidak ada efek samping.
2. **Server yang menentukan field yang dikendalikan server**: `id`, `created_at`, `created_by`, `status` awal.
3. **`201` + `Location`**, bukan `200`, bila resource baru dibuat (kecuali kontrak menyatakan lain).
4. **Duplikat adalah konflik**, bukan error server: `409`, bukan `500`.
5. **Normalisasi terjadi sebelum simpan** (trim, lowercase email, dsb) dan hasilnya terlihat di response.

## Test Design Techniques
- **Equivalence Partitioning** — payload valid / invalid per field.
- **Decision Table** — kombinasi required terisi × format benar × duplikat.
- **Boundary Value Analysis** — panjang maksimum, nilai min/max, ukuran payload.
- **State Transition** — belum ada → dibuat → response; gagal → tetap belum ada.

## Test Scenarios

### Positive Testing
- Payload minimal valid → `201`, body memuat `id` dan field yang digenerate server.
- Payload lengkap valid → seluruh field tersimpan dan dikembalikan sesuai input (setelah normalisasi).
- Field opsional tidak dikirim → default diterapkan dan terlihat di response.
- Header `Location` menunjuk URL resource yang baru dibuat dan URL tersebut dapat di-GET.
- Setelah create, resource muncul di collection dan pada GET detail.
- `created_at`/`updated_at` terisi dengan waktu server yang wajar.

### Negative Testing
- Required field hilang → `422` (atau `400`) dengan daftar field yang kurang; tidak ada record dibuat.
- Nilai invalid (format, enum, relasi tidak ada) → `422`, bukan `500`.
- Duplikat pada field unique → `409` dengan pesan yang menyebut field; tidak ada record kedua.
- JSON malformed → `400`; `Content-Type` salah → `415`.
- Field read-only (`id`, `created_at`, `role`, `owner_id`) dikirim → diabaikan atau ditolak, tidak dipakai.
- Tanpa autentikasi → `401`; tanpa izin create → `403`.
- Relasi ke parent yang tidak ada → `422`/`404`, bukan record yatim.

### Boundary Testing
- String tepat panjang maksimum diterima; maksimum + 1 ditolak.
- Angka di nilai minimum/maksimum domain; nol dan negatif bila tidak diizinkan.
- Array opsional: tidak dikirim, `[]`, dan jumlah maksimum item.
- Payload tepat di batas ukuran body; di atas batas → `413`.
- Unicode, emoji, dan karakter khusus tersimpan utuh (bukan mojibake).
- Dua request create identik berurutan → perilaku sesuai kontrak (duplikat ditolak atau idempoten).

### Integration Testing
- Create → GET detail → nilai sama dengan yang dikirim.
- Create → collection: item baru muncul, `count` bertambah tepat satu.
- Create dengan idempotency key → hanya satu record walau request diulang (lihat `api-idempotency`).
- Create memicu proses turunan (notifikasi, audit, sync) → terpicu tepat sekali.
- Create bersamaan dengan payload duplikat → satu `201`, sisanya `409` (lihat `api-concurrency`).
- Kegagalan di proses turunan → transaksi utama di-rollback atau ditandai untuk retry sesuai desain.

## Test Data
- Payload minimal, payload lengkap, dan payload dengan setiap required field dihapus satu per satu.
- Nilai duplikat yang sudah ada di database (email, kode, NIK).
- Nilai batas panjang dan nilai angka min/max.
- Payload dengan field read-only diisi nilai berbeda (untuk uji mass assignment).
- Payload dengan karakter unicode/emoji dan spasi di awal/akhir.

## Expected Results
- `201 Created` + `Location` + body representasi resource.
- `id` di-generate server, unik, dan tidak dapat diprediksi berurutan bila itu kebijakan.
- Response mengembalikan nilai **setelah normalisasi**, bukan input mentah.
- `409` untuk duplikat; `422` untuk validasi field; `415` untuk content-type salah.
- Tidak ada record parsial setelah respons gagal (diverifikasi lewat collection/DB).
- Field yang dikendalikan server tidak berubah walau dikirim client.
- `created_by`/`owner_id` berasal dari identitas token, bukan dari body.

## Common Defects
- Mengembalikan `200` padahal resource baru dibuat (kontrak mengharapkan `201`).
- Duplikat menyebabkan `500` karena unique constraint tidak ditangkap.
- Record parsial tersimpan ketika validasi berjalan setelah insert.
- ID dari client dipercaya (client dapat menimpa/menebak ID).
- `created_at` memakai timezone lokal server, bukan UTC/format kontrak.
- Normalisasi tidak diterapkan: email dengan spasi/huruf besar tersimpan berbeda.
- `created_by` diambil dari body sehingga user bisa membuat data atas nama orang lain.
- Dua submit cepat menghasilkan dua record (tidak ada idempotency/unique check).

## Security Considerations
- **Mass assignment**: hanya field yang diizinkan kontrak yang boleh dibaca dari body.
- Jangan percaya `owner_id`, `role`, `status`, atau `is_active` dari client.
- Rate limit endpoint create untuk mencegah spam/pembuatan massal.
- Validasi tipe konten untuk mencegah CSRF bila autentikasi berbasis cookie.
- Jangan mengembalikan field internal atau data pengguna lain di body `201`.

## References
- OpenAPI Specification — requestBody, `201`, `Location` header.
- Google AIP-133 (Create) — semantik standard method Create.
- OWASP Web Security Testing Guide — mass assignment, input validation.
- ISTQB CTFL v4.0.1 — decision table, equivalence partitioning.
