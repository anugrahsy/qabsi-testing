# UI Table Testing

## Overview
Menguji **tabel data**: rendering, sorting, filtering, pagination, dan aksi per baris. Risiko utama: data tidak sinkron dengan API, sorting salah, kolom terpotong, dan aksi baris menargetkan baris yang salah.

## When to Apply
Setiap tabel/grid data — daftar, master data, laporan, dan tabel dengan aksi (edit/hapus/detail). Aplikasikan bersama `api-get-collection`, `api-sorting`, `api-pagination`, dan `ui-loading`.

## Testing Principles
1. Tabel adalah **cerminan** collection API — data harus sinkron dengan sumber.
2. Sorting/filtering harus **deterministik** dan stabil (tidak acak antar refresh).
3. Aksi per baris harus menargetkan baris yang **benar** (pakai ID, bukan index).
4. State tabel (page, sort, filter) harus jelas dan bisa direset.
5. Kolom & data harus tetap terbaca di berbagai lebar layar.

## Test Design Techniques
- Equivalence Partitioning — kelompok nilai filter.
- Boundary Value Analysis — batas halaman, baris kosong.
- State Transition — state tabel (kosong, loading, terisi, error).
- Exploratory — kombinasi sort + filter + pindah halaman.

## Test Scenarios

### Positive Testing
- Tabel merender data sesuai response collection.
- Sorting ascending/descending per kolom → urutan benar.
- Filter → hanya baris yang cocok tampil.
- Pagination → navigasi halaman benar, jumlah per halaman sesuai.
- Aksi per baris (edit/hapus) menargetkan baris yang benar.

### Negative Testing
- Data kosong → tampil empty state (delegasi `ui-empty-state`).
- Filter tanpa hasil → empty state dengan opsi reset filter.
- Sorting kolom yang tidak disortir server → perilaku sesuai kontrak.
- Baris yang dihapus di backend → tidak tampil setelah refresh.

### Boundary Testing
- Tabel dengan 1 baris, 0 baris, banyak baris.
- Halaman terakhir dengan sisa baris.
- Kolom dengan teks sangat panjang → truncate/wrap, bukan overflow.
- Banyak kolom → scroll horizontal tetap bisa dibaca.

### Integration Testing
- Tabel + pagination API (delegasi `api-pagination`).
- Tabel + sorting API (delegasi `api-sorting`).
- Tabel + filter API (delegasi `api-filtering`).
- Tabel + aksi baris + konfirmasi (delegasi `ui-modal`).
- Tabel + loading skeleton (delegasi `ui-loading`).

## Test Data
- Dataset 0, 1, banyak baris.
- Data dengan nilai sama di kolom sort (uji stabilitas).
- Teks panjang, angka, tanggal, status untuk tiap tipe kolom.

## Expected Results
- Data tabel identik dengan response API (tidak ada baris hilang/duplikat).
- Sorting stabil — baris bernilai sama tidak berubah posisi acak.
- Aksi baris mempengaruhi record dengan ID yang benar.
- State tabel konsisten setelah refresh/sort/filter.

## Common Defects
- Aksi baris pakai index → setelah sort/filter salah target.
- Sorting client vs server tidak konsisten.
- Kolom terpotong tanpa tooltip/truncate indicator.
- Pagination off-by-one (baris terakhir hilang/duplikat).
- State tabel hilang saat navigasi balik.
- Data tidak refresh setelah aksi (hapus/edit) tanpa reload manual.

## Security Considerations
- Data sensitif di tabel harus terscope oleh otoritas (delegasi `auth-object-access`).
- Aksi masal (bulk delete) butuh konfirmasi + otorisasi server.
- Jangan render nilai yang bisa menyuntik XSS tanpa escape.

## References
- Google AIP-158 (Pagination), AIP-132 (List)
- ISTQB CTFL v4.0.1
- WCAG 2.1 — Info and Relationships (1.3.1)
