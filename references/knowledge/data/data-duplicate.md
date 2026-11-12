# Data Duplicate Testing

## Overview
Menguji **unique constraints** dan pencegahan data duplikat. Risiko utama: record duplikat masuk, unique constraint tidak mencakup kombinasi field yang benar, dan race condition menghasilkan duplikat.

## When to Apply
Setiap field/kombinasi field yang harus unik: email, username, kode, NIK, dan identitas bisnis lain. Aplikasikan bersama `data-integrity` dan `data-concurrency`.

## Testing Principles
1. Unique constraint harus ada di **level database**, bukan hanya validasi aplikasi.
2. Tentukan **cakupan uniqueness** (case-sensitive? termasuk soft-deleted? per scope?).
3. Duplikat harus ditolak dengan error jelas, bukan diam-diam overwrite.
4. Uji uniqueness terhadap **concurrent write** (race condition).

## Test Design Techniques
- Equivalence Partitioning — nilai unik vs duplikat.
- Boundary Value Analysis — nilai mirip (case, whitespace, trailing space).
- Decision Table — kombinasi field pembentuk unique.

## Test Scenarios

### Positive Testing
- Nilai unik → tersimpan.
- Nilai sama di scope berbeda (jika unik per scope) → keduanya tersimpan.
- Nilai yang pernah dihapus (soft-delete) → bisa dipakai ulang sesuai kontrak.

### Negative Testing
- Nilai duplikat persis → ditolak.
- Nilai beda case (jika case-insensitive unik) → ditolak.
- Nilai dengan trailing/leading space → ditolak/dinormalisasi sesuai kontrak.
- Duplikat pada kombinasi field (mis. kode + periode) → ditolak.

### Boundary Testing
- Nilai tepat di batas panjang unique field → tersimpan unik.
- Dua nilai yang sama setelah normalisasi (trim, lowercase) → ditolak.

### Integration Testing
- Duplicate + concurrent create (delegasi `data-concurrency`).
- Duplicate + soft delete (delegasi `data-soft-delete`).
- Duplicate + import/batch (duplikat dalam satu batch).

## Test Data
- Nilai unik dan duplikatnya.
- Variasi case, whitespace, dan karakter mirip.
- Data yang sama di scope berbeda.

## Expected Results
- Duplikat ditolak dengan error jelas (mis. 409/422).
- Tidak ada record duplikat di database.
- Normalisasi (jika ada) diterapkan sebelum pengecekan uniqueness.

## Common Defects
- Unique constraint hanya di aplikasi → duplikat bisa masuk lewat import/DB langsung.
- Cakupan uniqueness salah (harusnya kombinasi field, tapi hanya satu field).
- Race condition menghasilkan duplikat saat dua create bersamaan.
- Soft-deleted record menghalangi create nilai sama tanpa kebijakan jelas.

## Security Considerations
- Duplikat bisa dipakai untuk enumerasi (perbedaan error "sudah ada" vs "tidak ditemukan").
- Pastikan pengecekan uniqueness tidak membocorkan keberadaan record milik user lain.

## References
- ISTQB CTFL v4.0.1
- Database integrity constraints (UNIQUE, composite unique)
