# API Filtering Testing

## Overview
Menguji parameter **filter** pada endpoint collection. Risiko utama: filter sebagian diterapkan, kombinasi filter salah logika (AND/OR), dan nilai invalid tak ditangani.

## When to Apply
Endpoint collection yang menerima parameter filter (mis. `status`, `kd_fakultas`, `tanggal`). Aplikasikan bersama `api-get-collection`, `api-pagination`, `api-combination`.

## Testing Principles
1. Filter harus diterapkan **konsisten** (semua record memenuhi kondisi).
2. Kombinasi multi-filter defaultnya **AND** (kecuali kontrak bilang lain).
3. Nilai filter tak tersedia → **empty result** (bukan error).
4. Case sensitivity harus konsisten dengan spesifikasi.

## Test Design Techniques
- Equivalence Partitioning — nilai filter valid/invalid.
- Decision Table — kombinasi beberapa kondisi filter.
- Combinatorial — banyak filter sekaligus (lihat `api-combination`).

## Test Scenarios

### Positive Testing
- Filter 1 field (exact) → hanya record yang cocok.
- Filter partial (contains) → record yang mengandung substring.
- Filter range (number/date) → record dalam rentang.
- Filter enum/dropdown → hanya nilai yang diperbolehkan.
- Filter beberapa parameter → semua kondisi diterapkan (AND).

### Negative Testing
- Filter nilai tidak tersedia → empty result.
- Filter nilai invalid (tipe salah) → error sesuai kontrak.
- Filter field tak dikenal → ditolak atau diabaikan sesuai kontrak.
- Filter dengan karakter spesial → tidak error/break.

### Boundary Testing
- Filter `null`/kosong → mengikuti definisi API (diabaikan atau default).
- Filter range batas bawah/atas → inclusive/exclusive sesuai kontrak.
- Filter case: `"active"` vs `"ACTIVE"` → konsisten dengan spesifikasi.

### Integration Testing
- Filter + pagination → pagination atas hasil terfilter.
- Filter + sorting → sort hanya pada hasil terfilter.
- Filter + search → keduanya diterapkan.

## Test Data
- Data dengan beberapa nilai status/kategori berbeda.
- Data di batas range (min/max).
- Data duplikat nilai (untuk verifikasi semua cocok).

## Expected Results
- Hanya record yang memenuhi filter ter-return.
- Kombinasi filter = AND (semua kondisi terpenuhi).
- Empty result untuk nilai tak tersedia.
- Error konsisten untuk nilai invalid.

## Common Defects
- Filter OR vs AND tertukar.
- Filter diabaikan diam-diam saat kombinasi.
- Case sensitivity tidak konsisten.
- Filter field tak dikenal → `500`.
- Range date/timezone salah (batas hari).

## Security Considerations
- Filter bisa dipakai enumerasi data → pastikan scope otoritas tetap.
- Parameter filter jadi vektor injection (SQLi) → parameterized query.
- Filter field sensitif (id user lain) → cek authorization.

## References
- Google AIP-132 (Filtering)
- OWASP WSTG (Input Validation)
