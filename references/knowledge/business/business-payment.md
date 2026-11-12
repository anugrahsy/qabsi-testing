# Business Payment Testing

## Overview
Menguji **pembayaran, refund, dan pembayaran parsial**. Risiko utama: nominal salah, transaksi ganda (double charge), refund berlebih atau tanpa otorisasi, dan status pembayaran tidak sinkron dengan gateway. Nilai finansial membuat modul ini prioritas tinggi.

## When to Apply
Fitur transaksi uang: pembayaran penuh/parsial, refund, pembatalan, dan rekonsiliasi dengan payment gateway. Aplikasikan bersama `business-transaction`, `input-currency`, `business-calculation`, `business-audit`.

## Testing Principles
1. Nominal yang dibayar harus **dihitung server-side** dari data otoritatif — bukan dari input client.
2. Pembayaran harus **idempoten**: callback/retry gateway tidak boleh memicu charge ganda.
3. **Refund tidak boleh melebihi nominal yang dibayar**, dan harus butuh otorisasi.
4. Status pembayaran harus **satu sumber kebenaran** yang direkonsiliasi dengan gateway (bukan tebak-tebakan).
5. Pembayaran parsial harus punya **alur pelunasan** (sisa tagihan) yang jelas.
6. Setiap perubahan nominal/status harus **tercatat** (lihat `business-audit`).

## Test Design Techniques
- Boundary Value Analysis — nominal minimum/maksimum, sisa tagihan ±1, refund tepat/lebih/kurang.
- State Transition — pending → paid / failed / refunded / partially refunded.
- Decision Table — kombinasi status pembayaran × jenis operasi (bayar/refund/batal).
- Concurrency Testing — callback ganda, pembayaran parsial bersamaan.

## Test Scenarios

### Positive Testing
- Pembayaran penuh nominal tepat → status paid, catatan tercatat.
- Pembayaran parsial → sisa tagihan berkurang tepat, status sesuai (partial/paid saat lunas).
- Refund sebagian → status partial refund, nominal dikembalikan tepat.
- Refund penuh → status refunded, tidak melebihi nominal dibayar.
- Callback sukses gateway → status berubah benar.

### Negative Testing
- Refund melebihi nominal yang dibayar → ditolak.
- Refund tanpa otorisasi → ditolak.
- Pembayaran nominal negatif/nol → ditolak.
- Callback ganda (notifikasi sukses terkirim dua kali) → tidak charge ganda.
- Pembayaran pada transaksi yang sudah dibatalkan → ditolak.
- Status gateway gagal/timeout → ditangani tanpa mengubah status salah.

### Boundary Testing
- Nominal minimum yang diperbolehkan dan tepat di bawahnya.
- Nominal maksimum dan tepat di atasnya.
- Refund tepat sebesar nominal dibayar (batas atas refund).
- Sisa tagihan = 1 satuan dan = 0 (lunas).

### Integration Testing
- Pembayaran + transaksi atomik: bayar + update status + stok dalam satu kesatuan (lihat `business-transaction`, `business-inventory`).
- Pembayaran + kalkulasi: diskon/pajak/pembulatan menghasilkan nominal benar (lihat `business-calculation`, `input-currency`).
- Pembayaran + audit: jejak nominal, status, aktor, waktu (lihat `business-audit`).
- Pembayaran + gateway eksternal: rekonsiliasi status dan penanganan timeout/retry (lihat `api-integration`).
- Pembayaran parsial + pelunasan bertahap hingga sisa nol.

## Test Data
- Nominal di batas (minimum, maksimum, ±1, sisa nol).
- Transaksi dalam berbagai status (pending, paid, failed, refunded).
- Skenario callback: sukses, gagal, timeout, duplikat.
- Akun dengan/tanpa otorisasi refund.
- Mata uang dan presisi desimal (lihat `input-currency`).

## Expected Results
- Nominal dibayar/dikembalikan selalu benar dan tidak pernah negatif/berlebih.
- Tidak ada double charge dari retry/callback ganda.
- Refund hanya sebesar yang dibayar dan hanya oleh pihak berwenang.
- Status pembayaran konsisten dengan gateway dan tercatat.

## Common Defects
- Nominal dihitung dari input client → bisa diubah.
- Callback gateway diproses dua kali → double charge.
- Refund melebihi nominal karena tidak divalidasi.
- Status ditandai paid padahal gateway gagal (atau sebaliknya).
- Pembayaran parsial tidak menghitung sisa tagihan dengan benar.
- Tidak idempoten: retry user menambah tagihan.

## Security Considerations
- Manipulasi nominal/status pembayaran dari client — wajib server-side dan terotorisasi.
- Race pada callback/refund — bisa menembus batas refund (lihat OWASP race condition).
- Rekonsiliasi gateway harus memakai token/signature valid, bukan percaya payload.

## References
- ISTQB CTFL v4.0.1 — State Transition, Decision Table.
- OWASP Web Security Testing Guide — Business Logic, Input Validation.
