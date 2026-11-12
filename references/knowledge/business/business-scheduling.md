# Business Scheduling Testing

## Overview
Menguji **jadwal, deadline, dan cut-off**: perilaku sistem yang bergantung pada waktu. Risiko utama: perilaku berbeda tepat sebelum/sesudah batas waktu, zona waktu salah, dan operasi di luar periode tidak ditolak (atau sebaliknya operasi sah terblokir).

## When to Apply
Fitur dengan batasan waktu: periode pengajuan, cut-off input, jadwal aktif/nonaktif, deadline, dan aturan "hanya pada periode X". Aplikasikan bersama `input-date`, `business-rules`.

## Testing Principles
1. Waktu adalah **batas bisnis** — uji tepat sebelum, tepat pada, dan tepat sesudah batas (boundary).
2. **Zona waktu (timezone)** harus eksplisit: zona mana yang jadi acuan cut-off (server vs user vs bisnis)?
3. Batas waktu biasanya **inklusif atau eksklusif** — pastikan sesuai kontrak (deadline 23:59 termasuk atau tidak).
4. Operasi di luar periode harus **ditolak eksplisit**, bukan diterima diam-diam atau error 500.
5. Perpanjangan/penyesuaian periode (extend) adalah perubahan aturan — uji efeknya.
6. Waktu server bisa dimanipulasi di lingkungan uji — pastikan hasil tidak bergantung jam mesin tester semata.

## Test Design Techniques
- Boundary Value Analysis — tepat sebelum/pada/sesudah deadline dan awal/akhir periode.
- Equivalence Partitioning — dalam periode, sebelum periode, setelah periode.
- State Transition — status periode (belum dibuka, aktif, tutup, diperpanjang).
- Time-travel / clock mocking — geser waktu sistem untuk mencapai titik batas tanpa menunggu.

## Test Scenarios

### Positive Testing
- Operasi dalam periode aktif → berhasil.
- Operasi tepat pada batas (mis. detik terakhir sebelum cut-off) → sesuai kontrak.
- Periode diperpanjang → operasi yang tadinya terlambat menjadi sah.
- Operasi pada hari/waktu khusus yang diizinkan → berhasil.

### Negative Testing
- Operasi sebelum periode dibuka → ditolak dengan pesan.
- Operasi setelah cut-off → ditolak dengan pesan.
- Deadline dimanipulasi via payload (kirim tanggal di masa lalu/turn-back) → ditolak.
- Operasi di hari/tanggal yang dilarang (hari libur, weekend, sesuai kontrak) → ditolak.

### Boundary Testing
- Tepat 1 detik/menit sebelum cut-off → masih diterima.
- Tepat pada momen cut-off → sesuai kontrak (inklusif/eksklusif).
- Tepat 1 detik/menit setelah cut-off → ditolak.
- Transisi tengah malam / pergantian tanggal / pergantian zona waktu.
- Tahun kabisat (29 Februari) bila jatuh pada batas.

### Integration Testing
- Jadwal + status transition: objek terkunci otomatis saat periode berakhir (lihat `business-status-transition`).
- Jadwal + business rules: aturan hanya berlaku pada periode tertentu (lihat `business-rules`).
- Jadwal + batch/scheduler: proses terjadwal jalan tepat waktu dan tidak dobel.
- Jadwal lintas zona waktu: user di zona berbeda menghadapi cut-off yang benar.
- Deadline + notifikasi/pengingat terkirim pada waktu yang tepat.

## Test Data
- Fixture dengan periode: belum mulai, aktif, sudah berakhir, diperpanjang.
- Timestamp tepat di titik batas (awal, akhir, ±1 satuan waktu).
- User/akun di zona waktu berbeda.
- Tanggal khusus: pergantian tahun, 29 Februari, pergantian DST bila relevan.

## Expected Results
- Operasi hanya diterima dalam periode yang sah, berdasar zona waktu acuan yang benar.
- Penolakan di luar periode eksplisit dengan pesan yang informatif.
- Perilaku di titik batas sesuai kontrak (inklusif/eksklusif) dan konsisten.
- Penyesuaian periode segera berlaku tanpa efek samping tak terduga.

## Common Defects
- Cek cut-off memakai zona waktu user (bisa dimanipulasi), bukan zona acuan bisnis.
- Batas eksklusif dianggap inklusif (atau sebaliknya) → operasi tepat di deadline salah keputusan.
- Perilaku berbeda antara cek di UI dan di server.
- Proses terjadwal jalan dobel atau tidak jalan sama sekali.
- Perpanjangan periode tidak diambil alih oleh cache/state lama.
- Perbandingan tanggal mengabaikan komponen waktu (tanggal sama, beda jam).

## Security Considerations
- Manipulasi waktu client (ubah jam perangkat / kirim timestamp palsu) untuk melewati cut-off — wajib divalidasi server-side.
- Deadline yang bisa diedit user biasa (via field tersembunyi) → eskalasi perlu otoritas.
- Race tepat di batas waktu: request masuk tepat sebelum cut-off diproses setelah cut-off — perilaku harus deterministik.

## References
- ISTQB CTFL v4.0.1 — Boundary Value Analysis, State Transition.
- ISO 8601 — format tanggal/waktu dan zona waktu.
