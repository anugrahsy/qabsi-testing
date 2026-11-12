# Input Identifier Validation Testing

## Overview
Menguji validasi identifier (ID): UUID, numeric ID, format, dan keberadaan resource. Risiko utama: format salah diterima, ID invalid menyebabkan 500 (bukan 4xx), dan ID milik resource lain bisa diakses (IDOR).

## When to Apply
Path/query parameter ID, field referensi (FK), atau identifier di body request.

## Testing Principles
1. Tentukan **jenis identifier** eksplisit: UUID (versi?), numeric (auto-increment), atau custom format.
2. Validasi **format** dulu (sintaks), lalu **keberadaan** (resource ada/tidak) — dua lapis berbeda.
3. Format invalid → 4xx (bukan 500); format valid tapi resource tidak ada → 404.
4. Bedakan identifier internal (integer) vs publik (UUID) — expose yang aman saja.
5. Validasi format tidak menggantikan otorisasi akses resource (delegasi `auth-object-access`).

## Test Design Techniques
- Equivalence Partitioning — kelas format valid/invalid; kelas UUID/numeric.
- Boundary Value Analysis — batas numeric (0, negatif, sangat besar, max int).
- State Transition — resource dibuat → dihapus → diakses (existence).

## Test Scenarios

### Positive Testing
- UUID format valid → diproses (ditemukan/tidak sesuai keberadaan).
- Numeric ID positif valid → diproses.
- Identifier dengan format custom sesuai kontrak → diproses.

### Negative Testing
- UUID format salah (panjang/karakter salah) → ditolak (4xx).
- Numeric ID non-numerik (`abc`) → ditolak.
- Numeric ID negatif/0 (jika invalid) → ditolak.
- Identifier kosong/null → ditolak.
- Format valid tapi resource tidak ada → 404 (bukan 500).

### Boundary Testing
- Numeric ID: 0, 1, negatif, max int (2^31-1), melebihi (2^63) → ditangani.
- UUID: panjang 36 karakter vs salah, versi UUID berbeda, nil UUID.

### Integration Testing
- Identifier dipakai akses resource milik user lain → ditolak (IDOR; delegasi `auth-object-access`).
- Identifier referensi (FK) → resource terkait harus ada (integritas; delegasi `data-integrity`).
- Identifier setelah resource dihapus → 404 (bukan crash).

## Test Data
- UUID valid/invalid (format salah, versi lain, nil UUID).
- Numeric ID valid (1, besar), invalid (0, negatif, non-numerik, overflow).
- Identifier resource yang ada vs tidak ada.
- Identifier milik resource user lain (untuk uji IDOR).

## Expected Results
- Format valid diproses; invalid ditolak 4xx dengan pesan jelas.
- Format valid tapi resource tidak ada → 404 (bukan 500).
- Akses resource milik orang lain ditolak (otorisasi).
- Overflow/tipe salah ditangani tanpa crash.

## Common Defects
- Format invalid → 500 (bukan 4xx).
- ID tidak ada → 500/null pointer (bukan 404).
- IDOR: akses resource milik user lain lolos.
- Numeric overflow tidak ditangani.
- Identifier internal (auto-increment) diekspos → memudahkan enumeration.

## Security Considerations
- OWASP Broken Object Level Authorization / IDOR — otorisasi akses resource, bukan hanya validasi format.
- Jangan expose identifier internal yang memudahkan enumeration (pakai UUID untuk publik).
- Overflow/tipe salah jangan sampai crash (DoS).
- Identifier di URL/log — jangan bocorkan info sensitif.

## References
- OWASP Input Validation Cheat Sheet
- OWASP API Security Top 10 — BOLA/IDOR
- RFC 4122 (UUID)
