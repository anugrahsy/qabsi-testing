# NFT Load Testing

## Overview
Menguji perilaku sistem pada **beban konkuren yang diharapkan** dalam produksi: sejumlah pengguna/transaksi normal dalam waktu bersamaan. Tujuannya memverifikasi sistem **mampu menangani beban target** tanpa melanggar SLA, bukan mencari batas maksimum (itu `nft-stress`).

Risiko utama: sistem lolos uji dengan 1 pengguna tetapi gagal saat dipakai banyak pengguna bersamaan, atau resource habis di bawah beban target yang realistis.

## When to Apply
- Sebelum rilis fitur yang diprediksi ramai dipakai (mis. pendaftaran, pengisian SKP/kinerja menjelang deadline).
- Ketika ada **target konkurensi** eksplisit (mis. N pengguna aktif, M transaksi/menit).
- Setelah perubahan arsitektur/infrastruktur yang memengaruhi kapasitas.
- Untuk memvalidasi hasil tuning/optimasi pada kondisi mendekati produksi.

## Testing Principles
1. Beban harus **merepresentasikan profil produksi** (mix read/write, jumlah user, pola pikir/waktu antar request) — bukan sekadar "banyak request".
2. Naikkan beban **bertahap** (ramp-up) sampai target, lalu pertahankan — jangan langsung maksimum.
3. Ukur metrik yang sama dengan `nft-performance` (response time, throughput, error rate) pada beban target.
4. Satu pengujian load harus bisa **diulang** dengan hasil konsisten.
5. Bedakan kegagalan **sistem** (resource/konfigurasi) dari kegagalan **script test** (data uji salah).

## Test Design Techniques
- **Workload Modeling** — bangun model beban dari data penggunaan nyata (jumlah user, distribusi operasi).
- **Ramp-up / Steady-state / Ramp-down** — pola kenaikan, penahanan, dan penurunan beban.
- **Equivalence Partitioning** — kelompokkan tipe pengguna/operasi berdasarkan berat bebannya.
- **Threshold Analysis** — tetapkan ambang pass/fail untuk tiap metrik sebelum menjalankan.

## Test Scenarios

### Positive Testing
- Sistem menangani beban konkuren target → response time dan error rate dalam ambang.
- Throughput pada beban target memenuhi kebutuhan bisnis.
- Resource (CPU, memory, DB connection) tetap dalam batas aman pada beban target.
- Tidak ada antrean/backlog yang terus menumpuk selama steady-state.

### Negative Testing
- Salah satu operasi berat dipanggil massal bersamaan → tidak menurunkan operasi lain di luar ambang.
- Koneksi database/third-party terbatas → sistem tetap stabil (mengantre atau gagal jelas, bukan hang).
- Data uji tidak valid/tidak ada → request gagal bersih tanpa membebani sistem.

### Boundary Testing
- Beban tepat pada batas target konkurensi → sistem masih memenuhi SLA.
- Beban sedikit di bawah target dalam waktu panjang → tetap stabil (transisi ke `nft-endurance`).
- Kombinasi operasi teringan vs terberat pada jumlah user target → keduanya tertangani.

### Integration Testing
- Beban menyentuh seluruh tumpukan: UI/client → API → database → cache → third-party.
- Verifikasi **connection pool** dan **thread pool** cukup untuk konkurensi target.
- Validasi **load balancer** mendistribusikan beban antar instance (jika ada).

## Test Data
- Akun pengguna uji dalam jumlah sesuai target konkurensi.
- Data bisnis yang cukup agar operasi (list, cari, simpan) tidak trivial.
- Distribusi operasi yang meniru pemakaian nyata (bukan satu endpoint saja).

## Expected Results
- Response time dan error rate dalam ambang SLA pada beban target.
- Throughput ≥ kebutuhan bisnis pada beban target.
- Utilisasi resource (CPU/mem/DB) tidak mendekati jenuh pada beban target.
- Tidak ada error `5xx`, timeout, atau connection pool exhaustion.

## Common Defects
- Connection pool DB terlalu kecil → antrean/timeout pada beban normal.
- Endpoint tertentu tidak siap konkurensi (race condition) → error saat banyak user.
- Load balancer belum dikonfigurasi → satu instance jadi bottleneck.
- Script test memakai satu akun/konteks → hasil tidak mewakili banyak user.
- Cache tidak dipanaskan (cold cache) → angka awal menyesatkan.

## Security Considerations
- Gunakan akun uji terisolasi — jangan load test dengan akun yang punya akses produksi.
- Pastikan beban test tidak memicu lockout akun/rate limiting yang mengganggu user asli.
- Data hasil load test harus dibersihkan agar tidak mengotori database.

## References
- ISTQB CTFL v4.0.1 — Performance Testing (Load Testing)
- ISO/IEC 25010 — Performance Efficiency
