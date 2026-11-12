# UI Empty State Testing

## Overview
Menguji **empty state** — tampilan saat tidak ada data atau hasil. Risiko utama: halaman terlihat error, user tidak tahu langkah berikutnya, dan empty state tertukar dengan loading/error state.

## When to Apply
Setiap area yang bisa kosong: tabel tanpa data, hasil pencarian nol, filter tanpa hasil, dan detail tanpa konten. Aplikasikan bersama `ui-loading` (bedakan dengan loading) dan `ui-error-state`.

## Testing Principles
1. Empty state ≠ error — harus dibedakan jelas dari error/loading.
2. Empty state harus **memberi arah** (CTA/penjelasan), bukan layar kosong.
3. Ada perbedaan konteks: "belum ada data" vs "hasil pencarian kosong" vs "filter menyingkirkan semua".
4. Empty state tetap harus menampilkan elemen penting (mis. tombol tambah, reset filter).
5. Pesan harus menjelaskan **kenapa** kosong dan **apa** yang bisa dilakukan.

## Test Design Techniques
- Equivalence Partitioning — penyebab kosong (no data, no result, filtered out).
- State Transition — loading → empty (bukan error).

## Test Scenarios

### Positive Testing
- Data kosong → tampil empty state dengan pesan jelas.
- Ada CTA yang relevan (tambah data, reset filter).
- Empty state konsisten visual dengan desain halaman.

### Negative Testing
- Empty state tidak tertukar dengan error state.
- Empty state tidak menampilkan CTA yang tidak berlaku pada konteks itu.
- Empty state tidak muncul saat seharusnya loading (belum selesai fetch).

### Boundary Testing
- Tepat 1 data → tidak tampil empty state.
- 0 data → tampil empty state.
- Hasil pencarian menyusut ke 0 → pesan "tidak ditemukan", bukan "belum ada data".

### Integration Testing
- Empty state + filter (delegasi `ui-table`).
- Empty state + search (delegasi `ui-dropdown`/pencarian).
- Empty state + loading transisi (delegasi `ui-loading`).

## Test Data
- Dataset kosong, 1 record, banyak record.
- Query pencarian yang menghasilkan 0 hasil.

## Expected Results
- Empty state tampil hanya saat benar-benar tidak ada data (bukan saat loading/error).
- Pesan membedakan konteks kosong (no data vs no result).
- Ada tindakan lanjut yang jelas untuk user.
- Transisi loading → empty berjalan mulus tanpa flicker.

## Common Defects
- Empty state tampil saat data masih loading (flash kosong).
- Pesan generik tanpa petunjuk langkah berikutnya.
- Empty state tidak membedakan "no data" vs "filter tidak cocok".
- CTA reset filter hilang sehingga user terjebak.
- Empty state tertukar dengan error (atau sebaliknya).

## Security Considerations
- Empty state tidak boleh membocorkan keberadaan data (mis. lewat perbedaan pesan) jika datanya sensitif.

## References
- ISTQB CTFL v4.0.1
- Nielsen Norman Group — Empty State UX
- WCAG 2.1 — Status Messages (4.1.3)
