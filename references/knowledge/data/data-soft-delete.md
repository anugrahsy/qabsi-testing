# Data Soft Delete Testing

## Overview
Menguji **soft delete** — penghapusan logis yang menandai record sebagai terhapus tanpa menghapus fisik. Risiko utama: record terhapus masih muncul di list/detail, referensi ke record terhapus rusak, dan restore/undelete tidak memulihkan relasi.

## When to Apply
Fitur hapus yang memakai flag deleted (mis. `deleted_at`, `is_deleted`) untuk menyimpan history atau mencegah kehilangan data permanen.

## Testing Principles
1. Soft delete = record **tidak tampil** di query normal (list/detail), tapi tetap ada di database.
2. Field penanda (timestamp/flag) harus **konsisten** dipakai semua jalur query.
3. **Restore** (undelete) harus memulihkan record beserta relasinya.
4. Uniqueness terhadap record soft-deleted tetap berlaku atau tidak, harus diputuskan oleh kontrak.

## Test Design Techniques
- State Transition — aktif → terhapus → ter-restore.
- Equivalence Partitioning — query yang menyaring vs tidak menyaring deleted.
- Decision Table — kombinasi status record + akses.

## Test Scenarios

### Positive Testing
- Soft delete record → record hilang dari list/detail normal.
- Record soft-deleted masih ada di database (flag terpasang benar).
- Restore record → record muncul kembali dengan data lengkap.
- Query yang eksplisit menyertakan deleted → record terhapus terlihat.

### Negative Testing
- Hard delete vs soft delete tercampur → tidak ada yang terhapus fisik saat seharusnya soft.
- Record soft-deleted dipakai referensi baru → ditolak/ditangani.
- Soft delete record yang sudah terhapus → idempoten/ditolak sesuai kontrak.
- Akses record soft-deleted lewat ID langsung → dikembalikan 404 (bukan data bocor).

### Boundary Testing
- Soft delete banyak record sekaligus → semua tersaring benar.
- Record dengan relasi anak saat induk di-soft-delete → perilaku cascade/restrict jelas.

### Integration Testing
- Soft delete + list/collection (delegasi `api-get-collection`).
- Soft delete + unique constraint (delegasi `data-duplicate`).
- Soft delete + relasi (delegasi `data-relationship`).

## Test Data
- Record aktif dan soft-deleted.
- Record dengan relasi ke record terhapus.
- Data yang dihapus lalu di-restore.

## Expected Results
- Record soft-deleted tidak muncul di hasil normal.
- Flag deleted terpasang dengan timestamp/aktor benar.
- Restore memulihkan record dan relasi.
- Tidak ada data bocor lewat query yang menyertakan deleted tanpa otorisasi.

## Common Defects
- Query list lupa menyaring deleted → record terhapus muncul.
- Soft delete tidak menyimpan timestamp/aktor.
- Unique constraint menghalangi create baru dengan nilai sama.
- Restore tidak memulihkan relasi anak.
- Detail record soft-deleted masih bisa diakses langsung.

## Security Considerations
- Record soft-deleted masih bisa mengandung data sensitif — akses harus dibatasi.
- Pastikan user tak bisa restore record di luar scope/otoritasnya.

## References
- ISTQB CTFL v4.0.1
- Database integrity constraints (UNIQUE, FOREIGN KEY)
