# API Authorization Testing

## Overview
Menguji **otorisasi** pada lapisan API: apakah pemanggil yang sudah terautentikasi boleh melakukan aksi pada resource tertentu. Risiko utama: pengecekan hanya di UI, pengecekan level endpoint tanpa level objek (BOLA/IDOR), dan kepercayaan pada header/klaim yang dikirim client untuk menentukan scope.

## When to Apply
Semua endpoint yang memuat data atau mengubah state, terutama yang punya konsep pemilik, organisasi, unit, atau role. Modul ini fokus pada **apa yang boleh dilakukan**; untuk identitas gunakan `api-authentication`. Untuk aturan akses berbasis atribut yang kompleks, gunakan modul domain `auth-abac`/`auth-object-access`.

## Testing Principles
1. **Otorisasi ditegakkan di server**, bukan diasumsikan dari UI.
2. **Dua level harus diuji**: endpoint (boleh memanggil method ini?) dan objek (boleh menyentuh record ini?).
3. **Deny by default** untuk role yang tidak disebutkan.
4. **Konteks scope berasal dari identitas tepercaya**, bukan dari header/body yang bisa diubah client.
5. **Konsisten di semua jalur baca/tulis**: list, detail, search, export, update, delete.

## Test Design Techniques
- **Decision Table** — role × kepemilikan × aksi × status resource.
- **Equivalence Partitioning** — role diizinkan / role tidak diizinkan / tanpa role.
- **State Transition** — role berubah (dinaikkan/dicabut) → akses berikutnya.
- **Combinatorial** — beberapa role sekaligus, beberapa scope sekaligus.

## Test Scenarios

### Positive Testing
- Role yang berwenang → aksi berhasil (`200`/`201`/`204`).
- Pemilik resource → dapat membaca dan mengubah resource miliknya.
- Admin/superuser → dapat mengakses lintas pemilik sesuai kebijakan.
- User dengan beberapa role → gabungan izin diterapkan (union), tanpa konflik.
- Scope konteks (organisasi/unit) yang sah → data yang dikembalikan hanya dari scope tersebut.

### Negative Testing
- Role tanpa izin → `403` (bukan `200` dengan data kosong yang menyembunyikan masalah).
- Tanpa role sama sekali → `403` (setelah autentikasi) atau `401` (tanpa identitas).
- User A mengakses ID milik user B (horizontal) → `403`/`404`, tidak ada data bocor.
- User biasa memanggil endpoint admin (vertical) → `403`.
- Method terlarang pada resource yang boleh dibaca (mis. GET boleh, DELETE tidak) → `403`, bukan `405` bila method ada tetapi tidak berwenang.
- Mengubah header scope (`X-Organization`, `X-Unit`) ke nilai lain → ditolak atau diabaikan, tidak mengubah data yang diakses.
- Mengubah field `owner_id`/`organization_id` di body → tidak mengubah kepemilikan.
- Endpoint nested (`/parents/{id}/children/{childId}`) dengan `childId` milik parent lain → `404`/`403`.

### Boundary Testing
- Role dengan izin paling minimal → hanya aksi yang diizinkan yang berhasil.
- Izin dicabut saat sesi aktif → akses berikutnya ditolak tanpa menunggu token kedaluwarsa (sesuai kebijakan).
- User dengan banyak role (batas atas) → evaluasi tetap benar.
- Resource tanpa pemilik (sistem) → aturan aksesnya eksplisit, bukan default allow.
- Resource pada batas scope (unit paling atas/bawah) → hanya terlihat oleh scope yang tepat.

### Integration Testing
- Konsistensi list vs detail vs update vs delete untuk resource yang sama.
- Search/filter/export tidak membocorkan record di luar scope.
- Gateway meneruskan identitas dengan benar; aplikasi tidak memakai header yang bisa dipalsukan.
- Service downstream menerima konteks otorisasi dan menerapkannya (bukan hanya service depan).
- Cache tidak menyajikan respons milik user lain (cache key memuat identitas/scope).
- Audit mencatat percobaan akses yang ditolak.

## Test Data
- User dengan role berbeda: admin, operator, viewer, tanpa role.
- Resource milik user A, user B, dan resource sistem.
- Beberapa organisasi/unit untuk menguji scoping.
- Token valid dengan klaim role berbeda dari role di database (uji kepercayaan klaim).
- Data di batas scope (unit anak, unit saudara).

## Expected Results
- `403` untuk terautentikasi tetapi tidak berwenang; `401` bila identitas tidak ada.
- Data di luar scope tidak pernah muncul di body, count, maupun error.
- Perubahan header/body scope tidak mengubah data yang dapat diakses.
- Keputusan otorisasi sama di seluruh endpoint untuk kondisi yang sama.
- Setelah izin dicabut, akses ditolak pada request berikutnya sesuai kebijakan.
- Percobaan akses ditolak tercatat di log/audit dengan identitas dan resource.

## Common Defects
- Otorisasi hanya dicek di frontend; API terbuka bila dipanggil langsung.
- BOLA/IDOR: detail dan update tidak memeriksa kepemilikan objek.
- Endpoint nested tidak memverifikasi relasi parent-child.
- Role dibaca dari klaim token lama sehingga pencabutan tidak berlaku.
- Scope diambil dari header yang dikirim client tanpa verifikasi.
- `200` dengan array kosong dipakai sebagai pengganti `403` sehingga masalah tersembunyi.
- Pengecekan role memakai nama role hardcoded, bukan permission.
- Endpoint export/download melewatkan filter scope.
- Service internal saling percaya tanpa meneruskan konteks otorisasi.

## Security Considerations
- **BOLA** (API1) dan **BFLA** (API5) adalah risiko utama: uji setiap objek dan setiap fungsi, bukan hanya satu endpoint per role.
- Jangan mengandalkan ID yang tidak bisa ditebak sebagai kontrol akses.
- Terapkan field-level authorization (mis. user boleh lihat tapi tidak boleh ubah field tertentu).
- Hindari kebocoran keberadaan resource lewat perbedaan `403`/`404`.
- Pastikan cache dan CDN tidak menyajikan respons terproteksi ke pengguna lain.

## References
- OWASP Web Security Testing Guide — WSTG-ATHZ (authorization testing), IDOR.
- OWASP API Security Top 10 — API1 BOLA, API5 BFLA.
- OpenAPI Specification — security schemes dan scope.
- NIST RBAC — model role dan permission (untuk desain kontrol).
