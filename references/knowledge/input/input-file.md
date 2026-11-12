# Input File Validation Testing

## Overview
Menguji validasi upload file: MIME type, ekstensi, ukuran, dan file korup. Risiko utama: file berbahaya (executable) lolos, MIME/ekstensi dipalsukan, ukuran tak dibatasi (DoS), dan file korup diproses tanpa deteksi.

## When to Apply
Endpoint upload (multipart), form lampiran dokumen/arsip, atau field file di body request.

## Testing Principles
1. Validasi **server-side** (ukuran, tipe, konten) — client-side saja tidak cukup (bisa bypass via API).
2. Jangan percaya MIME dari client (mudah dipalsukan); verifikasi **magic bytes/signature** konten.
3. Gunakan whitelist tipe & ekstensi (mis. PDF, DOCX, gambar) — bukan blacklist.
4. Batas ukuran eksplisit (max file size) & batas jumlah file.
5. Bedakan validasi file vs penyimpanan (nama file aman, path traversal, overwrite).

## Test Design Techniques
- Equivalence Partitioning — kelas tipe valid/invalid, kelas ukuran.
- Boundary Value Analysis — ukuran tepat di batas (max-1, max, max+1), jumlah file.
- Decision Table — kombinasi ekstensi × MIME × ukuran.

## Test Scenarios

### Positive Testing
- File dengan tipe & ekstensi di whitelist → diterima.
- File ukuran di bawah batas → diterima.
- File dengan MIME deklarasi & magic bytes cocok → diterima.

### Negative Testing
- Tipe tidak di whitelist (`.exe`, `.sh`, `.php`) → ditolak.
- MIME palsu (executable di-rename `.pdf`) → ditolak via magic bytes.
- Ukuran melebihi batas → ditolak.
- File kosong (0 byte) → ditolak/diterima sesuai kontrak.
- Tanpa file / field hilang → ditolak.
- Jumlah file melebihi batas → ditolak.

### Boundary Testing
- Ukuran = max-1 → diterima; = max → diterima; = max+1 → ditolak.
- Jumlah file tepat di batas vs melebihi.
- File 0 byte vs 1 byte.

### Integration Testing
- File diunggah → tersimpan dengan nama aman (tidak bisa path traversal / overwrite).
- File diunduh kembali → konten identik (round-trip integrity).
- File korup dibuka/diproses → ditangani (ditolak atau error jelas, bukan crash).

## Test Data
- File valid per tipe (PDF, DOCX, PNG) kecil & besar.
- File dengan ekstensi/MIME palsu (executable di-rename).
- File kosong (0 byte), file korup (dipotong/truncated).
- File ukuran batas (max-1, max, max+1).
- Nama file berbahaya (`../../etc/passwd`, nama panjang, karakter khusus).

## Expected Results
- File valid diterima; tipe/ukuran invalid ditolak dengan pesan jelas.
- MIME/ekstensi diverifikasi terhadap konten (magic bytes).
- Ukuran & jumlah file dibatasi.
- Nama file disanitasi (tidak ada path traversal).

## Common Defects
- Hanya validasi ekstensi → executable lolos.
- Hanya percaya MIME client → tipe palsu lolos.
- Ukuran tidak dibatasi → DoS disk/memory.
- Nama file asli dipakai mentah → path traversal / overwrite.
- File korup diproses → crash/unhandled error.
- Ukuran hanya dicek client-side → bypass via API.

## Security Considerations
- OWASP File Upload Cheat Sheet — whitelist, magic bytes, batas ukuran, nama file aman.
- Path traversal via nama file — jangan pakai nama client mentah.
- Upload executable/script → risiko RCE; pastikan tidak dieksekusi di server.
- DoS via file sangat besar / banyak file sekaligus.

## References
- OWASP File Upload Cheat Sheet
- OWASP Input Validation Cheat Sheet
