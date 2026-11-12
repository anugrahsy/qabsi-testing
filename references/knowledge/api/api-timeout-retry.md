# API Timeout & Retry Testing

## Overview
Menguji perilaku sistem saat operasi memakan waktu lebih lama dari batas, dan saat kegagalan sementara (transient) di-retry. Risiko utama: request menggantung tanpa batas, retry menciptakan efek ganda pada operasi tidak idempoten, dan kegagalan sementara dilaporkan sebagai kegagalan permanen yang membingungkan pengguna.

## When to Apply
Endpoint yang memanggil dependency (database, layanan lain, penyimpanan file) atau menjalankan proses berat (report, sinkronisasi, batch). Wajib dipasangkan dengan `api-idempotency` bila retry menyentuh operasi tulis, dan `api-integration` bila dependency-nya eksternal.

## Testing Principles
1. **Setiap panggilan eksternal punya timeout eksplisit.** Tidak ada timeout = risiko thread/connection habis.
2. **Retry hanya untuk kegagalan transient**, dengan jumlah terbatas dan backoff.
3. **Retry tidak boleh menggandakan efek samping**; operasi tulis membutuhkan idempotency key atau pengecekan status.
4. **Timeout harus menghasilkan kode yang tepat** (`504`/`503`), bukan `500` generik atau respons sukses palsu.
5. **Batas waktu end-to-end diketahui** dan lebih kecil dari timeout client.

## Test Design Techniques
- **Boundary Value Analysis** — durasi tepat di bawah, tepat pada, dan di atas timeout; jumlah retry maksimum.
- **State Transition** — sukses → gagal transient → retry sukses; gagal → retry habis → error akhir.
- **Equivalence Partitioning** — error transient (timeout, `503`, koneksi putus) vs permanen (`400`, `422`).
- **Fault Injection** — mensimulasikan dependency lambat, putus, dan error sesaat.

## Test Scenarios

### Positive Testing
- Dependency merespons dalam batas waktu → request sukses dengan latensi wajar.
- Dependency gagal sekali (transient) lalu pulih → retry berhasil, pengguna menerima sukses.
- Retry memakai backoff (jeda meningkat), bukan loop rapat.
- Request yang di-retry pada operasi tulis menghasilkan **satu** efek samping.
- Setelah retry berhasil, response konsisten dengan hasil akhir.

### Negative Testing
- Dependency tidak pernah merespons → request berhenti pada timeout dengan `504` (atau `503` sesuai kontrak), bukan menggantung.
- Dependency mengembalikan `500` berulang → setelah batas retry, error permukaan dikembalikan; tidak retry tanpa henti.
- Dependency mengembalikan error permanen (`400`/`422`) → **tidak** di-retry.
- Timeout terjadi setelah operasi tulis berhasil di sisi dependency → tidak ada duplikasi saat client retry.
- Client memutus koneksi di tengah proses → server tidak meninggalkan transaksi setengah jadi.
- Timeout pada endpoint baca → tidak mengubah state apa pun.

### Boundary Testing
- Durasi respons = timeout − 1 detik → sukses; = timeout + 1 detik → timeout.
- Jumlah percobaan = batas retry → masih dicoba; batas + 1 → berhenti.
- Backoff pada percobaan pertama vs terakhir sesuai kebijakan.
- Total waktu seluruh retry masih di bawah timeout client (tidak ada "sukses di client, gagal di server").
- Timeout sangat kecil (mis. 1 ms) → gagal rapi, bukan crash.

### Integration Testing
- Dependency lambat (slow response) → endpoint tetap membebaskan resource (tidak ada kebocoran koneksi).
- Dependency down total → circuit breaker membuka dan gagal cepat, bukan menumpuk request.
- Retry storm: banyak client retry bersamaan → tidak memperparah dependency yang sedang down.
- Timeout pada gateway konsisten dengan timeout aplikasi (tidak ada dua ambang yang bertabrakan).
- Operasi asinkron (job/queue) → timeout pada enqueue ditangani berbeda dari timeout pada eksekusi.
- Log dan metrik mencatat timeout serta retry dengan korelasi request.

## Test Data
- Simulasi latency dependency: normal, mendekati timeout, melebihi timeout.
- Simulasi error: koneksi putus, `503`, `500`, error permanen `422`.
- Payload operasi tulis dengan idempotency key untuk uji duplikasi.
- Konfigurasi retry: maksimum percobaan, base backoff, timeout per percobaan.
- Beban paralel untuk menguji retry storm dan circuit breaker.

## Expected Results
- Latensi request dibatasi oleh timeout yang terdokumentasi.
- `504 Gateway Timeout` (atau `503` sesuai kontrak) saat dependency melewati batas, dengan body error konsisten.
- Retry hanya pada error transient; error permanen langsung dikembalikan.
- Jumlah percobaan tidak melebihi batas; total waktu masih dalam SLA.
- Efek samping operasi tulis tetap satu kali walau retry terjadi.
- Resource (koneksi, thread) dilepas setelah timeout.
- Kegagalan tercatat di log/metrik dengan ID korelasi yang sama antar percobaan.

## Common Defects
- Tidak ada timeout pada panggilan HTTP/database sehingga request menggantung.
- Retry tanpa batas atau tanpa backoff sehingga memperparah outage.
- Retry pada `POST` tanpa idempotency → dua record/transaksi.
- Timeout dilaporkan sebagai `200` dengan data kosong (kegagalan tersamar).
- Timeout dilaporkan `500` sehingga client tidak tahu boleh retry.
- Total waktu retry melebihi timeout client → client menyerah, server tetap memproses, hasil tidak pernah diterima.
- Kebocoran koneksi setelah timeout (pool habis secara bertahap).
- Circuit breaker tidak ada sehingga setiap request menunggu penuh.
- Timeout berbeda antara gateway dan aplikasi sehingga error tidak konsisten.

## Security Considerations
- Slowloris/resource exhaustion: timeout wajib ada pada level koneksi dan aplikasi.
- Retry amplification dapat dijadikan DoS bila penyerang memicu endpoint mahal berulang.
- Jangan sertakan detail internal (host dependency, stack) pada pesan timeout.
- Pastikan retry tidak melewati kontrol otorisasi/rate limit.

## References
- RFC 9110 — HTTP Semantics (`504`, `503`, `Retry-After`).
- OWASP Web Security Testing Guide — WSTG-BUSL, denial of service.
- Google SRE Book — handling overload, retries, and backoff (praktik industri).
- ISTQB CTFL v4.0.1 — state transition, boundary value analysis.
