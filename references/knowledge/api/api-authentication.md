# API Authentication Testing

## Overview
Menguji mekanisme **autentikasi** pada lapisan API: keberadaan dan validitas token/kredensial, masa berlaku, penandatanganan, pencabutan, dan perilaku saat identitas tidak dapat diverifikasi. Risiko utama: token kedaluwarsa atau palsu tetap diterima, signature tidak diverifikasi, dan endpoint mengembalikan data ketika kredensial tidak ada.

## When to Apply
Semua endpoint yang dilindungi (kecuali endpoint publik yang dinyatakan eksplisit). Modul ini fokus pada **siapa Anda**; untuk **apa yang boleh Anda lakukan** gunakan `api-authorization`. Untuk alur login UI/flow kredensial, gunakan modul domain `auth-*`.

## Testing Principles
1. **Deny by default.** Tanpa kredensial valid, endpoint terlindungi harus menolak.
2. **Verifikasi signature dan klaim**, bukan sekadar decode token.
3. **Kedaluwarsa dihormati** dengan toleransi clock skew yang eksplisit dan kecil.
4. **Pencabutan berlaku cepat** (logout, ganti password, akun nonaktif).
5. **Pesan error tidak membedakan** penyebab kegagalan secara berlebihan (hindari oracle).

## Test Design Techniques
- **Equivalence Partitioning** — token valid / kedaluwarsa / rusak / tidak ada / dicabut.
- **Boundary Value Analysis** — waktu tepat sebelum, tepat pada, dan sesudah `exp`; panjang token.
- **State Transition** — login → aktif → logout → token ditolak; refresh → token baru.
- **Decision Table** — kombinasi signature × expiry × issuer × audience × status akun.

## Test Scenarios

### Positive Testing
- Token valid dan belum kedaluwarsa → request diproses, identitas benar.
- Token diperbarui lewat refresh → token baru berfungsi, data pengguna tetap sama.
- Token dengan scope/klaim yang diperlukan → diizinkan.
- Beberapa sesi aktif untuk user yang sama → masing-masing token valid sesuai kebijakan.
- Setelah logout, token yang sama ditolak; token sesi lain tetap berlaku (atau semua dicabut, sesuai kontrak).

### Negative Testing
- Tanpa header `Authorization` → `401` + `WWW-Authenticate`.
- Skema salah (`Basic`, `Token` alih-alih `Bearer`) → `401`.
- Token malformed (bukan tiga segmen, base64 rusak) → `401`, bukan `500`.
- Signature dimodifikasi / token ditandatangani kunci lain → `401`.
- Algoritma `none` atau algoritma di luar yang diizinkan → `401`.
- Token kedaluwarsa → `401` dengan alasan yang sesuai kontrak.
- `iss`/`aud` tidak sesuai → `401`.
- Token milik akun yang dinonaktifkan/dihapus → `401`/`403`.
- Token dicabut (logout, ganti password) → `401` segera setelah pencabutan.
- Endpoint publik dipanggil dengan token invalid → tetap melayani (bila memang publik) atau `401`, konsisten dengan kontrak.

### Boundary Testing
- Request tepat sebelum `exp` → diterima; tepat sesudah `exp` → ditolak.
- Selisih clock server-client dalam batas toleransi → masih diterima.
- Token dengan `nbf` (not before) di masa depan → ditolak.
- Token berumur sangat panjang melampaui batas kebijakan → ditolak atau dianggap invalid.
- Nilai header sangat panjang / banyak segmen tambahan → ditolak rapi.

### Integration Testing
- Layanan autentikasi tidak tersedia → endpoint mengembalikan `503` (fail closed), bukan meloloskan request.
- Token diteruskan antar-service dengan benar (tidak hilang di gateway).
- Refresh token diputar (rotation): refresh lama tidak dapat dipakai ulang.
- Logout di satu perangkat tidak merusak sesi perangkat lain kecuali kebijakan menyatakan global.
- Perubahan role/status akun tercermin pada request berikutnya (tidak menunggu token kedaluwarsa lebih dari kebijakan).
- Cache tidak menyajikan respons terproteksi ke request tanpa token.

## Test Data
- Token valid untuk user aktif; token valid untuk user nonaktif.
- Token kedaluwarsa, token `nbf` di masa depan, token dengan signature diubah.
- Token dengan `alg: none`, `kid` tidak dikenal, `aud`/`iss` salah.
- Token yang sudah dicabut; refresh token lama setelah rotasi.
- Kredensial salah berulang (untuk melihat lockout/throttle, lihat `api-rate-limit`).

## Expected Results
- `401 Unauthorized` untuk semua kegagalan autentikasi, dengan `WWW-Authenticate: Bearer`.
- Tidak ada data resource yang dikembalikan saat autentikasi gagal.
- Signature, `exp`, `nbf`, `iss`, `aud`, dan status akun semuanya diverifikasi.
- Token yang dicabut langsung ditolak (dalam batas cache kebijakan).
- Error body tidak membedakan "token tidak ada" vs "signature salah" secara berlebihan.
- Endpoint fail closed saat layanan identitas tidak tersedia.

## Common Defects
- Token kedaluwarsa masih diterima karena `exp` tidak diperiksa.
- Signature tidak diverifikasi (hanya di-decode), sehingga token bisa dipalsukan.
- `alg: none` diterima atau algoritma ditentukan oleh header token (algorithm confusion).
- `kid` dipakai untuk memuat kunci dari sumber yang bisa dikendalikan penyerang.
- Token dicabut tetap berlaku sampai kedaluwarsa.
- `401` dikembalikan sebagai `403`/`500` sehingga client tidak melakukan re-autentikasi.
- Endpoint meloloskan request saat layanan auth timeout (fail open).
- Token tertulis di URL/query sehingga bocor ke log.
- Refresh token dapat dipakai berulang tanpa rotasi.

## Security Considerations
- Verifikasi signature dengan algoritma yang di-whitelist; jangan percaya `alg` dari token.
- Validasi `iss`, `aud`, `exp`, `nbf`, dan `kid` terhadap kunci yang dikenal.
- Jangan menaruh token di URL, log, atau pesan error.
- Terapkan pencabutan (denylist/versi token) agar logout dan ganti password efektif.
- Rate limit dan lockout pada endpoint autentikasi untuk mencegah brute force.
- Gunakan TLS; tolak token yang dikirim lewat koneksi tidak aman.

## References
- RFC 6750 — Bearer Token Usage (`WWW-Authenticate`, `401`).
- RFC 7519 — JSON Web Token (klaim `exp`, `nbf`, `iss`, `aud`).
- OWASP Web Security Testing Guide — WSTG-ATHN (authentication), WSTG-SESS (session).
- OWASP API Security Top 10 — API2 Broken Authentication.
