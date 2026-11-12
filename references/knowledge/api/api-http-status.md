# API HTTP Status Testing

## Overview
Menguji ketepatan **status code HTTP** untuk setiap hasil operasi — sukses, gagal validasi, gagal autentikasi, konflik, dan error server. Risiko utama: `4xx` dilaporkan sebagai `500`, error validasi dilaporkan `200`, atau kode yang dipakai tidak membedakan penyebab sehingga client tidak bisa bereaksi benar (retry, login ulang, tampilkan pesan field).

## When to Apply
Setiap endpoint, sebagai lapisan lintas-modul. Dipakai untuk menilai hasil dari modul `api-*` lain: satu skenario di modul mana pun tetap harus diverifikasi kode statusnya. Modul ini tidak menggantikan pengujian body error (lihat `api-error-handling`).

## Testing Principles
1. **Kode status adalah bagian dari kontrak.** Setiap hasil harus punya kode yang didokumentasikan, bukan kode "kebetulan".
2. **4xx = kesalahan client, 5xx = kesalahan server.** Validasi yang gagal tidak boleh menghasilkan `500`.
3. **Kode harus spesifik**: `401` ≠ `403` ≠ `404`; `400` ≠ `422`; `409` ≠ `422`.
4. **Kode harus konsisten lintas endpoint** untuk kondisi yang sama.
5. **Body mengikuti kode**: `204` tanpa body, `201` dengan `Location`, `3xx` dengan `Location`.

## Test Design Techniques
- **Equivalence Partitioning** — kelompok hasil: sukses, validasi, authn, authz, not found, konflik, server error.
- **Decision Table** — kombinasi kondisi input × status resource × kredensial → kode yang diharapkan.
- **Boundary Value Analysis** — ukuran payload (`413`), jumlah request (`429`), panjang header (`431`).
- **State Transition** — kode pada percobaan pertama vs pengulangan.

## Test Scenarios

### Positive Testing
- GET berhasil → `200`.
- POST membuat resource → `201` + `Location`.
- POST menerima proses asinkron → `202` + referensi status.
- DELETE/aksi tanpa body → `204`.
- HEAD → `200` dengan header sama seperti GET, tanpa body.
- `304 Not Modified` untuk conditional GET yang tidak berubah.

### Negative Testing
- Validasi field gagal → `400` atau `422` (pilih satu sesuai kontrak), bukan `500`.
- Kredensial tidak ada/invalid/kedaluwarsa → `401` + `WWW-Authenticate`.
- Terautentikasi tetapi tidak berwenang → `403`.
- Resource tidak ada → `404`.
- Method tidak didukung pada path tersebut → `405` + header `Allow`.
- `Content-Type` tidak didukung → `415`.
- Bentrok versi/duplikat → `409` (atau `412` untuk precondition).
- Terlalu banyak request → `429` + `Retry-After`.
- Payload terlalu besar → `413`.
- Exception tak tertangani → `500` dengan body generik, tanpa stack trace.
- Dependency eksternal gagal/timeout → `502`/`503`/`504`, bukan `500` generik.

### Boundary Testing
- `204` dipastikan **tidak** memiliki body (termasuk newline/whitespace).
- `201` dipastikan memiliki `Location` yang valid dan dapat diakses.
- `401` dipastikan menyertakan `WWW-Authenticate`.
- `405` dipastikan menyertakan `Allow` dengan method yang benar.
- `429` dipastikan menyertakan `Retry-After` numerik/datetime.
- `3xx` dipastikan menyertakan `Location` dan bukan loop redirect.

### Integration Testing
- Kode dari aplikasi konsisten dengan kode dari gateway/proxy (gateway tidak menimpa `4xx` menjadi `502`).
- Kode status sama untuk kondisi sama di seluruh endpoint (mis. validasi selalu `422`).
- Error pada proses turunan dipetakan ke kode yang sesuai, bukan selalu `500`.
- Client dapat membedakan skenario retry (`429`, `503`, `504`) dari skenario permanen (`400`, `422`).
- Body error mengikuti kode (lihat `api-error-handling`).

## Test Data
- Request valid, request dengan satu field invalid, request tanpa token.
- Token valid milik user tanpa izin; token kedaluwarsa; token rusak.
- ID tidak ada; ID valid; ID pada resource terhapus.
- Payload melebihi batas ukuran; request melebihi batas rate.
- Dependency eksternal yang disimulasikan down/timeout (lihat `api-integration`).

## Expected Results
- Setiap hasil memakai kode yang terdaftar di kontrak endpoint.
- `4xx` hanya untuk kesalahan yang bisa diperbaiki client; `5xx` hanya untuk kegagalan server.
- `401` + `WWW-Authenticate`; `403` tanpa header itu; `404` untuk tidak ada.
- `405` + `Allow`; `429` + `Retry-After`; `413` saat melebihi batas ukuran.
- `201` + `Location`; `204` benar-benar tanpa body.
- Body `5xx` tidak memuat stack trace, query SQL, nama host internal, atau versi library.
- Kode status tidak berubah-ubah untuk kondisi yang sama pada pengujian berulang.

## Common Defects
- Mengembalikan `200` dengan body `{success: false}` untuk kegagalan.
- Validasi input menghasilkan `500` karena exception tidak dipetakan.
- `401` dipakai untuk user yang sudah login tetapi tidak berhak (harusnya `403`).
- `404` dipakai untuk input invalid sehingga client tidak tahu field mana yang salah.
- `201` tanpa `Location`, atau `Location` menunjuk URL yang tidak dapat diakses.
- `204` tetap mengirim body JSON.
- Duplikat menghasilkan `500` (unique constraint bocor).
- Semua error dependency dipetakan ke `500`, menghilangkan sinyal retry.
- Gateway mengubah `401` aplikasi menjadi `502`.

## Security Considerations
- Perbedaan `403` vs `404` dapat membocorkan keberadaan resource; tetapkan kebijakan konsisten.
- `5xx` yang verbose membocorkan stack trace, path, dan versi.
- `429`/`401` yang terlalu informatif memudahkan enumerasi akun.
- Pastikan kode tidak mengungkap mekanisme internal (mis. `500` khusus untuk "DB down").

## References
- RFC 9110 — HTTP Semantics, definisi status code dan semantiknya.
- OpenAPI Specification — responses per status code.
- OWASP Web Security Testing Guide — WSTG-ERRH (improper error handling), WSTG-INFO.
- ISTQB CTFL v4.0.1 — equivalence partitioning, decision table.
