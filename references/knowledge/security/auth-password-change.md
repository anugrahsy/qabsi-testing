# Authentication Password Change Testing

## Overview
Menguji fitur **ubah password** yang dilakukan pengguna yang sudah login: verifikasi **password saat ini**, penetapan **password baru**, dan kebijakan terkait (riwayat password, invalidasi sesi). Risiko utama: ubah password tanpa memverifikasi password lama, password baru sama dengan lama, dan sesi lama tidak dirotasi.

## When to Apply
Fitur "ubah password" pada profil/pengaturan akun pengguna yang terautentikasi. Aplikasikan bersama `auth-password-reset` (bandingkan: ini jalur terautentikasi), `input-password`, dan `auth-session`.

## Testing Principles
1. Ubah password **wajib verifikasi password saat ini** (kecuali reset password).
2. Password baru harus **berbeda** dari password lama (dan tunduk kebijakan).
3. Kebijakan riwayat password (tidak boleh reuse N password terakhir) diterapkan bila kontrak menyatakan.
4. Setelah ganti password, **sesi/token lama diinvalidasi** (atau dirotasi) sesuai kontrak.
5. Transmisi password wajib terenkripsi; password tidak boleh muncul di response/log.

## Test Design Techniques
- Equivalence Partitioning — password lama benar/salah, password baru valid/invalid.
- Boundary Value Analysis — panjang password baru min/max.
- State Transition — status sesi setelah password berubah.
- Decision Table — kombinasi password lama × password baru × kebijakan.

## Test Scenarios

### Positive Testing
- Password lama benar + password baru valid → berhasil, password baru berlaku.
- Login dengan password baru → berhasil; password lama → ditolak.
- Sesi lain diinvalidasi (atau dirotasi) setelah ganti password sesuai kontrak.
- Konfirmasi/notifikasi keamanan terkirim (sesuai kontrak).

### Negative Testing
- Password lama salah → ditolak.
- Password baru sama dengan password lama → ditolak.
- Password baru tidak memenuhi kebijakan kompleksitas → ditolak.
- Password baru menyalahi riwayat (reuse) → ditolak (bila kebijakan ada).
- Field kosong / konfirmasi tidak cocok → ditolak validasi.
- Ganti password tanpa autentikasi → ditolak.

### Boundary Testing
- Password baru tepat di panjang minimum/maksimum.
- Riwayat reuse: password ke-N yang dilarang vs ke-(N+1) yang boleh.
- Karakter khusus/Unicode pada password baru → sesuai kebijakan.

### Integration Testing
- Ubah password + `auth-session`/`auth-token` — token lama tidak bisa dipakai lagi.
- Ubah password + audit log — kejadian tercatat.
- Ubah password + `auth-password-reset` — kedua jalur konsisten soal kebijakan password.

## Test Data
- Akun dengan password lama yang diketahui benar/salah.
- Set password baru: valid, sama-dengan-lama, reuse riwayat, tak memenuhi kebijakan.
- Sesi/token aktif di beberapa perangkat.

## Expected Results
- Password lama salah → ditolak (`400`/`401`).
- Password baru valid dan berbeda → berhasil, password lama tidak berlaku.
- Riwayat password diterapkan (reuse ditolak) sesuai kontrak.
- Sesi/token lama tidak lagi valid setelah perubahan (atau sesuai kebijakan rotasi).
- Tidak ada password terekspos di response/log.

## Common Defects
- Ubah password tanpa memverifikasi password lama (perlu autentikasi ulang).
- Password baru boleh sama dengan lama.
- Riwayat password tidak dicek (bisa reuse password lama).
- Sesi/token lama tetap valid setelah ganti password.
- Konfirmasi password hanya dicek di client (bisa di-bypass via API).

## Security Considerations
- Account takeover bila endpoint ubah password tanpa verifikasi password lama.
- Reuse password → risiko bila password lama pernah bocor.
- Session fixation / sesi lama tidak dirotasi setelah perubahan.

## References
- OWASP WSTG — Testing for Weak Password Reset / Change (WSTG-ATHN-07)
- OWASP ASVS — V2 Authentication (password security)
- ISTQB CTFL v4.0.1 — teknik test design
