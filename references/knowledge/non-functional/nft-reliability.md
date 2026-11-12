# NFT Reliability Testing

## Overview
Menguji kemampuan sistem untuk **tetap berfungsi dan pulih** saat terjadi kegagalan: dependensi mati, jaringan terputus, proses crash, data hilang, atau timeout. Fokus pada **recovery, fault tolerance, dan ketersediaan** — bukan kecepatan (`nft-performance`).

Risiko utama: kegagalan satu komponen meruntuhkan seluruh sistem, transaksi tidak konsisten saat gagal di tengah jalan, dan tidak ada mekanisme pemulihan otomatis.

## When to Apply
- Sistem yang harus **selalu tersedia** (high availability) atau kritikal terhadap operasional.
- Aplikasi dengan **dependensi eksternal** (database, third-party, antrean) yang bisa gagal.
- Setelah menambah/mengubah mekanisme retry, fallback, atau failover.
- Untuk memvalidasi RTO/RPO (target waktu pemulihan dan kehilangan data).

## Testing Principles
1. Uji **kegagalan secara sengaja** (fault injection): matikan dependensi, putuskan jaringan, kill proses.
2. Bedakan **failover vs failback**: pindah ke cadangan, lalu kembali ke utama.
3. Periksa **konsistensi data** setelah kegagalan — pemulihan cepat tapi data rusak = gagal.
4. Retry harus **idempoten dan ber-backoff** agar tidak memperparah beban.
5. Dokumentasikan RTO/RPO yang diharapkan sebelum menguji agar punya kriteria pass/fail.

## Test Design Techniques
- **Fault Injection / Chaos Testing** — sengaja menginjeksi kegagalan untuk mengamati perilaku.
- **Recovery Testing** — verifikasi sistem pulih ke kondisi normal setelah kegagalan.
- **Failover Testing** — verifikasi perpindahan ke komponen cadangan.
- **State Transition** — modelkan state sistem (normal, degraded, failed, recovering).

## Test Scenarios

### Positive Testing
- Dependensi mati → sistem men-degrade dengan jelas, tidak crash total.
- Dependensi kembali hidup → sistem pulih otomatis (reconnect) tanpa restart manual.
- Proses/instance crash → restart otomatis dan layanan kembali tersedia.
- Transaksi gagal di tengah → rollback konsisten, tidak ada data partial.

### Negative Testing
- Jaringan terputus (timeout) → request gagal terstruktur, tidak hang selamanya.
- Database tidak tersedia → sistem mengembalikan error jelas (bukan `500` ambigu).
- Antrean/queue penuh atau mati → pesan tidak hilang diam-diam.
- Ketergantungan lambat → timeout terpicu dan request tidak menggantung.

### Boundary Testing
- Retry pada batas maksimum percobaan → berhenti dengan benar, tidak loop tak terbatas.
- Timeout tepat pada batas waktu → request dibatalkan tepat waktu.
- Kegagalan berulang (flapping) → sistem tidak thrash antar state.
- RTO/RPO pada batas target → pemulihan masih dalam ambang.

### Integration Testing
- Failover antar instance (primary→secondary) → sesi/state tetap terjaga.
- Pemulihan data dari backup/replica → data utuh dan konsisten.
- Circuit breaker → terbuka saat dependensi gagal, setengah-terbuka saat pulih.

## Test Data
- Skenario kegagalan untuk tiap dependensi (DB, cache, third-party, queue).
- Transaksi yang bisa gagal di tengah (untuk verifikasi rollback).
- Backup/replica untuk uji pemulihan data.

## Expected Results
- Sistem tetap tersedia (atau degrade terkendali) saat komponen gagal.
- Pemulihan terjadi otomatis dalam batas RTO/RPO yang ditetapkan.
- Tidak ada kehilangan/korupsi data setelah kegagalan.
- Error saat kegagalan terstruktur dan informatif tanpa bocorkan internal.

## Common Defects
- Tidak ada timeout → request menggantung selamanya saat dependensi lambat.
- Retry tanpa backoff → membombardir dependensi yang sedang pulih.
- Retry tidak idempoten → transaksi ganda saat request diulang.
- Tidak ada circuit breaker → satu dependensi mati meruntuhkan semua.
- Data partial write saat crash (tanpa transaksi/atomicity).
- Failover berhasil tapi state/session user hilang.

## Security Considerations
- Fault injection bisa memengaruhi data — lakukan di environment terisolasi.
- Error saat kegagalan jangan mengekspos detail arsitektur/kredensial.
- Pastikan mekanisme failover tidak membuka celah akses (mis. akun fallback yang tidak diproteksi).

## References
- ISTQB CTFL v4.0.1 — Reliability Testing (Non-functional)
- ISO/IEC 25010 — Reliability (Maturity, Availability, Fault tolerance, Recoverability)
