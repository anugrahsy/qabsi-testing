# Data Concurrency Testing

## Overview
Menguji **concurrent updates** dan **race conditions** saat beberapa proses menulis/membaca record yang sama. Risiko utama: lost update, dirty read, deadlock, dan data korup akibat interleaving transaksi.

## When to Apply
Fitur dengan akses bersamaan ke data yang sama: dua user update record sama, batch job vs user, dan operasi counter/stok. Aplikasikan bersama `data-transaction`.

## Testing Principles
1. Uji dengan **dua atau lebih** client menulis record sama secara bersamaan.
2. Kenali fenomena concurrency: **lost update**, **dirty read**, **non-repeatable read**, **phantom read**.
3. Mekanisme pengendalian (optimistic lock, pessimistic lock, versioning) harus mencegah korupsi.
4. **Isolation level** transaksi menentukan perilaku yang diperbolehkan.

## Test Design Techniques
- Fault Injection — interleave/penundaan di tengah operasi.
- State Transition — state record saat dua transaksi bersaing.
- Decision Table — kombinasi operasi (read-modify-write, update, delete).

## Test Scenarios

### Positive Testing
- Dua update field berbeda pada record sama → keduanya tersimpan tanpa saling menimpa.
- Optimistic lock → update kedua ditolak bila version berubah.
- Counter di-increment bersamaan → total benar (tidak lost update).

### Negative Testing
- Dua update field sama bersamaan → salah satu menang, yang lain ditolak/dideteksi (bukan lost update diam-diam).
- Read-modify-write bersamaan → tidak ada nilai salah akibat read basi.
- Transaksi bersamaan pada record sama → salah satu menunggu/rollback (deadlock ditangani).

### Boundary Testing
- Banyak client (N) update record sama → hasil konsisten.
- Transaksi panjang bersamaan dengan transaksi pendek → tidak saling korup.

### Integration Testing
- Concurrency + transaksi/atomicity (delegasi `data-transaction`).
- Concurrency + unique constraint (delegasi `data-duplicate`).
- Concurrency + konsistensi API (delegasi `data-consistency`).

## Test Data
- Record yang sama diakses banyak client.
- Counter/field numerik yang di-increment.
- Data dengan version/timestamp untuk optimistic lock.

## Expected Results
- Tidak ada lost update (perubahan tidak hilang diam-diam).
- Konflik terdeteksi dan ditangani sesuai kontrak (retry/reject).
- Data tetap konsisten setelah concurrent write selesai.
- Tidak ada deadlock yang menggantung tanpa timeout/recovery.

## Common Defects
- Lost update: update terakhir menimpa perubahan sebelumnya.
- Tidak ada optimistic lock → dua user saling menimpa tanpa sadar.
- Read-modify-write tanpa transaksi → counter/nilai salah.
- Deadlock tidak ditangani → request hang.
- Isolation level terlalu rendah → dirty read.

## Security Considerations
- Race condition bisa dieksploitasi (mis. double-spend, melampaui batas).
- Jangan expose detail concurrency (version, lock) ke user yang bisa dimanipulasi.

## References
- ISTQB CTFL v4.0.1
- Database ACID & transaction isolation levels (lost update, dirty read, deadlock)
