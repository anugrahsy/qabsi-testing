# UI Notification Testing (Toast, Alert, Notifications)

## Overview
Menguji **notifikasi** — toast, alert, dan pesan status yang memberi tahu hasil aksi. Risiko utama: notifikasi hilang terlalu cepat/tidak muncul, menumpuk, tidak bisa diakses screen reader, dan pesan tidak sinkron dengan state sebenarnya.

## When to Apply
Setiap feedback non-blocking: sukses submit, error transient, peringatan, dan notifikasi sistem. Aplikasikan bersama `ui-error-state` (error blocking) dan `ui-loading` (proses berjalan).

## Testing Principles
1. Notifikasi harus **tepat waktu** — muncul saat kejadian, bukan terlambat/terlewat.
2. Durasi tampil cukup dibaca; notifikasi penting (error) tidak boleh auto-hilang terlalu cepat.
3. Notifikasi harus **diumumkan ke screen reader** (aria-live/role=status/alert).
4. Banyak notifikasi sekaligus → ditumpuk/diurut wajar, tidak menutupi UI penting.
5. Pesan harus konsisten dengan state aktual (jangan "sukses" padahal gagal).

## Test Design Techniques
- State Transition — muncul → tampil → auto-dismiss / manual close.
- Equivalence Partitioning — jenis notifikasi (info/sukses/warning/error).
- Exploratory — banyak aksi beruntun yang memicu banyak notifikasi.

## Test Scenarios

### Positive Testing
- Aksi sukses → notifikasi sukses tampil.
- Notifikasi bisa ditutup manual (jika ada tombol close).
- Auto-dismiss berjalan sesuai durasi yang ditentukan.
- Jenis notifikasi (info/sukses/warning/error) terbedakan jelas (bukan cuma warna).

### Negative Testing
- Aksi gagal → notifikasi error, bukan sukses.
- Notifikasi tidak muncul padahal aksi terjadi → defect.
- Notifikasi error tidak auto-hilang sebelum dibaca (atau ada akses riwayat).
- Notifikasi lama bertahan terus tanpa close → defect.

### Boundary Testing
- Banyak notifikasi beruntun → semua tampil/terurut, tidak saling menimpa.
- Durasi sangat pendek → pesan masih bisa dibaca (tidak flicker).
- Notifikasi saat notifikasi lain masih tampil → stacking benar.

### Integration Testing
- Notifikasi + aksi sukses/gagal (delegasi `ui-button`, `ui-form`).
- Notifikasi + error state (delegasi `ui-error-state`).
- Notifikasi + upload selesai (delegasi `ui-file-upload`).
- Notifikasi + accessibility (delegasi `ui-accessibility`).

## Test Data
- Aksi yang memicu tiap jenis notifikasi (sukses, error, warning, info).
- Skenario banyak aksi beruntun.

## Expected Results
- Notifikasi muncul sesuai kejadian, dengan jenis dan pesan yang benar.
- Durasi & cara tutup sesuai desain; error penting tidak terlewat.
- Screen reader mengumumkan notifikasi tanpa mengganggu fokus.
- Tidak menumpuk tak terkendali atau menutupi aksi penting.

## Common Defects
- Notifikasi error auto-hilang terlalu cepat.
- Jenis notifikasi hanya dibedakan warna (tidak aksesibel).
- Notifikasi tidak diumumkan ke screen reader.
- Banyak notifikasi menimpa satu sama lain (hilang).
- Pesan sukses muncul padahal request gagal (tidak sinkron).
- Toast menutupi tombol penting dan tidak bisa di-dismiss.

## Security Considerations
- Jangan tampilkan data sensitif/token di notifikasi.
- Notifikasi error jangan membocorkan detail internal.
- Pastikan notifikasi tidak bisa dipalsukan UI-nya untuk phishing (konsistensi sumber pesan).

## References
- WCAG 2.1 — Status Messages (4.1.3)
- WAI-ARIA — alert/status roles
- ISTQB CTFL v4.0.1
