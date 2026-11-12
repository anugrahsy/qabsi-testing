# Business Calculation Testing

## Overview
Menguji **perhitungan bisnis**: formula, pembulatan (rounding), akumulasi total, dan konversi satuan. Risiko utama: pembulatan tidak konsisten antar lapisan, akumulasi galat (rounding error menumpuk), presisi desimal hilang, dan urutan operasi berbeda menghasilkan hasil berbeda.

## When to Apply
Fitur yang menghitung nilai: total harga/diskon/pajak, rata-rata, skor/penilaian, konversi (jam ke menit, satuan ke unit), dan formula yang hasilnya dipakai untuk keputusan bisnis. Aplikasikan bersama `input-number`, `input-currency`.

## Testing Principles
1. Rumus adalah **kontrak eksplisit** — verifikasi hasil terhadap contoh perhitungan manual, bukan sekadar "angka terlihat masuk akal".
2. **Presisi dan pembulatan harus didefinisikan** (berapa desimal, mode pembulatan) dan konsisten di UI, API, dan penyimpanan.
3. **Urutan operasi memengaruhi hasil** — uji pembulatan per item vs pembulatan di akhir.
4. Uji **akumulasi galat** pada perhitungan berulang/banyak baris.
5. Nilai ekstrem (sangat besar/sangat kecil) harus ditangani tanpa overflow/underflow.
6. Divisi oleh nol dan nilai `null` harus ditangani eksplisit.

## Test Design Techniques
- Equivalence Partitioning — kelompok nilai masuk rumus (positif, nol, negatif jika relevan).
- Boundary Value Analysis — nilai minimum/maksimum, batas desimal, nilai ekstrem.
- Combinatorial Testing — kombinasi komponen rumus (diskon + pajak + potongan).
- Error Guessing — divisi nol, pembulatan setengah (x.5), angka besar.

## Test Scenarios

### Positive Testing
- Input standar → hasil sesuai rumus (verifikasi dengan perhitungan manual/independen).
- Komponen rumus bernilai nol/kosong → hasil sesuai rumus.
- Kombinasi beberapa komponen rumus → hasil sesuai.
- Konversi satuan → hasil akurat sesuai faktor konversi.

### Negative Testing
- Divisi oleh nol → error ditangani eksplisit (bukan `Infinity`/`NaN`/500).
- Input `null`/kosong pada komponen rumus → ditangani sesuai kontrak (default/ditolak).
- Input non-numerik pada field perhitungan → ditolak validasi.
- Nilai di luar rentang wajar (negatif pada field non-negatif) → ditolak.

### Boundary Testing
- Nilai dengan pecahan tepat di titik pembulatan (x.5, x.005 untuk 2 desimal).
- Nilai terbesar yang mungkin (jumlah baris maksimum × harga maksimum) → tanpa overflow.
- Nilai terkecil non-nol (presisi maksimum) → tidak hilang karena pembulatan.
- Persentase 0% dan 100% (dan >100% bila relevan).
- Hasil perhitungan tepat di ambang batas kategori (mis. lulus/tidak, kenaikan level).

### Integration Testing
- Perhitungan per item + total keseluruhan → konsisten (jumlah per item == total).
- Perhitungan di UI vs API vs laporan → hasil identik.
- Perhitungan yang disimpan lalu dihitung ulang (recompute) → hasil stabil/identik.
- Perubahan komponen rumus (update harga/skor) → total turunan ikut diperbarui.
- Rounding lintas mata uang (lihat `input-currency`).

## Test Data
- Contoh perhitungan manual dengan hasil yang diketahui (expected value pasti).
- Nilai pecahan di sekitar titik pembulatan.
- Dataset besar (banyak baris) untuk akumulasi galat.
- Nilai ekstrem (sangat besar, sangat kecil, nol, negatif jika relevan).

## Expected Results
- Hasil sesuai rumus kontrak, dengan presisi dan pembulatan yang didefinisikan.
- Konsistensi: perhitungan yang sama selalu menghasilkan hasil yang sama (deterministik).
- Total agregat == penjumlahan komponen (dengan aturan pembulatan yang konsisten).
- Nilai tidak valid menghasilkan penanganan eksplisit, bukan nilai rusak (`NaN`, `Infinity`, angka absurd).

## Common Defects
- Pembulatan berbeda antara UI (format tampilan) dan backend (nilai tersimpan).
- Pembulatan per baris vs di akhir menghasilkan selisih (total tidak cocok dengan jumlah item).
- Presisi hilang karena tipe data (integer division, floating point).
- Divisi oleh nol menyebabkan error/NaN.
- Akumulasi galat pada dataset besar.
- Urutan operasi rumus salah (precedence) — hasil beda tipis tapi sistemik.
- Re-compute menghasilkan angka berbeda dari perhitungan awal.

## Security Considerations
- Manipulasi input perhitungan (harga/diskon dari client) — nilai wajib dihitung server-side.
- Pembulatan bisa dieksploitasi (rounding attack): selisih kecil diakumulasi secara massal.
- Nilai ekstrem untuk memicu overflow dan perilaku tak terduga.

## References
- ISTQB CTFL v4.0.1 — Equivalence Partitioning, Boundary Value Analysis, Error Guessing.
- IEEE 754 — floating point (risiko presisi).
