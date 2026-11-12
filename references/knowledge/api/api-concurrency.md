# API Concurrency Testing

## Overview
Menguji perilaku API saat beberapa request menyentuh resource yang sama secara bersamaan. Risiko utama: **lost update** (perubahan satu request menghapus perubahan request lain), duplikasi data akibat check-then-act, deadlock yang muncul sebagai `500`, dan counter/kuota yang melenceng.

## When to Apply
Endpoint tulis pada data bersama: update saldo/stok/kuota, ubah status workflow, klaim/assign tugas, submit yang sama dua kali, approve bersamaan. Pasangkan dengan `api-idempotency` (request identik) dan `data-concurrency` (level database).

## Testing Principles
1. **Concurrency adalah kondisi yang harus dirancang**, bukan kebetulan. Kontrak harus menyatakan strategi: optimistic locking, pessimistic lock, atau last-write-wins.
2. **Tidak boleh ada lost update tanpa pemberitahuan.**
3. **Konflik dilaporkan** (`409`/`412`), bukan ditelan.
4. **Operasi gabungan harus atomik** (baca-ubah-tulis dalam satu transaksi/lock).
5. **Hasil akhir harus konsisten** dengan urutan eksekusi yang terjadi (serializable atau terdokumentasi).

## Test Design Techniques
- **Concurrency Testing** — N request paralel pada resource yang sama.
- **State Transition** — state awal → dua transisi bersamaan → state akhir.
- **Decision Table** — optimistic/pessimistic × ada/tidak precondition × resource sama/beda.
- **Boundary Value Analysis** — jumlah paralel tepat pada batas lock/queue.

## Test Scenarios

### Positive Testing
- Dua update pada **resource berbeda** secara paralel → keduanya berhasil, tidak saling memengaruhi.
- Update dengan `If-Match`/versi terbaru → berhasil dan versi bertambah.
- Dua request create dengan nilai unik berbeda → keduanya membuat record masing-masing.
- Operasi baca paralel saat ada update → membaca state sebelum atau sesudah secara utuh (tidak campuran).
- Antrian/queue memproses item bersamaan tanpa kehilangan item.

### Negative Testing
- Dua update pada field yang sama dengan versi sama → satu berhasil, satu `409`/`412`.
- Dua create dengan nilai unique sama secara bersamaan → satu `201`, satu `409`.
- Dua approve pada item yang sama → hanya satu transisi yang berlaku; yang kedua ditolak.
- Dua delete bersamaan → satu `204`, satu `404`/`204` sesuai kontrak, tidak ada `500`.
- Update saat delete berlangsung → hasil akhir deterministik (tidak ada record "hidup kembali").
- Check-then-act pada kuota/stok: dua request membaca sisa 1 → hanya satu yang boleh berhasil.

### Boundary Testing
- Jumlah request paralel tepat pada batas koneksi/pool → tidak ada timeout massal.
- Nilai counters: dua increment bersamaan → hasil akhir bertambah dua (bukan satu).
- Stok/kuota = 1 dengan dua pembeli bersamaan → satu sukses, satu gagal, tidak minus.
- Retry otomatis saat konflik → jumlah percobaan terbatas dan hasil akhir benar.
- Lock timeout: transaksi panjang → gagal rapi, bukan deadlock permanen.

### Integration Testing
- Dua aplikasi/instance mengakses database yang sama → locking tetap berlaku.
- Cache dan database tidak berbeda setelah update bersamaan (invalidasi benar).
- Event/notifikasi dari dua update tidak terkirim ganda atau hilang.
- Proses background (job) menulis bersamaan dengan request pengguna → tidak saling menimpa.
- Database constraint (unique, foreign key) menjadi jaring pengaman terakhir dan error-nya dipetakan ke `409`, bukan `500`.
- Transaksi terdistribusi: commit sebagian tidak meninggalkan state tidak konsisten.

## Test Data
- Satu resource dengan versi/ETag yang diketahui.
- Sepasang nilai update berbeda untuk field yang sama.
- Nilai unique yang sama untuk uji create bersamaan.
- Counter/stok dengan nilai 0, 1, dan banyak.
- Konfigurasi pool koneksi dan lock timeout.
- Skrip pengirim request paralel dengan sinkronisasi start.

## Expected Results
- Tidak ada lost update tanpa notifikasi; konflik mengembalikan `409`/`412` beserta state terbaru.
- Hanya satu pemenang pada create dengan nilai unique sama; sisanya `409`.
- Counter/stok berubah sesuai jumlah operasi yang berhasil (tidak minus, tidak dobel).
- Tidak ada deadlock yang muncul sebagai `500` berulang; bila lock timeout, pesannya jelas.
- State akhir selalu konsisten dengan salah satu urutan eksekusi yang valid.
- Respons setiap request mencerminkan hasil yang benar-benar tersimpan.

## Common Defects
- Lost update: dua update bersamaan, perubahan pertama hilang tanpa error.
- Duplikasi record karena pengecekan unique dilakukan sebelum insert tanpa constraint.
- Counter melenceng (read-modify-write tanpa atomic increment).
- Stok menjadi negatif pada pembelian bersamaan.
- Deadlock database bocor sebagai `500` tanpa retry.
- Approve ganda menghasilkan dua transisi status.
- Update dan delete bersamaan menghasilkan record yatim atau "resurrect".
- Retry otomatis pada konflik menimpa perubahan pengguna lain.
- Cache menyajikan state lama setelah update paralel.

## Security Considerations
- Race condition pada klaim kupon/kuota/role dapat dieksploitasi untuk mendapatkan lebih dari yang diizinkan.
- Double-spend pada transaksi/ saldo adalah dampak keamanan, bukan hanya bug data.
- Pastikan pengecekan otorisasi dan penulisan berada dalam batas transaksi yang sama (TOCTOU).
- Rate limit dan lock tidak boleh menjadi jalur DoS (lock dipegang terlalu lama oleh penyerang).

## References
- RFC 9110 — HTTP Semantics, `If-Match` dan conditional requests (`412`).
- OWASP Web Security Testing Guide — WSTG-BUSL (business logic, race conditions).
- OWASP API Security Top 10 — API6 Unrestricted Access to Sensitive Business Flows.
- ISTQB CTFL v4.0.1 — state transition testing.
