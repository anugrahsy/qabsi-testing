# Input Enum Validation Testing

## Overview
Menguji validasi input enum (nilai dari daftar tetap): allowed values, invalid values, dan case sensitivity. Risiko utama: nilai di luar daftar diterima, case sensitivity tidak konsisten, dan daftar nilai valid tidak sinkron antara UI dan backend.

## When to Apply
Field yang nilainya terbatas: status, tipe, kategori, role, pilihan dropdown/multi-select.

## Testing Principles
1. Tentukan **daftar nilai valid** secara eksplisit (enum set).
2. Tentukan **case sensitivity**: enum umumnya case-sensitive & exact match (`ACTIVE` ≠ `active`) — konsisten di semua jalur.
3. Nilai tidak dikenal harus **ditolak (fail closed)** — jangan di-silent-default.
4. Nilai numerik vs string untuk enum: konsisten, jangan campur `1` dan `"1"`.
5. Default & kosong: apakah enum boleh kosong/null (optional) atau wajib diisi.

## Test Design Techniques
- Equivalence Partitioning — kelas nilai valid (setiap anggota enum) vs invalid.
- Boundary Value Analysis — relevan jika enum bernilai numerik/berurutan.
- State Transition — enum sebagai status yang transisinya dibatasi (delegasi `business-status-transition`).

## Test Scenarios

### Positive Testing
- Setiap nilai enum valid → diterima.
- Nilai enum dengan casing tepat (jika case-sensitive) → diterima.
- Enum optional kosong/null → diterima sesuai kontrak.

### Negative Testing
- Nilai di luar daftar → ditolak.
- Casing berbeda (`active` vs `ACTIVE`) → ditolak/diterima sesuai kontrak (harus konsisten).
- Kosong/null saat wajib → ditolak.
- Nilai numerik vs string tidak konsisten → ditolak.
- Whitespace di sekitar nilai → ditolak/ditrim sesuai kontrak.

### Boundary Testing
- Enum bernilai numerik: batas bawah/atas (jika relevan).
- Enum dengan satu-satunya nilai valid vs banyak nilai.

### Integration Testing
- Nilai enum konsisten antara validasi input & penggunaannya di business logic (status/role).
- Nilai enum disimpan & dibaca kembali → tidak berubah.
- Daftar enum backend sinkron dengan opsi UI (tidak ada opsi yang jika dipilih ditolak).

## Test Data
- Semua nilai enum valid, diuji satu per satu.
- Nilai invalid: di luar daftar, casing beda, whitespace, null, kosong.
- Nilai numerik vs string untuk enum yang sama.
- Daftar enum penuh (untuk cek sinkronisasi UI).

## Expected Results
- Nilai enum valid diterima; invalid ditolak dengan pesan jelas.
- Case sensitivity konsisten dengan kontrak di semua jalur.
- Nilai tidak dikenal ditolak (fail closed).

## Common Defects
- Nilai di luar enum diterima (validasi longgar).
- Case sensitivity tidak konsisten (sebagian jalur menerima, sebagian menolak).
- Nilai tidak dikenal diabaikan diam-diam → default tak terduga.
- Enum numerik & string dicampur (`1` vs `"1"`).
- Daftar enum UI tidak sinkron dengan backend.

## Security Considerations
- OWASP Input Validation Cheat Sheet — whitelist enum (fail closed).
- Enum dipakai untuk authorization/status → nilai tak valid bisa bypass logic; validasi wajib ketat.
- Jangan expose enum internal yang tidak relevan ke publik.

## References
- OWASP Input Validation Cheat Sheet
- OpenAPI Specification (enum)
