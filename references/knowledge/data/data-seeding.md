# Data Seeding Testing

## Overview
Menguji **seeding data** — pembuatan data awal (master data, default, test fixtures) yang dipakai aplikasi. Risiko utama: seed tidak idempoten (duplikat saat dijalankan ulang), data default hilang/salah, dan fixture test tidak mencerminkan data nyata.

## When to Apply
Setiap kali ada seed data (database seeder, fixture test, data referensi default) yang harus tersedia sebelum aplikasi berjalan atau sebelum test dijalankan.

## Testing Principles
1. Seed harus **idempoten** — dijalankan ulang tidak menduplikasi.
2. Data default/referensi harus **lengkap dan benar** sebelum fitur bergantung padanya.
3. Fixture test harus **representatif** — mencakup kasus valid, invalid, dan boundary.
4. Pisahkan seed produksi vs fixture test (jangan campur data nyata).

## Test Design Techniques
- Equivalence Partitioning — jenis data yang di-seed.
- Decision Table — kombinasi kondisi seed (fresh vs existing).
- Boundary Value Analysis — seed pada DB kosong vs berisi sebagian.

## Test Scenarios

### Positive Testing
- Seed pada DB kosong → semua data awal terbentuk benar.
- Seed dijalankan ulang → idempoten, tidak duplikat.
- Data default tersedia sebelum fitur dependen dipakai.
- Fixture test menyediakan data untuk skenario valid/invalid/boundary.

### Negative Testing
- Seed dengan referensi ke data yang belum ada → gagal jelas, tidak parsial.
- Seed dijalankan saat data sudah ada sebagian → tidak menimpa data yang tak seharusnya.
- Fixture tidak mengandung data yang melanggar constraint.

### Boundary Testing
- Seed dalam jumlah besar → selesai tanpa error.
- Seed nilai pada batas constraint → valid.

### Integration Testing
- Seed + integrity/unique (delegasi `data-integrity`, `data-duplicate`).
- Seed + relasi (delegasi `data-relationship`).
- Seed sebagai prerequisite test case lain.

## Test Data
- DB kosong vs berisi sebagian.
- Data referensi default (master data).
- Fixture untuk kasus valid, invalid, boundary.

## Expected Results
- Data awal lengkap dan benar setelah seed.
- Seed idempoten (tidak duplikat saat diulang).
- Fixture test stabil dan deterministik antar run.
- Tidak ada seed produksi yang bocor ke environment test (dan sebaliknya).

## Common Defects
- Seed tidak idempoten → duplikat saat dijalankan ulang.
- Data default hilang/salah → fitur dependen gagal.
- Fixture tidak deterministik → test flaky.
- Seed produksi vs test tercampur.
- Seed bergantung urutan yang tidak dijamin.

## Security Considerations
- Seed produksi bisa mengandung data sensitif/credential — jangan expose.
- Pastikan seed tidak membuat akun default dengan password lemah/terkenal.

## References
- ISTQB CTFL v4.0.1
- Test fixture & test data management best practices
