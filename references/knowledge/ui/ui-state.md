# UI State Testing (Persistence, Refresh, Stale State)

## Overview
Menguji **state UI** — bagaimana data dan kondisi halaman bertahan, di-refresh, dan terhindar dari stale (data basi). Risiko utama: perubahan tidak tersimpan, refresh menghapus pekerjaan user, dan tampilan menampilkan data lama yang tidak lagi benar.

## When to Apply
Setiap halaman/komponen yang menyimpan state: form yang belum di-submit, filter/tabel, draft, dan data yang bisa berubah di tempat lain. Aplikasikan bersama `ui-form`, `ui-table`, dan `data-consistency`.

## Testing Principles
1. State harus **jelas sumbernya** — apa yang disimpan di mana (URL, storage, server) dan kapan di-reset.
2. **Refresh/reload** tidak boleh menghancurkan pekerjaan user tanpa peringatan.
3. UI harus **sinkron** dengan sumber data — stale state harus dicegah/dideteksi.
4. State yang tidak lagi valid harus **di-invalidate** saat data diubah di tempat lain.
5. Perilaku state harus **konsisten** antara navigasi, refresh, dan sesi baru.

## Test Design Techniques
- State Transition — dirty/clean, saved/unsaved, fresh/stale.
- Exploratory — refresh di tengah proses, buka dua tab, ubah data di tempat lain.

## Test Scenarios

### Positive Testing
- Isi form → refresh → data masih ada (jika ada autosave/draft).
- Filter/sort tabel → navigasi balik → state filter tetap (atau sesuai kontrak).
- Update data di satu tempat → tampilan lain ter-refresh/ter-invalidate.
- Sesi baru → state kembali ke default yang benar.

### Negative Testing
- Refresh di tengah submit → tidak ada data ganda/hilang.
- Data diubah di tab lain → tab lama tidak menampilkan stale tanpa indikasi.
- State tersimpan korup/parsial → fallback ke default aman.
- Navigasi balik ke halaman dengan data terhapus → ditangani (bukan error).

### Boundary Testing
- State kosong vs terisi saat refresh berulang.
- Autosave tepat saat user menutup halaman (timing balapan).
- Dua aksi update bersamaan pada data yang sama (delegasi `ui-behavior`).

### Integration Testing
- State + form draft (delegasi `ui-form`).
- State + tabel filter (delegasi `ui-table`).
- State + navigasi back (delegasi `ui-navigation`).
- State + konsistensi server (delegasi `data-consistency`).

## Test Data
- Form dengan nilai sebagian (dirty), tabel dengan filter aktif.
- Data yang diubah dari sesi/klien lain.

## Expected Results
- Refresh/navigasi memulihkan atau me-reset state sesuai kontrak secara konsisten.
- Tidak ada data basi yang tampil seolah-olah masih valid.
- Perubahan tersimpan tidak hilang; perubahan dibatalkan tidak tersisa.
- Perilaku identik di refresh, navigasi, dan sesi baru (kecuali kontrak menyatakan lain).

## Common Defects
- Refresh menghapus input form tanpa peringatan.
- Stale cache — data lama tampil setelah diubah di tempat lain.
- State tersimpan di storage yang salah (session vs local) → perilaku beda antar tab.
- Data ganda saat refresh di tengah submit (tidak idempoten).
- State tidak di-reset saat logout/berpindah user.
- Autosave gagal diam-diam → user mengira tersimpan padahal tidak.

## Security Considerations
- State tersimpan di client (localStorage/sessionStorage) bisa dibaca/dimanipulasi — jangan simpan data sensitif/token di sana.
- State lintas user harus terisolasi — tidak boleh bocor antar akun/sesi.
- Validasi ulang di server saat state client dipakai untuk operasi berubah data.

## References
- ISTQB CTFL v4.0.1
- OWASP WSTG — Testing for Session Management
- WCAG 2.1 — Consistent behavior
