# Data Integrity Testing

## Overview
Menguji **integrity constraints** database: NOT NULL, UNIQUE, CHECK, FOREIGN KEY, default value, dan tipe data. Risiko utama: data invalid masuk ke sistem, constraint tidak ditegakkan, dan inkonsistensi nilai antar kolom/baris.

## When to Apply
Setiap kali data ditulis ke database (create/update/import/migration) dan setiap verifikasi skema. Aplikasikan bersama `data-crud`, `data-relationship`, `data-duplicate`.

## Testing Principles
1. Constraint di database adalah **lapisan pertahanan terakhir** — harus ditegakkan di level DB, bukan hanya aplikasi.
2. Uji constraint **positif** (data valid diterima) dan **negatif** (data invalid ditolak).
3. Null vs empty string vs default punya semantik berbeda — bedakan.
4. Verifikasi constraint tetap berlaku setelah migrasi/backfill.

## Test Design Techniques
- Equivalence Partitioning — nilai yang memenuhi vs melanggar constraint.
- Boundary Value Analysis — batas constraint (panjang, range).
- Decision Table — kombinasi constraint pada satu record.

## Test Scenarios

### Positive Testing
- Field NOT NULL diisi → tersimpan.
- Field UNIQUE dengan nilai unik → tersimpan.
- Nilai memenuhi CHECK constraint → tersimpan.
- Default value terisi saat kolom dikosongkan.

### Negative Testing
- Field NOT NULL diisi null → ditolak.
- Field UNIQUE dengan nilai duplikat → ditolak.
- Nilai melanggar CHECK constraint → ditolak.
- Tipe data salah (string ke kolom integer) → ditolak/dikonversi sesuai kontrak.

### Boundary Testing
- Panjang string tepat di batas kolom → diterima.
- Panjang melebihi batas kolom → ditolak.
- Nilai numerik tepat batas range → diterima/ditolak sesuai CHECK.

### Integration Testing
- Constraint + foreign key (delegasi `data-relationship`).
- Constraint + unique (delegasi `data-duplicate`).
- Constraint setelah migrasi/backfill (delegasi `data-migration`).

## Test Data
- Nilai valid pada batas constraint.
- Nilai yang melanggar tiap jenis constraint.
- Data null vs empty string vs whitespace.

## Expected Results
- Data valid tersimpan, data invalid ditolak dengan error jelas.
- Constraint ditegakkan konsisten di semua jalur tulis (API, import, batch).
- Tidak ada record dengan nilai di luar batas constraint.

## Common Defects
- Constraint hanya dicek di aplikasi, DB bisa diisi langsung.
- Null vs empty string tidak dibedakan.
- Default value salah/tidak terpasang.
- CHECK constraint terlalu longgar/terlalu ketat.
- Constraint hilang/berubah setelah migrasi.

## Security Considerations
- Data invalid bisa jadi vektor injection/business logic bypass.
- Jangan andalkan validasi aplikasi saja untuk integritas data.

## References
- ISTQB CTFL v4.0.1
- Database integrity constraints (NOT NULL, UNIQUE, CHECK, FOREIGN KEY, DEFAULT)
