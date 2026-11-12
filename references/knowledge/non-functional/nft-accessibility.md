# NFT Accessibility Testing

## Overview
Menguji aplikasi agar **dapat digunakan oleh semua orang**, termasuk pengguna dengan disabilitas (penglihatan, pendengaran, motorik, kognitif) dan pengguna teknologi bantu (screen reader). Acuan utama **WCAG** (Web Content Accessibility Guidelines).

Risiko utama: konten tidak terbaca screen reader, operasi hanya bisa via mouse, kontras rendah, dan navigasi keyboard terputus — mengecualikan sebagian pengguna dan melanggar kepatuhan.

## When to Apply
- Aplikasi web/mobile yang digunakan publik atau internal secara luas.
- Saat ada persyaratan kepatuhan aksesibilitas (regulasi/standar organisasi).
- Setelah perubahan besar pada UI (desain ulang, komponen baru, tabel/form kompleks).
- Bersamaan dengan pengujian UI (kolaborasi dengan `ui-*`).

## Testing Principles
1. Uji terhadap **kriteria sukses WCAG** (level A/AA/AAA sesuai target), bukan sekadar "terlihat bagus".
2. Kombinasikan **uji manual + alat otomatis** — alat otomatis hanya menemukan sebagian kecil isu.
3. Gunakan **teknologi bantu asli** (screen reader) dan **keyboard saja** — bukan hanya inspeksi kode.
4. Aksesibilitas bukan pelengkap akhir; periksa sejak desain agar tidak jadi rework besar.
5. Satu komponen yang gagal (mis. modal tanpa fokus) bisa memblokir seluruh alur — periksa end-to-end.

## Test Design Techniques
- **WCAG Success Criterion Mapping** — petakan tiap elemen ke kriteria (1.1.1, 1.3.1, 2.1.1, 4.1.2, dsb).
- **Keyboard-only Walkthrough** — jalankan seluruh alur tanpa mouse.
- **Screen Reader Walkthrough** — jalankan alur dengan NVDA/JAWS/VoiceOver.
- **Automated Scan** (Axe, Lighthouse) — deteksi awal, dikonfirmasi manual.
- **Contrast & Zoom Analysis** — periksa rasio kontras dan perilaku pada zoom/reflow.

## Test Scenarios

### Positive Testing
- Semua elemen interaktif dapat dijangkau dan dioperasikan **hanya dengan keyboard**.
- Setiap elemen punya **nama/teks alternatif** yang benar (alt, label, aria-label).
- Urutan fokus logis dan terlihat jelas (visible focus indicator).
- Kontras teks memenuhi rasio minimum (WCAG 1.4.3 / 1.4.11).
- Konten tetap terbaca dan berfungsi pada zoom hingga 200% / reflow.

### Negative Testing
- Tanpa mouse → semua tindakan (buka modal, pilih, submit) tetap bisa dilakukan.
- Dengan screen reader → struktur (heading, tabel, form, status) terbaca benar.
- Gambar tanpa alt / ikon tanpa label → teridentifikasi sebagai gagal.
- Konten hanya berupa warna (mis. status merah/hijau) tanpa penanda lain → teridentifikasi gagal.

### Boundary Testing
- Teks dengan panjang ekstrem → tidak tumpang tindih/terpotong tanpa akses.
- Area target sentuh minimal (target size) → cukup besar pada batas minimum.
- Kontras pada warna dengan selisih tipis → berada tepat pada rasio ambang.
- Konten dinamis/notifikasi → diumumkan screen reader tanpa hilang.

### Integration Testing
- Alur form lengkap: label → input → error → submit → umpan balik, semua aksesibel.
- Modal/dialog: fokus masuk, terperangkap, dan kembali setelah ditutup.
- Navigasi antar halaman/rute → fokus dipindahkan dengan benar.
- Tabel data kompleks → header/relasi terbaca oleh screen reader.

## Test Data
- Akun/profil dengan preferensi aksesibilitas berbeda (jika relevan).
- Konten panjang dan konten multilingual (untuk uji reflow/pembacaan).
- Daftar periksa WCAG untuk level target (A/AA/AAA).

## Expected Results
- Kriteria sukses WCAG pada level target terpenuhi.
- Semua fungsi dapat dioperasikan via keyboard dan screen reader.
- Kontras, nama aksesibel, dan struktur semantik sesuai pedoman.
- Tidak ada perangkap fokus (focus trap bocor) atau urutan fokus yang kacau.

## Common Defects
- Elemen interaktif hanya via mouse (div/span tanpa keyboard handler).
- Gambar/ikon tanpa alt/aria-label.
- Kontras teks di bawah rasio minimum.
- Modal tidak mengelola fokus (fokus tidak masuk/keluar modal).
- Form tanpa label yang terasosiasi benar.
- Status/error hanya ditandai warna, tanpa teks/ikon.
- Heading/landmark tidak semantik sehingga navigasi screen reader kacau.

## Security Considerations
- Teknologi bantu/screen reader tidak boleh dijadikan vektor menyembunyikan konten — konten harus sama untuk semua.
- Konten yang "disembunyikan dari screen reader" (aria-hidden) jangan menyembunyikan info sensitif dari pengguna lain secara salah.
- Pengujian aksesibilitas memakai data uji, bukan data pengguna asli.

## References
- WCAG 2.2 (Web Content Accessibility Guidelines) — kriteria sukses A/AA/AAA
- WAI-ARIA Authoring Practices — pola widget aksesibel
- ISO/IEC 25010 — Usability (Accessibility sub-characteristic)
