# Flow — Langkah Detail Tiap Skill

## Routing (tentukan kondisi)

1. Baca ticket/instruksi → ekstrak konteks: repo BE/FE, link Confluence API contract, target web, user testing (1/2/3), deskripsi.
2. Tentukan kondisi:
   - Tanpa PRD + tanpa test case → `analyze-testing`.
   - PRD + test case ada → `testing`.
   - Hanya PRD → `prd-generate`.
   - Hanya test case → `test-case-generate`.
   - Security assessment → `security-testing`.
3. Cek destinasi (report/bug). Tak ditentukan → tanya user. Ditentukan → eksekusi.
4. Jalankan skill yang sesuai.

## Analyze Testing

1. Baca ticket → konteks (repo, contract, web, user).
2. `git clone` repo BE & FE.
3. Analisa code → alur, logika, aturan, cara kerja.
4. PRD (kalau belum ada).
5. Test case (.md) pakai ISTQB.
6. Buat child ticket test case (opsional).
7. Testing: Chrome DevTools + Playwright; login SSO via `uii-gateway-login` kalau UII app.
8. Enrich test case pakai knowledge module relevan (context-driven).
9. Rekam video bug (screencast: `navigate` dulu → `screencast_start` → `screencast_stop`).
10. Report → Confluence (format bebas dulu).
11. Bug ticket → ClickUp (default), assign dari contract Consumer/Maintainer.

## Testing (PRD + test case ada)

1. Baca ticket → link contract, target web, PRD/test case.
2. Testing detail sesuai test case; enrich knowledge module.
3. Rekam bug → report → bug ticket + assign.

## Generate PRD

1. Clone repo. 2. Analisa code. 3. Tulis PRD.

## Generate Test Case

1. Sumber: PRD atau analisa kode. 2. Susun test case (ISTQB). 3. Enrich knowledge module.

## Security Testing

1. Tentukan scope (endpoint/URL + role + kontrak).
2. Load knowledge `security/*` + `nft-security`.
3. Jalankan checklist OWASP WSTG/ASVS.
4. Report temuan → bug ticket.

## Prinsip Lintas Flow

- **Context-driven knowledge selection** — identifikasi fitur dulu, load modul relevan saja.
- **Knowledge ≠ test case.**
- **Expected behavior** (dari kontrak aplikasi) ≠ **recommended behavior** (dari standar industri).
- **Prioritas berbasis risiko.**
- **Jangan tulis DB prod. Jangan commit/push kecuali user suruh.**
- **Assignee bug**: resolve dari contract Consumer/Maintainer, bukan tebak gender.
