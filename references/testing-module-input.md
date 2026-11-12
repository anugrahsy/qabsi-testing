# Testing Module — Input & Data Validation

Index domain input. Detail tiap modul di `knowledge/input/<file>.md`.

## Kapan dipakai
Saat fitur punya field input (form, request body, parameter). Load modul sesuai tipe field.

| Modul | Cakupan |
|---|---|
| `input-email.md` | Format (RFC 5322), domain, uniqueness, normalization |
| `input-password.md` | Panjang, kompleksitas, whitespace (NIST 800-63B) |
| `input-username.md` | Allowed chars, uniqueness, reserved words |
| `input-phone.md` | E.164, country code, NIK, KTP, passport |
| `input-number.md` | Integer, decimal, precision, overflow |
| `input-date.md` | Format, leap year, range, timezone |
| `input-text.md` | Length, whitespace, Unicode, special chars |
| `input-url.md` | Syntax, protocol, domain, SSRF |
| `input-file.md` | MIME vs magic bytes, size, path traversal |
| `input-image.md` | Format, dimensi, metadata |
| `input-array.md` | Empty, duplicate, item limits |
| `input-object.md` | Required, nested, mass assignment |
| `input-enum.md` | Allowed values, case sensitivity |
| `input-currency.md` | Presisi desimal, rounding, ISO 4217 |
| `input-identifier.md` | UUID, numeric ID, existence, IDOR |

Setiap modul muat positive/negative/boundary/equivalence partitioning. Tidak semua teknik dipaksa.
