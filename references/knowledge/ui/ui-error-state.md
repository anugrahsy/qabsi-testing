# UI Error State Testing

## Overview
Menguji **error state** — feedback saat operasi gagal dan mekanisme pemulihan (retry). Risiko utama: error tidak jelas, tidak ada jalan keluar, dan user kehilangan konteks/input yang sudah diisi.

## When to Apply
Setiap kegagalan yang tampil di UI: request gagal, submit gagal, dan error server. Aplikasikan bersama `ui-loading` (loading harus berakhir ke error) dan `ui-notification` (error non-blocking).

## Testing Principles
1. Error harus **jelas dan actionable** — apa yang salah + apa yang bisa dilakukan.
2. Bedakan error **transient** (bisa retry) vs **permanen** (perlu ubah input).
3. Error state tidak boleh menghilangkan data/input user yang sudah ada.
4. Error teknis (stack trace, kode) tidak boleh diekspos ke user.
5. Retry harus benar-benar mengulang operasi, bukan menambah state aneh.

## Test Design Techniques
- State Transition — loading → error → retry → success/error.
- Equivalence Partitioning — jenis error (network, 4xx, 5xx, timeout).
- Exploratory — retry berulang, retry saat kondisi berubah.

## Test Scenarios

### Positive Testing
- Request gagal → error state tampil dengan pesan jelas.
- Ada tombol/opsi retry → klik retry, operasi diulang dan bisa sukses.
- Error dari server (validasi) → pesan ditampilkan di lokasi tepat (field/global).

### Negative Testing
- Error transient tanpa retry → user terjebak (defect yang harus ditemukan).
- Error permanen → tidak menampilkan tombol retry yang tidak berguna.
- Retry berkali-kali → tidak menumpuk error/duplikasi state.
- Navigasi balik saat error → state tidak rusak.

### Boundary Testing
- Timeout / offline → error jelas, retry saat koneksi pulih.
- Error 5xx vs 4xx → pesan dan tindakan berbeda sesuai jenis.
- Error saat submit form → data input tidak hilang.

### Integration Testing
- Error + loading transisi (delegasi `ui-loading`).
- Error + notifikasi toast (delegasi `ui-notification`).
- Error + form validasi (delegasi `ui-form`).
- Error + retry request API (delegasi `api-timeout-retry`).

## Test Data
- Simulasi error 400/401/403/404/422/500, timeout, offline.
- Data input yang sudah diisi sebelum error terjadi.

## Expected Results
- Error tampil dengan pesan yang bisa dipahami dan ditindaklanjuti.
- Loading berakhir ke error (tidak hang), error bisa dipulihkan via retry.
- Data user tidak hilang saat error.
- Tidak ada kebocoran detail teknis ke user.

## Common Defects
- Pesan error generik tanpa tindakan ("Terjadi kesalahan").
- Loading berhenti tapi error state tidak muncul (blank).
- Retry menggandakan data / membuat state tidak konsisten.
- Input user terhapus saat submit gagal.
- Stack trace / detail internal tampil ke user.
- Error tertelan (swallowed) — user tidak tahu ada yang gagal.

## Security Considerations
- Jangan ekspos stack trace, SQL, path file, atau detail internal.
- Error yang membedakan respons (mis. "user tidak ditemukan") bisa jadi oracle enumerasi — hati-hati.
- Log error di sisi server harus memadai tanpa bocor ke client.

## References
- OWASP WSTG — Error Handling
- ISTQB CTFL v4.0.1
- WCAG 2.1 — Error Identification (3.3.1)
