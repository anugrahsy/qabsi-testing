# UI Button Testing

## Overview
Menguji **tombol/aksi** sebagai pemicu interaksi: klik, state disabled, dan klik berulang. Risiko utama: aksi terpicu ganda, tombol aktif saat seharusnya disabled, dan tidak ada feedback saat aksi diproses.

## When to Apply
Setiap elemen yang memicu aksi — submit, save, delete, approve, download, dan tombol aksi pada tabel/modal. Aplikasikan bersama `ui-behavior` (double-click guard) dan `ui-state` (state setelah aksi).

## Testing Principles
1. Tombol harus punya **state** jelas: normal, hover, focus, active, disabled, loading.
2. Aksi yang **destruktif** (delete, submit final) wajib punya proteksi klik ganda.
3. Tombol disabled harus **benar-benar** tidak bisa dipicu (bukan cuma visual).
4. Ada feedback setelah klik (loading, disable, atau hasil) agar user tidak menebak.
5. Aksi yang butuh waktu harus menonaktifkan tombol atau menampilkan progress.

## Test Design Techniques
- State Transition — siklus state tombol (idle → loading → sukses/gagal → idle).
- Equivalence Partitioning — kondisi yang mengaktifkan vs menonaktifkan tombol.
- Exploratory — kombinasi cepat klik ganda, klik saat loading.

## Test Scenarios

### Positive Testing
- Klik tombol → aksi terpicu sekali dan hasil sesuai.
- Tombol aktif hanya saat prasyarat terpenuhi (mis. form valid).
- Tombol punya label jelas menyatakan aksinya.
- Keyboard: Enter/Space memicu tombol saat focus.

### Negative Testing
- Klik ganda cepat → aksi hanya tereksekusi sekali.
- Klik saat disabled → tidak ada efek.
- Klik saat loading → tidak memicu aksi kedua.
- Kondisi prasyarat tidak terpenuhi → tombol disabled.

### Boundary Testing
- Klik tepat saat aksi selesai (balapan disable vs enable).
- Klik ganda dengan interval sangat cepat.
- Tombol aksi panjang (timeout) — state selama proses.

### Integration Testing
- Tombol submit + validasi form (delegasi `ui-form`).
- Tombol delete + konfirmasi (delegasi `ui-modal`).
- Tombol aksi + notifikasi hasil (delegasi `ui-notification`).
- Tombol aksi + request API (delegasi `api-idempotency`).

## Test Data
- State form valid/invalid untuk kondisi enable/disable.
- Data yang memicu proses cepat vs lambat (untuk uji loading state).

## Expected Results
- Satu klik = satu aksi; klik ganda tidak menggandakan efek.
- Tombol disabled tidak merespons klik maupun keyboard.
- Ada feedback selama proses (spinner/disabled), kembali ke state normal setelahnya.
- Label & warna konsisten dengan semantik aksi (mis. merah untuk destruktif).

## Common Defects
- Double submit → data duplikat (guard hilang di client ATAU server).
- Tombol disabled hanya visual — masih bisa dipicu via keyboard/script.
- Tidak ada loading state → user klik berulang.
- Tombol tetap disabled setelah proses gagal/selesai.
- Handler terpasang ganda (event listener dobel) → aksi terpicu dua kali.
- Label ambigu ("OK", "Ya") — tidak menjelaskan apa yang terjadi.

## Security Considerations
- Aksi berbahaya (delete, transfer) wajib konfirmasi + otorisasi ulang di server.
- Jangan andalkan disabled di client untuk mencegah aksi — selalu validasi otoritas di server.
- Aksi sensitif sebaiknya butuh token anti-CSRF (jika stateful session).

## References
- ISTQB CTFL v4.0.1
- WCAG 2.1 — Name/Role/Value (4.1.2), Target Size (2.5.5)
- OWASP WSTG — Business Logic Testing
