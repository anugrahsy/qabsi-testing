# NFT Scalability Testing

## Overview
Menguji kemampuan sistem untuk **tumbuh** menangani beban/data/pengguna yang meningkat — lewat **penambahan resource** (vertical: upgrade kapasitas) atau **penambahan instance** (horizontal: scale out). Fokus pada seberapa baik performa **bertambah seiring resource**, bukan sekadar bertahan pada beban (`nft-load`).

Risiko utama: menambah instance tidak menambah kapasitas (bottleneck shared state), sistem tidak bisa di-scale-out, atau peningkatan data membuat operasi makin lambat tidak linear.

## When to Apply
- Aplikasi yang diprediksi **tumbuh** jumlah pengguna/data seiring waktu.
- Saat mengevaluasi **autoscaling** dan arsitektur cloud.
- Setelah menambah/mengubah komponen berbagi (database, cache, session store).
- Untuk menentukan strategi scaling (vertical vs horizontal) yang tepat.

## Testing Principles
1. Ukur **perubahan performa terhadap perubahan resource** — scaling berhasil bila kapasitas naik mendekati linear.
2. Identifikasi **bottleneck shared state** (session, cache, DB, file lokal) yang menghalangi scale-out.
3. Uji **vertical** (naikkan resource) dan **horizontal** (tambah instance) sebagai dua jalur berbeda.
4. Data tumbuh juga bagian dari scalability — bukan hanya jumlah user.
5. Scaling harus **tanpa kehilangan konsistensi** data/state antar instance.

## Test Design Techniques
- **Capacity Planning Analysis** — proyeksikan kebutuhan resource untuk beban di masa depan.
- **Horizontal vs Vertical Comparison** — bandingkan hasil scale-out vs scale-up.
- **Throughput Curve Analysis** — plot throughput vs jumlah instance/resource.
- **Bottleneck Isolation** — temukan komponen yang membatasi pertumbuhan linear.

## Test Scenarios

### Positive Testing
- Menambah instance → throughput naik (mendekati proporsional).
- Menambah resource (CPU/mem) → operasi berat makin cepat.
- Peningkatan volume data → response time tetap dalam ambang yang dapat diterima.
- State/session tetap konsisten saat request tersebar ke banyak instance.

### Negative Testing
- State tersimpan lokal per instance (bukan shared) → request ke instance lain kehilangan state.
- Satu komponen (mis. DB) jadi bottleneck → menambah instance tidak menambah kapasitas.
- Autoscaling gagal/skala turun → tidak ada kehilangan request/state.

### Boundary Testing
- Jumlah instance minimum (1) dan maksimum yang didukung → keduanya stabil.
- Volume data pada batas atas yang diproyeksikan → operasi list/cari tetap memadai.
- Lonjakan yang memicu scale-up mendadak → kapasitas bertambah tepat waktu.

### Integration Testing
- Load balancer + autoscaling + instance baru → request terdistribusi tanpa error.
- Database yang di-shard/read-replica → konsistensi baca-tulis terjaga.
- Cache terdistribusi → tidak ada stale data antar instance.

## Test Data
- Dataset dengan beberapa ukuran (kecil hingga proyeksi maksimum).
- Beban yang meningkat bertahap untuk mengukur kurva throughput.
- Konfigurasi resource/instance yang bervariasi (untuk perbandingan).

## Expected Results
- Throughput meningkat mendekati linear saat resource/instance ditambah.
- Tidak ada bottleneck shared state yang memblokir scale-out.
- Konsistensi data/state terjaga lintas instance.
- Peningkatan volume data tidak menurunkan performa di luar ambang.

## Common Defects
- Session/state disimpan di file/memory lokal → tidak bisa scale-out.
- Database tunggal jadi bottleneck → scale-out aplikasi sia-sia.
- Autoscaling lambat/overshoot → spike tak tertangani atau biaya membengkak.
- Sticky session wajib → distribusi beban tidak merata.
- Cache lokal per instance → data tidak konsisten antar instance.
- Indeks tidak scalable → query makin lambat seiring data tumbuh.

## Security Considerations
- Instance yang di-scale-out harus punya konfigurasi keamanan identik (jangan ada instance "telanjang").
- Shared state/session yang dipindahkan ke store terpusat harus terenkripsi dan ter-scope per user.
- Uji scaling jangan sampai mengonsumsi resource/budget cloud secara tak terkendali.

## References
- ISTQB CTFL v4.0.1 — Performance/Scalability Testing
- ISO/IEC 25010 — Performance Efficiency (Capacity)
- Google AIP-158 — pagination sebagai strategi menangani data besar
