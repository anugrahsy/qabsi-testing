# Input Image Validation Testing

## Overview
Menguji validasi upload gambar: format, dimensi, resolusi, dan metadata. Risiko utama: file non-gambar lolos (image dengan payload), dimensi/resolusi tidak dibatasi (decompression bomb), dan metadata EXIF membocorkan PII.

## When to Apply
Upload avatar, foto profil, galeri, atau field gambar. Aplikasikan bersama `input-file` untuk ukuran, tipe, dan jumlah file.

## Testing Principles
1. Verifikasi konten benar-benar gambar via magic bytes (atau re-encode) — bukan hanya ekstensi/MIME.
2. Tentukan batas **dimensi** (lebar × tinggi) dan **jumlah pixel** — cegah decompression bomb.
3. Tentukan format yang didukung (JPEG, PNG, WebP) & batas ukuran file (dari `input-file`).
4. Metadata (EXIF): putuskan dipertahankan, di-strip, atau diabaikan — waspadai PII (GPS, info kamera).
5. Bedakan validasi upload vs pemrosesan (resize, thumbnail) — keduanya perlu diuji.

## Test Design Techniques
- Equivalence Partitioning — kelas format valid/invalid, kelas dimensi.
- Boundary Value Analysis — dimensi minimum/maksimum, jumlah pixel, ukuran file.
- Decision Table — kombinasi format × dimensi × ukuran.

## Test Scenarios

### Positive Testing
- Gambar format didukung (JPEG/PNG) → diterima.
- Gambar dengan dimensi dalam batas → diterima.
- Gambar dengan metadata umum → diterima (atau metadata di-strip sesuai kontrak).

### Negative Testing
- File non-gambar di-rename `.png` → ditolak (magic bytes).
- Format tidak didukung (BMP/TIFF/GIF) → ditolak/diterima sesuai kontrak.
- Dimensi melebihi batas → ditolak.
- Ukuran file melebihi batas → ditolak.
- Gambar korup (header valid, data rusak) → ditolak/ditangani dengan error jelas.

### Boundary Testing
- Dimensi tepat di batas (max-1, max, max+1 pixel).
- Jumlah pixel di batas (mis. 100MP) → di atas batas ditolak.
- Ukuran file tepat di batas (delegasi `input-file`).
- Gambar dimensi minimal (1×1) / 0×0.

### Integration Testing
- Gambar di-upload → thumbnail/resize dihasilkan tanpa error (decompression bomb dihindari).
- Gambar disimpan → metadata EXIF di-strip (tidak bocor GPS) sesuai kebijakan.
- Gambar ditampilkan ulang → konten benar (tidak corrupt).

## Test Data
- Gambar valid (JPEG, PNG, WebP) kecil & besar.
- File non-gambar di-rename `.png`/`.jpg`.
- Gambar korup (truncated, header palsu).
- Gambar dimensi ekstrem (1×1, 10000×10000, decompression bomb: file kecil pixel banyak).
- Gambar dengan EXIF GPS/PII.

## Expected Results
- Gambar valid (format & dimensi) diterima; non-gambar/invalid ditolak.
- Dimensi & jumlah pixel dibatasi (anti decompression bomb).
- Metadata ditangani sesuai kebijakan (strip PII).
- Proses resize/thumbnail tidak crash pada gambar ekstrem.

## Common Defects
- Non-gambar lolos (hanya cek ekstensi) → stored XSS/RCE via image payload.
- Decompression bomb (dimensi besar, file kecil) → DoS saat decode.
- EXIF GPS/PII tidak di-strip.
- Dimensi tidak divalidasi → UI/layout rusak atau resource habis.
- Format tidak didukung tetap diproses → crash.

## Security Considerations
- OWASP File Upload Cheat Sheet — verifikasi konten gambar; re-encode untuk sanitasi.
- Decompression bomb → batasi jumlah pixel sebelum decode.
- Strip metadata EXIF untuk hilangkan PII (GPS, info kamera).
- SVG (jika didukung) berpotensi XSS (script inline) — perlakukan khusus.

## References
- OWASP File Upload Cheat Sheet
- OWASP Input Validation Cheat Sheet
