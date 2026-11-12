# Input Array Validation Testing

## Overview
Menguji validasi input array: array kosong, item duplikat, dan batas jumlah item. Risiko utama: array kosong diterima saat minimal 1 item wajib, duplikat tidak terdeteksi, jumlah item tak dibatasi (DoS), dan validasi item tidak diterapkan.

## When to Apply
Field array di body request (JSON): list ID, tags, pilihan multi-select, item batch.

## Testing Principles
1. Tentukan **item schema** — setiap elemen divalidasi dengan aturan yang sama (delegasi ke modul input terkait).
2. Tentukan batas **jumlah item** (min/max) secara eksplisit.
3. Tentukan kebijakan **duplikat**: ditolak, di-unique-kan, atau dibiarkan.
4. Bedakan array kosong `[]` (valid untuk optional) vs field hilang/null (belum diisi).
5. `null` sebagai elemen vs `null` sebagai nilai array — dua kasus berbeda, keduanya harus ditentukan.

## Test Design Techniques
- Equivalence Partitioning — kelas jumlah item (kosong, satu, banyak), kelas elemen valid/invalid.
- Boundary Value Analysis — jumlah item min/max (min-1, min, max, max+1).
- Decision Table — kombinasi duplikat × jumlah × validitas elemen.

## Test Scenarios

### Positive Testing
- Array dengan item valid → diterima.
- Array 1 item → diterima.
- Array dalam batas jumlah → diterima.
- Array kosong (jika optional) → diterima.
- Elemen dengan tipe/nilai sesuai schema → diterima.

### Negative Testing
- Array kosong saat minimal 1 item wajib → ditolak.
- Melebihi jumlah maksimum → ditolak.
- Elemen invalid (tipe salah / melanggar schema) → ditolak.
- `null` sebagai elemen → ditolak/diterima sesuai kontrak.
- Bukan array (string/object) → ditolak.
- Duplikat item → ditolak/di-unique sesuai kontrak.

### Boundary Testing
- Jumlah item = min-1 → ditolak; = min → diterima; = max → diterima; = max+1 → ditolak.
- Array 1 elemen vs banyak elemen.

### Integration Testing
- Validasi elemen konsisten dengan validasi field tunggal yang setara.
- Duplikat di-unique-kan → hasil akhir konsisten dengan yang tersimpan.
- Array dipakai operasi batch → semua item diproses; kegagalan sebagian ditangani dengan jelas.

## Test Data
- Array kosong, 1 item, banyak item, di batas min/max.
- Array dengan elemen invalid (tipe/nilai salah, null).
- Array dengan duplikat.
- Array dengan elemen bertipe campur (jika schema longgar).

## Expected Results
- Array valid (jumlah & item) diterima; invalid ditolak dengan pesan jelas.
- Jumlah item dibatasi (min/max).
- Duplikat ditangani sesuai kontrak (reject/unique).
- Pesan error menunjukkan posisi/identitas elemen yang invalid (jika relevan).

## Common Defects
- Array kosong diterima saat wajib minimal 1 item.
- Jumlah item tidak dibatasi → DoS.
- Duplikat tidak terdeteksi → data ganda.
- Validasi item tidak diterapkan (hanya jumlah yang dicek).
- Elemen `null` tidak ditangani → crash.
- Error tidak menunjukkan elemen mana yang invalid.

## Security Considerations
- OWASP Input Validation Cheat Sheet — batasi jumlah item (anti-DoS), validasi setiap elemen.
- Array sangat besar → resource exhaustion saat parsing & pemrosesan.
- Elemen yang diteruskan ke query/DB → risiko injeksi (validasi per elemen).

## References
- OWASP Input Validation Cheat Sheet
- OpenAPI Specification (schema array & items)
