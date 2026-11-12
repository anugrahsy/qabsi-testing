# API Rate Limit Testing

## Overview
Menguji pembatasan laju request (rate limiting/throttling): berapa banyak request diizinkan per jendela waktu, bagaimana kelebihannya ditolak, dan apakah informasi kuota dikomunikasikan dengan benar. Risiko utama: limit tidak berlaku (brute force/abuse), limit terlalu agresif memblokir pengguna sah, dan `429` tanpa `Retry-After` sehingga client retry membabi buta.

## When to Apply
Endpoint publik, endpoint autentikasi, endpoint mahal (export, report, upload), dan API yang dipakai integrasi mesin. Untuk retry setelah `429`, lihat `api-timeout-retry`; untuk pembatasan per akun pada login, lihat modul domain `auth-*`.

## Testing Principles
1. **Batas harus terdefinisi dan terukur**: berapa request, per apa (IP/user/token/tenant), per jendela waktu apa.
2. **Penolakan terjadi sebelum kerja mahal**, bukan setelah query/penulisan.
3. **`429` wajib informatif**: `Retry-After`, dan bila ada, header kuota.
4. **Counter tidak bocor antar identitas**: kuota user A tidak mengurangi user B.
5. **Reset jendela waktu deterministik**, tanpa lonjakan di batas jendela.

## Test Design Techniques
- **Boundary Value Analysis** — request ke-(limit), ke-(limit+1), setelah reset.
- **Equivalence Partitioning** — di bawah limit / tepat limit / di atas limit.
- **State Transition** — jendela penuh → ditolak → jendela reset → diterima.
- **Concurrency Testing** — request bersamaan di sekitar batas.

## Test Scenarios

### Positive Testing
- Request di bawah batas → `2xx` dan header kuota (bila ada) mencerminkan sisa.
- Request ke-(limit) tepat → masih diterima.
- Setelah jendela waktu berlalu → kuota pulih dan request diterima kembali.
- Limit per pengguna: user lain tetap dapat mengirim saat satu user mencapai batas.
- Endpoint dengan limit berbeda (baca vs tulis) menerapkan nilainya masing-masing.

### Negative Testing
- Request ke-(limit+1) dalam jendela yang sama → `429` + `Retry-After`.
- Lonjakan burst melebihi batas → ditolak, tidak ada kerja yang dieksekusi.
- Request tanpa identitas (anonim) → dibatasi per IP/proxy dengan benar.
- Memalsukan `X-Forwarded-For` untuk menghindari limit → tidak berhasil (hanya proxy tepercaya yang dihitung).
- Berganti token untuk menghindari limit → tetap dibatasi sesuai kebijakan per akun/IP.
- Request setelah `Retry-After` → diterima, bukan langsung `429` lagi.
- Rate limit tidak menyebabkan `500` atau memutus koneksi tanpa respons.

### Boundary Testing
- Tepat pada batas jendela (mis. detik ke-59 dan ke-60) → perilaku konsisten.
- Limit = 1 → request pertama diterima, kedua `429`.
- `Retry-After` = 0 atau nilai sangat kecil → tidak memicu loop.
- Nilai `Retry-After` berupa detik vs tanggal HTTP → sesuai kontrak.
- Jumlah header kuota (`X-RateLimit-Limit`, `Remaining`, `Reset`) konsisten dengan counter sebenarnya.
- Request bersamaan tepat di batas → total yang lolos tidak melebihi limit (tidak ada race).

### Integration Testing
- Gateway dan aplikasi tidak menerapkan limit ganda yang tidak terdokumentasi.
- Load balancer dengan beberapa instance berbagi counter (bukan per instance) bila limit bersifat global.
- Client/harness yang mematuhi `Retry-After` berhasil setelah jendela reset.
- Endpoint autentikasi lebih ketat daripada endpoint baca biasa.
- Monitoring/alert menerima sinyal saat limit sering tercapai (indikasi abuse atau limit terlalu rendah).
- `429` tidak di-cache oleh proxy dan tidak disajikan ke request berikutnya.

## Test Data
- Skenario beban: N request berurutan tepat di bawah, pada, dan di atas limit.
- Beberapa identitas (user/token/IP) untuk menguji isolasi counter.
- Nilai `X-Forwarded-For` palsu dan asli.
- Konfigurasi jendela waktu pendek (mis. 60 detik) untuk pengujian cepat.
- Request paralel di sekitar batas untuk menguji race.

## Expected Results
- `429 Too Many Requests` untuk kelebihan, dengan `Retry-After` yang valid.
- Header kuota (bila ada) akurat: `limit`, `remaining`, `reset` konsisten satu sama lain.
- Tidak ada efek samping (record, email, transaksi) dari request yang ditolak.
- Kuota pulih setelah jendela berakhir; tidak ada blockade permanen.
- Counter terisolasi per identitas sesuai kebijakan.
- Request paralel tidak melampaui limit yang ditetapkan.
- Endpoint tetap merespons cepat saat menolak (tidak menggantung).

## Common Defects
- `429` dikirim tanpa `Retry-After` sehingga client retry agresif.
- Counter dihitung setelah proses dijalankan, sehingga request yang ditolak tetap menulis data.
- Limit per instance sehingga dengan 3 instance efektif menjadi 3× limit.
- Race condition: request paralel semuanya lolos karena counter dibaca sebelum ditulis.
- Counter tidak pernah reset (blockade permanen) atau reset terlalu sering.
- Limit dapat diakali dengan mengganti header `X-Forwarded-For`.
- Limit diterapkan pada IP proxy sehingga semua pengguna di belakang NAT berbagi kuota.
- `429` di-cache dan disajikan ke request yang seharusnya diterima.
- Endpoint mahal tidak dibatasi sehingga dapat dipakai untuk resource exhaustion.

## Security Considerations
- Rate limit adalah kontrol utama terhadap **brute force**, **credential stuffing**, **enumerasi**, dan **scraping**.
- Terapkan pada endpoint autentikasi, reset password, dan OTP dengan ambang lebih ketat.
- Jangan membocorkan apakah suatu akun ada lewat perbedaan respons saat limit.
- Pastikan penyerang tidak bisa mereset kuota dengan mengganti IP/token.
- Batasi juga ukuran request dan kedalaman query, bukan hanya jumlah request.

## References
- RFC 6585 — Additional HTTP Status Codes (§4 `429 Too Many Requests`).
- RFC 9110 — HTTP Semantics, `Retry-After`.
- IETF RateLimit header fields (draft) — `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`.
- OWASP Web Security Testing Guide — WSTG-ATHN (brute force), WSTG-BUSL.
