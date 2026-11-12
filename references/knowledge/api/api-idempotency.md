# API Idempotency Testing

## Overview
Menguji jaminan bahwa request yang diulang tidak menghasilkan efek ganda. Fokus pada endpoint **tidak idempoten secara alami** (`POST` create, pembayaran, pengajuan) yang memakai **idempotency key**, serta pada method yang menurut spesifikasi sudah idempoten (`GET`, `PUT`, `DELETE`). Risiko utama: retry jaringan menghasilkan dua record, dua transaksi, atau dua notifikasi.

## When to Apply
Endpoint yang membuat efek samping dan mungkin di-retry oleh client, gateway, atau job: create resource, submit pengajuan, transaksi pembayaran, kirim notifikasi. Aplikasikan bersama `api-timeout-retry` (retry otomatis) dan `api-concurrency` (request bersamaan).

## Testing Principles
1. **Efek samping terjadi tepat sekali**, berapa pun jumlah request dengan kunci sama.
2. **Response replay identik** dengan response pertama (status dan body), bukan hasil baru.
3. **Kunci sama + payload berbeda = konflik**, bukan diam-diam memakai payload pertama atau membuat record baru.
4. **Kunci harus terikat konteks** (user/tenant), sehingga kunci yang sama dari user lain tidak bertabrakan atau dipakai ulang.
5. **Masa simpan kunci terbatas** dan perilaku setelah kedaluwarsa dinyatakan kontrak.

## Test Design Techniques
- **State Transition** — request pertama → diproses; request kedua → replay; setelah TTL → perilaku baru.
- **Decision Table** — kunci ada/tidak × payload sama/beda × request pertama/berikutnya.
- **Boundary Value Analysis** — panjang kunci, TTL, jumlah request berulang.
- **Concurrency Testing** — beberapa request dengan kunci sama dikirim bersamaan.

## Test Scenarios

### Positive Testing
- Request dengan `Idempotency-Key` baru → diproses, efek samping satu kali, response disimpan.
- Request yang sama diulang dengan kunci dan payload identik → response pertama diputar ulang, tidak ada efek samping baru.
- `GET` diulang → hasil sama, tidak mengubah state.
- `PUT` dengan payload sama diulang → state akhir sama.
- `DELETE` diulang → state akhir sama (resource tetap terhapus), kode konsisten.
- Retry otomatis setelah timeout jaringan → hanya satu record/transaksi.

### Negative Testing
- Kunci sama dengan payload berbeda → `409`/`422` dengan pesan jelas, tidak membuat record kedua.
- Tanpa kunci pada endpoint yang mewajibkannya → `400`.
- Kunci kosong atau hanya whitespace → `400`.
- Kunci kedaluwarsa (melewati TTL) dipakai lagi untuk payload baru → diperlakukan sebagai request baru (sesuai kontrak), bukan replay salah.
- Kunci milik user lain dipakai → tidak boleh mengembalikan response milik user tersebut (isolasi per pemilik).
- Dua request berbeda kunci dengan payload sama → dua efek samping (kunci berbeda = request berbeda), sesuai desain.

### Boundary Testing
- Panjang kunci minimum dan maksimum; melebihi batas → `400`.
- Request berulang dalam jumlah besar dengan kunci sama → tetap satu efek samping, tidak menghabiskan resource.
- Tepat pada batas TTL → perilaku sesuai kontrak (masih replay atau sudah expired).
- Kunci dengan karakter khusus/unicode → diterima atau ditolak secara konsisten.
- Kunci yang sama dikirim pada dua endpoint berbeda → tidak saling memengaruhi (scope per endpoint).

### Integration Testing
- Retry gateway/proxy setelah timeout → satu efek samping.
- Client crash setelah request terkirim lalu mengulang → satu efek samping.
- Request bersamaan dengan kunci sama (race) → satu diproses, lainnya menunggu/replay; tidak ada dua record (lihat `api-concurrency`).
- Efek samping turunan (notifikasi, webhook, jurnal) juga hanya sekali.
- Penyimpanan kunci gagal (storage down) → endpoint gagal aman (fail closed) atau perilaku yang didokumentasikan, bukan lanjut tanpa proteksi.
- Replay mengembalikan header yang sama (`Location`, `Content-Type`) seperti response asli.

## Test Data
- Payload create valid dengan kunci unik.
- Payload identik dan payload berbeda untuk kunci yang sama.
- Kunci milik user A dan user B.
- Kunci pada batas panjang dan kunci dengan karakter khusus.
- Skenario TTL: kunci baru, kunci hampir kedaluwarsa, kunci sudah kedaluwarsa.
- Simulasi timeout/retry pada level client dan gateway.

## Expected Results
- Efek samping (record, transaksi, notifikasi) berjumlah tepat satu untuk satu kunci.
- Response replay identik: status, body, dan header kunci.
- `409`/`422` untuk kunci sama dengan payload berbeda.
- Kunci terisolasi per pengguna/tenant dan per endpoint.
- Request bersamaan tidak menghasilkan dua efek samping.
- Setelah TTL, perilaku sesuai kontrak dan tidak mencampur response lama dengan payload baru.
- Retry setelah timeout tidak menciptakan data ganda.

## Common Defects
- Retry menghasilkan dua record karena tidak ada pengecekan kunci.
- Kunci hanya dicek di client, bukan di server.
- Request bersamaan lolos pengecekan karena "check-then-act" tanpa lock/unique constraint.
- Kunci sama dengan payload berbeda tetap membuat record baru.
- Replay mengembalikan response yang baru dihitung (mis. `created_at` berbeda).
- Kunci tidak discope per user sehingga satu user dapat membaca hasil user lain.
- TTL tidak diterapkan sehingga penyimpanan kunci tumbuh tanpa batas.
- Response asli tidak disimpan; replay mengembalikan `200` kosong.
- Notifikasi/webhook terkirim dua kali walau record hanya satu.

## Security Considerations
- Kunci idempotensi yang dapat ditebak/dipakai ulang lintas user berpotensi membocorkan response orang lain.
- Simpan hasil replay bersama identitas pemilik dan validasi sebelum mengembalikan.
- Batasi ukuran dan jumlah kunci untuk mencegah penyalahgunaan storage (DoS).
- Jangan sertakan data sensitif berlebih pada response yang disimpan lama.

## References
- IETF Idempotency-Key HTTP Header Field (draft) — semantik kunci dan replay.
- RFC 9110 — HTTP Semantics, §9.2.2 (metode idempoten).
- OpenAPI Specification — header parameter `Idempotency-Key`.
- OWASP Web Security Testing Guide — business logic / race condition.
