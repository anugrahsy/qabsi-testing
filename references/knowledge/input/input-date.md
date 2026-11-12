# Input Date Validation Testing

## Overview
Menguji validasi input tanggal: format, validitas kalender (termasuk leap year), range, dan timezone. Risiko utama: format ambigu (DD/MM vs MM/DD), tanggal invalid (30 Februari), timezone menggeser tanggal, dan range tidak divalidasi.

## When to Apply
Form tanggal lahir, periode, deadline, jadwal, atau field `date`/`datetime` di body request.

## Testing Principles
1. Tentukan **format & timezone** eksplisit (ISO 8601 `YYYY-MM-DD`, atau datetime + offset).
2. Tanggal harus valid secara kalender: leap year dan jumlah hari per bulan (28/29/30/31).
3. Bedakan date-only vs datetime: datetime punya komponen waktu & timezone.
4. Range (min/max) & relasi (start ≤ end) harus divalidasi.
5. Timezone: tentukan interpretasi (UTC, lokal server, atau ikut offset input) — hindari silent shift.

## Test Design Techniques
- Equivalence Partitioning — kelas format valid/invalid; kelas bulan/hari valid.
- Boundary Value Analysis — batas tahun (min/max), batas bulan (1/12), batas hari (1/28-31), leap year.
- Decision Table — kombinasi format × validitas kalender × range.

## Test Scenarios

### Positive Testing
- Format ISO `YYYY-MM-DD` valid → diterima.
- Tanggal leap year `2024-02-29` → diterima.
- Batas akhir bulan `2023-01-31`, `2023-04-30` → diterima.
- Datetime dengan timezone/offset → diterima sesuai kontrak.
- Tanggal dalam range min/max → diterima.

### Negative Testing
- Format salah (`DD/MM/YYYY`, `MM-DD-YYYY`) → ditolak (jika kontrak ISO).
- Tanggal invalid `2023-02-30`, `2023-04-31`, `2023-13-01` → ditolak.
- `2023-02-29` (bukan leap year) → ditolak.
- Non-tanggal (huruf, angka acak) → ditolak.
- Tanggal di luar range → ditolak.
- start > end → ditolak (jika relasi divalidasi).

### Boundary Testing
- Tahun minimum/maksimum & sekitarnya (min-1, min, max, max+1).
- Tahun `0000` / tahun invalid → ditolak.
- Batas hari tiap bulan (Jan 31, Feb 28/29, Apr 30).
- Datetime tepat di batas range (00:00:00 vs 23:59:59).

### Integration Testing
- Tanggal disimpan & dibaca kembali tanpa berubah (round-trip).
- Timezone konsisten: tanggal sama dikenali sama lintas zona.
- Range tanggal dipakai filter/query → hasil sesuai (delegasi `api-filtering`).

## Test Data
- Tanggal ISO valid/invalid, format alternatif.
- Leap year (2024-02-29) vs non-leap (2023-02-29).
- Batas bulan (28/29/30/31).
- Tanggal di luar range, tahun ekstrem.
- Datetime dengan offset timezone berbeda (`+07:00`, `Z`).

## Expected Results
- Tanggal valid (format & kalender) diterima; invalid ditolak dengan pesan jelas.
- Leap year & jumlah hari per bulan ditangani benar.
- Range & relasi (start ≤ end) divalidasi.
- Timezone diinterpretasi konsisten (tidak ada silent shift).

## Common Defects
- `2023-02-29` / `2023-02-30` lolos (validasi kalender lemah).
- Format DD/MM vs MM/DD tertukar (ambiguitas).
- Timezone shift mengubah tanggal (disimpan beda 1 hari).
- Range tidak divalidasi (tanggal masa lalu/futuristik ekstrem).
- Leap year tidak ditangani (29 Feb selalu ditolak).
- String date diterima tanpa parsing → sort/filter salah.

## Security Considerations
- OWASP Input Validation Cheat Sheet — format strict (regex + library parsing), server-side.
- Timezone handling mencegah logic error di deadline/cut-off.
- Jangan andalkan parser date yang lenient (menerima format tak diinginkan / auto-koreksi tanggal invalid).

## References
- ISO 8601 (Date and time format)
- OWASP Input Validation Cheat Sheet
