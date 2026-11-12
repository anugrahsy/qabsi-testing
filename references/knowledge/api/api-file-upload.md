# API File Upload Testing

## Overview
Menguji endpoint unggah berkas (`multipart/form-data`): validasi tipe, ukuran, jumlah, nama berkas, penyimpanan, dan integritas hasil unggahan. Risiko utama: validasi hanya berdasarkan ekstensi, berkas besar dibaca penuh ke memori, path traversal lewat nama berkas, dan berkas yatim/tidak konsisten saat terjadi kegagalan.

## When to Apply
Setiap endpoint yang menerima berkas: dokumen pendukung, foto profil, lampiran pengajuan, impor data. Untuk perilaku UI (progress, preview, hapus), gunakan modul domain `ui-file-upload`; untuk validasi umum berkas, `input-file`.

## Testing Principles
1. **Validasi isi berkas, bukan hanya nama/ekstensi** (magic bytes/MIME sebenarnya).
2. **Batas ukuran dan jumlah ditegakkan sebelum pemrosesan penuh**, untuk mencegah kehabisan memori/disk.
3. **Nama berkas dari client tidak pernah dipakai langsung** sebagai path.
4. **Unggahan bersifat atomik**: metadata dan berkas konsisten, tidak ada yatim.
5. **Berkas tersimpan tidak dapat dieksekusi dan tidak dapat diakses publik tanpa otorisasi.**

## Test Design Techniques
- **Equivalence Partitioning** — tipe diizinkan/ditolak, ukuran valid/berlebih.
- **Boundary Value Analysis** — ukuran tepat batas, batas + 1 byte; jumlah berkas; panjang nama.
- **Decision Table** — ekstensi × MIME sebenarnya × ukuran × jumlah.
- **State Transition** — upload → validasi → simpan → metadata; gagal → bersih.

## Test Scenarios

### Positive Testing
- Berkas valid (tipe & ukuran diizinkan) → `201`/`200` dengan ID/URL berkas.
- Metadata tersimpan benar: nama asli, ukuran, tipe, checksum, pemilik.
- Unggah beberapa berkas dalam satu request → semua tersimpan dengan metadata masing-masing.
- Berkas dengan nama mengandung spasi/unicode → tersimpan tanpa merusak path.
- Setelah unggah, berkas dapat diunduh kembali dan isinya identik (checksum sama).
- Berkas dengan ukuran tepat pada batas maksimum → diterima.

### Negative Testing
- Tanpa bagian `file` → `400` dengan pesan field yang kurang.
- Nama field multipart salah → `400`.
- Berkas kosong (0 byte) → `400`/`422` sesuai kontrak.
- Ukuran melebihi batas → `413`, dan berkas tidak tersimpan.
- Tipe tidak diizinkan (mis. executable, skrip) → `415`.
- Ekstensi `.jpg` tetapi isi sebenarnya PDF/HTML → ditolak (validasi magic bytes).
- Nama berkas berisi path traversal (`../../etc/passwd`) → disanitasi, disimpan dengan nama aman.
- Berkas rusak/terpotong → `400`/`422`, tidak tersimpan dalam keadaan setengah.
- Tanpa autentikasi/izin → `401`/`403`.
- Unggah ke resource milik orang lain → `403`/`404`.

### Boundary Testing
- Ukuran = batas maksimum → diterima; batas + 1 byte → `413`.
- Jumlah berkas = batas maksimum; batas + 1 → ditolak.
- Panjang nama berkas maksimum; nama sangat panjang → dipotong/ditolak dengan aman.
- Nama berkas kosong atau hanya ekstensi (`.pdf`) → ditangani.
- Gambar dengan dimensi sangat besar / decompression bomb → ditolak dengan aman.
- Berkas dengan banyak bagian multipart (batas parser) → ditolak rapi, bukan crash.

### Integration Testing
- Unggah → simpan metadata di database → unduh: konsisten.
- Kegagalan penyimpanan (disk penuh/storage error) → tidak ada metadata yatim; atau berkas dihapus.
- Kegagalan database setelah berkas tersimpan → berkas dibersihkan (kompensasi).
- Pemindaian antivirus/validasi lanjutan → berkas terinfeksi ditolak dan tidak dapat diunduh.
- Presigned URL (bila ada) → kedaluwarsa sesuai kontrak dan tidak dapat dipakai ulang di luar scope.
- Unggah paralel beberapa berkas → tidak saling menimpa walau nama sama (nama unik).
- Gateway/proxy meneruskan multipart tanpa merusak boundary dan ukuran.

## Test Data
- Berkas valid per tipe yang diizinkan (gambar, PDF, dokumen).
- Berkas dengan ekstensi benar tetapi isi salah (polyglot: JPEG+HTML).
- Berkas berukuran: 0 byte, 1 byte, tepat batas, batas + 1, sangat besar.
- Nama berkas: normal, spasi, unicode, sangat panjang, path traversal.
- Berkas rusak/terpotong dan arsip dengan rasio kompresi ekstrem (zip bomb).
- Skenario storage/DB gagal untuk menguji kompensasi.

## Expected Results
- `201`/`200` dengan identitas berkas yang dapat dipakai untuk mengunduh.
- `413` untuk ukuran berlebih, `415` untuk tipe tidak diizinkan, `400` untuk multipart tidak lengkap.
- Tipe diverifikasi dari isi berkas, bukan hanya `Content-Type`/ekstensi yang dikirim client.
- Nama berkas tersimpan disanitasi; path traversal tidak berpengaruh.
- Ukuran dan checksum yang tercatat sama dengan berkas sebenarnya.
- Tidak ada berkas atau metadata yatim setelah respons gagal.
- Berkas tidak dapat diakses tanpa otorisasi; URL unduh tidak dapat ditebak.

## Common Defects
- Validasi hanya ekstensi; berkas berbahaya dengan ekstensi diizinkan lolos.
- Ukuran diperiksa setelah seluruh body dibaca ke memori (kehabisan memori).
- Batas jumlah berkas tidak diterapkan.
- Nama berkas client dipakai langsung sebagai path → path traversal/overwrite.
- Berkas disimpan publik di bucket yang dapat dienumerasi.
- Metadata tersimpan tetapi berkas gagal disimpan (atau sebaliknya).
- Unggahan paralel dengan nama sama saling menimpa.
- `Content-Type` response saat unduh salah sehingga browser mengeksekusi konten.
- Berkas berbahaya (SVG/HTML) dapat memicu stored XSS saat ditampilkan inline.
- Antivirus dilewati karena pemindaian hanya pada beberapa tipe.

## Security Considerations
- **Unrestricted file upload** adalah jalur umum menuju RCE/stored XSS: whitelist tipe, validasi isi, simpan di luar webroot.
- Sanitasi nama berkas; jangan gunakan nama asli sebagai path.
- Batasi ukuran dan jumlah untuk mencegah DoS (disk/memori).
- Sajikan berkas dengan `Content-Disposition: attachment` dan `Content-Type` yang aman untuk tipe berisiko.
- Verifikasi kepemilikan saat unduh; jangan mengandalkan URL yang tidak dapat ditebak.
- Waspadai XXE pada berkas XML/SVG dan zip bomb pada arsip.

## References
- RFC 7578 — Returning Values from Forms: `multipart/form-data`.
- OWASP File Upload Cheat Sheet — validasi, penyimpanan, penyajian.
- OWASP Web Security Testing Guide — WSTG-BUSL (file upload), WSTG-INPV.
- OpenAPI Specification — requestBody `multipart/form-data`, `413`/`415`.
