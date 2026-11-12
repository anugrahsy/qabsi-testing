# Rules — Standar QA & Teknik Test Design

Landasan metodologi QABSI. Sumber: ISTQB CTFL v4.0.1, ISO 29119.

## Prinsip Testing (ISTQB)

1. Testing menunjukkan adanya defect, bukan membuktikan tidak ada defect.
2. Exhaustive testing tidak mungkin — gunakan teknik + prioritas risiko.
3. Early testing — cari defect sedini mungkin.
4. Defect clustering — sebagian kecil modul memuat sebagian besar defect.
5. Pesticide paradox — test case yang sama lama-lama tak menemukan bug baru.
6. Testing context-dependent — cara testing beda per konteks.
7. Absence-of-errors fallacy — bebas bug ≠ memenuhi kebutuhan bisnis.

## Teknik Test Design

### A. Equivalence Partitioning (EP)
Bagi input jadi kelompok dengan perilaku sama. Uji satu perwakilan tiap kelompok.
- Valid: nilai dalam kelompok diterima.
- Invalid: nilai luar kelompok ditolak.

### B. Boundary Value Analysis (BVA)
Uji nilai di batas min/max. Bug sering di batas.
- Below minimum → reject; minimum → accept; above minimum → accept.
- Below maximum → accept; maximum → accept; above maximum → reject.

### C. Decision Table Testing
Kombinasi kondisi → hasil. Pakai saat hasil bergantung banyak kondisi.

### D. State Transition Testing
Uji transisi status yang boleh/tidak. Setiap transisi punya aturan.

### E. Pairwise / Combinatorial
Kombinasi parameter. Kurangi jumlah kasus tanpa kehilangan cakupan penting.

### F. Error Guessing / Exploratory
Berdasar pengalaman + heuristik. Bukan pengganti teknik formal.

## Struktur Test Case

| Field | Keterangan |
|---|---|
| Test Case ID | Identitas unik |
| Module | Modul yang diuji |
| Feature | Fitur yang diuji |
| Scenario | Kondisi yang diuji |
| Preconditions | Kondisi awal |
| Test Data | Data yang dipakai |
| Test Steps | Langkah pengujian |
| Expected Result | Hasil seharusnya (spesifik, verifiable) |
| Actual Result | Hasil aktual |
| Status | Pass / Fail / Blocked |
| Priority | Critical / High / Medium / Low |
| Severity | Tingkat dampak defect |
| Evidence | Screenshot, log, response API, video |

Expected Result wajib spesifik & verifiable. Hindari "sistem berjalan normal".

## Jenis Testing

Unit · Component · Integration · Functional · API · Contract · E2E · Regression · Security · Performance · Accessibility · Compatibility.

## Bug Report Standard

- Summary singkat (1 kalimat: apa, di mana, dampak).
- Steps to reproduce (urutan pasti).
- Expected vs Actual.
- Environment (browser, device, endpoint, env).
- Evidence (screenshot/video/log/curl).
- Severity (dampak) vs Priority (urgensi) terpisah.

## Knowledge vs Test Case

Knowledge = metode & skenario yang perlu dipertimbangkan. Test case = hasil penerapannya pada aplikasi tertentu. Jangan samakan.
