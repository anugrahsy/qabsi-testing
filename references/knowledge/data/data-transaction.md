# Data Transaction Testing

## Overview
Menguji **atomicity transaksi** database: commit, rollback, dan konsistensi saat operasi multi-step berhasil atau gagal sebagian. Risiko utama: operasi setengah jalan meninggalkan state inkonsisten, rollback tidak memulihkan semua perubahan, dan transaksi yang saling tumpang tindih.

## When to Apply
Operasi yang mengubah **lebih dari satu** record/tabel secara atomik: transfer, approval multi-entitas, batch update, dan alur yang harus all-or-nothing.

## Testing Principles
1. Transaksi bersifat **atomic**: semua perubahan commit bersama, atau tidak ada yang tersimpan (rollback).
2. Kegagalan di langkah mana pun harus **memulihkan semua** perubahan sebelumnya.
3. **Isolation** antar transaksi menentukan apa yang terlihat transaksi lain (delegasi `data-concurrency`).
4. Verifikasi commit benar-benar **terpersist** (durable) — bukan hanya di memori.

## Test Design Techniques
- State Transition — state sebelum/sesudah transaksi.
- Decision Table — kombinasi sukses/gagal per langkah.
- Fault Injection — memaksa kegagalan di langkah tertentu.

## Test Scenarios

### Positive Testing
- Semua langkah sukses → commit → semua perubahan tersimpan.
- Commit eksplisit → perubahan terpersist ke database.
- Nested transaction → commit terdalam hanya berlaku saat transaksi luar commit.

### Negative Testing
- Langkah terakhir gagal → rollback → tidak ada perubahan tersimpan (atomicity).
- Langkah tengah gagal → rollback → perubahan langkah sebelumnya dibatalkan.
- Rollback gagal (error di handler) → state tidak konsisten terdeteksi.
- Commit setelah koneksi putus → tidak ada commit sebagian.

### Boundary Testing
- Transaksi dengan banyak baris (batch besar) → semua atau tidak sama sekali.
- Transaksi timeout → rollback otomatis.
- Nilai batas numerik yang menyebabkan overflow di tengah transaksi → rollback.

### Integration Testing
- Transaksi + concurrency (dua transaksi tulis record sama) — delegasi `data-concurrency`.
- Transaksi + relasi cascade (delegasi `data-relationship`).
- Transaksi lintas tabel (master + detail di-update atomik).

## Test Data
- Operasi multi-step yang bisa gagal di langkah berbeda.
- Record yang berubah di lebih dari satu tabel.
- Data yang memicu error/exception di tengah transaksi.

## Expected Results
- Sukses penuh → semua perubahan tercommit.
- Gagal sebagian → tidak ada perubahan tercommit (rollback penuh).
- Tidak ada state "setengah jadi" setelah kegagalan.
- Database tetap konsisten (constraint/relasi terjaga).

## Common Defects
- Operasi multi-step tanpa transaksi → gagal di tengah meninggalkan state parsial.
- Rollback tidak membatalkan semua statement (sebagian sudah auto-commit).
- Exception ditangkap tapi transaksi tidak di-rollback.
- Commit terjadi walau salah satu langkah gagal (tidak ada pengecekan hasil).
- Deadlock/timeout tidak ditangani.

## Security Considerations
- Transaksi yang gagal bisa membocorkan state parsial bila error handler menampilkan detail internal.
- Race pada transaksi bisa dimanfaatkan untuk memanipulasi data (delegasi `data-concurrency`).

## References
- ISTQB CTFL v4.0.1
- Database ACID properties (Atomicity, Consistency, Isolation, Durability)
