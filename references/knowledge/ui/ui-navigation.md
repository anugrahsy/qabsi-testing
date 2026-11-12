# UI Navigation Testing

## Overview
Menguji **navigasi** — routing, redirect, back/forward, dan menu. Risiko utama: link menuju halaman salah, redirect loop, state hilang saat back, dan akses ke halaman tanpa otorisasi.

## When to Apply
Setiap perpindahan halaman/rute, menu, breadcrumb, dan guard akses. Aplikasikan bersama `auth-rbac`/`auth-object-access` (guard) dan `ui-state` (state saat kembali).

## Testing Principles
1. Navigasi harus **deterministik** — URL yang sama menuju halaman yang sama.
2. Back/forward browser harus berperilaku wajar (state pulih atau di-reset sesuai kontrak).
3. Redirect harus berakhir (tidak loop) dan menuju target yang benar.
4. Akses halaman tanpa izin harus diblokir + diarahkan dengan jelas.
5. Navigasi aktif harus terindikasi (menu/breadcrumb), user tahu posisinya.

## Test Design Techniques
- State Transition — antar halaman, guard, redirect.
- Exploratory — kombinasi back/forward, deep link, bookmark.

## Test Scenarios

### Positive Testing
- Klik menu/link → halaman tujuan benar, URL sesuai.
- Deep link / bookmark URL valid → halaman terbuka benar.
- Redirect → menuju target yang dimaksud, tanpa loop.
- Breadcrumb/indikator aktif sesuai posisi halaman.

### Negative Testing
- URL tidak valid → halaman not found yang jelas (bukan blank).
- Akses halaman tanpa otorisasi → diblokir + redirect ke halaman yang tepat.
- Redirect loop → terdeteksi, tidak hang.
- Back setelah logout → tidak bisa mengakses halaman terproteksi.

### Boundary Testing
- Back/forward berulang cepat → tidak crash/state rusak.
- Deep link ke halaman yang butuh data tidak ada → fallback jelas.
- Navigasi saat ada perubahan belum disimpan → konfirmasi (delegasi `ui-modal`).

### Integration Testing
- Navigasi + guard otorisasi (delegasi `auth-rbac`).
- Navigasi + state halaman (delegasi `ui-state`).
- Navigasi + breadcrumb/menu aktif.
- Navigasi + loading antar halaman (delegasi `ui-loading`).

## Test Data
- URL valid, invalid, dan yang butuh otorisasi.
- State form "belum disimpan".

## Expected Results
- Setiap link/menu menuju halaman yang benar.
- URL konsisten dengan halaman yang tampil.
- Redirect berakhir dan benar; back/forward tidak merusak state.
- Halaman terproteksi tidak bisa diakses tanpa izin.

## Common Defects
- Redirect loop (A → B → A) tanpa henti.
- State hilang/rusak saat back (form kosong, filter reset).
- Menu aktif tidak sinkron dengan halaman.
- Halaman not found blank tanpa petunjuk.
- Guard client saja — akses langsung via URL lolos.
- Tombol back setelah submit mengulang aksi (resubmit).

## Security Considerations
- Guard navigasi di client bukan pengganti otorisasi server.
- Pastikan halaman terproteksi tidak di-render sebelum auth dicek.
- Redirect terbuka (open redirect) bisa dipakai phishing — validasi URL tujuan.

## References
- OWASP WSTG — Testing for Open Redirect, Authorization
- ISTQB CTFL v4.0.1
- WCAG 2.1 — Consistent Navigation (3.2.3)
