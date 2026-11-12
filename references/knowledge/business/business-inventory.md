# Business Inventory Testing

## Overview
Menguji **stok, reservasi, dan ketersediaan** — jumlah sumber daya terbatas yang dikelola sistem. Risiko utama: stok bisa negatif, overselling (menjual melebihi yang ada), reservasi tidak dilepas, dan dua proses memakai resource yang sama bersamaan.

## When to Apply
Fitur dengan jumlah/kapasitas terbatas: stok barang, kuota pendaftaran, sisa kursi, slot jadwal, dan kapasitas ruang/peserta. Aplikasikan bersama `business-transaction`, `data-concurrency`.

## Testing Principles
1. Ketersediaan adalah **invarian bisnis**: stok/kuota tidak boleh negatif atau melebihi kapasitas.
2. Operasi pengurangan (claim) harus **atomik** — cek + kurangi tidak boleh terpisah (rentan race).
3. Bedakan **stok tersedia vs ter-reservasi** — reservasi menahan stok tanpa mengurangi stok fisik secara permanen.
4. **Pelepasan (release)** wajib: reservasi yang dibatalkan/kadaluarsa harus mengembalikan stok.
5. Overselling dicegah lewat **locking/transaksi** saat konkuren, bukan sekadar cek nilai.
6. Aturan realokasi/pengisian ulang (restock) harus didefinisikan.

## Test Design Techniques
- Boundary Value Analysis — stok 0, 1, kapasitas maksimum, kapasitas ±1.
- State Transition — available → reserved → consumed/released.
- Concurrency Testing — dua claim bersamaan pada unit terakhir.
- Decision Table — kombinasi jumlah diminta vs jumlah tersedia.

## Test Scenarios

### Positive Testing
- Meminta jumlah ≤ stok tersedia → berhasil, stok berkurang tepat.
- Reservasi valid → stok ter-reservasi, ketersediaan berkurang.
- Pelepasan reservasi → stok kembali tersedia.
- Meminta tepat sisa stok terakhir → berhasil, stok menjadi 0.

### Negative Testing
- Meminta melebihi stok tersedia → ditolak.
- Meminta saat stok 0 → ditolak.
- Meminta jumlah negatif/nol → ditolak.
- Melepas reservasi yang tidak ada / sudah dilepas → ditolak atau idempoten sesuai kontrak.
- Reservasi pada resource yang sudah penuh → ditolak.

### Boundary Testing
- Stok awal = 1, meminta 1 → berhasil, sisa 0.
- Stok = 1, meminta 2 → ditolak.
- Kapasitas maksimum tercapai → tidak bisa tambah/claim lagi.
- Reservasi tepat di batas waktu kedaluwarsa → dilepas otomatis atau tidak sesuai kontrak.

### Integration Testing
- Inventori + transaksi atomik (lihat `business-transaction`) — cek + kurangi satu kesatuan.
- Inventori + concurrency: dua user meminta unit terakhir bersamaan → hanya satu menang (lihat `data-concurrency`).
- Inventori + pembatalan: pembatalan transaksi melepas stok yang ditahan.
- Inventori + pembayaran: stok dikurangi saat pembayaran sukses (atau saat reservasi, sesuai kontrak — lihat `business-payment`).
- Inventori + batch/scheduler: pelepasan otomatis reservasi kedaluwarsa.

## Test Data
- Resource dengan stok 0, 1, banyak, dan tepat kapasitas.
- Dua akun/sesi untuk claim konkuren.
- Reservasi aktif, kadaluarsa, dan sudah dilepas.
- Data untuk memicu overselling (jumlah diminta > sisa).

## Expected Results
- Stok/kuota tidak pernah negatif atau melebihi kapasitas.
- Claim hanya berhasil bila jumlah tersedia mencukupi, dan berkurang tepat.
- Reservasi yang dilepas/kadaluarsa mengembalikan ketersediaan.
- Dua claim konkuren pada unit terakhir → hanya satu yang berhasil (tidak oversell).

## Common Defects
- Overselling: dua request bersamaan sama-sama lolos cek stok.
- Stok menjadi negatif karena cek dan pengurangan terpisah.
- Reservasi tidak pernah dilepas saat transaksi dibatalkan/expired → stok "hilang".
- Restock/realokasi menimpa stok tanpa koordinasi.
- Penghitungan tersedia = total - terpakai salah (tidak memakai reservasi).
- Idempotensi: retry memotong stok dua kali.

## Security Considerations
- Manipulasi jumlah via request (claim negatif, jumlah sangat besar) untuk mengubah stok.
- Race condition dieksploitasi untuk oversell (klaim melebihi kapasitas).
- Melepas reservasi milik pihak lain (IDOR) untuk menambah ketersediaan sendiri.

## References
- ISTQB CTFL v4.0.1 — State Transition, Decision Table.
- OWASP Web Security Testing Guide — Business Logic (race condition).
