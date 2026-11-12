# UI Form Testing

## Overview
Menguji interaksi manusia dengan **form**: pengisian, validasi inline, submission, dan reset. Risiko utama: validasi tidak konsisten antara client dan server, data hilang saat error, field required tidak terblokir, dan feedback error tidak jelas.

## When to Apply
Setiap komponen form di UI — create/edit, pencarian, filter, login, dan form multi-step. Aplikasikan bersama modul `input-*` (validasi nilai), `ui-button` (aksi submit), dan `ui-state` (data tersimpan/stale).

## Testing Principles
1. Validasi client = kenyamanan; validasi server = sumber kebenaran. Keduanya harus konsisten.
2. Feedback error harus **dekat** dengan field yang salah, bukan sekadar toast global.
3. Submission harus **idempoten** dari sisi UX — klik ganda tidak membuat data ganda.
4. Data yang sudah diisi tidak boleh hilang saat validasi gagal atau navigasi tak sengaja.
5. Form harus bisa diselesaikan **tanpa mouse** (keyboard + label terkait).

## Test Design Techniques
- Equivalence Partitioning — kelompok input valid/invalid per field.
- Boundary Value Analysis — panjang maksimum, nilai batas wajib/tidak.
- State Transition — state field (pristine, dirty, valid, invalid, disabled).
- Decision Table — kombinasi required + optional + format.

## Test Scenarios

### Positive Testing
- Isi semua field valid → submit sukses, data tersimpan.
- Field optional dikosongkan → tetap submit sukses.
- Nilai default/prefill benar dan bisa diedit.
- Form dibersihkan setelah submit sukses (atau sesuai kontrak).

### Negative Testing
- Field required kosong → terblokir + pesan error spesifik per field.
- Format salah (email, angka, tanggal) → error inline muncul.
- Submit dengan data invalid → tidak terkirim ke server.
- Error dari server → ditampilkan di UI, bukan blank/error tak jelas.

### Boundary Testing
- Input panjang maksimum → diterima tepat di batas.
- Input panjang maksimum + 1 → ditolak dengan pesan.
- Angka min/max pada nilai batas dan sedikit di luar.
- Banyak field error sekaligus → semua pesan tampil, tidak hanya yang pertama.

### Integration Testing
- Form + autosave/draft (delegasi `ui-state`).
- Form + upload file (delegasi `ui-file-upload`).
- Form + validasi server (delegasi `api-post-create`/`api-put-update`).
- Form multi-step: data step sebelumnya bertahan saat pindah step.

## Test Data
- Dataset valid lengkap per field.
- Dataset dengan tiap field invalid (satu per satu dan gabungan).
- Nilai batas panjang/angka.
- Data dengan karakter khusus, Unicode, whitespace, leading/trailing space.

## Expected Results
- Field invalid diberi tanda + pesan jelas, focus berpindah ke field pertama yang error.
- Submit ganda hanya menghasilkan satu record.
- Data pengguna tidak hilang saat submit gagal.
- Setelah sukses, form kembali ke state awal atau sesuai kontrak.

## Common Defects
- Validasi client dan server tidak sinkron (client lolos, server tolak).
- Pesan error generik ("Terjadi kesalahan") tanpa menunjuk field.
- Data ter-reset total saat satu field gagal validasi.
- Submit bisa diklik berulang → data duplikat.
- Field disabled tidak dikirim / field readonly malah bisa diedit.
- Autofill browser menghasilkan nilai tak terduga (perlu diuji).

## Security Considerations
- Jangan andalkan validasi client saja — selalu uji bypass validasi via request langsung.
- Data sensitif (password, token) tidak boleh tampil sebagai teks polos di field.
- Autocomplete atribut untuk field sensitif (mis. `autocomplete="off"`/`new-password`).
- XSS: input user yang dirender kembali di form harus di-escape.

## References
- ISTQB CTFL v4.0.1 — teknik desain test case
- OWASP WSTG — Input Validation Testing
- WCAG 2.1 — Label in Name, Error Identification (3.3.1)
