# Input Currency Validation Testing

## Overview
Menguji validasi input nilai mata uang: presisi desimal, kode currency, dan rounding. Risiko utama: presisi salah (float vs decimal), pembulatan tidak konsisten, kode currency tidak valid, dan nilai negatif/overflow tidak ditangani.

## When to Apply
Field nominal/uang: harga, gaji, anggaran, jumlah pembayaran. Aplikasikan bersama `input-number` untuk range & tipe dasar.

## Testing Principles
1. Gunakan **decimal atau integer (satuan cent)**, bukan float, untuk uang — hindari error float (0.1 + 0.2 ≠ 0.3).
2. Tentukan **presisi desimal** per currency (mis. IDR 2 digit, JPY 0 digit).
3. Tentukan **kode currency** valid (ISO 4217) jika payload menyertakan currency.
4. Tentukan aturan **pembulatan** (round half up/down, truncate) & kapan diterapkan.
5. Batas nilai: apakah negatif diizinkan? maksimum berapa? (cek overflow).

## Test Design Techniques
- Equivalence Partitioning — kelas nilai valid/invalid, kelas currency code.
- Boundary Value Analysis — nilai min/max, batas presisi desimal.
- Decision Table — kombinasi nilai × currency × presisi.

## Test Scenarios

### Positive Testing
- Nilai desimal dengan presisi sesuai currency → diterima.
- Nilai bulat tanpa desimal → diterima.
- Nilai dengan kode currency valid (IDR, USD) → diterima.
- Nol → diterima (jika valid).

### Negative Testing
- Lebih banyak digit desimal dari presisi → ditolak/dibulatkan sesuai kontrak.
- Nilai non-numerik → ditolak.
- Kode currency tidak valid (`ABC`) → ditolak.
- Negatif saat tidak diizinkan → ditolak.
- Nilai melebihi maksimum → ditolak (overflow).

### Boundary Testing
- Nilai min/max & sekitarnya.
- Presisi desimal tepat di batas (2 digit vs 3 digit).
- Nilai terbesar yang bisa ditampung (long/double) → overflow ditangani.
- Nilai `0` vs `0.00` vs `0.004`.

### Integration Testing
- Pembulatan konsisten antara input, kalkulasi, dan penyimpanan (delegasi `business-calculation`).
- Nilai disimpan sebagai decimal/cent → dibaca kembali tanpa drift.
- Konversi antar currency (jika ada) → rate & pembulatan konsisten.

## Test Data
- Nilai dengan presisi bervariasi (0, 0.5, 0.10, 0.999, 1234.567).
- Nilai batas min/max, negatif, nol.
- Kode currency valid/invalid (ISO 4217).
- Nilai yang memicu error float (0.1 + 0.2, 1.005).

## Expected Results
- Nilai valid (presisi & currency) diterima; invalid ditolak dengan pesan jelas.
- Presisi desimal & pembulatan konsisten sesuai kontrak.
- Tidak ada error float (disimpan sebagai decimal/cent).
- Overflow/negatif ditangani sesuai kontrak.

## Common Defects
- Uang disimpan sebagai float → pembulatan salah (0.1 + 0.2).
- Presisi desimal tidak konsisten antar currency.
- Aturan pembulatan tidak ditentukan (round vs truncate) → hasil beda antar jalur.
- Kode currency tidak divalidasi.
- Overflow nilai besar tidak ditangani.

## Security Considerations
- OWASP Input Validation Cheat Sheet — format strict, gunakan decimal/cent.
- Float error bisa menjadi logic bug finansial → wajib decimal.
- Nilai besar/negatif → manipulasi finansial; validasi range ketat.

## References
- ISO 4217 (Currency codes)
- OWASP Input Validation Cheat Sheet
- IEEE 754 (floating-point) — alasan menghindari float untuk uang
