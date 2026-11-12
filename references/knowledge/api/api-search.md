# API Search Testing

## Overview
Menguji parameter **search** (keyword) pada endpoint collection. Risiko utama: partial vs exact match salah, case sensitivity tidak konsisten, dan whitespace/special char merusak query.

## When to Apply
Endpoint collection yang mendukung pencarian keyword. Aplikasikan bersama `api-get-collection`, `api-filtering`, `api-combination`.

## Testing Principles
1. Definisikan kontrak search: **exact** atau **partial (contains)**.
2. Keyword kosong → kembalikan seluruh data (bukan error).
3. Case sensitivity harus konsisten dengan spesifikasi.
4. Whitespace leading/trailing harus dinormalisasi (atau sengaja dipertahankan).

## Test Design Techniques
- Equivalence Partitioning — keyword cocok/tidak.
- Boundary — keyword kosong, sangat panjang.
- Combinatorial — search + filter (lihat `api-combination`).

## Test Scenarios

### Positive Testing
- Exact match → record yang persis cocok.
- Partial match → record yang mengandung substring.
- Case-insensitive → `"Anugrah"` == `"anugrah"` (sesuai spesifikasi).
- Keyword dengan spasi → hasil sesuai.

### Negative Testing
- Keyword tidak ditemukan → empty result.
- Keyword kosong → seluruh data (bukan error).
- Keyword special character (`%`, `_`, `'`, `"`) → tidak break/error.
- Keyword sangat panjang → ditangani aman (bukan crash).

### Boundary Testing
- Leading/trailing whitespace → dinormalisasi.
- Keyword 1 karakter vs batas maksimum panjang.
- Unicode/emoji → sesuai dukungan.

### Integration Testing
- Search + filter → keduanya diterapkan.
- Search + pagination → hasil pencarian terpaginasi.
- Search + sort → sort hasil pencarian.

## Test Data
- Data dengan substring overlapping (mis. "ana" cocok di banyak record).
- Data case berbeda.
- Data dengan special char.
- Keyword tanpa hasil.

## Expected Results
- Hasil sesuai kontrak (exact/partial).
- Empty result untuk keyword tak ditemukan.
- Keyword kosong = seluruh data.
- Case sensitivity konsisten.

## Common Defects
- Search jadi exact saat seharusnya partial (atau sebaliknya).
- Keyword kosong → `400`/`500` (harusnya return semua).
- Special char (`%`/`_`) jadi wildcard SQL tak sengaja.
- Whitespace tak dinormalisasi → hasil tak konsisten.
- Search lintas field tak jelas (field mana yang dicari).

## Security Considerations
- Search = vektor SQLi/LIKE injection → parameterized query.
- Search bisa dipakai enumerasi data → batasi scope otoritas.
- Wildcard tak terkontrol → resource exhaustion (query lambat).

## References
- OWASP WSTG (Input Validation, SQL Injection)
- Google AIP-132 (Filtering/search conventions)
