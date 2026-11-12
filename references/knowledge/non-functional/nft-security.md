# NFT Security Testing

## Overview
Menguji **aspek keamanan** aplikasi sebagai atribut non-functional: menemukan celah yang bisa dieksploitasi (authn, authz, input, kriptografi, session, error handling). Acuan utama **OWASP ASVS** untuk daftar periksa verifikasi dan **OWASP WSTG** untuk teknik pengujiannya.

Risiko utama: akses tak sah ke data, kebocoran informasi, manipulasi data, dan penyalahgunaan fitur bisnis. Bedakan dari modul `auth-*` (fokus perilaku identitas/akses) — modul ini fokus pada **assessment celah keamanan** menyeluruh.

## When to Apply
- Aplikasi yang menangani **data sensitif** (pribadi, akademik, keuangan).
- Sebelum rilis produksi atau setelah perubahan besar pada auth/API.
- Saat ada temuan audit/penetration test yang harus diverifikasi.
- Sebagai gate wajib untuk aplikasi yang terpapar internet.

## Testing Principles
1. Pilih **tingkat ASVS** (L1/L2/L3) sesuai profil risiko aplikasi — jangan terapkan semua cek tanpa dasar.
2. Verifikasi **per perilaku/requirement ASVS**, bukan menebak "coba-coba eksploit".
3. Bedakan **expected vs recommended**: kontrak/standar menentukan yang wajib, sisanya risiko.
4. Pengujian yang **menulis/menghapus** data harus di environment terisolasi.
5. Laporkan dengan **severity + bukti** yang dapat direproduksi, bukan sekadar "berpotensi lemah".

## Test Design Techniques
- **Threat Modeling** (STRIDE) — petakan aset, ancaman, dan permukaan serang sebelum menguji.
- **Requirement-based Verification** — petakan tiap cek ke requirement ASVS tertentu.
- **Equivalence Partitioning / BVA** — pada input yang rawan injeksi.
- **State Transition** — pada alur auth/session (login, logout, timeout, lockout).
- **Negative & Abuse Case** — sengaja melanggar asumsi (input berbahaya, akses lintas scope).

## Test Scenarios

### Positive Testing
- Autentikasi kuat: kredensial valid diterima, identitas terverifikasi benar.
- Otorisasi tepat: user hanya mengakses resource dalam scope-nya.
- Input divalidasi dan di-output secara aman (bebas injeksi XSS/SQL).
- Data sensitif terenkripsi saat transit (TLS) dan saat disimpan (hashing/encryption sesuai jenis data).
- Session/token punya expiry dan invalidasi yang benar.

### Negative Testing
- Input berbahaya (SQLi, XSS, command injection, path traversal) → ditolak/netral.
- Akses lintas scope/role (IDOR, privilege escalation) → ditolak `403`/`404`.
- Token/session kadaluarsa, dipalsukan, atau dipakai ulang → ditolak.
- Request tanpa header otorisasi / dengan kredensial salah → ditolak.

### Boundary Testing
- Panjang/format input pada batas maksimum → tidak memicu overflow/DoS.
- Batas percobaan login (lockout) → aktif pada ambang yang tepat.
- Expiry token/session tepat pada batas waktu → invalid setelahnya.
- Ukuran payload/file pada batas → tetap aman (anti-DoS).

### Integration Testing
- Alur auth menyeluruh: login → akses → logout → session invalid.
- Interaksi dengan third-party (SSO, payment, email) → tidak bocorkan kredensial.
- Log/error handling → tidak mengekspos stack trace, token, atau data sensitif.
- Header keamanan (CSP, X-Content-Type-Options, dsb) terpasang benar.

## Test Data
- Akun dengan berbagai role/level untuk verifikasi otorisasi.
- Payload serangan terstandardisasi (dari OWASP, mis. daftar payload XSS/SQLi).
- Token/session dengan variasi state (valid, expired, tampered).
- Data lintas tenant/scope untuk verifikasi isolasi.

## Expected Results
- Semua requirement ASVS pada tingkat yang dipilih terpenuhi.
- Input berbahaya ditolak/dinetralkan tanpa dampak.
- Akses di luar otorisasi selalu ditolak, tanpa kebocoran data.
- Tidak ada data sensitif terekspos di response, log, atau error.
- Kriptografi memakai algoritma standar yang masih dianggap aman.

## Common Defects
- Injeksi (SQL, XSS, command, XXE) karena input/output tidak dinetralkan.
- IDOR / broken access control — user bisa akses data user lain.
- Kredensial/session lemah: token tanpa expiry, JWT tanpa verifikasi signature.
- Data sensitif tidak terenkripsi saat transit atau disimpan plaintext.
- Error/log mengekspos stack trace / data internal.
- Algoritma kriptografi usang (MD5/SHA-1 untuk password, dsb).

## Security Considerations
- Pengujian ini sendiri adalah aktivitas sensitif: batasi akses ke tool, laporan, dan environment uji.
- Jangan gunakan exploit sungguhan terhadap sistem produksi tanpa izin tertulis.
- Laporkan temuan ke jalur yang benar, jangan simpan kredensial/payload di repo publik.

## References
- OWASP Application Security Verification Standard (ASVS) — daftar periksa per level
- OWASP Web Security Testing Guide (WSTG) — teknik pengujian
- OWASP Top 10 — prioritas risiko umum
