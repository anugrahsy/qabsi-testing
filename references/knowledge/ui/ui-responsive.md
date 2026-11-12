# UI Responsive Testing

## Overview
Menguji tampilan dan interaksi di **berbagai ukuran layar/perangkat** (mobile, tablet, desktop). Risiko utama: konten terpotong, elemen tidak bisa dioperasikan di layar kecil, dan interaksi touch vs mouse berbeda perilaku.

## When to Apply
Setiap halaman/komponen yang harus tampil baik lintas perangkat. Aplikasikan bersama `nft-compatibility` (browser/OS) dan `ui-accessibility` (target sentuh).

## Testing Principles
1. Responsive = **fungsional**, bukan sekadar visual rapi — elemen harus tetap bisa dipakai.
2. Tidak boleh ada scroll horizontal yang tak diinginkan atau konten terpotong.
3. Target sentuh di layar kecil harus cukup besar (minimal ~44×44 px).
4. Interaksi hover (mouse) butuh padanan di touch (tap/long-press).
5. Uji pada breakpoint **nyata**, bukan hanya resize jendela — perilaku bisa beda.

## Test Design Techniques
- Equivalence Partitioning — rentang lebar (mobile/tablet/desktop) sebagai kelas.
- Boundary Value Analysis — tepat di titik breakpoint (di atas/bawah).

## Test Scenarios

### Positive Testing
- Setiap breakpoint (mobile/tablet/desktop) menampilkan konten lengkap.
- Elemen utama (navigasi, tombol, form) bisa dioperasikan di semua ukuran.
- Tabel lebar → scroll horizontal / responsif, tetap terbaca.

### Negative Testing
- Layar sangat kecil → tidak ada elemen penting yang hilang/tertutup.
- Layar besar → konten tidak membentang aneh / tetap terstruktur.
- Hover-only action → ada cara akses di perangkat touch.

### Boundary Testing
- Lebar tepat di breakpoint dan ±1 px → transisi layout tidak janggal.
- Orientasi portrait ↔ landscape di mobile → layout menyesuaikan.
- Zoom browser (200%) → konten tetap bisa dibaca/digunakan.

### Integration Testing
- Responsive + tabel (delegasi `ui-table`).
- Responsive + modal/dropdown (delegasi `ui-modal`, `ui-dropdown`).
- Responsive + touch target (delegasi `ui-accessibility`).
- Responsive + kompatibilitas browser (delegasi `nft-compatibility`).

## Test Data
- Ukuran viewport mobile (mis. 360×640), tablet (768×1024), desktop (1366×768+).
- Konten panjang (teks, tabel lebar, banyak kolom).

## Expected Results
- Konten lengkap dan bisa dioperasikan di semua breakpoint tanpa scroll horizontal tak wajar.
- Tidak ada elemen yang terpotong atau tertutup.
- Touch dan mouse menghasilkan perilaku yang setara.

## Common Defects
- Tabel/modal terpotong di layar kecil.
- Menu navigasi tidak bisa diakses di mobile.
- Hover-only action tidak bisa dipakai di touch.
- Scroll horizontal muncul karena elemen fixed-width.
- Breakpoint meleset — layout rusak di rentang tertentu.
- Ukuran sentuh terlalu kecil → sulit di-tap.

## Security Considerations
- Elemen yang disembunyikan via CSS (hidden responsif) tetap ada di DOM — jangan andalkan CSS untuk menyembunyikan data sensitif.
- Konten yang "disembunyikan" di mobile harus tetap di-scope otorisasi yang sama.

## References
- ISTQB CTFL v4.0.1
- WCAG 2.1 — Reflow (1.4.10), Target Size (2.5.5)
- Google Web Fundamentals — Responsive Web Design
