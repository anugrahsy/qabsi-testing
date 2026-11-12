# Input Text Validation Testing

## Overview
Menguji validasi input teks bebas (single-line/multi-line): panjang, whitespace, Unicode, dan special characters. Risiko utama: XSS dari karakter khusus, whitespace tak terlihat lolos, panjang tak dibatasi (DoS), dan encoding Unicode rusak.

## When to Apply
Field teks: nama, alamat, catatan, komentar, deskripsi, judul — single-line maupun textarea.

## Testing Principles
1. Tentukan **panjang maksimum** eksplisit — dan tentukan dihitung per karakter atau per byte (beda untuk Unicode).
2. Bedakan single-line (tanpa newline) vs multi-line (boleh newline).
3. Whitespace: putuskan apakah leading/trailing ditrim, hanya-spasi ditolak, atau diizinkan.
4. Karakter khusus (`<`, `>`, `&`, `"`, `'`) diterima sebagai data, tapi wajib di-encode saat render (anti-XSS) — jangan ditolak di input.
5. Unicode: tentukan dukungan karakter (emoji, aksen, non-Latin) & normalisasi (NFC/NFKC).

## Test Design Techniques
- Equivalence Partitioning — kelas panjang (kosong, normal, maksimum, melebihi), kelas karakter.
- Boundary Value Analysis — panjang min/maks (max-1, max, max+1) dalam karakter & byte.
- State Transition — field empty → filled → cleared (untuk required vs optional).

## Test Scenarios

### Positive Testing
- Teks normal (huruf, angka, spasi) → diterima.
- Teks dengan tanda baca & simbol umum → diterima.
- Unicode (aksen, non-Latin, emoji) → diterima sesuai kontrak.
- Teks panjang maksimum → diterima.
- Whitespace leading/trailing → ditrim sesuai kontrak.

### Negative Testing
- Kosong / hanya spasi → ditolak (jika required).
- Melebihi panjang maksimum → ditolak.
- Newline di single-line field → ditolak.
- Karakter kontrol (null, `\u0000`) → ditolak.
- Whitespace tak terlihat (zero-width space, NBSP) → ditangani sesuai kontrak.

### Boundary Testing
- Panjang = max-1 → diterima; = max → diterima; = max+1 → ditolak.
- Panjang dalam byte (multibyte Unicode) vs karakter → konsisten dengan kontrak.
- Leading/trailing whitespace tepat di batas panjang.

### Integration Testing
- Teks disimpan & ditampilkan ulang → karakter khusus di-encode (tidak dieksekusi sebagai HTML).
- Panjang maksimum konsisten antara form (maxLength) & endpoint.
- Teks multi-line dirender dengan line break yang benar.

## Test Data
- Teks kosong, 1 karakter, normal, max-1, max, max+1.
- Karakter khusus HTML (`<script>`, `&`, `"`, `'`).
- Unicode: emoji, aksen, CJK, RTL.
- Whitespace: leading/trailing, hanya spasi, zero-width, NBSP.
- Newline (`\n`, `\r\n`) untuk single vs multi-line.

## Expected Results
- Teks valid diterima; invalid ditolak dengan pesan jelas.
- Panjang dibatasi (karakter/byte) sesuai kontrak.
- Karakter khusus disimpan sebagai data, di-encode saat render (XSS-safe).
- Unicode ditangani tanpa rusak (encoding konsisten).

## Common Defects
- Panjang dihitung byte tapi tampil karakter → Unicode terpotong/ditolak salah.
- XSS: karakter khusus dirender tanpa encoding.
- Hanya-spasi lolos (field tampak terisi tapi kosong).
- Zero-width/NBSP lolos → duplikat "kosong".
- Newline tidak divalidasi di single-line field.
- Trimming tidak konsisten (API vs UI).

## Security Considerations
- OWASP Input Validation Cheat Sheet — batasi panjang, whitelist jika memungkinkan.
- OWASP XSS Prevention — output encoding saat render (bukan menolak `<>` di input).
- Unicode normalization (NFC/NFKC) mencegah bypass (homoglyph, zero-width).
- Panjang tak terbatas → DoS/resource exhaustion.

## References
- OWASP Input Validation Cheat Sheet
- OWASP XSS Prevention Cheat Sheet
- Unicode Normalization (NFC/NFKC)
