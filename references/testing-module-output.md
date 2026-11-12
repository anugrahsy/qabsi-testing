# Testing Module — Output (Report & Bug Ticket)

Format output QABSI. Bebas dulu, template menyusul, fleksibel per kondisi.

## Report (Confluence)

Struktur minimum:

```markdown
# QA Report — [Ticket] [Judul]

## Info          # ticket, tanggal, tester, environment
## Scope         # target web, user, API contract
## Ringkasan     # apa yang diuji + hasil
## Test Cases    # tabel: ID | skenario | expected | actual | status
## Temuan Bug    # list bug + link ticket
## Evidence      # screenshot, video, curl, log
## Catatan       # keterbatasan, catatan
```

## Bug Ticket (ClickUp)

Field minimum:
- **Summary** — 1 kalimat: apa, di mana, dampak.
- **Steps to Reproduce** — urutan pasti.
- **Expected vs Actual**.
- **Environment** — browser, endpoint, env (dev/stag/prod).
- **Evidence** — video/screenshot/curl.
- **Assignee** — resolve dari contract Consumer/Maintainer.

Catatan: task type "Bug" mungkin tak ada di ClickUp → prefix `[BUG]` + label.
