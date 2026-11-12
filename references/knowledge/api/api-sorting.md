# API Sorting Testing

## Overview
Menguji parameter **sort** (`sort`, `order`) pada endpoint collection. Risiko utama: sort alfabet vs numerik tertukar, multiple sort field salah prioritas, dan urutan tidak stabil.

## When to Apply
Endpoint collection yang mendukung sorting. Aplikasikan bersama `api-get-collection`, `api-pagination`, `api-combination`.

## Testing Principles
1. Sort numerik harus **numerik** (10 > 9), bukan alfabet ("10" < "9").
2. Sort tanggal harus kronologis benar (termasuk timezone).
3. Nilai null/empty harus punya posisi deterministik (pertama/terakhir).
4. Urutan harus **stabil** — nilai sama → urutan tidak acak.

## Test Design Techniques
- Equivalence Partitioning — arah sort (asc/desc), tipe field.
- Boundary — nilai null, nilai sama.
- Combinatorial — multi sort field (lihat `api-combination`).

## Test Scenarios

### Positive Testing
- Ascending: A→Z, terkecil→terbesar, terlama→terbaru.
- Descending: Z→A, terbesar→terkecil, terbaru→terlama.
- Sort by date.
- Sort by number (bukan urutan alfabet).
- Multiple sort fields (mis. `sort=name,created_at`).

### Negative Testing
- Sort field tak diizinkan → ditolak/diabaikan sesuai kontrak.
- `order` nilai invalid → error sesuai kontrak.
- Sort field yang tak ada → error/ignore sesuai kontrak.

### Boundary Testing
- Sort field dengan nilai sama → urutan stabil (tie-break).
- Sort field dengan null/empty → posisi konsisten (pertama/terakhir).

### Integration Testing
- Sort + pagination → urutan konsisten saat berpindah halaman.
- Sort + filter → sort hanya pada hasil terfilter.
- Sort + search → sort hasil pencarian.

## Test Data
- Angka yang menipu urutan alfabet (2, 10, 9).
- Tanggal lintas timezone.
- Nilai null/empty dan nilai duplikat.
- Teks campuran uppercase/lowercase.

## Expected Results
- Urutan sesuai arah (asc/desc) dan tipe data (numerik/datetime).
- Tie-break deterministik untuk nilai sama.
- Null konsisten di awal/akhir.
- Urutan tidak berubah saat pindah halaman.

## Common Defects
- Sort numerik jadi alfabet ("10" sebelum "9").
- Case-sensitive sort (uppercase/lowercase tak konsisten).
- Null memecah urutan.
- Multiple sort field prioritas terbalik.
- Urutan berubah antar halaman (tanpa default sort eksplisit).

## Security Considerations
- Sort field bebas bisa expose kolom sensitif → whitelist field sort.
- Sort pada dataset besar → performance (pastikan index).

## References
- Google AIP-132 (Ordering)
- OpenAPI Specification
