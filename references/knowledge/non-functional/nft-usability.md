# NFT Usability Testing

## Overview
Menguji seberapa **mudah, efisien, dan memuaskan** aplikasi digunakan oleh pengguna target untuk menyelesaikan tugasnya. Fokus pada **pengalaman pengguna**, bukan pada benar/salah fungsi (functional) atau kecepatan teknis (`nft-performance`).

Risiko utama: alur membingungkan, tugas sederhana butuh banyak langkah, pesan error tidak membantu, dan pengguna tidak bisa menyelesaikan tujuannya tanpa bantuan.

## When to Apply
- Fitur baru atau desain ulang yang mengubah cara pengguna bekerja.
- Aplikasi dengan **proses multi-langkah** (form panjang, workflow, pengisian data).
- Saat ada keluhan pengguna atau tingkat kesalahan input yang tinggi.
- Sebelum rilis untuk memvalidasi asumsi desain dengan pengguna nyata.

## Testing Principles
1. Uji dengan **pengguna target asli** (atau representatif) — bukan hanya asumsi tim pengembang.
2. Ukur **efektivitas** (selesai?), **efisiensi** (berapa langkah/waktu?), **kepuasan** (bagaimana rasanya?).
3. Amati **perilaku nyata**, bukan opini — apa yang dikatakan vs apa yang dilakukan bisa beda.
4. Fokus pada **tugas utama** pengguna, bukan setiap tombol.
5. Usability bersifat kontekstual — hasil diukur terhadap profil pengguna dan tujuan spesifik.

## Test Design Techniques
- **Task-based Evaluation** — beri pengguna tugas nyata, amati penyelesaiannya.
- **Think-aloud Protocol** — pengguna menyuarakan pikirannya selama mengerjakan tugas.
- **Heuristic Evaluation** (Nielsen) — inspeksi oleh evaluator terhadap 10 prinsip.
- **A/B Testing** — bandingkan dua varian desain pada tugas yang sama.
- **Survei / SUS (System Usability Scale)** — ukur kepuasan secara kuantitatif.

## Test Scenarios

### Positive Testing
- Pengguna menyelesaikan tugas inti **tanpa bantuan** dan tanpa jalan buntu.
- Alur utama efisien (jumlah langkah wajar, tidak berlebihan).
- Pesan umpan balik (sukses/error/loading) jelas dan membantu langkah berikutnya.
- Istilah/label konsisten dan dipahami pengguna target.

### Negative Testing
- Pengguna melakukan kesalahan input → pesan error jelas dan memberi jalan keluar.
- Pengguna tersesat/klik salah → ada cara kembali/membatalkan yang jelas.
- Data penting gagal disimpan → pengguna diberi tahu dan tidak kehilangan pekerjaan.
- Tugas dibatalkan di tengah → tidak ada state membingungkan yang tertinggal.

### Boundary Testing
- Form dengan banyak field (panjang maksimum) → tetap bisa dikelola pengguna.
- Pengguna baru (belum terlatih) → bisa menyelesaikan tugas dasar.
- Alur multi-langkah pada langkah terakhir → tidak ada kebingungan saat hampir selesai.

### Integration Testing
- Alur end-to-end dari perspektif pengguna (bukan per layar).
- Konsistensi antar layar/modul (navigasi, istilah, pola interaksi).
- Interaksi dengan umpan balik sistem (loading, error, notifikasi) dalam konteks tugas.

## Test Data
- Profil pengguna target (peran, tingkat keahlian, konteks kerja).
- Skenario tugas realistis dengan tujuan yang jelas.
- Data uji yang tidak menyesatkan pengguna selama evaluasi.

## Expected Results
- Tingkat penyelesaian tugas tinggi (mayoritas pengguna berhasil tanpa bantuan).
- Waktu/langkah penyelesaian dalam batas yang wajar untuk tiap tugas inti.
- Skor kepuasan (mis. SUS) mencapai ambang yang ditetapkan.
- Error pengguna menurun dibanding baseline (jika menguji perbaikan).

## Common Defects
- Alur membingungkan: langkah tidak berurutan atau tersembunyi.
- Pesan error teknis (kode) yang tidak bisa dipahami pengguna.
- Label/istilah tidak konsisten antar layar.
- Tidak ada umpan balik setelah aksi (user ragu apakah tersimpan).
- Terlalu banyak langkah untuk tugas sederhana.
- Tidak ada jalan kembali/batal yang jelas dari keadaan error.

## Security Considerations
- Evaluasi usability memakai data uji, bukan data pengguna asli yang sensitif.
- Rekaman sesi/screen capture harus dianonimkan dan dapat persetujuan partisipan.
- Jangan arahkan pengguna ke alur yang mengekspos data sensitif selama pengujian.

## References
- ISO 9241-11 — definisi usability (effectiveness, efficiency, satisfaction)
- ISO/IEC 25010 — Usability quality characteristics
- Nielsen Norman Group — 10 Usability Heuristics
