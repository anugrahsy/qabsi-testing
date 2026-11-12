# UI Accessibility Testing

## Overview
Menguji **aksesibilitas** — apakah UI bisa dipakai oleh semua orang, termasuk pengguna keyboard-only dan pembaca layar (screen reader). Risiko utama: elemen tak terjangkau keyboard, label/relasi hilang, kontras rendah, dan informasi hanya tersampaikan lewat warna.

## When to Apply
Setiap komponen UI interaktif. Aplikasikan bersama semua modul `ui-*` (focus, label, state) dan `nft-accessibility` (evaluasi menyeluruh). Referensi utama: **WCAG 2.1** (level A/AA).

## Testing Principles
1. **Keyboard-first**: semua fungsi bisa diakses tanpa mouse (tab, enter, space, arrow, escape).
2. **Perceivable**: informasi tidak boleh hanya lewat warna — butuh teks/ikon pendukung.
3. **Operable**: urutan fokus logis, focus terlihat, target cukup besar, cukup waktu.
4. **Understandable**: label jelas, bahasa konsisten, error teridentifikasi.
5. **Robust**: markup sesuai semantik/ARIA sehingga teknologi bantu bisa membaca.

## Test Design Techniques
- Equivalence Partitioning — kelompok elemen sejenis (input, tombol, tabel, dialog).
- Exploratory — jalur keyboard lengkap + screen reader pass.
- Checklist WCAG per kriteria yang relevan.

## Test Scenarios

### Positive Testing
- Tab → fokus bergerak urut dan terlihat (focus visible).
- Semua aksi bisa dijalankan hanya dengan keyboard.
- Field punya label yang terasosiasi (label for / aria-label / aria-labelledby).
- Gambar dekoratif/bermakna punya alt text yang tepat.
- Kontras teks memenuhi WCAG (4.5:1 normal, 3:1 teks besar).
- Screen reader mengumumkan perubahan state (error, loading, hasil).

### Negative Testing
- Aksi yang hanya bisa via mouse → defect (harus ada jalur keyboard).
- Warna saja sebagai pembeda status → defect (butuh indikator lain).
- Focus tersembunyi/tidak terlihat → defect.
- Error tidak teridentifikasi oleh screen reader → defect.
- Navigasi skip-link tidak ada di halaman panjang → defect.

### Boundary Testing
- Zoom 200% → konten tetap bisa dibaca (reflow).
- Ukuran target sentuh minimum (~44×44 px).
- Urutan fokus di layout kompleks (modal, tabel) tetap benar.

### Integration Testing
- Modal + focus trap (delegasi `ui-modal`).
- Dropdown/combobox keyboard (delegasi `ui-dropdown`).
- Form + error identification (delegasi `ui-form`).
- Table + semantic header (delegasi `ui-table`).

## Test Data
- Halaman dengan form, tabel, modal, dan elemen status/notifikasi.
- Konten dengan warna status (merah/hijau) dan ikon.

## Expected Results
- Semua interaksi bisa lewat keyboard dengan fokus terlihat dan urut.
- Label/relasi/alt tersedia dan benar.
- Informasi status tidak bergantung hanya pada warna.
- Screen reader bisa membaca struktur dan perubahan state.

## Common Defects
- Focus outline dihilangkan (outline: none) tanpa pengganti.
- Input tanpa label terkait (placeholder dipakai sebagai label).
- Icon button tanpa aria-label.
- Status sukses/error hanya lewat warna.
- Focus tidak terkunci di modal / tidak kembali ke trigger.
- Kontras rendah pada teks abu-abu di atas putih.
- Error tidak diumumkan (aria-live hilang).

## Security Considerations
- Konten yang sengaja disembunyikan dari screen reader (aria-hidden) jangan dipakai untuk menyembunyikan data sensitif dari teknologi bantu secara keliru.
- CAPTCHA/anti-bot harus punya alternatif aksesibel (bila relevan).

## References
- WCAG 2.1 (POUR: Perceivable, Operable, Understandable, Robust)
- WAI-ARIA Authoring Practices
- ISTQB CTFL v4.0.1
