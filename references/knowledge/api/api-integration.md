# API Integration Testing

## Overview
Menguji interaksi API dengan **layanan eksternal** (penyedia pihak ketiga, service internal lain, message broker, webhook): kesesuaian kontrak, penanganan kegagalan dependency, dan konsistensi data lintas sistem. Risiko utama: respons provider dipercaya mentah, tidak ada timeout/retry, data setengah jadi saat salah satu sisi gagal, dan webhook yang tidak diverifikasi.

## When to Apply
Setiap alur yang bergantung pada sistem di luar batas aplikasi: pembayaran, pengiriman email/SMS, sinkronisasi data ke sistem lain, verifikasi identitas, integrasi SSO. Untuk endpoint yang hanya memanggil database sendiri, modul ini tidak diperlukan; gunakan `api-contract` dan `api-timeout-retry`.

## Testing Principles
1. **Kontrak dengan provider adalah eksternal dan bisa berubah** — uji asumsi, jangan hanya happy path.
2. **Kegagalan provider harus ditangani eksplisit**: timeout, error, rate limit, respons tidak valid.
3. **Integrasi tidak boleh membuat data setengah jadi**; gunakan pola kompensasi/outbox/idempotency.
4. **Eventual consistency diakui**: uji keadaan antara (pending) dan konvergensi akhir.
5. **Verifikasi keaslian pesan masuk** (webhook signature, mTLS) dan jangan percaya payload mentah.

## Test Design Techniques
- **Equivalence Partitioning** — respons provider: sukses, error bisnis, error teknis, respons tidak valid.
- **State Transition** — pending → sukses; pending → gagal → retry → sukses; pending → kedaluwarsa.
- **Decision Table** — hasil lokal × hasil provider (commit/rollback/compensate).
- **Fault Injection** — provider down, lambat, mengembalikan data rusak, membalas ganda.

## Test Scenarios

### Positive Testing
- Alur normal dengan sandbox/stub provider → data terkirim dan tersimpan konsisten.
- Respons provider dipetakan ke status domain dengan benar (mis. `paid` → status transaksi sesuai).
- Webhook/callback valid dengan signature benar → diproses sekali.
- Eventual consistency: setelah waktu tunggu wajar, data lokal dan remote konvergen.
- Pagination/sinkronisasi dari provider mengambil seluruh halaman tanpa duplikat/hilang.
- Kredensial dan endpoint provider dikonfigurasi per environment (bukan hardcoded).

### Negative Testing
- Provider tidak tersedia/timeout → aplikasi mengembalikan error yang tepat (`502`/`503`/`504`) atau menerima sebagai pending, sesuai desain.
- Provider mengembalikan `4xx` (kredensial salah, validasi bisnis) → tidak di-retry, error dipetakan jelas.
- Provider mengembalikan `5xx`/`429` → di-retry dengan backoff, lalu gagal rapi setelah batas.
- Respons provider tidak valid (JSON rusak, field hilang, tipe salah) → ditolak, tidak disimpan sebagian.
- Webhook dengan signature salah/tidak ada → `401`/`403`, tidak diproses.
- Webhook duplikat (retry provider) → diproses satu kali (idempotensi).
- Callback untuk transaksi yang tidak dikenal → diabaikan dengan aman dan dicatat.
- Provider membalas sangat lambat melampaui timeout → tidak menggantung.

### Boundary Testing
- Respons provider tepat pada batas ukuran/field yang didukung.
- Retry pada batas jumlah percobaan; setelahnya status akhir jelas.
- Nominal transaksi pada batas minimum/maksimum yang didukung provider.
- Token/kredensial hampir kedaluwarsa saat dipakai.
- Sinkronisasi pada jumlah halaman maksimum dan data kosong.
- Webhook yang tiba sangat cepat (sebelum transaksi lokal commit).

### Integration Testing
- Uji kontrak terhadap sandbox/versi provider sebenarnya (bukan hanya mock).
- Provider mengubah skema respons (field baru/dihapus) → aplikasi tidak crash.
- Dua service yang saling memanggil tidak deadlock dan tidak saling menunggu tanpa timeout.
- Message broker: pesan gagal diproses masuk dead-letter queue, tidak hilang diam-diam.
- Outbox/queue: pesan terkirim walau proses aplikasi restart.
- Rekonsiliasi: data lokal vs remote dibandingkan dan selisih dilaporkan.
- Log dan trace menyatukan satu transaksi lintas sistem (ID korelasi).

## Test Data
- Sandbox/stub provider dengan skenario: sukses, error bisnis, error teknis, timeout, respons rusak.
- Payload webhook valid, signature salah, duplikat, dan untuk resource tidak dikenal.
- Data sinkronisasi: kosong, satu halaman, banyak halaman, data berubah saat sinkronisasi.
- Kredensial valid, kedaluwarsa, dan salah scope.
- Transaksi pada batas nominal dan batas waktu kedaluwarsa.

## Expected Results
- Status domain mencerminkan hasil provider secara akurat, termasuk status pending.
- Tidak ada data setengah jadi: baik keduanya tersimpan, atau tidak ada (dengan kompensasi).
- Retry hanya untuk error transient; error permanen tidak diulang.
- Webhook dengan signature tidak valid ditolak dan tidak mengubah state.
- Webhook duplikat tidak menggandakan efek.
- Konvergensi tercapai dalam waktu yang didokumentasikan setelah provider pulih.
- Error provider dipetakan ke kode HTTP yang tepat, tanpa membocorkan detail internal provider.

## Common Defects
- Tidak ada timeout pada panggilan provider sehingga request menggantung.
- Respons provider dipercaya mentah tanpa validasi skema.
- Retry pada operasi tidak idempoten → pembayaran/notifikasi ganda.
- Error provider `500` dipetakan ke `200` karena dianggap "sudah dikirim".
- Webhook tidak diverifikasi signature → penyerang dapat memalsukan status pembayaran.
- Webhook duplikat diproses dua kali.
- Transaksi lokal commit tetapi pengiriman ke provider gagal, tanpa kompensasi/outbox.
- Kredensial provider di-hardcode atau bocor di log.
- Sinkronisasi berhenti di halaman pertama tanpa indikasi.
- Perubahan skema provider menyebabkan `500` massal.

## Security Considerations
- **Webhook signature verification** dan perlindungan replay (timestamp/nonce).
- **SSRF**: URL provider/callback tidak boleh berasal dari input pengguna tanpa whitelist.
- Jangan menonaktifkan validasi TLS untuk "mempermudah" koneksi.
- Simpan kredensial di secret manager; jangan di kode/log.
- Validasi dan batasi data yang dikirim ke provider (minimalisasi data pribadi).
- Pastikan kegagalan provider tidak membuka jalur bypass (mis. verifikasi dianggap lolos saat error).

## References
- OpenAPI Specification — kontrak API pihak ketiga maupun internal.
- OWASP Web Security Testing Guide — WSTG-INPV, SSRF, webhook security.
- OWASP ASVS — verifikasi komunikasi eksternal dan integritas data.
- Google SRE Book — retry, timeout, dan penanganan dependency failure (praktik industri).
