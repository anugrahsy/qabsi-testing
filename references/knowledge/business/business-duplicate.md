# Business Duplicate Testing

## Overview
Menguji **duplicate submission** — pencegahan dan penanganan data ganda dari sisi bisnis (bukan sekadar unique constraint database). Risiko utama: submit berulang membuat record kembar, double-click/double-submit lolos, duplikat lintas sesi/user tidak terdeteksi, dan pengecekan duplikat bisa di-bypass.

## When to Apply
Operasi create/submit yang tidak boleh menghasilkan data kembar: pendaftaran, pengajuan, pemesanan, entri satu-per-periode. Aplikasikan bersama `api-post-create`, `api-idempotency`, `data-duplicate`, `ui-behavior` (double-click guard).

## Testing Principles
1. Bedakan tiga lapis: **UI guard** (double-click), **API idempotency** (request berulang), **business rule duplikat** (data identik dari waktu/sesi berbeda) — uji ketiganya terpisah.
2. Penanganan duplikat harus **didefinisikan kontrak**: ditolak dengan error, atau dianggap sukses mengembalikan record yang sudah ada.
3. Definisi "duplikat" harus jelas: field apa saja yang menentukan (kombinasi kunci bisnis), termasuk normalisasi (whitespace, case) bila relevan.
4. Duplikat yang **sah secara bisnis** (mis. item sama di transaksi berbeda) tidak boleh ikut terblokir.
5. Penghapusan/soft-delete lalu buat ulang → perilaku duplikat harus sesuai kontrak (record terhapus masih dianggap duplikat atau tidak).

## Test Design Techniques
- Equivalence Partitioning — data identik vs berbeda pada field kunci.
- Boundary Value Analysis — selisih minimal yang membuat data tidak dianggap duplikat.
- Combinatorial Testing — kombinasi field kunci yang sama/beda.
- Concurrency Testing — dua submit bersamaan (race) pada data yang sama.

## Test Scenarios

### Positive Testing
- Submit data unik → berhasil dibuat.
- Submit data dengan field kunci berbeda dari yang sudah ada → berhasil.
- Submit ulang request yang sama (idempotent retry) → tidak ada record ganda.
- Kombinasi data yang sah terlihat mirip → tetap diterima.

### Negative Testing
- Submit data identik dengan yang sudah ada → ditolak/dedup sesuai kontrak (bukan record kembar).
- Double-click tombol submit → hanya satu record.
- Submit bersamaan (dua tab/dua request paralel) → hanya satu record.
- Duplikat dengan variasi kosmetik (whitespace tambahan, beda kapitalisasi) → sesuai aturan normalisasi kontrak.
- Submit duplikat setelah record asal dihapus (soft delete) → sesuai kontrak.

### Boundary Testing
- Data berbeda pada tepat satu field kunci → tidak duplikat.
- Selisih minimal antar data (angka ±1, satu karakter beda) → tidak duplikat.
- Submit berulang dengan jeda sangat pendek (race window).

### Integration Testing
- Duplikat + API create (lihat `api-post-create`, `api-idempotency`).
- Duplikat + concurrency (lihat `api-concurrency`, `data-concurrency`).
- Duplikat + UI double-click guard (lihat `ui-behavior`) — guard UI gagal tetap aman di server.
- Duplikat lintas user/sesi — user berbeda mengirim data sama.
- Duplikat + workflow: submit ulang setelah penolakan (resubmit) — diperbolehkan atau tidak sesuai kontrak.

## Test Data
- Pasangan data identik, hampir identik, dan jelas berbeda.
- Data dengan variasi kosmetik (whitespace, case, format).
- Dua sesi/akun untuk submit paralel.
- Record yang sudah di-soft-delete dengan kunci sama.

## Expected Results
- Tidak pernah ada record kembar yang tersimpan dari submit berulang/paralel.
- Respons duplikat sesuai kontrak (mis. 409/422 dengan pesan, atau 200 mengembalikan existing).
- Data unik tetap diterima (tidak over-blocking).
- Perilaku konsisten antara retry idempotent dan duplikat bisnis.

## Common Defects
- Cek duplikat hanya di UI — bypass lewat API langsung.
- Double-click membuat dua record (guard hanya di frontend).
- Race condition: dua request paralel lolos cek duplikat keduanya.
- Normalisasi tidak konsisten (" Budi" vs "Budi" dianggap beda, atau sebaliknya terlalu ketat).
- Over-blocking: data sah ditolak karena aturan duplikat terlalu luas.
- Soft-deleted record tidak dihitung padahal bisnis mengharuskan (atau sebaliknya).

## Security Considerations
- Bypass cek duplikat lewat manipulasi whitespace/case/encoding.
- Race flooding: spam request paralel untuk menembus pemeriksaan.
- Resource exhaustion bila duplikat tidak dibatasi (data menumpuk).

## References
- ISTQB CTFL v4.0.1 — Equivalence Partitioning, Boundary Value Analysis.
- OWASP Web Security Testing Guide — Business Logic (race condition).
