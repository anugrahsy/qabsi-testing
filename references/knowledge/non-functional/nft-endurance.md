# NFT Endurance (Soak) Testing

## Overview
Menguji sistem di bawah **beban normal yang dipertahankan lama** untuk mendeteksi masalah yang baru muncul setelah waktu berjalan: kebocoran memory (memory leak), koneksi yang tidak dilepas, resource yang menumpuk, dan degradasi bertahap. Berbeda dari `nft-load` (durasi pendek) dan `nft-stress` (beban melampaui kapasitas).

Risiko utama: sistem stabil di jam pertama tetapi gagal di jam ke-N karena resource terkuras perlahan, atau data sementara menumpuk tanpa batas.

## When to Apply
- Sistem yang **berjalan terus-menerus** (24/7) tanpa restart rutin.
- Sebelum rilis ke produksi jangka panjang.
- Ketika ada kecurigaan memory leak / penurunan performa seiring waktu.
- Setelah perubahan yang menambah proses background, cron, queue, atau cache.

## Testing Principles
1. Beban = **normal/target** (bukan ekstrem), durasi = **panjang** — kombinasi inilah yang membedakan endurance.
2. Pantau **tren resource** sepanjang waktu: memory, connection, thread, disk, antrean — bukan hanya nilai sesaat.
3. Penurunan performa **bertahap** (degradasi lambat) adalah sinyal utama yang dicari.
4. Gunakan beban dengan **variasi operasi** agar semua jalur kode (termasuk yang jarang) ikut dieksekusi berulang.
5. Durasi harus cukup untuk mengekspos kebocoran (biasanya berjam-jam, bukan menit).

## Test Design Techniques
- **Soak Testing** — beban stabil dalam durasi panjang sambil memantau tren.
- **Trend / Growth Analysis** — plot metrik vs waktu untuk deteksi kenaikan monoton.
- **State Accumulation Analysis** — cek pertumbuhan data sementara (log, cache, session, file temp).
- **Recovery Baseline** — bandingkan kondisi sebelum vs sesudah soak.

## Test Scenarios

### Positive Testing
- Sistem tetap memenuhi SLA response time selama seluruh durasi soak.
- Penggunaan memory **stabil** (naik-turun wajar) — bukan naik monoton tanpa turun.
- Jumlah koneksi/thread kembali ke nilai dasar setelah aktivitas selesai.
- Data sementara (cache, log, session) tumbuh dalam batas yang terkendali.

### Negative Testing
- Operasi yang membuka resource (koneksi, file) dipanggil berulang → resource tidak bocor.
- Proses background/cron berjalan berulang → tidak menumpuk job/entri yang gagal.
- Satu operasi gagal berulang → tidak menambah akumulasi error/antrean tak terbatas.

### Boundary Testing
- Cache/session pada batas expiry → entry lama benar-benar dibersihkan.
- Log/temp file mendekati batas ukuran → rotasi/cleanup berjalan.
- Antrean job yang hampir penuh dalam durasi lama → tidak terjadi penumpukan tak terkendali.

### Integration Testing
- Interaksi panjang dengan database (connection leak antar operasi berulang).
- Interaksi dengan third-party/queue yang lambat atau kadang gagal.
- Garbage collection / memory management pada runtime aplikasi.

## Test Data
- Beban campuran realistis yang diulang selama durasi panjang.
- Operasi yang menciptakan data sementara (upload, session, cache, log).
- Mekanisme pemantauan resource (grafik memory/connection vs waktu).

## Expected Results
- Memory dan resource tidak tumbuh monoton (tidak ada leak).
- Response time stabil sepanjang durasi, tidak menurun bertahap.
- Tidak ada penumpukan koneksi/thread/session/antrean di akhir soak.
- Sistem tetap sehat setelah soak tanpa perlu restart.

## Common Defects
- Memory leak (object tidak dilepas → penggunaan memory naik terus).
- Koneksi DB/HTTP tidak ditutup → connection pool akhirnya habis.
- Cache tanpa eviction → tumbuh tanpa batas sampai OOM.
- Log/file temp tidak di-rotasi → disk penuh setelah berjalan lama.
- Job cron/queue gagal diulang terus tanpa backoff → antrean menumpuk.
- Timer/scheduler bocor (setInterval/goroutine tidak dihentikan).

## Security Considerations
- Data sementara (session, cache, log) yang menumpuk bisa jadi mengandung PII — verifikasi cleanup.
- Jalankan soak di environment terisolasi; durasi panjang berarti akumulasi data uji besar.
- Pantau bahwa log yang tumbuh tidak mencatat kredensial/data sensitif.

## References
- ISTQB CTFL v4.0.1 — Performance Testing (Endurance/Soak Testing)
- ISO/IEC 25010 — Performance Efficiency & Reliability
