# Business Status Transition Testing

## Overview
Menguji **perubahan status yang diperbolehkan** pada objek bisnis (mis. draft → submitted → approved/rejected → completed). Risiko utama: transisi tidak sah bisa terjadi, transisi sah justru terblokir, status tidak sinkron dengan data turunannya, dan status bisa dimanipulasi langsung lewat parameter.

## When to Apply
Objek apa pun yang punya field status dengan nilai lebih dari satu dan aturan perpindahan: pengajuan, tiket, pesanan, penilaian, dokumen. Modul ini inti dari `business-workflow` dan `business-approval` — kedua modul itu memakai teknik modul ini.

## Testing Principles
1. **State Transition Testing (ISTQB)** adalah teknik utama: modelkan status sebagai **state**, aksi/event sebagai **transisi**, dan tentukan transisi yang sah serta tidak sah.
2. Uji transisi **valid** (harus berhasil), transisi **invalid** (harus ditolak), dan transisi yang **tidak terdefinisi** (perilaku eksplisit).
3. Status objek harus **satu-satunya sumber kebenaran** — tampilan dan logika turunan mengikuti status, bukan sebaliknya.
4. Perpindahan status harus **terikat aktor/otoritas** (siapa boleh memicu transisi apa).
5. Transisi bisa punya **syarat tambahan** (dokumen lengkap, periode aktif) — syarat gagal = transisi gagal.
6. Setiap transisi tercatat di audit trail (lihat `business-audit`).

## Test Design Techniques
- **State Transition Testing** (utama, ISTQB):
  1. Identifikasi semua **state** (status) — mis. draft, submitted, approved, rejected, completed.
  2. Identifikasi semua **event/aksi** yang memicu transisi — mis. submit, approve, reject, revise.
  3. Buat **state transition diagram/tabel**: state awal × event → state akhir (+ valid/tidak valid).
  4. Derive test: **0-switch coverage** (semua transisi valid sekali) → **invalid transition** (transisi tidak sah harus ditolak) → **N-switch** bila urutan event penting.
- Decision Table — syarat tambahan transisi (otoritas × syarat × event).
- Equivalence Partitioning — kelompok state yang diperlakukan sama oleh suatu aksi.
- Exploratory — kombinasi urutan tidak lazim (approve setelah reject, dsb.).

## Test Scenarios

### Positive Testing
- Tiap transisi valid dalam diagram: state awal benar + aksi sah + aktor berwenang → state akhir benar.
- Happy path urutan penuh: dari state awal ke state akhir lewat jalur utama.
- Transisi dengan syarat terpenuhi → berhasil dan efek turunan mengikuti.
- Transisi yang boleh berulang (mis. revise di state tertentu) → bisa dilakukan sesuai kontrak.

### Negative Testing
- Transisi tidak sah (state awal salah untuk aksi tersebut) → ditolak dengan pesan jelas.
- Aksi oleh aktor tanpa otoritas pada transisi tersebut → ditolak.
- Transisi dengan syarat tidak terpenuhi → ditolak (status tidak berubah).
- Manipulasi status langsung via payload/parameter → tidak berpengaruh.
- Aksi pada objek yang sudah final/terkunci → ditolak atau idempoten sesuai kontrak.

### Boundary Testing
- State pertama (tidak ada transisi mundur lebih awal) dan state terminal (tidak ada transisi maju).
- Transisi tepat pada batas waktu (mis. state berubah otomatis saat periode berakhir — lihat `business-scheduling`).
- Objek baru dibuat langsung di-dispatch semua aksi (belum pernah transisi).

### Integration Testing
- Transisi + workflow tahapan (lihat `business-workflow`).
- Transisi + approval (lihat `business-approval`) — approve/reject sebagai transisi berotoritas.
- Transisi + audit trail: setiap perubahan status tercatat siapa/kapan/dari-ke (lihat `business-audit`).
- Transisi + data turunan: aksi/status turunan (notifikasi, hak akses dokumen) mengikuti status.
- Transisi + concurrency: dua aksi transisi bersamaan pada objek yang sama → hanya satu yang berhasil (lihat `data-concurrency`).

## Test Data
- Objek di **setiap state** (setup langsung ke state target untuk mempercepat).
- Akun dengan otoritas berbeda untuk transisi yang berbeda.
- State transition diagram/tabel dari kontrak/PRD sebagai dasar derive test.
- Objek dengan syarat transisi terpenuhi vs tidak terpenuhi.

## Expected Results
- Hanya transisi yang didefinisikan yang bisa terjadi; transisi lain ditolak (status tidak berubah).
- State akhir sesuai diagram; tidak ada status antara/ ambigu.
- Transisi ditolak bila aktor tidak berwenang atau syarat tidak terpenuhi.
- Setiap transisi valid tercatat di jejak perubahan status.
- Status objek konsisten dengan data/tampilan turunannya.

## Common Defects
- Endpoint aksi tidak memeriksa status saat ini (approve bisa dari state apa pun).
- Transisi tidak sah "berhasil diam-diam" tanpa error.
- Status berubah tapi data turunan/logika tidak mengikuti (inkonsisten).
- Status bisa diset langsung lewat field di payload update umum.
- Urutan aksi bersamaan (race) menghasilkan status tidak valid.
- State tanpa jalan keluar (stuck) — objek tidak bisa diproses lagi.
- Status terminal masih bisa dimodifikasi.

## Security Considerations
- Manipulasi transisi lewat parameter (langsung set status) — wajib ditolak server-side.
- Otorisasi per transisi: aktor tidak boleh memicu transisi di luar wewenang (OWASP WSTG Authorization).
- Status sebagai dasar hak akses (mis. dokumen hanya terlihat setelah submitted) — uji tidak bisa ditembus.

## References
- ISTQB CTFL v4.0.1 — State Transition Testing (state, event, transition, 0-switch/N-switch coverage, invalid transition).
- OWASP Web Security Testing Guide — Authorization, Business Logic.
