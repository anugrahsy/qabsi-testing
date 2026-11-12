# UI Modal / Dialog Testing

## Overview
Menguji **modal/dialog** sebagai overlay yang menahan perhatian user: buka, tutup, backdrop, escape, dan focus. Risiko utama: interaksi "bocor" ke konten di belakang, focus tidak terkunci, dan state hilang saat menutup.

## When to Apply
Setiap modal, dialog konfirmasi, drawer, dan popover yang menimpa konten utama. Aplikasikan bersama `ui-accessibility` (focus trap) dan `ui-behavior` (konfirmasi ganda).

## Testing Principles
1. Modal harus **modal** — interaksi di belakangnya diblokir saat terbuka.
2. Focus harus **terkunci** dalam modal dan kembali ke trigger saat ditutup.
3. Semua jalur tutup (tombol X, Cancel, backdrop, Escape) harus konsisten perilakunya.
4. Konten/screen reader harus memahami modal adalah dialog terpisah.
5. Tutup modal tidak boleh meninggalkan state setengah jadi (konfirmasi vs batal).

## Test Design Techniques
- State Transition — open → interact → close (via berbagai jalur).
- Exploratory — kombinasi jalur tutup dan interupsi.

## Test Scenarios

### Positive Testing
- Buka modal → tampil, focus masuk ke elemen pertama/dialog.
- Tutup via tombol X/Cancel → modal tertutup, perubahan dibatalkan.
- Escape → menutup modal (kecuali kontrak menyatakan lain).
- Aksi utama (save/confirm) → modal tertutup dan aksi tereksekusi.

### Negative Testing
- Klik di luar modal (backdrop) → menutup (atau tidak, sesuai kontrak).
- Escape saat ada perubahan belum disimpan → konfirmasi/hold (sesuai kontrak).
- Klik konten di belakang modal → tidak terpengaruh.
- Buka modal kedua di atas modal pertama → stacking/close benar.

### Boundary Testing
- Escape ditekan berulang cepat → tidak crash/state aneh.
- Modal dengan konten panjang → scroll dalam modal, bukan halaman.
- Modal dibuka-tutup berulang → tidak ada memory leak/duplikasi.

### Integration Testing
- Modal konfirmasi + aksi destruktif (delegasi `ui-button`).
- Modal form + validasi (delegasi `ui-form`).
- Modal + state data di belakang (delegasi `ui-state`).

## Test Data
- Konten modal pendek vs panjang (overflow).
- State "ada perubahan belum disimpan".

## Expected Results
- Saat terbuka: scroll/klik terkunci di modal, background inert.
- Semua jalur tutup berperilaku konsisten (batal vs konfirmasi).
- Focus kembali ke elemen pemicu setelah modal ditutup.
- Aksi yang dibatalkan tidak meninggalkan perubahan.

## Common Defects
- Interaksi di belakang modal masih aktif (scroll/klik bocor).
- Focus tidak terkunci → keyboard navigasi keluar modal.
- Escape menutup tanpa konfirmasi padahal ada data belum tersimpan.
- Dua modal bertumpuk, yang di belakang ikut tertutup.
- Focus tidak kembali ke trigger (hilang/ke body).
- Modal tetap ada di DOM tersembunyi → dibaca screen reader.

## Security Considerations
- Modal konfirmasi bukan pengganti otorisasi — aksi tetap divalidasi di server.
- Data sensitif di modal tidak boleh bocor ke log/aria yang tidak perlu.
- Hati-hati clickjacking lewat overlay yang menutupi UI penting.

## References
- WCAG 2.1 — Focus Order (2.4.3), Focus Not Obscured
- WAI-ARIA Authoring Practices — Dialog (Modal) Pattern
- ISTQB CTFL v4.0.1
