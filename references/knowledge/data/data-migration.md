# Data Migration Testing

## Overview
Menguji **migrasi skema dan data**: perubahan struktur tabel, backfill, dan konversi data lama ke bentuk baru. Risiko utama: data hilang/rusak saat migrasi, migrasi tidak idempoten, dan aplikasi lama tidak kompatibel dengan skema baru.

## When to Apply
Setiap perubahan skema database, backfill data historis, atau migrasi antar versi/format. Aplikasikan bersama `data-integrity` dan `data-consistency`.

## Testing Principles
1. Migrasi harus **idempoten** — dijalankan ulang tidak merusak data.
2. **Rollback** harus tersedia dan teruji (up + down).
3. Verifikasi **data sebelum vs sesudah** migrasi (jumlah, nilai, relasi).
4. Migrasi besar harus aman di data nyata (backup + verifikasi).

## Test Design Techniques
- Equivalence Partitioning — data yang berubah vs tidak berubah.
- State Transition — skema/data sebelum vs sesudah migrasi.
- Combinatorial — kombinasi tipe data lama → baru.

## Test Scenarios

### Positive Testing
- Migrasi up → skema baru terbentuk benar.
- Data lama terkonversi ke format baru dengan nilai benar.
- Backfill kolom baru → terisi sesuai aturan.
- Migrasi dijalankan ulang → idempoten, tidak duplikat/rusak.

### Negative Testing
- Migrasi down/rollback → kembali ke skema lama dengan data utuh.
- Data yang tidak valid pada format lama → migrasi menangani (skip/error) tanpa crash.
- Migrasi gagal di tengah → tidak meninggalkan state setengah jadi.

### Boundary Testing
- Data dalam jumlah besar → migrasi selesai tanpa kehilangan record.
- Nilai null/empty pada kolom yang di-migrasi → tertangani.

### Integration Testing
- Migrasi + integrity constraint (delegasi `data-integrity`).
- Migrasi + relasi/orphan (delegasi `data-relationship`).
- Migrasi + konsistensi API (delegasi `data-consistency`).

## Test Data
- Snapshot database sebelum migrasi.
- Data lama dengan berbagai format/nilai (termasuk null/empty).
- Data dalam jumlah signifikan.

## Expected Results
- Skema dan data sesudah migrasi sesuai spesifikasi.
- Jumlah record sebelum vs sesudah konsisten.
- Migrasi idempoten dan dapat di-rollback.
- Tidak ada data hilang, korup, atau relasi putus.

## Common Defects
- Migrasi tidak idempoten → data duplikat saat dijalankan ulang.
- Rollback tidak diuji → gagal mengembalikan skema/data.
- Backfill mengisi nilai salah/overwrite data.
- Migrasi mengunci tabel lama (downtime) tanpa rencana.
- Data lama yang tidak valid dibiarkan crash migrasi.

## Security Considerations
- Data sensitif di kolom lama bisa bocor bila migrasi menyisakan kolom tak terpakai.
- Pastikan migrasi tidak menaikkan hak akses/ekspose data yang sebelumnya tersembunyi.

## References
- ISTQB CTFL v4.0.1
- Database schema/data migration best practices
