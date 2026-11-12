# UI Loading State Testing

## Overview
Menguji **state loading** — spinner, skeleton, dan indikator proses — saat data/aksi tertunda. Risiko utama: loading tidak pernah selesai, feedback tak muncul, layout "jump" saat konten muncul, dan state loading tertukar antar area.

## When to Apply
Setiap proses async: fetch data tabel, submit form, navigasi, dan operasi lambat. Aplikasikan bersama `ui-table`, `ui-form`, dan `ui-state` (hasil setelah loading selesai).

## Testing Principles
1. Loading harus **terlihat** — user tahu sistem sedang bekerja, bukan diam.
2. Loading harus **berakhir** di semua kondisi (sukses, gagal, timeout).
3. Skeleton lebih baik dari spinner kosong untuk data terstruktur (kurangi layout shift).
4. Jangan tampilkan banyak loading bersamaan untuk satu area (state ganda).
5. Loading lambat perlu indikator progress atau estimasi, bukan spinner tanpa batas.

## Test Design Techniques
- State Transition — idle → loading → success/error/empty.
- Exploratory — interupsi loading (navigasi, klik lain) saat proses berjalan.

## Test Scenarios

### Positive Testing
- Fetch data → indikator loading tampil, lalu diganti konten.
- Skeleton sesuai struktur konten (tidak layout shift besar).
- Proses selesai → loading hilang, konten/feedback muncul.

### Negative Testing
- Request gagal → loading berhenti, error state tampil (delegasi `ui-error-state`).
- Request timeout → loading berhenti dengan feedback, bukan hang.
- Data kosong → loading berhenti, empty state tampil (delegasi `ui-empty-state`).
- Loading tidak pernah berakhir (bug) → terdeteksi, tidak diam saja.

### Boundary Testing
- Proses sangat cepat → loading tidak flicker mengganggu.
- Proses sangat lambat → ada indikasi masih berjalan.
- Multiple request paralel → loading berakhir saat semua selesai (atau sesuai kontrak).

### Integration Testing
- Loading + tabel data (delegasi `ui-table`).
- Loading + submit form (delegasi `ui-button`).
- Loading + race condition (delegasi `ui-behavior`).

## Test Data
- Data dengan latency rendah vs tinggi (mock/network throttle).
- Response sukses, error, dan timeout.

## Expected Results
- Indikator loading muncul dan selalu berakhir (sukses/gagal/kosong).
- Tidak ada konten "kosong sebentar" tanpa indikator saat menunggu data.
- Layout stabil — konten muncul tanpa lompatan besar.
- Tidak ada dua indikator loading untuk satu area.

## Common Defects
- Loading spinner tanpa batas saat request gagal (tidak di-handle).
- Layout shift besar — konten muncul dan mendorong halaman.
- Loading state menutupi aksi user (bisa ditekan di balik overlay).
- Beberapa spinner bersamaan untuk satu data.
- Flicker saat data cepat (spinner muncul sekejap).
- Skeleton ukurannya tidak sesuai konten final.

## Security Considerations
- Overlay loading jangan sampai bisa di-bypass untuk aksi yang belum selesai.
- Jangan bocorkan status proses internal (mis. error teknis) ke indikator publik.

## References
- ISTQB CTFL v4.0.1
- Nielsen Norman Group — Response Time & Feedback
- WCAG 2.1 — Status Messages (4.1.3)
