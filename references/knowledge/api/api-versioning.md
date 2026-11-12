# API Versioning Testing

## Overview
Menguji pengelolaan versi API: apakah versi dipilih secara eksplisit, apakah versi lama tetap berperilaku sesuai kontraknya, dan apakah perubahan breaking hanya terjadi pada versi baru. Risiko utama: perubahan breaking dirilis tanpa menaikkan versi, versi diabaikan sehingga semua client mendapat perilaku terbaru, dan versi lama dihapus sebelum masa transisi berakhir.

## When to Apply
API yang dikonsumsi lebih dari satu client (mobile, web, integrasi pihak ketiga) atau yang dirilis berulang. Modul ini dipakai saat merancang skenario regresi lintas versi dan saat menguji endpoint yang ditandai deprecated.

## Testing Principles
1. **Versi adalah bagian dari kontrak.** Request tanpa versi harus punya perilaku default yang terdokumentasi.
2. **Versi lama tetap stabil** sampai dinyatakan dihapus; bug fix non-breaking boleh, breaking tidak.
3. **Deprecation dikomunikasikan mesin-dan-manusia**: header + dokumentasi + tanggal.
4. **Versi tidak boleh bercampur** dalam satu response (field v1 dan v2 sekaligus tanpa aturan).
5. **Perubahan skema data harus kompatibel** dengan semua versi yang masih dilayani.

## Test Design Techniques
- **Equivalence Partitioning** — versi didukung / tidak didukung / tidak dikirim.
- **Boundary Value Analysis** — versi tertua, terbaru, versi tepat sebelum/sesudah dihapus.
- **Decision Table** — versi × endpoint × field yang berubah.
- **State Transition** — versi aktif → deprecated → retired.

## Test Scenarios

### Positive Testing
- Request ke versi terbaru → perilaku dan schema versi tersebut.
- Request ke versi lama yang masih didukung → perilaku lama tetap utuh.
- Request tanpa versi → memakai default yang didokumentasikan, konsisten.
- Response menyertakan penanda versi (header/body) bila kontrak menyatakan.
- Endpoint deprecated masih berfungsi dan mengembalikan header deprecation.
- Dua versi berjalan berdampingan dalam satu deployment tanpa saling mengganggu.

### Negative Testing
- Versi tidak didukung → `400`/`404`/`406` sesuai kontrak, dengan pesan yang menyebut versi yang didukung.
- Format versi invalid (`vabc`, `1.x`) → `400`, bukan `500`.
- Versi di path berbeda dari versi di header → ditolak atau aturan presedensi jelas.
- Endpoint yang dihapus pada versi baru → `404` pada versi itu, tetap ada pada versi lama.
- Field yang dihapus pada versi baru masih dikirim ke client versi lama (sesuai kontrak lama).
- Client versi lama mengirim field yang sudah tidak ada → diabaikan/ditolak sesuai kontrak versi tersebut.

### Boundary Testing
- Versi tertua yang masih didukung → semua skenario utama tetap lolos.
- Versi tepat sebelum di-retire → masih melayani.
- Versi setelah tanggal sunset → ditolak dengan pesan yang jelas.
- Nomor versi besar (mis. `v10`) → routing benar, bukan salah parse.
- Perbedaan perilaku pada batas yang berubah antar versi (mis. limit maksimum pagination berbeda).
- Field opsional yang menjadi required di versi baru → client lama tidak rusak.

### Integration Testing
- Client lama (berbasis versi lama) menjalankan alur end-to-end terhadap API baru.
- Client baru terhadap API lama → gagal dengan pesan jelas, bukan data salah.
- Service internal memakai versi yang dipin; upgrade satu service tidak merusak yang lain.
- Migrasi database kompatibel dengan dua versi kode yang berjalan bersamaan.
- Deprecation header muncul di semua response versi yang deprecated, termasuk error.
- Monitoring mencatat pemakaian per versi untuk memutuskan sunset.

## Test Data
- Request dengan versi: tertua, terbaru, tidak didukung, tidak dikirim, format invalid.
- Payload yang field-nya berbeda antar versi (ada di v1, dihapus di v2, ditambah di v3).
- Snapshot response per versi sebagai baseline regresi.
- Client/skrip yang mewakili konsumen versi lama dan baru.
- Konfigurasi routing versi (path, header, query).

## Expected Results
- Setiap versi mengembalikan schema dan perilaku sesuai kontraknya masing-masing.
- Versi tidak didukung ditolak dengan kode yang konsisten dan daftar versi yang valid.
- Request tanpa versi memakai default yang sama setiap kali (tidak berubah diam-diam).
- Endpoint deprecated tetap berfungsi dan menyertakan `Deprecation`/`Sunset`.
- Tidak ada field versi lain bocor ke response versi yang sedang dilayani.
- Perubahan breaking hanya muncul pada versi baru.

## Common Defects
- Breaking change dirilis pada versi yang sama (client lama rusak tanpa peringatan).
- Parameter versi diabaikan sehingga semua request mendapat perilaku terbaru.
- Default version berubah tanpa diumumkan.
- Versi lama dihapus sebelum tanggal sunset yang dijanjikan.
- Response mencampur field dari dua versi.
- Endpoint deprecated tidak mengirim header deprecation.
- Routing versi salah parse untuk nomor dua digit.
- Bug diperbaiki hanya di versi terbaru padahal juga ada di versi lama yang masih didukung (tanpa keputusan eksplisit).
- Perbedaan perilaku antar versi tidak terdokumentasi sehingga sulit diuji.

## Security Considerations
- Versi lama yang tidak dipatch menjadi jalur masuk bagi kerentanan yang sudah diperbaiki.
- Pastikan versi deprecated tetap menerapkan kontrol autentikasi/otorisasi yang sama.
- Jangan mengungkap detail internal (changelog, roadmap) lewat pesan versi tidak didukung.
- Sunset harus ditegakkan agar attack surface lama tidak terbuka selamanya.

## References
- OpenAPI Specification — versioning dan `info.version`.
- Google AIP-185 — API versioning.
- RFC 8594 — The Sunset HTTP Header Field.
- Semantic Versioning 2.0.0 — makna major/minor/patch (untuk perubahan breaking).
