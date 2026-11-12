# Business Workflow Testing

## Overview
Menguji **workflow / tahapan proses bisnis** — rangkaian langkah berurutan yang membawa sebuah objek dari awal hingga selesai. Risiko utama: tahap bisa dilewati, urutan tidak ditegakkan, objek tersangkut di tahap tertentu, dan aktor yang salah bisa maju/mundur tahap.

## When to Apply
Fitur multi-tahap: pengajuan bertingkat, proses yang melewati beberapa unit/aktor, alur dengan kondisi percabangan, dan proses yang punya urutan wajib (mis. draft → submit → review → final). Aplikasikan bersama `business-status-transition`, `business-approval`, `business-audit`.

## Testing Principles
1. Workflow punya **urutan tahap yang harus ditegakkan** — tidak boleh ada tahap yang terlewati.
2. Setiap tahap punya **aktor/pelaku dan aksi** yang sah — uji siapa boleh apa di tahap mana.
3. Percabangan (branching) didasari **kondisi eksplisit** — uji tiap cabang.
4. Objek harus selalu berada di **satu tahap yang valid** — tidak boleh stuck atau ambigu.
5. Maju/mundur tahap adalah transisi — perlakukan sebagai state transition (lihat `business-status-transition`).
6. Rollback/pengembalian tahap harus mengembalikan kondisi data yang konsisten.

## Test Design Techniques
- State Transition — tahap sebagai state, aksi sebagai transisi (wajib).
- Decision Table — kondisi percabangan menuju tahap berikutnya.
- Path Testing / Use Case Scenario — jalur utama (happy path) dan jalur alternatif.
- Equivalence Partitioning — kelompok input yang menentukan cabang.

## Test Scenarios

### Positive Testing
- Happy path: objek melewati seluruh tahap berurutan sampai selesai.
- Percabangan valid → objek menuju tahap yang benar sesuai kondisi.
- Setiap aksi tahap menghasilkan status/efek yang sesuai.
- Aktor yang sah melakukan aksi di tahap yang benar → berhasil.

### Negative Testing
- Mencoba melompati tahap (skip) → ditolak.
- Mencoba aksi tahap N+1 saat masih di tahap N → ditolak.
- Aktor yang tidak sah memajukan/memundurkan tahap → ditolak.
- Aksi ganda pada tahap yang sama → ditangani (idempoten atau ditolak).
- Mundur ke tahap yang tidak diperbolehkan → ditolak.

### Boundary Testing
- Objek di tahap pertama (belum ada pendahulu) — mundur tidak dimungkinkan.
- Objek di tahap terakhir (sudah final) — maju tidak dimungkinkan, hanya mundur bila diizinkan.
- Kondisi percabangan tepat pada nilai ambang → cabang yang benar dipilih.

### Integration Testing
- Workflow + approval (lihat `business-approval`).
- Workflow + status transition (lihat `business-status-transition`).
- Workflow + audit trail (lihat `business-audit`) — tiap perpindahan tercatat.
- Workflow + notifikasi/aktifitas turunan yang terpicu pada tiap tahap.

## Test Data
- Objek di tiap tahap (untuk mempersingkat setup saat menguji transisi).
- Akun dengan role/aktor berbeda (pemohon, reviewer, approver, admin).
- Kombinasi kondisi percabangan.
- Data yang memicu tiap cabang alternatif.

## Expected Results
- Objek hanya berpindah tahap lewat transisi yang sah dan berurutan.
- Setiap perpindahan tercatat (aktor, waktu, dari→ke).
- Kondisi percabangan menghasilkan tahap tujuan yang benar.
- Objek tidak pernah berada dalam tahap yang tidak valid/stuck.

## Common Defects
- Tahap bisa di-skip karena validasi urutan tidak ditegakkan.
- Aksi tidak dicek terhadap tahap saat ini (bisa maju dari tahap mana pun).
- Aktor tidak dibatasi per tahap (siapa pun bisa maju).
- Percabangan memilih cabang salah karena kondisi dievaluasi tidak benar.
- Objek stuck karena tidak ada transisi keluar dari suatu tahap.
- Efek samping tahap (notifikasi, log) tidak terpicu konsisten.

## Security Considerations
- Otorisasi per tahap: aktor tidak boleh menjalankan aksi di luar tahap/otoritasnya.
- Manipulasi identitas tahap lewat parameter (ID tahap) untuk mem-bypass urutan.
- Transisi wajib divalidasi server-side, bukan hanya disembunyikan di UI.

## References
- ISTQB CTFL v4.0.1 — State Transition Testing, Decision Table.
- OWASP Web Security Testing Guide — Business Logic, Authorization.
