# Input Email Validation Testing

## Overview
Menguji validasi input alamat email: sintaks format, domain, keunikan, dan normalisasi. Risiko utama: format valid ditolak (false negative), format invalid lolos (false positive), email duplikat tidak terdeteksi, dan normalisasi tidak konsisten (mis. `User@Example.com` vs `user@example.com`).

## When to Apply
Form registrasi, login, profil, notifikasi email, atau endpoint yang menerima field email — terutama saat email dipakai sebagai identitas atau kontak pengguna.

## Testing Principles
1. Bedakan validasi **sintaks** (format) vs **keberadaan/deliverability** (domain benar, email terkirim) — jangan digabung; deliverability bukan bagian validasi input.
2. Normalisasi harus **konsisten dan terdokumentasi**: lowercase domain, trim whitespace, dsb.
3. Uniqueness ditentukan kasusnya: case-insensitive, trailing dot, alias `+` (jika didukung) — dokumentasikan.
4. Karakter yang diizinkan mengikuti RFC 5322 (dan RFC 6531 untuk email internationalized/IDN) — putuskan dukungan non-ASCII sebelum testing.
5. Jangan buat expected result seolah aturan kompleksitas (mis. TLD harus 2-3 huruf) wajib, kecuali kontrak menyatakannya.

## Test Design Techniques
- Equivalence Partitioning — kelas format valid vs invalid (local-part, domain, TLD).
- Boundary Value Analysis — panjang maksimum (local-part 64, total 255 per RFC).
- Decision Table — kombinasi format × uniqueness × normalisasi.

## Test Scenarios

### Positive Testing
- Format standar `user@example.com` diterima.
- Local-part dengan titik `first.last@example.com` diterima (jika didukung).
- Local-part dengan tag `+` (`user+tag@example.com`) diterima (jika didukung).
- Domain subdomain `user@sub.example.co.id` diterima.
- Email internationalized/IDN diterima/ditolak sesuai kontrak.
- Whitespace di sekitar ter-trim.

### Negative Testing
- Tanpa `@` → ditolak.
- Tanpa local-part (`@example.com`) → ditolak.
- Tanpa domain (`user@`) → ditolak.
- Spasi di tengah → ditolak.
- Dua `@` → ditolak.
- Karakter invalid di local-part → ditolak.
- Domain tanpa titik/TLD → ditolak sesuai kontrak.

### Boundary Testing
- Local-part 64 karakter → diterima; 65 → ditolak (RFC 5322).
- Total 254 karakter → diterima; 255/256 → ditolak.
- Panjang label domain (subdomain) maksimum → sesuai kontrak.

### Integration Testing
- Uniqueness: email terdaftar ditolak saat create; diizinkan saat update milik sendiri.
- Normalisasi: `User@Example.com` vs `user@example.com` diperlakukan sama (case-insensitive) sesuai kontrak.
- Email + password saat login → email ternormalisasi cocok dengan data tersimpan.

## Test Data
- Kumpulan email valid & invalid (mencakup local-part/domain/TLD).
- Email dengan local-part/domain panjang maksimum.
- Email duplikat beda casing (untuk uniqueness).
- Email dengan whitespace, trailing dot, tag `+`.
- IDN/email Unicode (jika didukung).

## Expected Results
- Format valid diterima; invalid ditolak dengan pesan jelas.
- Normalisasi konsisten (trim, lowercase sesuai aturan).
- Duplikat (case-insensitive) ditolak.
- Pesan error menyebut field & alasan, bukan generic "invalid".

## Common Defects
- Regex terlalu ketat menolak email valid (mis. TLD > 3 karakter, tag `+`).
- Regex terlalu longgar menerima email invalid (mis. spasi, double dot).
- Uniqueness check case-sensitive → duplikat `User@x.com` vs `user@x.com`.
- Normalisasi tidak diterapkan → login gagal karena beda casing.
- Deliverability disamakan dengan validasi sintaks (false negative).

## Security Considerations
- OWASP Input Validation Cheat Sheet — validasi server-side, jangan andalkan client-side.
- Email sebagai identitas → hindari account enumeration (respon berbeda untuk email terdaftar vs tidak).
- Normalisasi mencegah duplikasi akun / identity spoofing.

## References
- RFC 5322 (Internet Message Format)
- RFC 6531 (SMTPUTF8 / internationalized email)
- OWASP Input Validation Cheat Sheet
