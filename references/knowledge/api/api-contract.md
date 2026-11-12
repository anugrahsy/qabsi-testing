# API Contract Testing

## Overview
Menguji kesesuaian request dan response dengan **kontrak** yang disepakati (OpenAPI, PRD, dokumentasi internal): nama field, tipe data, required/optional, nullability, format, dan struktur nested. Risiko utama: kontrak dan implementasi menyimpang tanpa terdeteksi, sehingga client rusak diam-diam (silent breakage) dan bug baru muncul di sisi konsumen, bukan di API.

## When to Apply
Setiap endpoint yang punya spesifikasi tertulis — dan selalu lebih dulu sebelum menguji perilaku detail (pagination, error handling). Modul ini adalah "lapisan pertama" yang dipakai ulang oleh modul `api-*` lain: bila kontrak belum jelas, hasil pengujian modul lain sulit dinilai benar/salah.

## Testing Principles
1. **Kontrak adalah sumber kebenaran**, bukan asumsi penguji. Bila kontrak ambigu, itu temuan tersendiri (defect dokumentasi), bukan izin menebak.
2. **Optional ≠ nullable.** Field yang boleh tidak dikirim berbeda dari field yang boleh bernilai `null`. Keduanya diuji terpisah.
3. **Validasi bentuk dan semantik.** Tipe benar tapi makna salah (mis. `status: "1"` vs `"active"`) tetap defect.
4. **Kebijakan unknown field harus konsisten** di seluruh endpoint: diabaikan atau ditolak, pilih satu.
5. **Schema drift dicek otomatis**, bukan manual per field, bila tersedia validator OpenAPI.

## Test Design Techniques
- **Equivalence Partitioning** — field ada/tidak ada, tipe valid/invalid, enum valid/invalid.
- **Decision Table** — kombinasi required × present × tipe benar (2^n baris, disaring ke kombinasi bermakna).
- **Boundary Value Analysis** — panjang string, jumlah item array, presisi angka, kedalaman objek.
- **Schema-based / property-based testing** — generate payload dari schema, bandingkan hasil validasi dengan respons aktual.

## Test Scenarios

### Positive Testing
- Payload lengkap valid → `2xx`, response lolos validasi schema OpenAPI tanpa error.
- Payload minimal (hanya required) → `2xx`, field opsional memakai default atau tidak muncul konsisten.
- Semua field response bertipe sesuai kontrak (`integer` bukan `string`, `array` bukan objek tunggal).
- Enum mengembalikan nilai yang terdaftar di kontrak, bukan nilai internal.
- Nested object/array punya bentuk yang sama di setiap item.

### Negative Testing
- Satu required field dihapus → `400`/`422` dengan error menunjuk field tersebut, bukan `500`.
- Field dikirim dengan tipe salah (string untuk integer, objek untuk string) → ditolak `4xx`, tidak dikonversi diam-diam.
- `null` dikirim untuk field non-nullable → ditolak dengan pesan jelas.
- Field tak dikenal dikirim → diabaikan atau ditolak **konsisten** sesuai kontrak (bukan kadang diterima, kadang tidak).
- Body bukan JSON valid / kosong → `400`, bukan `500`.
- Field read-only (`id`, `created_at`) dikirim client → diabaikan atau ditolak, tidak pernah dipakai.

### Boundary Testing
- String tepat di panjang maksimum → diterima; maksimum + 1 → ditolak `422`.
- String kosong `""` vs `null` vs field tidak dikirim → tiga perilaku berbeda, diverifikasi sesuai kontrak.
- Array kosong `[]` vs array dengan 1 item vs jumlah maksimum item.
- Angka di batas tipe (integer 32/64-bit), nilai negatif, dan presisi desimal (mis. 2 digit vs 4 digit).
- Objek nested pada kedalaman maksimum yang diizinkan.

### Integration Testing
- Response GET detail dan item di dalam GET collection memakai **schema yang sama**.
- Response error memakai envelope yang sama dengan response sukses yang didokumentasikan.
- Kontrak lintas versi: field yang dihapus/diubah hanya pada versi baru (lihat `api-versioning`).
- Kontrak file upload (multipart) sesuai definisi (lihat `api-file-upload`).
- Consumer-driven contract: jalankan kontrak milik client terhadap API untuk mendeteksi breaking change.

## Test Data
- Payload minimal valid dan payload lengkap valid.
- Satu fixture per field required yang dihapus (isolasi penyebab error).
- Fixture tipe salah per tipe data: string, integer, boolean, array, object, null.
- Nilai batas: panjang maksimum, angka min/max, string unicode dan emoji.
- Response tersimpan (snapshot) dari versi sebelumnya untuk mendeteksi drift.

## Expected Results
- Semua response `2xx` lolos validasi schema tanpa error tambahan.
- `Content-Type` response sesuai kontrak (`application/json; charset=utf-8`, dsb).
- Error `4xx` menyebut field yang salah dan alasan yang dapat dibaca mesin (kode) maupun manusia (pesan).
- Tidak ada field yang tidak didokumentasikan muncul di response produksi.
- Field opsional konsisten: selalu ada, selalu absen, atau eksplisit `null` — bukan campuran antar request.
- Perubahan breaking (hapus field, ubah tipe, ubah required) terdeteksi oleh validator, bukan oleh laporan pengguna.

## Common Defects
- Nama field tidak konsisten (`snake_case` di satu endpoint, `camelCase` di endpoint lain).
- Tipe longgar: integer dikirim sebagai string dan diterima tanpa error; boolean sebagai `"true"`.
- Required field tidak benar-benar divalidasi (hanya dicek di UI).
- Field opsional kadang `null`, kadang tidak ada, tanpa aturan.
- Field internal (mis. `deleted_at`, `internal_note`) bocor ke response publik.
- Format tanggal berbeda antar endpoint (ISO-8601 vs epoch vs `dd/mm/yyyy`).
- Breaking change dirilis tanpa menaikkan versi.
- Response sukses dan error memakai bentuk envelope berbeda.

## Security Considerations
- **Mass assignment / over-posting**: field yang tidak ada di kontrak tetapi diterima dan tersimpan (mis. `role`, `is_admin`).
- Field sensitif tidak boleh muncul walau schema longgar (password hash, token, NIK).
- Pesan error validasi jangan membocorkan nama tabel, query, atau struktur internal.
- Schema publik jangan mengungkap endpoint/admin internal.

## References
- OpenAPI Specification — schema, required, nullable, response object.
- OWASP Web Security Testing Guide — WSTG-APIT (API testing), mass assignment.
- ISTQB CTFL v4.0.1 — equivalence partitioning, decision table, boundary value analysis.
- Google AIP-133 / AIP-134 — bentuk resource pada create/update.
