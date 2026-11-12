# Business Transaction Testing

## Overview
Menguji **konsistensi transaksi bisnis** — operasi yang terdiri dari beberapa langkah dan harus berhasil seluruhnya atau gagal seluruhnya (atomicity). Risiko utama: kegagalan di tengah proses meninggalkan data setengah jadi, efek samping tidak ikut di-rollback, dan transaksi konkuren saling menimpa.

## When to Apply
Operasi multi-langkah yang harus atomik: pembayaran + pembaruan status, pemindahan data antar tabel, proses yang menulis ke lebih dari satu resource, dan alur yang memicu efek samping (notifikasi, log, update stok). Aplikasikan bersama `data-transaction`, `data-concurrency`.

## Testing Principles
1. Transaksi bisnis harus **atomik**: semua langkah commit atau semua rollback.
2. Kegagalan di langkah mana pun harus **membatalkan seluruh efek** — tidak ada state setengah jadi.
3. **Efek samping** (notifikasi, log, update turunan) harus ikut konsisten dengan transaksi utama.
4. **Idempotensi**: mengulang request yang sama tidak boleh menghasilkan efek ganda.
5. Transaksi konkuren harus **terisolasi** — tidak saling menimpa atau membaca state setengah jadi.
6. Batas transaksi harus jelas — apa yang masuk dan apa yang di luar transaksi.

## Test Design Techniques
- State Transition — state sebelum/sesudah transaksi.
- Decision Table — kombinasi langkah berhasil/gagal.
- Fault Injection — memaksa kegagalan di langkah tertentu (titik tengah transaksi).
- Concurrency Testing — dua transaksi bersamaan pada data yang sama.

## Test Scenarios

### Positive Testing
- Seluruh langkah berhasil → semua perubahan tersimpan konsisten.
- Transaksi dengan data valid → hasil akhir benar di semua resource terkait.
- Operasi idempoten diulang → tidak ada efek ganda.

### Negative Testing
- Kegagalan di langkah pertama → tidak ada perubahan sama sekali.
- Kegagalan di langkah tengah → semua perubahan sebelumnya di-rollback.
- Kegagalan di langkah terakhir → seluruh transaksi dibatalkan.
- Kegagalan efek samping (mis. notifikasi gagal) → perilaku sesuai kontrak (rollback atau dicatat terpisah).
- Input tidak valid di salah satu langkah → seluruh transaksi ditolak.

### Boundary Testing
- Transaksi dengan jumlah item minimum (1) dan maksimum.
- Transaksi yang menyentuh batas saldo/stok (lihat `business-inventory`, `business-payment`).
- Waktu eksekusi mendekati timeout → perilaku saat timeout.

### Integration Testing
- Transaksi + concurrency: dua transaksi pada data yang sama (lihat `data-concurrency`).
- Transaksi + database commit/rollback (lihat `data-transaction`).
- Transaksi + efek samping (notifikasi, audit, log) — konsistensi lintas resource.
- Transaksi + pemrosesan batch/latarbelakang (partial failure pada batch).

## Test Data
- Data yang memicu kegagalan di tiap langkah (mis. saldo kurang, stok habis, ID tidak ada).
- Fixture untuk verifikasi rollback (data sebelum transaksi sebagai pembanding).
- Dua transaksi yang menyasar data yang sama (untuk konkurensi).
- Data dengan jumlah item bervariasi.

## Expected Results
- Semua langkah berhasil → konsisten penuh; satu langkah gagal → tidak ada perubahan yang bertahan.
- Tidak ada state setengah jadi yang bisa diamati dari luar.
- Pengulangan request yang sama tidak menghasilkan efek ganda.
- Hasil akhir identik dengan kontrak, terlepas dari urutan/paralelisme yang sah.

## Common Defects
- Rollback tidak mencakup efek samping (notifikasi terkirim padahal transaksi gagal).
- Transaksi tidak atomik karena antar resource tidak dikoordinasikan.
- Request diulang menghasilkan efek ganda (tidak idempoten).
- Race condition: dua transaksi membaca nilai sama lalu menulis bergantian (lost update).
- Timeout meninggalkan data setengah jadi tanpa mekanisme recovery.
- Batas transaksi salah: langkah yang seharusnya di luar ikut di-rollback (atau sebaliknya).

## Security Considerations
- TOCTOU (time-of-check/time-of-use): nilai dicek lalu berubah sebelum dipakai.
- Manipulasi idempotency key untuk memicu efek ganda.
- Balapan (race) bisa dieksploitasi untuk melewati batas saldo/stok.

## References
- ISTQB CTFL v4.0.1 — State Transition, Decision Table.
- OWASP Web Security Testing Guide — Business Logic (race condition, TOCTOU).
