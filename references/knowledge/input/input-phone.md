# Input Phone Validation Testing

## Overview
Menguji validasi nomor telepon dan identitas bernomor (NIK/KTP, passport): format E.164, country code, dan panjang. Risiko utama: format lokal vs internasional campur aduk, country code salah, dan identifier nasional (NIK) divalidasi dengan aturan yang salah.

## When to Apply
Form kontak, OTP/verifikasi nomor, profil, atau endpoint yang menerima nomor telepon / nomor identitas nasional.

## Testing Principles
1. Nomor telepon: normalkan ke **E.164** (`+` + country code + subscriber number, maksimum 15 digit) sebelum simpan.
2. Tentukan apakah country code wajib eksplisit atau ada default (mis. Indonesia `+62`).
3. NIK/KTP/passport punya **aturan format sendiri** — jangan dicampur dengan validasi telepon.
4. Jangan validasi keberadaan nomor (terdaftar di operator) sebagai bagian validasi input — itu verifikasi terpisah.
5. Format tampilan vs format simpan berbeda: simpan E.164, tampil format lokal.

## Test Design Techniques
- Equivalence Partitioning — kelas nomor valid (E.164) vs invalid; kelas country code.
- Boundary Value Analysis — panjang 15 digit (maksimum E.164) & panjang NIK (16 digit).
- Decision Table — kombinasi country code × panjang × karakter.

## Test Scenarios

### Positive Testing
- Nomor E.164 valid `+6281234567890` → diterima.
- Nomor dengan country code berbeda `+15551234567` → diterima.
- Nomor tanpa `+` tapi dengan country code default → dinormalisasi.
- NIK 16 digit valid → diterima (jika field NIK).

### Negative Testing
- Huruf di dalam nomor → ditolak.
- Simbol selain `+` (spasi, `-`, `.`, `(`) → ditolak atau dinormalisasi sesuai kontrak.
- Panjang > 15 digit (E.164) → ditolak.
- Country code tidak dikenal → ditolak.
- NIK panjang bukan 16 → ditolak.
- Nomor kosong / hanya `+` → ditolak.

### Boundary Testing
- Nomor 15 digit → diterima; 16 digit → ditolak (E.164).
- NIK 15 digit → ditolak; 16 → diterima; 17 → ditolak.
- Country code 1 digit (`+1`) vs 3 digit tidak valid → sesuai kontrak.

### Integration Testing
- Normalisasi E.164 konsisten simpan & verifikasi OTP (nomor sama dikenali satu).
- Nomor dengan country code default vs eksplisit → disimpan sama.
- NIK dipakai untuk cek duplikasi → format ternormalisasi dulu.

## Test Data
- Nomor E.164 valid/invalid, panjang batas 15/16.
- Variasi country code (`+1`, `+44`, `+62`, code tidak valid).
- Format lokal Indonesia (08xx) vs internasional.
- NIK 16 digit valid/invalid (panjang salah, non-digit).
- Nomor dengan separator (spasi, `-`) untuk uji normalisasi.

## Expected Results
- Nomor E.164 valid diterima & ternormalisasi konsisten.
- Invalid ditolak dengan pesan jelas.
- NIK/KTP divalidasi dengan aturan identitas nasional, bukan aturan telepon.
- Format simpan (E.164) konsisten.

## Common Defects
- Format lokal (08xx) disimpan mentah tanpa normalisasi → duplikat OTP.
- Country code default salah (mis. `+62` menjadi `+620`).
- Spasi/separator tidak dinormalisasi → nomor sama dianggap beda.
- NIK divalidasi sebagai telepon (atau sebaliknya).
- Nomor > 15 digit lolos (melanggar E.164).

## Security Considerations
- OWASP Input Validation Cheat Sheet — whitelist digit & `+`, server-side.
- Nomor telepon sebagai identitas → risiko account enumeration via OTP/registrasi.
- Jangan log nomor penuh (PII) tanpa masking.

## References
- ITU-T E.164 (The international public telecommunication numbering plan)
- OWASP Input Validation Cheat Sheet
