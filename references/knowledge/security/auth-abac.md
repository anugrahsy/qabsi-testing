# Authorization ABAC Testing

## Overview
Menguji **Attribute-Based Access Control (ABAC)**: keputusan akses berdasarkan **atribut** subjek (user), objek (resource), aksi, dan konteks/lingkungan — bukan sekadar role. Risiko utama: atribut hilang/ambigu dievaluasi salah, kebijakan saling konflik, dan kombinasi atribut yang tidak teruji lolos/tertolak keliru.

## When to Apply
Sistem yang otorisasinya bergantung atribut dinamis: unit organisasi (X-Organization), jabatan, status data, waktu, lokasi, atau relasi pemilik — bukan role statis semata. Aplikasikan bersama `auth-rbac` dan `auth-object-access`.

## Testing Principles
1. Tentukan **atribut keputusan** (subjek/objek/aksi/lingkungan) dan kebijakan evaluasinya.
2. Uji **kombinasi atribut** yang menentukan keputusan — bukan atribut tunggal.
3. Atribut **missing/null** harus dievaluasi eksplisit (default deny atau sesuai kebijakan).
4. Kebijakan yang **saling bertentangan** harus punya aturan resolusi (deny-overrides/permit-overrides).
5. Perubahan atribut harus langsung memengaruhi keputusan (jangan stale).

## Test Design Techniques
- Combinatorial Testing — kombinasi atribut (pairwise bila atribut banyak).
- Decision Table — matriks atribut × keputusan akses.
- Equivalence Partitioning — nilai atribut yang diizinkan vs tidak.
- Boundary Value Analysis — batas nilai atribut (rentang, tanggal, level).

## Test Scenarios

### Positive Testing
- Kombinasi atribut yang memenuhi kebijakan → akses diizinkan.
- Atribut objek (mis. unit organisasi) sesuai → akses diizinkan.
- Perubahan atribut (mis. pindah unit) langsung mengubah keputusan akses.

### Negative Testing
- Kombinasi atribut yang tidak memenuhi → ditolak (`403`).
- Atribut missing/null → dievaluasi eksplisit (deny sesuai kebijakan).
- Atribut di luar domain yang dikenal → ditolak/ditangani aman.
- Subjek mencoba memanipulasi atribut (mis. mengubah header konteks) → ditolak.
- Kebijakan konflik → resolusi sesuai aturan (deny-overrides default).

### Boundary Testing
- Nilai atribut tepat di batas (mis. batas tanggal/rentang level) → keputusan sesuai.
- Atribut kosong vs tidak ada (empty vs missing) → beda evaluasi sesuai kontrak.
- Kombinasi atribut minimum yang cukup vs yang kurang satu syarat.

### Integration Testing
- ABAC + `auth-object-access` — kepemilikan resource sebagai atribut objek.
- ABAC + `auth-rbac` — role sebagai salah satu atribut subjek.
- ABAC + header konteks (`X-Organization`) — atribut lingkungan diterapkan konsisten.

## Test Data
- Set nilai atribut subjek/objek/aksi/lingkungan.
- Kombinasi atribut valid/invalid (termasuk pairwise).
- Atribut missing/null/empty.
- Kebijakan yang saling konflik (untuk uji resolusi).

## Expected Results
- Kombinasi atribut memenuhi kebijakan → diizinkan; selain itu → `403`.
- Atribut missing/null → default deny (atau sesuai kebijakan eksplisit).
- Perubahan atribut langsung mengubah keputusan akses.
- Konflik kebijakan diselesaikan konsisten (deny-overrides).

## Common Defects
- Keputusan hanya bergantung satu atribut (atribut lain diabaikan).
- Atribut missing/null dievaluasi sebagai allow (default allow).
- Kebijakan konflik tidak punya resolusi → hasil nondeterministik.
- Atribut dari client (header) dipercaya tanpa validasi server.
- Perubahan atribut tidak langsung berefek (cache/stale).

## Security Considerations
- Manipulasi atribut client-side (header/claim) untuk naikkan akses.
- Default allow pada atribut yang tidak dikenali.
- Kebijakan terlalu kompleks → celah kombinasi atribut tidak teruji.
- Atribut stale (data unit/jabatan lama) memberi akses keliru.

## References
- OWASP WSTG — Testing for Authorization (WSTG-ATHZ)
- OWASP ASVS — V4 Access Control
- NIST SP 800-162 (ABAC)
- ISTQB CTFL v4.0.1 — combinatorial/decision table testing
