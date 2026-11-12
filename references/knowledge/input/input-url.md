# Input URL Validation Testing

## Overview
Menguji validasi input URL: sintaks, protocol, domain, dan malformed URL. Risiko utama: URL invalid lolos, protocol berbahaya (`javascript:`) diterima, SSRF via URL internal, dan open redirect.

## When to Apply
Field link (website, profil, avatar, callback, webhook URL) atau parameter yang menerima URL.

## Testing Principles
1. Tentukan komponen yang diizinkan: protocol (http/https saja?), host, port, path.
2. Bedakan validasi **sintaks** (bentuk URL) vs **nilai/keamanan** (protocol & host) — keduanya perlu.
3. Protocol whitelist: hanya `http`/`https` kecuali kontrak bilang lain (blokir `javascript:`, `file:`, `data:`).
4. Host: pastikan ada domain valid; waspadai IP internal/loopback (SSRF) bila server melakukan fetch.
5. Normalisasi & decoding (`%20`, double-encode) harus dipertimbangkan agar tidak bisa bypass validasi.

## Test Design Techniques
- Equivalence Partitioning — kelas URL valid/invalid, kelas protocol.
- Boundary Value Analysis — panjang URL maksimum.
- Decision Table — kombinasi protocol × host × path.

## Test Scenarios

### Positive Testing
- `https://example.com` → diterima.
- URL dengan path/query `https://example.com/path?q=1` → diterima.
- URL dengan port `https://example.com:8443` → diterima.
- URL dengan subdomain → diterima.

### Negative Testing
- Tanpa protocol (`example.com`) → ditolak/diterima sesuai kontrak.
- Protocol berbahaya `javascript:alert(1)`, `data:`, `file:` → ditolak.
- Protocol tidak ada di whitelist (`ftp://`) → ditolak.
- Host kosong / tanpa titik → ditolak.
- Spasi / karakter invalid → ditolak.
- Malformed (`http://`, `://`, `https://.com`) → ditolak.

### Boundary Testing
- URL dengan panjang maksimum → diterima; melebihi → ditolak.
- Label domain panjang maksimum → sesuai kontrak.

### Integration Testing
- URL disimpan lalu dipakai redirect → host divalidasi ulang saat consume (bukan hanya saat input) untuk cegah open redirect.
- URL sebagai webhook/callback → SSRF check (blokir internal/loopback) saat server fetch.
- URL dengan encoding (`%2F`, double-encode) diproses benar, tidak melewati validasi.

## Test Data
- URL valid/invalid: variasi protocol, host, port, path, query.
- Protocol berbahaya (`javascript:`, `data:`, `file:`, `vbscript:`).
- IP internal/loopback (`127.0.0.1`, `localhost`, `169.254.169.254`, `10.x`, `192.168.x`).
- URL malformed & encoded (`%00`, `%2F%2F`).
- URL panjang maksimum.

## Expected Results
- URL valid diterima; invalid & protocol berbahaya ditolak dengan pesan jelas.
- Hanya protocol di whitelist yang lolos.
- Host divalidasi (termasuk anti-SSRF untuk server-side fetch).

## Common Defects
- `javascript:`/`data:` lolos → XSS via URL.
- Validasi sintaks saja → SSRF/internal access saat server fetch URL.
- Open redirect (host tidak divalidasi ulang saat redirect).
- URL tanpa protocol ditolak padahal kontrak mengizinkan (atau sebaliknya).
- Double-encode melewati validasi.

## Security Considerations
- OWASP Input Validation Cheat Sheet — protocol whitelist.
- OWASP SSRF Prevention Cheat Sheet — blokir internal/loopback/metadata IP saat server-side fetch.
- OWASP Unvalidated Redirects and Forwards — validasi host saat redirect.
- URL yang difetch server = vektor SSRF, wajib diuji.

## References
- OWASP Input Validation Cheat Sheet
- OWASP SSRF Prevention Cheat Sheet
- OWASP Unvalidated Redirects and Forwards Cheat Sheet
- RFC 3986 (Uniform Resource Identifier — sintaks)
