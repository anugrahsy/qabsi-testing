# NFT Compatibility Testing

## Overview
Menguji aplikasi agar **berfungsi benar di berbagai lingkungan target**: browser, sistem operasi, perangkat, resolusi layar, dan versi dependensi. Tujuannya memastikan tidak ada fitur yang rusak hanya karena perbedaan platform.

Risiko utama: fitur bekerja di satu browser tapi gagal di browser lain, tampilan rusak di ukuran layar tertentu, atau versi API/dependensi lama tidak lagi didukung.

## When to Apply
- Aplikasi web yang diakses lewat **banyak browser/perangkat** (tidak terkontrol seperti internal web).
- Setelah upgrade library/framework/versi API (kompatibilitas mundur).
- Saat menetapkan **matriks dukungan** (browser/OS mana yang didukung resmi).
- Aplikasi mobile lintas OS/versi (Android/iOS).

## Testing Principles
1. Tentukan **matriks dukungan resmi** dulu (browser/OS/versi mana yang wajib didukung) — jangan uji semua kombinasi tanpa batas.
2. Prioritaskan kombinasi berdasarkan **pangsa pengguna aktual** (risiko tertinggi = paling banyak dipakai).
3. Bedakan **fungsional** (fitur rusak) vs **visual** (hanya tampilan beda tapi berfungsi).
4. Gunakan kombinasi **emulator/simulator + perangkat asli** — keduanya punya keterbatasan.
5. Fitur yang tidak didukung harus **gagal dengan jelas / fallback**, bukan crash diam-diam.

## Test Design Techniques
- **Compatibility Matrix** — tabel kombinasi browser × OS × perangkat × versi.
- **Equivalence Partitioning** — kelompokkan browser berdasarkan engine (Blink/Gecko/WebKit).
- **Pairwise / Combinatorial** — kurangi kombinasi tanpa kehilangan cakupan.
- **Feature Detection Analysis** — cek API/fitur yang beda dukungan antar platform.

## Test Scenarios

### Positive Testing
- Fitur inti (login, list, form, submit) berfungsi di setiap browser/OS yang didukung.
- Tampilan/layout tetap benar (tidak tumpang tindih) di resolusi target.
- API/dependensi versi lama yang masih didukung tetap bekerja.
- Fitur dengan fallback (mis. fitur modern tidak didukung) → fallback berjalan.

### Negative Testing
- Browser/versi di luar matriks dukungan → ditangani (blokir + pesan, atau berfungsi tapi tanpa jaminan).
- Fitur yang mengandalkan API khusus browser → tidak crash di browser tanpa dukungan.
- Koneksi ke versi API/dependensi yang tidak kompatibel → error jelas, bukan perilaku aneh.

### Boundary Testing
- Resolusi layar minimum dan maksimum yang didukung → layout tetap berfungsi.
- Versi browser tertua dan terbaru dalam matriks → keduanya berfungsi.
- Ukuran viewport ekstrem (sangat sempit/sangat lebar) → tidak rusak fatal.

### Integration Testing
- Alur end-to-end penuh di tiap platform utama (bukan hanya satu halaman).
- Interaksi dengan third-party (SSO, payment, widget) di tiap browser.
- Penyimpanan/cookie/localStorage di tiap browser (perilaku bisa beda).

## Test Data
- Matriks dukungan resmi (browser/OS/versi/resolusi).
- Akun uji dan dataset yang sama untuk membandingkan antar platform.
- Daftar fitur/API yang diketahui punya beda dukungan antar platform.

## Expected Results
- Semua kombinasi dalam matriks dukungan lulus fungsional.
- Perbedaan antar platform hanya **visual minor**, bukan kegagalan fungsi.
- Fitur di luar dukungan gagal dengan pesan/fallback yang jelas.
- Tidak ada crash akibat API/fitur yang tidak didukung platform.

## Common Defects
- Fitur JavaScript modern tanpa polyfill → rusak di browser lama.
- CSS khusus browser (prefix) tidak lengkap → layout rusak.
- Cookie/localStorage/behavior beda antar browser → state hilang.
- Ketergantungan pada resolusi tetap → rusak di layar kecil/besar.
- User-Agent sniffing salah → fitur salah diarahkan.
- Upgrade library/API memutus kompatibilitas mundur tanpa fallback.

## Security Considerations
- Browser lama di luar dukungan bisa jadi vektor keamanan (tanpa patch) — arahkan pengguna ke versi aman.
- Jangan andalkan deteksi browser untuk keputusan keamanan (mudah dipalsukan).
- Uji kompatibilitas jangan memakai akun produksi lintas perangkat yang tidak terkontrol.

## References
- ISO/IEC 25010 — Compatibility (Co-existence, Interoperability)
- ISTQB CTFL v4.0.1 — Non-functional Testing
- Can I Use (caniuse.com) — matriks dukungan fitur web per browser
