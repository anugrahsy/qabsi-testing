# Business Audit Testing

## Overview
Menguji **audit trail** — jejak perubahan data yang menjawab "siapa melakukan apa, kapan, dari apa menjadi apa". Risiko utama: perubahan penting tidak tercatat, jejak tidak bisa diaudit karena atribut hilang (aktor/waktu/nilai lama), dan jejak bisa diubah atau dihapus.

## When to Apply
Data yang perubahannya harus dapat ditelusuri: data finansial, keputusan/approval, perubahan status, dan data sensitif/teregulasi. Aplikasikan bersama `business-status-transition`, `business-approval`, `data-consistency`.

## Testing Principles
1. Tentukan **perubahan apa yang wajib diaudit** (yang penting bisnis), bukan semua field secara membabi buta.
2. Tiap entri audit minimal memuat: **aktor, waktu, aksi, objek, nilai sebelum (from) dan sesudah (to)**.
3. Audit trail harus **append-only** — entri tidak boleh diubah atau dihapus oleh pengguna biasa.
4. Jejak harus **konsisten lintas lapisan**: transaksi di UI/API/batch semua tercatat dengan format sama.
5. Waktu audit harus memakai **zona waktu acuan yang jelas** dan tidak bisa diubah oleh aktor.
6. Data audit harus bisa **dibaca ulang** (rekonstruksi sejarah perubahan) tanpa gap.

## Test Design Techniques
- State Transition — jejak mengikuti tiap perubahan status (lihat `business-status-transition`).
- Use Case Scenario — jalankan aksi, lalu verifikasi jejak yang dihasilkan.
- Decision Table — aksi × field berubah × aktor → entri audit yang diharapkan.
- Data Integrity — hubungan antara record utama dan entri auditnya.

## Test Scenarios

### Positive Testing
- Perubahan data penting → entri audit dibuat dengan aktor, waktu, aksi, dari→ke benar.
- Perubahan status/approval → jejak transisi tercatat lengkap.
- Aksi dari berbagai lapisan (UI, API, batch) → semua tercatat.
- Entri audit bisa dibaca/direkonstruksi menjadi urutan perubahan yang benar.

### Negative Testing
- Perubahan yang harusnya tidak diaudit → tidak membuat entri berlebih (over-audit) sesuai kontrak.
- Perubahan oleh sistem/batch → aktor sistem tercatat jelas (bukan aktor kosong).
- Pengguna mencoba menghapus/mengubah entri audit → ditolak.
- Operasi gagal/rollback → jejak sesuai kontrak (tidak mencatat perubahan yang tidak jadi, atau mencatat percobaan).

### Boundary Testing
- Perubahan field dengan nilai null → dari/to null tercatat benar.
- Perubahan cepat berurutan pada objek yang sama → urutan waktu (timestamp) terjaga tanpa tabrakan.
- Volume tinggi: banyak perubahan → tidak ada entri hilang.

### Integration Testing
- Audit + status transition: setiap transisi valid terekam (lihat `business-status-transition`).
- Audit + approval: keputusan dan delegasi terekam (lihat `business-approval`).
- Audit + transaction: rollback tidak meninggalkan jejak menyesatkan (lihat `business-transaction`).
- Audit + report/rekonsiliasi: data laporan cocok dengan jejak audit.

## Test Data
- Record dengan berbagai status perubahan dan aktor berbeda.
- Aksi yang mengubah banyak field sekaligus.
- Operasi gagal (untuk verifikasi perilaku jejak pada kegagalan).
- Perubahan yang melibatkan nilai null.

## Expected Results
- Setiap perubahan wajib-audit menghasilkan tepat satu entri dengan atribut lengkap.
- Jejak append-only: tidak bisa diubah/dihapus.
- Rekonstruksi sejarah perubahan menghasilkan urutan yang benar dan tanpa gap.
- Aktor dan waktu tercatat akurat, konsisten di semua lapisan.

## Common Defects
- Perubahan penting tidak diaudit (field ditambah tapi lupa dimasukkan audit).
- Nilai sebelum (from) tidak disimpan — hanya catat nilai baru.
- Aktor tidak tercatat pada proses batch/background.
- Entri audit bisa diedit/dihapus oleh pengguna.
- Zona waktu ambigu sehingga urutan perubahan salah.
- Over-audit: perubahan tidak penting membanjiri log sehingga sulit ditelusuri.

## Security Considerations
- Integritas audit: jejak harus tahan tampering (tidak bisa diubah/hapus).
- Non-repudiation: aktor tercatat sehingga aksi tidak bisa disangkal.
- Akses baca audit juga harus dibatasi otoritas (jejak bisa mengandung data sensitif).

## References
- ISTQB CTFL v4.0.1 — State Transition, Use Case Scenario.
- OWASP Web Security Testing Guide — Audit & Logging (WSTG-ATHZ/WSTG-BUSLOGIC).
