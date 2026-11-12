# UI Behavior Testing (Debounce, Double-click Guard, Race Condition)

## Overview
Menguji **perilaku dinamis UI** yang berkaitan dengan waktu dan pemanggilan berulang: **debounce/throttle**, **double-click guard**, dan **race condition** antar request async. Risiko utama: aksi terpicu ganda, data ditimpa oleh response lama, dan input user hilang karena balapan request.

## When to Apply
Setiap interaksi yang memicu request async atau handler berulang: pencarian real-time, autocomplete, submit, tombol aksi, dan fetch data yang bisa tumpang tindih. Aplikasikan bersama `ui-button`, `ui-form`, dan `api-concurrency`.

## Testing Principles
1. **Debounce** menunda eksekusi sampai user berhenti mengetik; **throttle** membatasi frekuensi. Uji keduanya sesuai kebutuhan.
2. **Double-click guard** mencegah satu aksi diproses dua kali — di client ATAU server (idealnya keduanya).
3. **Race condition**: response harus diurutkan/dibatalkan agar response lama tidak menimpa hasil terbaru.
4. Tiap request async harus **dibatalkan atau diabaikan** bila sudah tidak relevan (user sudah mengetik lagi / berpindah).
5. Perilaku harus **deterministik** — tidak bergantung pada urutan response yang kebetulan cepat.

## Test Design Techniques
- State Transition — idle → waiting → processing → settled.
- Exploratory — ketik cepat, klik ganda, throttle jaringan untuk memicu balapan.
- Combinatorial — beberapa aksi async bersamaan.

## Test Scenarios

### Positive Testing
- Debounce: ketik lalu berhenti → request hanya sekali (bukan per ketukan).
- Double-click guard: klik ganda cepat → hanya satu request/satu efek.
- Race: request lama selesai setelah request baru → hasil yang tampil adalah yang terbaru.
- Throttle: aksi berulang (scroll/resize) dibatasi frekuensinya.

### Negative Testing
- Ketik cepat di search → tidak ada hasil "stale" yang menimpa hasil akhir.
- Klik submit berkali-kali → tidak ada data duplikat.
- Navigasi pergi saat request belum selesai → request dibatalkan, tidak crash.
- Dua request paralel → urutan response tidak menentukan hasil akhir yang salah.

### Boundary Testing
- Debounce dengan jeda tepat di threshold → hanya satu trigger.
- Klik ganda dengan interval sangat cepat (di bawah guard window).
- Response A (lama) tiba tepat setelah response B (baru).

### Integration Testing
- Debounce + search/autocomplete (delegasi `ui-dropdown`).
- Double-click guard + submit (delegasi `ui-button`, `ui-form`).
- Race + fetch data (delegasi `ui-loading`, `ui-state`).
- Race + server idempotency (delegasi `api-idempotency`, `api-concurrency`).

## Test Data
- Network throttle (latency bervariasi antar request) untuk memicu race.
- Input yang berubah cepat (ketik beruntun).
- Dua request dengan payload berbeda (verifikasi hasil terakhir menang).

## Expected Results
- Satu aksi user = satu efek, berapapun kecepatan klik/ketik.
- Hasil akhir UI selalu mencerminkan request terakhir, bukan yang selesai terakhir.
- Tidak ada data duplikat dari klik ganda.
- Request yang sudah tidak relevan dibatalkan/diabaikan tanpa error mengganggu.

## Common Defects
- Debounce tidak diterapkan → request per ketukan (membanjiri server).
- Double-click guard hanya di server → UI tetap tampak memproses ganda.
- Response lama menimpa response baru (race tidak di-handle).
- Request tidak dibatalkan saat navigasi → memory leak/state aneh.
- Guard pakai index/timeout yang salah → aksi sah ikut terblokir.
- Loading state tertukar saat dua request tumpang tindih.

## Security Considerations
- Rate limit di client (debounce/throttle) bukan pengganti rate limit server.
- Request paralel yang tidak dibatalkan bisa jadi vektor abuse (request flooding).
- Idempotensi server wajib untuk aksi yang berubah data (delegasi `api-idempotency`).

## References
- ISTQB CTFL v4.0.1
- Google AIP — idempotency & concurrency
- OWASP WSTG — Business Logic Testing
