# UI File Upload Testing

## Overview
Menguji **upload file di UI** — pemilihan file, progress, preview, dan penghapusan. Risiko utama: feedback progress tidak ada, file salah ter-upload, preview tidak sesuai, dan batasan ukuran/tipe tidak ditegakkan di UI.

## When to Apply
Setiap alur upload: form dengan lampiran, drag-and-drop, preview gambar, dan multi-upload. Aplikasikan bersama `input-file`/`input-image` (validasi tipe/ukuran) dan `api-file-upload`.

## Testing Principles
1. Upload harus punya **feedback jelas**: progress, sukses, gagal — user tidak menebak.
2. Validasi tipe/ukuran di client = kenyamanan; server = kebenaran. Keduanya konsisten.
3. **Cancel/hapus** saat upload berjalan harus benar-benar membatalkan (termasuk request).
4. Preview harus mencerminkan file yang benar, tidak bocor antar file.
5. File gagal upload tidak boleh mengunci alur (bisa dihapus/ulang).

## Test Design Techniques
- Equivalence Partitioning — tipe/ukuran file valid vs invalid.
- Boundary Value Analysis — ukuran tepat di batas, sedikit di atas/bawah.
- State Transition — idle → selecting → uploading → success/error → removed.

## Test Scenarios

### Positive Testing
- Pilih file valid → upload, progress tampil, lalu sukses.
- Preview muncul untuk file yang mendukung (gambar).
- Hapus file → file terhapus dari daftar (dan tidak ter-upload).
- Multi-upload → semua file ter-upload dengan status per file.

### Negative Testing
- File melebihi ukuran maksimum → ditolak dengan pesan jelas.
- Tipe file tidak diizinkan → ditolak (ekstensi ATAU MIME).
- Upload dibatalkan di tengah → tidak ada file parsial yang tersimpan.
- File korup/0 byte → ditolak atau ditandai gagal dengan jelas.

### Boundary Testing
- Ukuran tepat di batas maksimum → diterima.
- Ukuran batas maksimum + 1 byte → ditolak.
- Jumlah file maksimum → diterima; +1 → ditolak.
- Upload file sangat besar → progress benar, tidak hang.

### Integration Testing
- Upload + form submit (delegasi `ui-form`).
- Upload + notifikasi hasil (delegasi `ui-notification`).
- Upload + validasi server (delegasi `api-file-upload`, `input-file`).
- Drag-and-drop + fallback klik untuk pilih file.

## Test Data
- File valid berbagai tipe (pdf, png, jpg, docx).
- File ukuran 0 byte, batas, melebihi batas, korup.
- File dengan nama panjang / karakter khusus.

## Expected Results
- Progress/status upload terlihat jelas; sukses/gagal terbedakan.
- Batasan tipe/ukuran ditegakkan di UI dan server.
- Preview sesuai file, tidak bocor antar file.
- Cancel/hapus menghapus file dan membatalkan request terkait.

## Common Defects
- Tidak ada progress → user mengira upload gagal/hang.
- Validasi client vs server beda (client lolos, server tolak).
- Hapus file hanya visual — file tetap ter-upload di balik layar.
- Preview bocor/tertukar antar file.
- Ekstensi diizinkan tapi konten berbahaya lolos (hanya cek ekstensi).
- Upload parsial tertinggal saat dibatalkan.

## Security Considerations
- Jangan hanya validasi ekstensi — cek MIME/konten aktual.
- File upload wajib di-scan & di-simpan di lokasi aman (tanpa eksekusi).
- Batasi ukuran & jumlah di server (anti resource exhaustion).
- Jangan render file upload langsung sebagai HTML (XSS via SVG/HTML).

## References
- OWASP WSTG — Testing File Upload
- ISTQB CTFL v4.0.1
- WCAG 2.1 — Status Messages (4.1.3)
