# Input Username Validation Testing

## Overview
Menguji validasi username: karakter yang diizinkan, panjang, keunikan, dan reserved words. Risiko utama: karakter khusus tak ditangani, duplikat case-insensitive tidak terdeteksi, username menyerupai reserved path/role, dan normalisasi tidak konsisten.

## When to Apply
Form registrasi, login dengan username, profil, atau endpoint yang memakai username sebagai identitas publik (handle, display name).

## Testing Principles
1. Tentukan **charset yang diizinkan** secara eksplisit (alfanumerik, titik, underscore, dsb) — kontrak aplikasi.
2. Keunikan ditentukan kasusnya (case-insensitive vs case-sensitive) — dokumentasikan.
3. Reserved words (mis. `admin`, `root`, `system`, path seperti `api`, `login`) harus didefinisikan.
4. Normalisasi (trim, lowercase) konsisten antara saat simpan & saat login/pencarian.
5. Bedakan username (login) vs display name (boleh bebas) — aturan berbeda.

## Test Design Techniques
- Equivalence Partitioning — kelas karakter valid/invalid, kelas reserved.
- Boundary Value Analysis — panjang minimum/maksimum.
- Decision Table — kombinasi charset × uniqueness × reserved.

## Test Scenarios

### Positive Testing
- Username alfanumerik valid → diterima.
- Username dengan karakter khusus yang diizinkan (`.` `_` `-`) → diterima.
- Username dengan panjang dalam batas → diterima.

### Negative Testing
- Kosong / hanya spasi → ditolak.
- Mengandung spasi (jika dilarang) → ditolak.
- Mengandung karakter khusus dilarang (`@`, `#`, `/`, `\`) → ditolak.
- Mengandung karakter Unicode/emoji (jika dilarang) → ditolak.
- Reserved word (`admin`, `system`, `api`) → ditolak sesuai kontrak.
- Duplikat (beda casing) → ditolak.

### Boundary Testing
- Panjang = min-1 → ditolak; = min → diterima; = max → diterima; = max+1 → ditolak.
- Leading/trailing whitespace → ditrim/ditolak sesuai kontrak.

### Integration Testing
- Uniqueness saat create vs update milik sendiri.
- Login dengan username ternormalisasi (case-insensitive) cocok dengan data tersimpan.
- Username dipakai sebagai URL/handle → valid sebagai path segment (tidak konflik reserved path).

## Test Data
- Username valid & invalid (per charset kontrak).
- Username dengan panjang batas.
- Duplikat beda casing.
- Daftar reserved words & path.
- Username dengan whitespace, karakter kontrol, Unicode.

## Expected Results
- Username valid diterima; invalid ditolak dengan pesan aturan.
- Uniqueness & reserved rules konsisten.
- Normalisasi (lowercase/trim) konsisten antara simpan & login.

## Common Defects
- Charset tidak dibatasi → injeksi/ambiguitas.
- Uniqueness case-sensitive → duplikat visual.
- Reserved words lolos → konflik route/role.
- Whitespace tak terlihat (zero-width, NBSP) lolos.
- Normalisasi berbeda saat simpan vs login.

## Security Considerations
- OWASP Input Validation Cheat Sheet — whitelist charset, server-side.
- Reserved words/path traversal: username jangan mengganggu routing (`..`, `/`).
- Username enumeration: respon berbeda untuk username terdaftar vs tidak.

## References
- OWASP Input Validation Cheat Sheet
- OWASP Authentication Cheat Sheet
