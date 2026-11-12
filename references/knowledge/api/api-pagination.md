# API Pagination Testing

## Overview
Menguji mekanisme **pagination** pada endpoint collection (`page`, `limit`, `offset`, `cursor`). Risiko utama: off-by-one, data duplikat/hilang antar halaman, dan parameter out-of-range tidak ditangani.

## When to Apply
Endpoint collection yang mendukung parameter pagination. Aplikasikan bersama `api-get-collection` dan `api-combination`.

## Testing Principles
1. Pagination harus **deterministik** — urutan stabil antar request.
2. Tidak boleh ada item **duplikat** atau **hilang** saat pindah halaman.
3. Parameter out-of-range harus ditangani sesuai kontrak (bukan crash/exception).
4. `limit` besar tak boleh menyebabkan resource exhaustion.

## Test Design Techniques
- Boundary Value Analysis — `page`/`limit` batas.
- Equivalence Partitioning — nilai valid/invalid.
- Combinatorial — pagination + filter + sort (lihat `api-combination`).

## Test Scenarios

### Positive Testing
- Page pertama → data halaman pertama.
- Page berikutnya → tidak mengulang data halaman sebelumnya.
- Page terakhir → jumlah data sesuai sisa record.
- Custom page size → jumlah sesuai `limit`.
- Cursor-based → `next_page`/`next_cursor` benar.

### Negative Testing
- Page = 0 → ditolak atau sesuai aturan validasi.
- Page negatif → ditolak/ditangani sesuai kontrak.
- Page di luar jangkauan → empty result sesuai kontrak.
- `limit` non-numerik → `400`/`422`.
- `limit` sangat besar → tidak menyebabkan resource exhaustion (dibatasi).

### Boundary Testing
- `limit` = 1 → maksimal 1 record.
- `limit` = batas maksimum → jumlah sesuai batas.
- `limit` = batas maksimum + 1 → ditolak/dikoreksi.
- `page` terakhir dengan sisa record → hanya sisa.

### Integration Testing
- Pagination + filtering: halaman kedua dari hasil yang sudah difilter.
- Pagination + sorting: urutan konsisten saat berpindah halaman.
- Pagination + search: hasil pencarian terpaginasi.
- Total `count`/`total` tetap konsisten lintas halaman.

## Test Data
- Fixture > 1 halaman (mis. 25 record, limit 10 → 3 halaman).
- Fixture yang difilter menyusut (untuk kombinasi).
- Record dengan nilai sort yang sama (urutan stabil).

## Expected Results
- Struktur response sesuai kontrak (`data`, `count`/`total`, `page`, `limit`, `next_page`).
- Tidak ada duplikat/hilang antar halaman.
- Urutan stabil antar request (dengan sort default eksplisit).
- `count`/`total` mencerminkan seluruh dataset (bukan per halaman), kecuali kontrak bilang lain.

## Common Defects
- Off-by-one: item terakhir halaman hilang.
- Item duplikat antar halaman.
- `total` = jumlah item per halaman, bukan seluruh dataset.
- `limit` besar tak dibatasi → resource exhaustion.
- `page`/`limit` invalid menyebabkan `500`.
- Urutan berubah saat pindah halaman (tanpa default sort).

## Security Considerations
- `limit` sangat besar → DoS/resource exhaustion (wajib ada batas maksimum).
- Cursor/token pagination bocor data lintas user.

## References
- Google AIP-158 (Pagination)
- OpenAPI Specification
