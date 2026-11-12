# Data Relationship Testing

## Overview
Menguji **relasi antar data**: foreign key, parent-child, cascade, dan orphan record. Risiko utama: referensi menunjuk data yang tak ada (orphan), cascade menghapus/mengubah data tak disengaja, dan data anak tanpa induk valid.

## When to Apply
Fitur yang melibatkan relasi database: master-detail, hierarki (parent-child), dan foreign key antar tabel. Aplikasikan bersama `data-crud` dan `data-integrity`.

## Testing Principles
1. Setiap foreign key harus menunjuk record induk yang **ada** (referential integrity).
2. Perilaku cascade (ON DELETE/ON UPDATE) harus **eksplisit** dan sesuai kebutuhan bisnis.
3. Orphan record (anak tanpa induk) harus dicegah atau ditangani.
4. Urutan operasi create/delete pada relasi penting (induk dulu baru anak; anak dulu baru induk saat hapus).

## Test Design Techniques
- State Transition — perubahan relasi antar state.
- Decision Table — kombinasi aksi (delete induk, update FK, dst).
- Equivalence Partitioning — referensi valid/invalid.

## Test Scenarios

### Positive Testing
- Create anak dengan FK valid → tersimpan.
- Read induk beserta anaknya → relasi benar.
- Update FK ke induk valid → berhasil.
- Delete anak → induk tetap ada.

### Negative Testing
- Create anak dengan FK menunjuk induk tak ada → ditolak.
- Update FK ke induk tak ada → ditolak.
- Delete induk yang masih punya anak → ditolak (RESTRICT) atau cascade sesuai kontrak.
- Set FK null tanpa izin → ditolak.

### Boundary Testing
- Induk dengan banyak anak (1:N besar) → konsisten.
- Hierarki dalam (parent-child bertingkat) → tidak ada siklus/loop.
- Siklus referensi (A→B→A) → ditolak/ditangani.

### Integration Testing
- Cascade delete induk → anak ikut terhapus (jika dirancang).
- Cascade update FK → anak ikut terupdate.
- Orphan record hasil migrasi (delegasi `data-migration`).

## Test Data
- Induk + anak valid (1:1, 1:N, N:M).
- FK menunjuk induk yang sudah dihapus.
- Hierarki bertingkat (3+ level).

## Expected Results
- Referential integrity terjaga: tidak ada FK menunjuk record tak ada.
- Perilaku cascade sesuai kontrak (delete/update menyebar benar).
- Tidak ada orphan record setelah operasi normal.

## Common Defects
- Cascade delete menghapus data yang seharusnya dipertahankan.
- RESTRICT tidak diterapkan → induk bisa dihapus padahal masih ada anak.
- Orphan record muncul karena delete tanpa cleanup.
- Relasi N:M tidak dimodelkan lewat tabel pivot dengan benar.

## Security Considerations
- Relasi bisa membocorkan data lintas entitas bila otorisasi tak mengecek ownership.
- Pastikan cascade tidak menghapus data milik user lain.

## References
- ISTQB CTFL v4.0.1
- Database integrity constraints (FOREIGN KEY, referential integrity, cascade)
