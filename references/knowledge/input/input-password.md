# Input Password Validation Testing

## Overview
Menguji validasi password: panjang minimum/maksimum, aturan kompleksitas, dan perlakuan whitespace. Risiko utama: aturan terlalu lemah (mudah ditebak) atau terlalu kaku (user frustrasi), whitespace tak terdeteksi, dan password tersimpan/log tanpa proteksi.

## When to Apply
Form pendaftaran, ganti password, reset password, atau endpoint yang menerima password baru. Bukan untuk testing penyimpanan hash (lihat `auth-password-*`).

## Testing Principles
1. Ikuti NIST SP 800-63B: panjang lebih penting dari kompleksitas; rekomendasi minimum 8 karakter, izinkan maksimum besar (mis. 64+).
2. Izinkan **semua karakter termasuk spasi** (NIST) — putuskan kontrak: spasi diizinkan, ditrim, atau dilarang.
3. Komposisi wajib (huruf+angka+simbol) tidak selalu wajib — kontrak aplikasi yang menentukan.
4. Bedakan validasi **saat set** vs **saat verifikasi** (login tidak menerapkan aturan kompleksitas).
5. Batas maksimum wajib ada (mis. 64) untuk cegah DoS pada proses hashing.

## Test Design Techniques
- Equivalence Partitioning — kelas panjang (terlalu pendek, valid, terlalu panjang) & kelas kompleksitas.
- Boundary Value Analysis — panjang minimum & maksimum (min-1, min, min+1; max-1, max, max+1).
- Decision Table — kombinasi panjang × kompleksitas.

## Test Scenarios

### Positive Testing
- Password memenuhi panjang & kompleksitas minimum → diterima.
- Password panjang (mis. 64+ karakter) → diterima.
- Password dengan spasi (jika diizinkan kontrak) → diterima.
- Password dengan simbol/Unicode (jika diizinkan) → diterima.

### Negative Testing
- Kosong → ditolak.
- Lebih pendek dari minimum → ditolak.
- Hanya huruf / hanya angka / hanya simbol (jika kompleksitas wajib) → ditolak.
- Mengandung karakter kontrol / null → ditolak.
- Sama dengan username/email → ditolak (jika aturan kemiripan ada).

### Boundary Testing
- Panjang = min-1 → ditolak; = min → diterima; = min+1 → diterima.
- Panjang = max → diterima; = max+1 → ditolak.
- Whitespace leading/trailing: ditrim, ditolak, atau dihitung — konsisten dengan kontrak.

### Integration Testing
- Set password → login dengan password baru berhasil.
- Reset password → password lama tidak berlaku lagi.
- Password baru sama dengan sebelumnya → ditolak/diizinkan sesuai kebijakan reuse.
- Aturan kompleksitas konsisten antara form & endpoint (tidak hanya client-side).

## Test Data
- Password panjang 0, min-1, min, min+1, max, max+1.
- Variasi komposisi (huruf saja, angka saja, campuran, dengan simbol).
- Password dengan spasi leading/trailing/tengah.
- Password sama dengan username/email (untuk aturan kemiripan).
- Daftar password umum (untuk deny-list, jika ada).

## Expected Results
- Password valid diterima; invalid ditolak dengan pesan aturan yang jelas.
- Aturan konsisten di semua jalur (form & API).
- Whitespace diperlakukan sesuai kontrak (tidak ambigu).
- Tidak ada pesan/log yang mengekspos karakter password.

## Common Defects
- Minimum terlalu pendek atau tidak ada.
- Maksimum terlalu kecil atau tidak ada (risiko DoS hashing).
- Spasi/whitespace tak terlihat tidak terdeteksi.
- Validasi hanya client-side → bypass lewat API.
- Password ditulis ke log / pesan error (leak).
- Aturan kompleksitas diterapkan saat login (seharusnya hanya saat set).

## Security Considerations
- NIST SP 800-63B — panjang minimum, izinkan semua karakter, hindari komposisi wajib berlebihan.
- OWASP — validasi server-side; jangan log password; kirim via TLS.
- Cegah DoS via password sangat panjang (batas maksimum + rate limit).
- Jangan tampilkan password di UI/log/respon.

## References
- NIST SP 800-63B (Digital Identity Guidelines — Authentication)
- OWASP Authentication Cheat Sheet
- OWASP Input Validation Cheat Sheet
