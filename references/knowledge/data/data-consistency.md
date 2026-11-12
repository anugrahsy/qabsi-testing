# Data Consistency Testing

## Overview
Menguji **konsistensi antara API dan database** — serta antar representasi data lain (cache, replica). Risiko utama: response API tidak mencerminkan data aktual di database, cache basi (stale), dan perbedaan hasil antar jalur baca.

## When to Apply
Setiap fitur yang membaca/menulis data lewat API, cache, atau replica. Aplikasikan bersama `data-crud`, `data-transaction`, dan `data-concurrency`.

## Testing Principles
1. Data yang di-return API harus **sama** dengan data di database (kecuali transformasi yang didefinisikan kontrak).
2. **Cache** harus di-invalidasi saat data berubah — tidak ada stale read.
3. **Replica/follower** punya lag yang harus diperhitungkan (eventual consistency).
4. Representasi data di tiap jalur (API, export, report) harus konsisten.

## Test Design Techniques
- State Transition — data berubah → API mencerminkan perubahan.
- Equivalence Partitioning — jalur baca yang berbeda.
- Decision Table — kombinasi sumber data (DB, cache, replica).

## Test Scenarios

### Positive Testing
- Create lewat API → baca langsung dari DB → nilai sama.
- Update lewat API → read berikutnya → nilai baru (bukan cache lama).
- Delete lewat API → read → data hilang.
- Export/report → konsisten dengan data di database.

### Negative Testing
- Cache tidak ter-invalidasi setelah update → detected stale read.
- Replica lag → read mengembalikan data lama (diverifikasi sesuai SLA).
- Transformasi field salah (mis. timezone, enum) → API vs DB beda nilai.

### Boundary Testing
- Update field ke null → API mengembalikan null konsisten.
- Data besar → API dan DB konsisten tanpa truncation.

### Integration Testing
- Konsistensi + transaksi (delegasi `data-transaction`).
- Konsistensi + concurrency (delegasi `data-concurrency`).
- Konsistensi + migrasi (delegasi `data-migration`).

## Test Data
- Record yang diubah nilainya (untuk deteksi stale).
- Data dengan nilai null/empty/default.
- Data lintas scope/otoritas.

## Expected Results
- API selalu mencerminkan state database terbaru (atau sesuai aturan konsistensi kontrak).
- Cache invalidated tepat waktu setelah write.
- Tidak ada perbedaan nilai antara API, DB, export, dan report.

## Common Defects
- Cache tidak di-invalidate setelah write → stale data.
- API membaca dari cache/replica tanpa memperhitungkan lag.
- Transformasi field salah → nilai API beda dengan DB.
- Eventual consistency tidak diinformasikan ke consumer.

## Security Considerations
- Stale cache bisa menampilkan data yang seharusnya sudah dihapus (data bocor).
- Pastikan cache/replica tidak menyimpan data sensitif lebih lama dari seharusnya.

## References
- ISTQB CTFL v4.0.1
- Database consistency & cache invalidation best practices
