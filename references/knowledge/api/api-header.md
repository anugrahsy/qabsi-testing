# API Header Testing

## Overview
Menguji peran **HTTP header** dalam request dan response: `Content-Type`, `Accept`, `Authorization`, header kustom (organisasi, korelasi, bahasa), serta header caching. Risiko utama: body diproses meski `Content-Type` salah, header kustom diabaikan/dipalsukan, dan header tidak diteruskan dengan benar melewati gateway.

## When to Apply
Semua endpoint, terutama yang menerima body (Content-Type), melakukan negosiasi format (Accept), memakai konteks header kustom (multi-tenant, lokalisasi), atau berada di belakang gateway/proxy. Untuk validasi token, lihat `api-authentication`.

## Testing Principles
1. **Header adalah kontrak**, sama seperti body. Header wajib tidak boleh opsional diam-diam.
2. **Content-Type menentukan parser**, bukan ditebak dari isi body.
3. **Header kustom yang memengaruhi data (scope, tenant)** tidak boleh dipercaya mentah dari client tanpa otorisasi.
4. **Nama header case-insensitive**, tetapi nilai dan duplikasinya harus ditangani eksplisit.
5. **Header harus bertahan melewati gateway** (tidak hilang, tidak ditimpa).

## Test Design Techniques
- **Equivalence Partitioning** — header ada/tidak ada, nilai valid/invalid/tidak didukung.
- **Decision Table** — kombinasi Content-Type × Accept × body.
- **Boundary Value Analysis** — panjang nilai header, jumlah header, ukuran total header.
- **State Transition** — respons `406`/`415` vs pemrosesan normal.

## Test Scenarios

### Positive Testing
- `Content-Type: application/json` + body JSON valid → diproses.
- `Accept: application/json` → response JSON.
- Header kustom yang didokumentasikan (mis. `X-Organization`, `X-Request-Id`) diterima dan memengaruhi hasil sesuai kontrak.
- `Authorization: Bearer <token>` valid → request diproses.
- Header korelasi yang dikirim client di-echo atau diteruskan ke response/log.
- `If-None-Match`/`If-Modified-Since` → `304` bila resource tidak berubah.

### Negative Testing
- Body dikirim tanpa `Content-Type` → `415` (bukan diproses).
- `Content-Type` tidak didukung (`text/plain`, `application/xml`) saat kontrak hanya JSON → `415`.
- `Content-Type: application/json` tetapi body bukan JSON → `400`.
- `Accept` tidak didukung → `406` (atau abaikan sesuai kontrak, tetapi konsisten).
- Header wajib kustom tidak dikirim → `400` dengan pesan yang menyebut header tersebut.
- `Authorization` malformed/tanpa skema → `401`, bukan `500`.
- Header duplikat dengan nilai berbeda → ditolak `400` atau aturan menang yang jelas.
- Header dengan karakter ilegal (CRLF) → ditolak `400`, tidak diteruskan.

### Boundary Testing
- Nilai header tepat pada panjang maksimum; melebihi → `431` atau `400`.
- Nilai header kosong `""` vs header tidak dikirim → perilaku berbeda dan konsisten.
- Nama header beda kapitalisasi (`content-type`, `Content-Type`) → diperlakukan sama.
- Nilai header dengan spasi di awal/akhir → di-trim atau ditolak sesuai kontrak.
- Banyak header sekaligus (batas jumlah) → tetap diproses.
- Header dengan karakter non-ASCII (nama organisasi beraksen) → encoding benar.

### Integration Testing
- Gateway meneruskan `Authorization`, `Content-Type`, dan header kustom ke aplikasi.
- Gateway menambahkan `X-Forwarded-For`/`X-Request-Id` tanpa menimpa nilai client secara tidak aman.
- CORS preflight (`OPTIONS`) mengembalikan `Access-Control-Allow-*` yang sesuai, bukan wildcard berbahaya.
- Respons cache: `Cache-Control`, `ETag`, `Vary` konsisten dengan perilaku cache.
- Header `Content-Type` pada response file/unduhan sesuai isi sebenarnya.
- Header korelasi muncul di log aplikasi dan response untuk penelusuran.

## Test Data
- Body JSON valid, body form-urlencoded, body multipart (lihat `api-file-upload`).
- Header set lengkap valid dan setiap header wajib dihilangkan satu per satu.
- Nilai header invalid: tipe konten salah, Accept tak didukung, token rusak.
- Nilai header dengan CRLF, kutip, dan karakter non-ASCII.
- Konfigurasi gateway/proxy dengan aturan forwarding.

## Expected Results
- `415` untuk `Content-Type` tidak didukung; body tidak diparsing.
- `406` bila `Accept` tidak dapat dipenuhi (bila kontrak menetapkan negosiasi).
- `400` untuk header wajib yang hilang/kosong, dengan pesan yang menyebut header.
- `401` untuk `Authorization` tidak valid; tidak pernah `500`.
- Header kustom yang memengaruhi scope divalidasi terhadap otorisasi, bukan dipercaya begitu saja.
- Header response (`Content-Type`, `X-Request-Id`, `Cache-Control`) sesuai kontrak.
- Header ilegal ditolak dan tidak muncul di response (tidak ada header injection).

## Common Defects
- Body tetap diparsing walau `Content-Type` salah atau tidak ada.
- `Content-Type` response salah (JSON dikirim sebagai `text/html`).
- Header kustom tidak diteruskan gateway sehingga scope/tenant selalu default.
- Pencarian header case-sensitive (`Content-type` gagal dikenali).
- `401` tidak menyertakan `WWW-Authenticate`.
- Header duplikat menimbulkan perilaku acak (nilai pertama vs terakhir).
- CORS `Access-Control-Allow-Origin: *` digabung `Allow-Credentials: true`.
- Header korelasi dibuat ulang di setiap hop sehingga log tidak bisa disatukan.
- Nilai header client dipercaya untuk menentukan tenant/organisasi.

## Security Considerations
- **Header injection / CRLF**: nilai header yang mengandung `\r\n` tidak boleh diteruskan.
- **Mass assignment lewat header**: header seperti `X-User-Id`, `X-Organization` tidak boleh menjadi sumber otorisasi tanpa verifikasi.
- **CORS**: konfigurasi longgar membuka akses lintas origin; `Vary: Origin` bila origin dinamis.
- **Host header injection**: jangan pakai `Host` mentah untuk membentuk URL reset password/redirect.
- Jangan mencatat `Authorization`/cookie ke log.
- `X-Forwarded-For` harus dipercaya hanya dari proxy tepercaya.

## References
- RFC 9110 — HTTP Semantics (header fields, Content-Type, Accept, Authorization).
- RFC 9111 — HTTP Caching (`Cache-Control`, `ETag`, `Vary`).
- OWASP Web Security Testing Guide — WSTG-CLNT (CORS), WSTG-INPV (header injection).
- OpenAPI Specification — header parameters dan response headers.
