# Setup — Konfigurasi Destinasi

## First Run

Saat pertama dijalankan, tanyakan & simpan default destinasi:

1. **Bug ticket** — ClickUp (default) / Jira / lainnya.
2. **Report** — Confluence (space/folder) / lainnya.
3. **Tooling** — Chrome DevTools + ClickUp + Confluence (prioritas); Playwright/Postman sesuai kondisi.
4. **Repo access** — user kasih URL, sudah login GitLab mandiri.

## Default (case user ini)

- Bug ticket → **ClickUp**.
- Report → **Confluence** (space AT).
- Destinasi tak ditentukan saat run → **tanya user**.

## Rule Destinasi

- Ditentukan di ticket/instruksi → eksekusi.
- Tidak ditentukan → tanya user sebelum tulis.

## Catatan Lingkungan

- ClickUp: task type "Bug" mungkin tidak ada → fallback prefix `[BUG]`.
- ClickUp storage attachment bisa penuh (`GBUSED_005`) → deteksi & fallback simpan lokal + link.
- Screencast: `navigate` dulu, baru `screencast_start`, hindari page tertutup saat rekam (hasil 0-byte).
- Atlassian MCP bisa di endpoint V1 deprecated — peringatkan user kalau muncul.
