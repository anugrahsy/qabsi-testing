# UI Dropdown / Select Testing

## Overview
Menguji **dropdown/select** sebagai kontrol pilihan: buka-tutup, pilih item, keyboard navigation, dan search/filter opsi. Risiko utama: pilihan tidak terseleksi benar, keyboard tidak bisa dipakai, dan opsi tidak sinkron dengan data sumber.

## When to Apply
Setiap dropdown/combobox/autocomplete — select tunggal/multi, searchable, grouped, dan dropdown bertingkat (dependent). Aplikasikan bersama `api-get-collection` (sumber data opsi) dan `ui-accessibility`.

## Testing Principles
1. Dropdown harus bisa dioperasikan penuh dengan **keyboard** (bukan hanya mouse).
2. Pilihan harus **deterministik** — urutan opsi stabil dan konsisten dengan sumber data.
3. State terpilih harus jelas terlihat (bukan hanya bergantung warna).
4. Opsi yang tak relevan (disabled, out of scope) harus benar-benar tidak bisa dipilih.
5. Nilai terpilih harus konsisten antara tampilan dan data yang dikirim.

## Test Design Techniques
- Equivalence Partitioning — kelompok opsi (aktif/disabled/group).
- State Transition — closed → open → selecting → selected.
- Boundary — opsi pertama/terakhir, pencarian tanpa hasil.

## Test Scenarios

### Positive Testing
- Buka dropdown → daftar opsi tampil sesuai sumber data.
- Pilih opsi → nilai tersimpan dan tampil di trigger.
- Pilih opsi via keyboard (Arrow + Enter) → sama seperti klik.
- Dropdown searchable → ketik keyword, opsi terfilter benar.

### Negative Testing
- Pilih opsi disabled → tidak bisa dipilih.
- Tutup tanpa memilih → nilai tetap sebelumnya.
- Ketik keyword tanpa hasil → tampil "no results" (delegasi `ui-empty-state`).
- Escape saat terbuka → tertutup tanpa mengubah pilihan.

### Boundary Testing
- Opsi pertama dan terakhir bisa dipilih.
- Dropdown dengan satu opsi saja.
- Dropdown dengan sangat banyak opsi (ribuan) → tetap responsif / virtualisasi.
- Multi-select: pilih semua, hapus semua.

### Integration Testing
- Dropdown dependent: opsi kedua ter-update saat opsi pertama berubah.
- Dropdown + form validasi (delegasi `ui-form`).
- Dropdown + sumber data async (delegasi `ui-loading`).
- Dropdown + keyboard navigation (delegasi `ui-accessibility`).

## Test Data
- Daftar opsi pendek, panjang, dan kosong.
- Opsi dengan label sama/panjang, karakter khusus.
- Data opsi yang berubah dari backend (uji sinkronisasi).

## Expected Results
- Nilai terpilih konsisten di tampilan, state, dan payload.
- Keyboard navigation lengkap: buka, navigasi, pilih, tutup.
- Opsi yang dihapus dari sumber tidak lagi bisa dipilih (stale dicegah).
- Pilihan tidak hilang saat dropdown dibuka-tutup.

## Common Defects
- Keyboard navigation tidak berfungsi (tidak bisa Arrow/Enter).
- Opsi disabled masih bisa dipilih via keyboard.
- Nilai tampil tapi payload kosong/berbeda (mismatch value vs label).
- Opsi stale (data lama) masih muncul setelah refresh.
- Posisi dropdown terpotong di tepi layar (overflow viewport).
- Multi-select: pilihan tidak bisa dihapus satu per satu.

## Security Considerations
- Opsi dari backend bisa mengandung konten berbahaya → render aman (escape).
- Jangan percaya nilai dropdown client — validasi enum di server (delegasi `input-enum`).
- Autocomplete jangan membocorkan data sensitif lewat pencarian.

## References
- WAI-ARIA Authoring Practices — Combobox / Listbox Pattern
- WCAG 2.1 — Keyboard (2.1.1)
- ISTQB CTFL v4.0.1
