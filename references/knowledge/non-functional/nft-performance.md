# NFT Performance Testing

## Overview
Menguji **kecepatan dan efisiensi** sistem pada beban normal: seberapa cepat response diberikan dan seberapa banyak transaksi yang bisa diproses per satuan waktu. Fokus pada **response time** dan **throughput** — bukan pada titik jenuh sistem (itu `nft-load`/`nft-stress`).

Risiko utama: response lambat pada operasi kritikal, throughput tidak memenuhi kebutuhan bisnis, dan bottleneck pada satu komponen menurunkan seluruh sistem.

## When to Apply
- Ada **SLA/SLO/target** eksplisit (mis. response `p95` < 2 detik).
- Operasi yang **sering dipakai** dan sensitif terhadap kecepatan (login, list data, submit form, pencarian, API kritikal).
- Sebelum rilis / perubahan besar yang berpotensi menurunkan performa.
- Setelah ada keluhan "lambat" tanpa penyebab fungsional yang jelas.

## Testing Principles
1. Ukur **response time** (latency) dan **throughput** (transaksi/detik) sebagai dua metrik terpisah — keduanya saling memengaruhi tapi tidak identik.
2. Gunakan **persentil** (`p50`, `p90`, `p95`, `p99`), bukan hanya rata-rata — rata-rata menyembunyikan outlier.
3. Test harus **deterministik dan repeatable**: environment, data, dan beban dibuat konsisten antar run.
4. Baseline dulu sebelum optimasi — tanpa baseline tidak bisa klaim "lebih cepat".
5. Perf testing bukan functional testing: hasilnya berupa angka + grafik + bottleneck, bukan pass/fail tunggal.

## Test Design Techniques
- **Benchmark / Baseline** — ukur metrik saat beban rendah sebagai titik acuan.
- **Equivalence Partitioning** — kelompokkan operasi berdasarkan tipe (read vs write, ringan vs berat, single vs batch).
- **Profiling & Bottleneck Isolation** — pisahkan penyebab: client, jaringan, aplikasi, atau database.
- **Comparison Testing** — bandingkan antar versi/rilis untuk deteksi regresi performa.

## Test Scenarios

### Positive Testing
- Operasi kritikal mencapai target response time di bawah beban normal.
- Throughput sistem memenuhi kebutuhan bisnis (transaksi/detik sesuai target).
- `p95`/`p99` berada di bawah ambang batas yang disepakati.
- Response tetap stabil ketika dataset bertambah dalam rentang yang diperkirakan.

### Negative Testing
- Operasi dengan payload/dataset besar → response time tetap terkendali atau gagal dengan jelas (bukan hang).
- Request pada resource yang tidak ada/berat → tidak memperlambat request lain secara signifikan.
- Lonjakan kecil mendadak → degradasi bertahap, bukan crash total.

### Boundary Testing
- Ukuran payload maksimum sesuai kontrak → response time masih dalam target.
- Ukuran dataset pada batas atas yang diperkirakan → throughput masih memadai.
- Operasi batch dengan jumlah item maksimum → selesai dalam durasi yang dapat diterima.

### Integration Testing
- End-to-end (UI → API → database) response time, bukan hanya per-komponen.
- Query ke database pada operasi list dengan join/filter kompleks → indeks bekerja.
- Ketergantungan eksternal (third-party API) → dampaknya terhadap response time.

## Test Data
- Dataset realistis (bukan kosong/tiruan minimal) agar pengukuran relevan.
- Dataset pada beberapa ukuran (kecil, menengah, target produksi).
- Operasi yang mewakili profil penggunaan nyata (read-heavy vs write-heavy).

## Expected Results
- Response time `p95`/`p99` di bawah ambang target yang disepakati.
- Throughput memenuhi kebutuhan bisnis.
- Tidak ada bottleneck dominan pada satu komponen (CPU, memory, I/O, DB).
- Metrik stabil (tidak fluktuatif liar) antar run pada kondisi sama.

## Common Defects
- N+1 query → banyak query kecil yang seharusnya bisa di-join/batch.
- Missing index pada kolom yang sering difilter/sort.
- Response payload terlalu besar (field tak perlu ikut ter-return).
- Blocking call / operasi sinkron yang seharusnya async.
- Connection pool habis karena koneksi tidak dilepas.
- Mengukur rata-rata saja sehingga outlier lambat tak terlihat.

## Security Considerations
- Perf testing tidak boleh memakai data produksi yang mengandung PII tanpa masking.
- Hindari DoS pada environment sendiri: kendalikan intensitas beban saat pengukuran.
- Optimasi performa (mis. cache) jangan sampai membocorkan data antar user/tenant.

## References
- ISTQB CTFL v4.0.1 — Performance Testing (bagian Non-functional Testing)
- ISO/IEC 25010 — Performance Efficiency quality characteristics
- Google AIP-132/158 — efisiensi collection API (pagination untuk batasi payload)
