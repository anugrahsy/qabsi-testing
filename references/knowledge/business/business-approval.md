# Business Approval Testing

## Overview
Menguji **alur persetujuan (approval)**: menyetujui, menolak, mendelegasikan, dan eskalasi keputusan. Risiko utama: keputusan bisa diambil oleh pihak yang tidak berwenang, penolakan tanpa alasan/tindak lanjut, delegasi mengubah otoritas tanpa jejak, dan keputusan ganda pada objek yang sama.

## When to Apply
Fitur yang butuh persetujuan berjenjang atau berperan: approve/reject, tanda tangan pejabat, validasi bertingkat (L1/L2/L3), dan alur delegasi wewenang. Aplikasikan bersama `business-workflow`, `business-status-transition`, `business-audit`.

## Testing Principles
1. Approval adalah **transisi status dengan otoritas khusus** — modelkan sebagai state transition.
2. Keputusan (approve/reject) harus **terikat aktor + waktu + alasan**.
3. Delegasi harus **eksplisit, terbatas waktu/lingkup, dan terdokumentasi** — tidak boleh mengubah otoritas secara diam-diam.
4. Satu objek tidak boleh punya **dua keputusan yang saling bertentangan** secara bersamaan.
5. Penolakan harus punya **alur tindak lanjut** (perbaikan, pengajuan ulang, banding) — bukan terminal mati.
6. Quorum / aturan kolektif (jika ada) harus ditegakkan.

## Test Design Techniques
- State Transition — draft/pending/approved/rejected/delegated sebagai state.
- Decision Table — kondisi keputusan (setuju + syarat, tolak + alasan).
- Equivalence Partitioning — tipe keputusan dan otoritas.
- Use Case Scenario — happy path approval dan jalur penolakan/delegasi.

## Test Scenarios

### Positive Testing
- Approver sah menyetujui → status berubah menjadi approved + tercatat.
- Approver sah menolak dengan alasan → status rejected + alasan tersimpan.
- Delegasi sah → penerima delegasi dapat bertindak dalam lingkup yang didelegasikan.
- Keputusan berjenjang maju ke approver berikutnya sesuai urutan.

### Negative Testing
- Aktor tanpa wewenang approve/reject → ditolak.
- Approve objek yang sudah approved → ditolak (atau idempoten sesuai kontrak).
- Reject objek yang sudah rejected → ditolak.
- Delegasi ke pihak yang tidak sah / di luar lingkup → ditolak.
- Delegasi kedaluwarsa digunakan → ditolak.
- Approve tanpa memenuhi prasyarat (dokumen belum lengkap) → ditolak.

### Boundary Testing
- Delegasi tepat pada batas waktu berakhir → perilaku di titik akhir.
- Approval berjenjang pada tahap pertama vs tahap terakhir (tidak ada approver berikutnya).
- Keputusan pada objek tanpa approver terdefinisi → ditangani eksplisit.

### Integration Testing
- Approval + workflow: keputusan menggerakkan tahap (lihat `business-workflow`).
- Approval + status transition: transisi approve/reject yang sah (lihat `business-status-transition`).
- Approval + audit: siapa, kapan, keputusan apa (lihat `business-audit`).
- Approval + notifikasi ke pihak terkait pada tiap keputusan.
- Penolakan → pengajuan ulang (resubmit) membuka kembali alur dengan benar.

## Test Data
- Akun dengan peran berbeda (pemohon, approver L1/L2/L3, penerima delegasi, admin).
- Objek dalam berbagai status (draft, pending, approved, rejected).
- Delegasi aktif, kedaluwarsa, dan di luar lingkup.
- Alasan penolakan (wajib vs opsional sesuai kontrak).

## Expected Results
- Hanya pihak berwenang yang dapat mengambil keputusan.
- Keputusan mengubah status secara benar dan tercatat (aktor, waktu, alasan).
- Delegasi hanya berlaku dalam lingkup dan waktu yang ditentukan.
- Tidak ada keputusan ganda/bertentangan pada objek yang sama.

## Common Defects
- Pemeriksaan otoritas hanya di UI — keputusan bisa dipalsukan via API.
- Delegasi tidak punya batas waktu/lingkup — wewenang bocor permanen.
- Penolakan tidak menyimpan alasan atau tidak punya alur tindak lanjut.
- Keputusan ganda bisa menimpa keputusan sebelumnya.
- Urutan approver berjenjang tidak ditegakkan (bisa dilompati).
- Jejak delegasi tidak tercatat sehingga sulit diaudit.

## Security Considerations
- IDOR/eskalasi: aktor memanipulasi ID objek untuk menyetujui objek di luar wewenang.
- Delegasi sebagai permukaan serangan — wajib divalidasi dan diaudit server-side.
- Integritas keputusan: keputusan tidak boleh diubah setelah tercatat tanpa jejak.

## References
- ISTQB CTFL v4.0.1 — State Transition Testing, Decision Table.
- OWASP Web Security Testing Guide — Authorization, Business Logic.
