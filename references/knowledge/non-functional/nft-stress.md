# NFT Stress Testing

## Overview
Menguji perilaku sistem saat didorong **melampaui kapasitas yang diharapkan**, untuk menemukan **titik patah (breaking point)**, cara sistem **terdegradasi**, dan bagaimana ia **pulih** setelah beban ekstrem diturunkan. Berbeda dari `nft-load` (beban target normal) dan `nft-performance` (kecepatan pada beban normal).

Risiko utama: tidak tahu batas kapasitas nyata, crash tanpa degradasi bertahap, dan sistem tidak pulih otomatis setelah beban berlebih berakhir.

## When to Apply
- Sebelum musim beban puncak (deadline pengumpulan, pendaftaran massal, rilis yang diprediksi melonjak).
- Untuk menentukan **batas kapasitas** dan kebutuhan autoscaling.
- Ketika perlu membuktikan sistem **fail gracefully** (degradasi bertahap, bukan crash).
- Setelah menambah fitur yang berpotensi dikonsumsi massal sekaligus.

## Testing Principles
1. Tujuan stress = menemukan **batas** dan **mode kegagalan**, bukan membuktikan sistem sanggup — melampaui target itu memang disengaja.
2. Naikkan beban sampai sistem menunjukkan **tanda degradasi** (response naik, error mulai muncul) lalu catat ambangnya.
3. Amati **pola degradasi**: bertahap dan terkendali (baik) vs langsung crash (buruk).
4. Selalu uji **pemulihan (recovery)**: setelah beban diturunkan, sistem harus kembali normal.
5. Jalankan di environment terisolasi — stress test bisa merusak data/lingkungan.

## Test Design Techniques
- **Spike Testing** — lonjakan beban mendadak dalam durasi sangat pendek.
- **Soak-to-failure / Ramp to failure** — naikkan beban terus-menerus sampai gagal.
- **Recovery Testing** — pantau pemulihan setelah beban ekstrem dihentikan.
- **Threshold & Trip Point Analysis** — identifikasi nilai beban saat metrik mulai melanggar ambang.

## Test Scenarios

### Positive Testing
- Sistem bertahan sampai titik tertentu di atas kapasitas target sebelum degradasi.
- Degradasi terjadi **bertahap** (response melambat, error meningkat) bukan crash tiba-tiba.
- Setelah beban diturunkan, response time dan error rate kembali normal.
- Tidak ada **korupsi data** selama dan sesudah beban ekstrem.

### Negative Testing
- Beban jauh di atas kapasitas → sistem menolak/gagal jelas (bukan hang tanpa respons).
- Lonjakan mendadak (spike) → sistem tidak crash, paling banyak menolak sebagian request.
- Koneksi database/third-party jenuh → sistem mengembalikan error terstruktur, bukan crash.

### Boundary Testing
- Beban tepat pada titik jenuh (breaking point) → respons konsisten dan terukur.
- Satu langkah di atas titik jenuh → degradasi teramati, bukan crash acak.
- Batas maksimum koneksi/thread/antrean → perilaku saat penuh (reject vs queue).

### Integration Testing
- Stress pada satu komponen (DB/third-party) → dampaknya ke komponen lain dan ke user.
- Autoscaling (jika ada) → berhasil menambah kapasitas saat beban melonjak.
- Circuit breaker/fallback → aktif saat dependensi gagal dan pulih setelah dependensi kembali.

## Test Data
- Volume data produksi-terwakili agar operasi tidak trivial.
- Skenario lonjakan (spike) dan kenaikan bertahap (ramp) sekaligus.
- Operasi yang paling berat/rentan sebagai target stress.

## Expected Results
- Breaking point teridentifikasi dan terdokumentasi.
- Degradasi bertahap dan terkendali, tanpa crash total mendadak.
- Sistem pulih otomatis setelah beban kembali normal.
- Tidak ada kehilangan/korupsi data akibat beban berlebih.
- Error yang muncul terstruktur dan tidak mengekspos detail internal.

## Common Defects
- Sistem crash total tanpa degradasi bertahap (tidak ada backpressure/throttling).
- Antrean (queue) tumbuh tanpa batas → memory habis → OOM.
- Tidak ada circuit breaker → kegagalan satu dependensi meruntuhkan semua.
- Data korup/partial write saat beban ekstrem (transaksi tidak atomic).
- Autoscaling lambat merespons sehingga spike tetap membuat crash.

## Security Considerations
- Stress test = bentuk DoS pada diri sendiri; isolasi penuh dari produksi wajib.
- Pastikan throttling/rate limit yang ada tidak justru mengunci akun uji bersama.
- Error saat stress tidak boleh bocorkan stack trace / detail infrastruktur.

## References
- ISTQB CTFL v4.0.1 — Performance Testing (Stress Testing)
- ISO/IEC 25010 — Performance Efficiency & Reliability
