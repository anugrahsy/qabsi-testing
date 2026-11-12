# API Combination Testing

## Overview
Menguji **kombinasi parameter** collection (filter + sort + pagination + search) sekaligus. Risiko utama: tiap parameter lolos sendiri tapi gagal saat digabung — urutan aplikasi parameter salah, data hilang/duplikat.

## When to Apply
Endpoint collection yang mendukung >1 parameter. **Prioritas tinggi** — banyak bug hanya muncul saat parameter digabung, lolos saat diuji terpisah.

## Testing Principles
1. Urutan aplikasi parameter harus jelas: **filter → search → sort → paginate**.
2. Pagination harus mengambil halaman dari **hasil yang sudah difilter, dicari, dan diurutkan**.
3. Tidak boleh ada data **duplikat/hilang** antar halaman pada hasil kombinasi.
4. Total `count`/`total` harus konsisten dengan kombinasi yang diterapkan.

## Test Design Techniques
- Combinatorial / pairwise — pilih subset kombinasi parameter.
- Decision Table — kondisi tiap parameter.
- Boundary — kombinasi dengan nilai batas.

## Test Scenarios

### Positive Testing
Contoh: `GET /api/employees?page=2&limit=10&status=active&sort=created_at&order=desc`
- Semua record memenuhi filter `status=active`.
- Urutan berdasarkan `created_at` descending.
- Pagination mengambil halaman kedua dari hasil yang sudah difilter + diurutkan.
- Tidak ada data duplikat/hilang antar halaman.

### Negative Testing
- Kombinasi dengan parameter invalid (mis. `order` invalid + filter valid) → error sesuai kontrak.
- Kombinasi filter menghasilkan empty + page di luar jangkauan → empty result valid.
- Parameter saling bertentangan (mis. sort field tak ada) → ditangani sesuai kontrak.

### Boundary Testing
- Filter + `limit=1` → tiap halaman 1 item terfilter.
- Filter + page terakhir → hanya sisa record terfilter.

### Integration Testing
- Filter + search + sort + pagination **semua sekaligus** → semua diterapkan benar.
- Ubah satu parameter → hasil berubah **konsisten** (tidak ada efek tak terduga).
- Kombinasi dengan otoritas scope (header `X-Organization`) → hasil tetap terscope.

## Test Data
- Dataset besar dengan variasi: status beda, nilai sort beda, substring search overlap.
- Data yang menyusut setelah filter (untuk verifikasi pagination).
- Record dengan nilai sort sama (tie-break stabil).

## Expected Results
- Hasil memenuhi **semua** parameter yang diterapkan.
- Urutan benar (sort setelah filter/search).
- Halaman benar (pagination atas hasil kombinasi).
- `count`/`total` konsisten dengan kombinasi.
- Perubahan satu parameter → hasil konsisten & bisa diprediksi.

## Common Defects
- Sort diterapkan **sebelum** filter (urutan salah setelah filter).
- Pagination dihitung dari dataset penuh, bukan hasil terfilter.
- Filter diabaikan saat search aktif.
- Total `count` tak memperhitungkan filter.
- Data duplikat antar halaman saat kombinasi.

## Security Considerations
- Kombinasi parameter kompleks → pastikan tetap parameterized (anti SQLi).
- Scope otoritas tetap diterapkan pada semua kombinasi.

## References
- Google AIP-132 (List: filtering, ordering, pagination)
- Google AIP-158 (Pagination)
