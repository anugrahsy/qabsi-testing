# API Get Collection Testing

## Overview
Menguji endpoint yang mengembalikan **kumpulan resource** (list/collection): tabel, dropdown, master data. Risiko utama: struktur response tidak konsisten, count salah, empty collection ditangani sebagai error, dan scoping data bocor.

## When to Apply
Endpoint `GET /...` yang response-nya array/list — bukan resource tunggal (`GET /.../{id}`). Contoh: daftar fakultas, tabel pegawai, dropdown jurusan.

## Testing Principles
1. Empty collection adalah **hasil valid** (200 + array kosong), bukan error.
2. Struktur tiap item dalam collection harus **identik** (field sama, tipe sama).
3. `count`/`total` harus konsisten dengan panjang `data`.
4. Collection harus **terscope** oleh otoritas/konteks request (header `X-Organization`, role, dst).

## Test Design Techniques
- Equivalence Partitioning — kelompok filter/value.
- Boundary Value Analysis — `limit`/`page` batas.
- Decision Table — kombinasi filter.
- Combinatorial — kombinasi parameter (delegasi ke `api-combination`).

## Test Scenarios

### Positive Testing
- Request tanpa parameter → mengembalikan collection default.
- Response body punya struktur konsisten (mis. `{count, data, param}`).
- Tiap item punya field sesuai kontrak (tipe & nama benar).
- Collection berisi data sesuai scope otoritas.

### Negative Testing
- Collection kosong → `200` + array kosong (bukan `404`/`500`).
- ID/path tidak valid → `400`/`404` sesuai kontrak.
- Parameter tak dikenal → diabaikan atau ditolak sesuai kontrak.

### Boundary Testing
- `limit` minimal (1) → maksimal 1 item.
- `limit` maksimal sesuai kontrak → jumlah sesuai batas.
- `limit` melebihi maksimum → ditolak/dikoreksi sesuai kontrak.
- `page` di luar jangkauan → empty result sesuai kontrak.

### Integration Testing
- Collection + filtering (delegasi `api-filtering`).
- Collection + pagination (delegasi `api-pagination`).
- Collection + sorting (delegasi `api-sorting`).
- Collection + search (delegasi `api-search`).

## Test Data
- Fixture dengan 0, 1, banyak record.
- Data lintas scope (untuk verifikasi scoping otoritas).
- Field bernilai `null` vs missing (untuk konsistensi).

## Expected Results
- HTTP `200` untuk collection valid (termasuk kosong).
- Struktur response sesuai kontrak.
- `count` == panjang `data` (atau `total` sesuai definisi kontrak).
- Tidak ada data di luar scope otoritas.

## Common Defects
- Empty collection → `404`/`500` (harusnya `200` + array kosong).
- `count`/`total` salah (tidak cocok data aktual).
- Field `null` vs missing tidak konsisten antar item.
- Data luar scope otoritas ikut ter-return.
- Pagination off-by-one (item terakhir hilang/duplikat).

## Security Considerations
- Otorisasi scoping: pastikan user tak melihat data di luar scope.
- Jangan expose field sensitif (id internal, dsb) kalau tak perlu.
- Rate limit / resource exhaustion kalau collection besar tanpa pagination.

## References
- OpenAPI Specification
- Google AIP-132 (List methods)
- Google AIP-158 (Pagination)
