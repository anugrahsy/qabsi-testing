# API Error Handling Testing

## Overview
Menguji **bentuk dan isi respons error**: skema error yang konsisten, kode yang dapat dibaca mesin, pesan yang dapat dibaca manusia, detail per field, dan tidak bocornya informasi internal saat terjadi exception. Risiko utama: setiap endpoint punya format error berbeda, stack trace/SQL bocor, dan error tak tertangani menghasilkan `500` tanpa informasi yang berguna.

## When to Apply
Semua endpoint. Modul ini melengkapi `api-http-status` (kode) dengan isi body, pencatatan log, dan propagasi error antar layanan. Terapkan saat mendesain error contract maupun saat menguji penanganan exception.

## Testing Principles
1. **Satu skema error untuk seluruh API** — field dan tipe sama di semua endpoint.
2. **Error harus actionable**: client tahu apa yang salah dan apa yang bisa dilakukan.
3. **Tidak ada kebocoran internal** pada respons yang dikirim ke client.
4. **Setiap error tercatat** di log dengan korelasi request, tanpa mencatat data sensitif.
5. **Error tidak boleh menelan kegagalan**: kegagalan yang dikembalikan sebagai sukses adalah defect paling berbahaya.

## Test Design Techniques
- **Equivalence Partitioning** — error validasi / autentikasi / otorisasi / not found / konflik / server.
- **Decision Table** — jenis exception × layer (validasi, DB, dependency) × hasil yang diharapkan.
- **Boundary Value Analysis** — jumlah error field banyak, panjang pesan, banyak item pada error array.
- **Fault Injection** — memicu exception tak terduga (DB down, dependency error, bug).

## Test Scenarios

### Positive Testing
- Error validasi mengembalikan envelope konsisten: kode, pesan, dan daftar field.
- Setiap field invalid punya entri tersendiri (field, kode, pesan).
- Error `404`/`409`/`403` memakai envelope yang sama dengan error validasi.
- Pesan error dapat dibaca manusia dan sesuai bahasa yang diminta (bila ada i18n).
- Respons error menyertakan ID korelasi yang juga ada di log.
- Error pada endpoint berbeda memiliki bentuk yang identik.

### Negative Testing
- Exception tak tertangani → `500` dengan pesan generik, **tanpa** stack trace, SQL, path file, atau versi library.
- Error database (constraint, koneksi putus) → dipetakan ke `409`/`503`, bukan membocorkan pesan SQL.
- Error dependency eksternal → `502`/`503` dengan pesan yang tidak menyebut detail internal.
- Error pada body yang bukan JSON → `400` dengan pesan yang jelas, bukan `500`.
- Error validasi dengan banyak field → semua field dilaporkan (atau batas yang terdokumentasi).
- Error yang seharusnya tidak terjadi (bug) tidak dikembalikan sebagai `200` dengan `{success: false}`.
- Error tidak menyebabkan koneksi terputus tanpa respons.

### Boundary Testing
- Satu error field vs sangat banyak error field (batas pelaporan).
- Pesan error tepat pada panjang maksimum; tidak terpotong di tengah karakter multibyte.
- Error array kosong tidak dikirim sebagai `errors: []` yang membingungkan.
- Nilai input berisi karakter khusus/unicode muncul utuh dan aman di pesan.
- Error pada payload sangat besar → `413` dengan envelope yang sama.
- Timeout dependency tepat pada batas → error yang konsisten (`504`), bukan campuran.

### Integration Testing
- Error dari service internal tidak diteruskan mentah ke client; dipetakan ke envelope publik.
- ID korelasi diteruskan antar service sehingga satu kegagalan dapat dilacak end-to-end.
- Gateway mempertahankan envelope error aplikasi (tidak menggantinya dengan halaman HTML).
- Error pada proses asinkron muncul di status job, bukan hilang.
- Log error memuat konteks yang cukup (endpoint, user, resource) tanpa data sensitif.
- Alerting terpicu untuk lonjakan `5xx`, bukan untuk `4xx` normal.

## Test Data
- Request dengan satu field invalid dan dengan banyak field invalid.
- Payload yang memicu constraint database (duplikat, foreign key).
- Simulasi dependency error/timeout.
- Input berisi karakter khusus, unicode, dan string sangat panjang.
- Skenario exception buatan (mis. mematikan koneksi DB di lingkungan uji).

## Expected Results
- Envelope error konsisten: mis. `code`, `message`, `errors[]`/`details`, `request_id`.
- Kode error dapat dibaca mesin dan stabil (tidak berubah teksnya antar rilis).
- Pesan menyebut apa yang salah tanpa mengungkap implementasi.
- `4xx` tidak memuat stack trace; `5xx` tidak memuat detail internal apa pun.
- Setiap error tercatat di log dengan level yang tepat dan ID korelasi.
- Tidak ada respons sukses untuk operasi yang gagal.
- Error dapat ditindaklanjuti: client tahu field mana, atau tahu boleh retry.

## Common Defects
- Format error berbeda-beda per endpoint (`message` vs `error` vs `msg`).
- Stack trace atau query SQL muncul di body `500`.
- Validasi hanya mengembalikan error pertama, menyulitkan perbaikan.
- `200 OK` dengan `{success: false}` sehingga monitoring tidak mendeteksi kegagalan.
- Pesan error kosong atau `null`.
- Error dependency diteruskan mentah (host internal, token, detail provider).
- Error tidak tercatat di log, atau tercatat tanpa ID korelasi.
- Pesan error membocorkan keberadaan akun/resource.
- Error pada satu item di batch menggagalkan seluruh batch tanpa menjelaskan item mana.
- Exception tertelan dan operasi dilaporkan sukses padahal tidak tersimpan.

## Security Considerations
- **Information disclosure** lewat stack trace, SQL, path, versi framework, dan konfigurasi.
- Pesan error tidak boleh memantulkan input mentah tanpa encoding (XSS pada konsumen HTML).
- Log injection: input dengan newline/karakter kontrol tidak boleh merusak format log.
- Pesan autentikasi tidak boleh membedakan "user tidak ada" vs "password salah".
- Pastikan error tidak membocorkan daftar endpoint/internal service.

## References
- RFC 9457 — Problem Details for HTTP APIs.
- OWASP Web Security Testing Guide — WSTG-ERRH (improper error handling).
- OpenAPI Specification — schema response error yang dapat dipakai ulang.
- OWASP Logging Cheat Sheet — praktik pencatatan tanpa data sensitif.
