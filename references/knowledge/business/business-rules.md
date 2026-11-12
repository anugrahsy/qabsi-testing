# Business Rules Testing

## Overview
Menguji **validasi aturan bisnis** — kondisi, kendala, dan ketentuan yang harus dipenuhi sebelum atau selama sebuah operasi dijalankan. Risiko utama: aturan hanya diterapkan sebagian, pengecualian tidak ditangani, aturan saling konflik, dan aturan bisa dilewati (bypass) karena hanya dicek di satu lapisan (mis. UI saja, bukan API).

## When to Apply
Fitur yang punya aturan bisnis eksplisit: syarat eligibilitas, batas nilai maksimum/minimum, diskon dan potongan, ketentuan periode (cut-off, semester, tahun anggaran), kebijakan kombinasi, dan syarat prasyarat sebelum submit/proses. Modul ini dasar bagi `business-workflow`, `business-approval`, `business-calculation`.

## Testing Principles
1. Aturan bisnis adalah **expected behavior** yang berasal dari kontrak/PRD, bukan standar industri — uji sesuai kontrak.
2. Setiap aturan berbentuk **kondisi (if) + konsekuensi (then)** — uji keduanya, bukan hanya kondisi.
3. Aturan **saling berinteraksi** — uji kombinasi, bukan hanya satu per satu.
4. Pengecualian (override/relaksasi) harus eksplisit, punya otoritas jelas, dan tercatat.
5. Prioritas berbasis risiko: aturan bernilai finansial/legal diuji lebih ketat daripada aturan kosmetik.
6. Tidak semua input berlaku untuk semua aturan — jangan asumsikan aturan universal.

## Test Design Techniques
- Decision Table — kombinasi kondisi aturan dan aksi yang dihasilkan.
- Equivalence Partitioning — kelompok nilai yang diperlakukan sama oleh aturan.
- Boundary Value Analysis — batas nilai yang menentukan lolos/gagal aturan.
- Combinatorial Testing — interaksi antar aturan (pairwise bila banyak aturan).
- State Transition — bila aturan bergantung pada status (delegasi ke `business-status-transition`).

## Test Scenarios

### Positive Testing
- Semua kondisi aturan terpenuhi → operasi berhasil.
- Nilai tepat pada batas yang diperbolehkan → lolos.
- Aturan dengan opsi default/standar → berjalan sesuai default.
- Pengecualian yang sah (dengan otoritas tepat) → diterapkan.

### Negative Testing
- Satu kondisi aturan dilanggar → operasi ditolak dengan pesan jelas.
- Input kosong/`null`/tidak terdefinisi → ditolak sesuai aturan.
- Nilai di luar ketentuan → ditolak, bukan diterima diam-diam.
- Pengecualian tanpa otoritas sah → ditolak.

### Boundary Testing
- Nilai tepat batas minimum → lolos.
- Nilai tepat batas maksimum → lolos.
- Nilai tepat satu di bawah minimum → ditolak.
- Nilai tepat satu di atas maksimum → ditolak.
- Batas yang berubah karena periode (cut-off tanggal) → diuji pada titik transisi.

### Integration Testing
- Kombinasi dua atau lebih aturan sekaligus → hasil sesuai tabel keputusan.
- Aturan + role/otoritas (lihat `auth-rbac`, `auth-object-access`).
- Aturan + periode/waktu (lihat `business-scheduling`).
- Aturan diterapkan konsisten di UI, API, dan proses batch/background.

## Test Data
- Nilai batas (min, max, min-1, max+1) untuk tiap aturan.
- Kombinasi nilai yang memicu konflik antar aturan.
- Data lintas periode (sebelum/setelah cut-off).
- Akun/role berbeda (untuk verifikasi pengecualian/otoritas).

## Expected Results
- Operasi berjalan **hanya bila semua aturan terpenuhi** (atau pengecualian sah).
- Penolakan konsisten di semua lapisan (UI, API, batch) dengan pesan yang menjelaskan aturan mana yang dilanggar.
- Tidak ada eksekusi parsial (sebagian efek terjadi, sebagian tidak).
- Pengecualian tercatat dan bisa diaudit.

## Common Defects
- Aturan hanya dicek di UI, tidak di API/backend (mudah di-bypass).
- Urutan evaluasi aturan salah sehingga hasil berbeda.
- Pengecualian tidak tercatat / tidak diaudit.
- Aturan di-hardcode per role/user, bukan berdasar kebijakan.
- Konflik antar aturan tidak diresolve → hasil tidak deterministik.
- Pesan error tidak menyebut aturan yang dilanggar.

## Security Considerations
- Business logic flaw (OWASP WSTG-ATHZ/BUSLOGIC): manipulasi parameter untuk melewati aturan.
- Jangan andalkan validasi client-side saja; aturan wajib ditegakkan server-side.
- Pengecualian/override adalah permukaan serangan — batasi otoritas dan audit.

## References
- ISTQB CTFL v4.0.1 — Decision Table, Equivalence Partitioning, Boundary Value Analysis.
- OWASP Web Security Testing Guide — Business Logic Testing.
