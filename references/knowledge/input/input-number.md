# Input Number Validation Testing

## Overview
Menguji validasi input numerik: integer, desimal, presisi, min/max, dan overflow. Risiko utama: tipe salah (string `"10"` vs number `10`), desimal diterima saat integer diharapkan, presisi float salah, dan overflow/underflow tidak ditangani.

## When to Apply
Form angka (umur, kuantitas, harga mentah, skor), parameter query, atau field numerik di body request.

## Testing Principles
1. Tentukan **tipe & domain** eksplisit: integer vs decimal, presisi desimal, min/max, signed/unsigned.
2. Bedakan nilai nol (valid) vs kosong/null (belum diisi).
3. Presisi desimal: tentukan jumlah digit di belakang koma & aturan pembulatan.
4. Overflow/underflow: nilai di luar kapasitas tipe harus ditolak, bukan wrap/exception.
5. Format input (koma ribuan, separator desimal lokal) vs nilai logis dipisahkan.

## Test Design Techniques
- Equivalence Partitioning — kelas valid (dalam range), invalid (non-numerik), di luar range.
- Boundary Value Analysis — min-1, min, min+1; max-1, max, max+1; batas presisi.
- Decision Table — kombinasi tipe × range × presisi.

## Test Scenarios

### Positive Testing
- Integer dalam range → diterima.
- Desimal dengan presisi diizinkan → diterima.
- Nol → diterima (jika valid).
- Negatif → diterima/ditolak sesuai kontrak (signed/unsigned).
- String yang merepresentasikan angka → diterima/ditolak sesuai kontrak.

### Negative Testing
- Non-numerik (huruf, simbol) → ditolak.
- Kosong / null → ditolak (atau valid, sesuai kontrak).
- Desimal saat integer diharapkan → ditolak.
- Lebih banyak digit desimal dari presisi → ditolak/dibulatkan sesuai kontrak.
- Notasi ilmiah / eksponensial → ditolak/diterima sesuai kontrak.

### Boundary Testing
- min-1 → ditolak; min → diterima; min+1 → diterima.
- max-1 → diterima; max → diterima; max+1 → ditolak.
- Batas tipe (int32 `2^31-1`, int64 `2^63-1`) → di luar batas ditolak (overflow).
- Presisi desimal: digit desimal tepat di batas vs melebihi.

### Integration Testing
- Nilai numerik dipakai kalkulasi → hasil konsisten (delegasi `business-calculation`).
- Presisi desimal konsisten simpan vs tampil (tidak ada rounding drift).
- Range min/max konsisten antara form & endpoint.

## Test Data
- Nilai min/max & sekitarnya (min-1, min, min+1, max-1, max, max+1).
- Batas tipe integer (2^31-1, 2^31, 2^63-1, 2^63).
- Desimal dengan presisi bervariasi (0.1, 0.10, 0.999).
- Non-numerik & notasi ilmiah.
- Nol, negatif, nilai sangat besar/kecil.

## Expected Results
- Nilai dalam domain & range diterima dengan tipe benar.
- Di luar range / tipe salah ditolak dengan pesan jelas.
- Overflow/underflow ditangani (ditolak), bukan wrap.
- Presisi desimal & pembulatan sesuai kontrak.

## Common Defects
- Overflow/underflow → wrap atau exception (500).
- Desimal diterima saat integer diharapkan (atau sebaliknya).
- Presisi float (0.1 + 0.2 ≠ 0.3) → hasil kalkulasi salah.
- Min > max tidak divalidasi di konfigurasi.
- `NaN` / `Infinity` lolos.
- Nol ditolak padahal valid (atau null dianggap 0).

## Security Considerations
- OWASP Input Validation Cheat Sheet — whitelist digit & format, server-side.
- Overflow/underflow bisa menjadi vektor DoS atau logic error.
- Nilai sangat besar untuk resource exhaustion (mis. quantity tak terbatas).

## References
- OWASP Input Validation Cheat Sheet
- IEEE 754 (floating-point arithmetic) — untuk presisi float
