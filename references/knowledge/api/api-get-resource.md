# API Get Resource Testing

## Overview
Menguji endpoint yang mengembalikan **satu resource berdasarkan identifier** (`GET /resources/{id}`). Risiko utama: resource tidak ada diperlakukan sebagai error server, resource terhapus masih tampil, dan akses lintas pemilik (IDOR) tidak dicegah. Modul ini fokus pada kebenaran lookup dan batas identitas, bukan pada bentuk collection.

## When to Apply
Endpoint detail: halaman detail pegawai, profil, dokumen, transaksi. Aplikasikan bersama `api-authorization` (ownership) dan `api-http-status` (pemetaan 404 vs 403). Bila response berupa list, gunakan `api-get-collection`.

## Testing Principles
1. **Satu ID = satu resource.** ID yang sama tidak boleh menghasilkan resource berbeda antar request.
2. **Not found adalah hasil normal**, bukan kegagalan sistem: `404`, bukan `500`.
3. **Keberadaan resource tidak boleh bocor ke pihak tak berhak.** Untuk resource milik orang lain, pilih `404` (menyembunyikan) atau `403` secara konsisten — jangan campur.
4. **Format ID divalidasi sebelum query**, agar ID aneh tidak sampai ke database.
5. **Resource terhapus tidak terlihat** sesuai kebijakan (hard/soft delete).

## Test Design Techniques
- **Equivalence Partitioning** — ID valid milik sendiri / milik orang lain / tidak ada / format invalid.
- **Boundary Value Analysis** — panjang ID, nilai 0/negatif, integer overflow, UUID varian.
- **State Transition** — resource aktif → terhapus → lookup ulang.
- **Decision Table** — kombinasi status autentikasi × kepemilikan × keberadaan resource.

## Test Scenarios

### Positive Testing
- ID valid milik sendiri → `200` + representasi lengkap resource.
- Response memuat `id` yang sama dengan yang diminta (echo yang benar).
- Semua field sesuai kontrak dan nilainya cocok dengan data sumber.
- Resource dengan relasi (parent/child) menampilkan relasi yang benar.
- Endpoint mengembalikan `ETag`/`Last-Modified` bila kontrak menyatakan caching.

### Negative Testing
- ID tidak ada di database → `404` dengan body error konsisten, bukan `500`.
- ID berformat salah (`abc` untuk ID numerik) → `400` atau `404` sesuai kontrak, bukan exception.
- ID resource yang sudah dihapus → `404` (atau `410` bila kontrak menyatakan Gone).
- Tanpa kredensial → `401`; kredensial valid tanpa izin → `403` atau `404` sesuai kebijakan.
- Resource milik pengguna lain → tidak mengembalikan data (IDOR test).
- ID milik tipe resource lain (mis. ID dokumen di endpoint pegawai) → `404`.

### Boundary Testing
- ID `0`, ID negatif, dan ID dengan leading zero (`007` vs `7`).
- ID tepat pada panjang maksimum dan maksimum + 1.
- Integer overflow (nilai di atas batas tipe) → ditolak rapi, bukan wrap-around.
- UUID huruf besar/kecil dan UUID tanpa hyphen → perilaku konsisten sesuai kontrak.
- ID dengan karakter khusus / URL-encoded (`%2F`, spasi) → tidak menyebabkan path traversal.

### Integration Testing
- Data dari GET detail identik dengan item yang sama di GET collection.
- GET detail setelah create/update menampilkan perubahan terbaru (bukan cache basi).
- Nested route (`/parents/{id}/children/{childId}`): child harus benar-benar milik parent tersebut.
- Resource terhapus hilang dari detail **dan** collection.
- Cache: request berulang dengan `If-None-Match` mengembalikan `304` bila tidak berubah.

## Test Data
- Resource aktif milik user A, resource aktif milik user B (untuk IDOR).
- Resource yang sudah di-soft-delete dan yang sudah di-hard-delete.
- ID dengan format: numerik, UUID, string alfanumerik (sesuai kontrak).
- Fixture dengan relasi lengkap dan fixture dengan relasi kosong.
- Nilai field nullable untuk memastikan bentuk `null` konsisten.

## Expected Results
- `200` untuk resource yang ada dan boleh diakses; body sesuai schema.
- `404` untuk tidak ada / sudah dihapus, dengan envelope error yang sama seperti endpoint lain.
- `401` tanpa kredensial, `403`/`404` untuk resource milik pihak lain — konsisten di semua endpoint.
- `id` di response selalu sama dengan `id` di path.
- Tidak ada stack trace, nama tabel, atau query di body error.
- Lookup ID invalid tidak menghasilkan query database yang tidak perlu (dapat diverifikasi dari log/DB).

## Common Defects
- Resource tidak ditemukan → `500` karena `null` tidak ditangani.
- Soft-deleted record masih bisa di-GET (filter `deleted_at` lupa dipasang).
- IDOR: user A bisa membaca resource user B hanya dengan mengganti ID.
- Inkonsistensi `403` vs `404` antar endpoint sehingga keberadaan resource bocor.
- ID terlalu panjang menyebabkan error database (bukan validasi di layer API).
- Nested route tidak memverifikasi kepemilikan child terhadap parent (child dari parent lain ikut tampil).
- Response mengembalikan objek parsial (field wajib hilang) untuk data lama.
- ID `0` atau leading zero diperlakukan sebagai ID lain.

## Security Considerations
- **BOLA/IDOR** (OWASP API Security API1): otorisasi level objek wajib dicek per resource, bukan hanya per endpoint.
- Enumerasi ID: bila ID mudah ditebak, pastikan respons tidak membedakan "ada tapi tidak berhak" vs "tidak ada".
- Jangan kirim field sensitif yang tidak dibutuhkan halaman detail.
- ID sebaiknya opaque (UUID) bila enumerasi menjadi risiko.

## References
- OpenAPI Specification — path parameter, response `200`/`404`.
- Google AIP-131 (Get) — semantik standard method Get.
- OWASP Web Security Testing Guide — WSTG-ATHZ (authorization), IDOR.
- OWASP API Security Top 10 — API1 Broken Object Level Authorization.
