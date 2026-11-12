# Data CRUD Testing

## Overview
Menguji operasi **persistence dasar** (Create, Read, Update, Delete) pada lapisan data. Risiko utama: data tidak tersimpan/terbaca benar, update menimpa field tak dimaksud, delete menghapus lebih dari yang seharusnya, dan state database tidak sesuai setelah tiap operasi.

## When to Apply
Setiap fitur yang menyimpan, membaca, mengubah, atau menghapus record di database — lewat API, batch job, atau proses internal. Aplikasikan sebagai dasar sebelum modul data lain (integrity, transaction, concurrency).

## Testing Principles
1. Verifikasi **state database** — bukan hanya response API/UI, tapi nilai aktual tersimpan benar.
2. Setiap operasi harus **tidak merusak** state bila diulang (idempotensi) kecuali kontrak bilang lain.
3. CRUD harus mematuhi **constraint** yang ada (delegasi ke `data-integrity`).
4. Read harus mencerminkan data yang baru saja di-Create/Update (perhitungkan eventual consistency bila ada).

## Test Design Techniques
- Equivalence Partitioning — kelompok input valid/invalid per field.
- Boundary Value Analysis — panjang/besar nilai batas.
- State Transition — perubahan state record antar operasi CRUD.
- Decision Table — kombinasi field wajib/opsional.

## Test Scenarios

### Positive Testing
- Create record valid → tersimpan lengkap, field sesuai input, ID/auto-generated benar.
- Read record yang ada → mengembalikan nilai tersimpan persis.
- Update record → hanya field yang dimaksud berubah, field lain tetap.
- Delete record → record benar-benar hilang dari database.

### Negative Testing
- Create dengan field wajib hilang → ditolak, tidak ada record parsial.
- Read ID tidak ada → hasil "not found" konsisten.
- Update ID tidak ada → gagal sesuai kontrak, tidak membuat record baru.
- Delete ID tidak ada → gagal sesuai kontrak (atau idempoten sukses).
- Update/delete record milik user lain → ditolak (otorisasi).

### Boundary Testing
- Field string panjang maksimum → tersimpan penuh.
- Field string melebihi maksimum → ditolak.
- Numerik pada nilai min/max → tersimpan tepat.
- Record dalam jumlah banyak → semua operasi konsisten.

### Integration Testing
- Create → Read (verifikasi nilai balik).
- Create → Update → Read (verifikasi hanya field target berubah).
- Create → Delete → Read (verifikasi record hilang).
- CRUD melalui API vs DB langsung (delegasi `data-consistency`).

## Test Data
- Record minimal valid (semua field wajib).
- Record dengan semua field opsional terisi.
- Data yang melewati batas panjang/nilai.
- ID valid dan tidak valid.

## Expected Results
- Record tersimpan dengan nilai field persis sesuai input.
- Update hanya mengubah field target.
- Delete menghapus tepat satu record target (tidak lebih).
- Operasi gagal tidak meninggalkan state parsial.

## Common Defects
- Update menimpa field yang tidak dikirim (kehilangan data).
- Delete menghapus record terkait (cascade tak disengaja).
- Create sukses tapi response vs DB berbeda.
- Auto-increment/ID duplikat atau lompat.
- Record parsial tertinggal saat operasi gagal.

## Security Considerations
- Otorisasi tiap operasi: user tak boleh CRUD data di luar scope.
- Jangan return field sensitif yang tak perlu pada Read.
- Log/audit perubahan data (delegasi `business-audit`).

## References
- ISTQB CTFL v4.0.1
- Database integrity constraints (UNIQUE, NOT NULL, FOREIGN KEY)
