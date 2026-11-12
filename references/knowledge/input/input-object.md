# Input Object Validation Testing

## Overview
Menguji validasi input object (JSON): required properties, nested schema, dan unexpected fields. Risiko utama: field wajib hilang tetap diterima, tipe field salah, nested object tidak divalidasi, dan field tak dikenal ditangani tidak konsisten (mass assignment).

## When to Apply
Body request berbentuk object/JSON (POST/PUT/PATCH), field nested object, atau payload kompleks.

## Testing Principles
1. Tentukan **required properties** secara eksplisit (mana wajib, mana optional).
2. Tentukan **tipe & schema** tiap field (delegasi ke modul input terkait).
3. Tentukan kebijakan **additional/unexpected fields**: ditolak, diabaikan, atau diteruskan.
4. Validasi **nested** object & array sampai kedalaman sesuai schema.
5. Bedakan field hilang vs `null` vs nilai default — ketiganya berbeda.

## Test Design Techniques
- Equivalence Partitioning — kelas payload valid/invalid per field; kelas required/optional.
- Boundary Value Analysis — kedalaman nested, jumlah field.
- Decision Table — kombinasi required × tipe × unexpected field.
- Combinatorial — kombinasi field optional yang hadir/absen.

## Test Scenarios

### Positive Testing
- Object dengan semua required field valid → diterima.
- Object dengan field optional diisi → diterima.
- Field optional dihilangkan → diterima (default berlaku sesuai kontrak).
- Nested object valid → diterima.
- Tipe tiap field sesuai schema → diterima.

### Negative Testing
- Required field hilang → ditolak.
- Tipe field salah (string vs number) → ditolak.
- `null` pada field non-nullable → ditolak.
- Nested object invalid (required field di dalamnya hilang) → ditolak.
- Unexpected field → ditolak/diabaikan sesuai kontrak.
- Bukan object (array/string) → ditolak.

### Boundary Testing
- Nested object sangat dalam → ditangani sesuai batas (bukan stack overflow).
- Jumlah field sangat banyak → ditangani.
- Field kosong `""` vs hilang vs `null` → masing-masing sesuai kontrak.

### Integration Testing
- Validasi object konsisten antar endpoint (POST vs PATCH — required vs optional bisa beda).
- Unexpected field tidak menimpa field internal (mass assignment).
- Nested object disimpan & dibaca kembali konsisten (round-trip).

## Test Data
- Payload lengkap valid; payload minimal (hanya required).
- Payload dengan tiap required field dihilangkan satu per satu.
- Payload dengan tipe field salah & `null`.
- Nested object valid/invalid, kedalaman ekstrem.
- Payload dengan unexpected/additional fields.

## Expected Results
- Object valid diterima; required hilang / tipe salah / nested invalid ditolak dengan pesan jelas.
- Unexpected fields ditangani sesuai kontrak (reject/ignore).
- Pesan error menunjuk field/path yang invalid.

## Common Defects
- Required field tidak divalidasi (hilang tetap diterima).
- Tipe field longgar (string `"123"` diterima sebagai number).
- Nested object tidak divalidasi.
- Unexpected field diteruskan → mass assignment/overwrite field internal (role, id).
- `null` vs missing tidak dibedakan.
- Error tidak menunjukkan path field yang invalid.

## Security Considerations
- OWASP Input Validation Cheat Sheet — validasi schema ketat, server-side.
- OWASP Mass Assignment — jangan biarkan unexpected field menimpa field internal.
- Deep nesting → stack overflow / DoS; batasi kedalaman payload.
- Validasi object di schema/gateway sebelum masuk business logic.

## References
- OWASP Input Validation Cheat Sheet
- OWASP Mass Assignment Cheat Sheet
- OpenAPI Specification (schema object)
