# QABSI — QA Testing Plugin untuk Claude Code

Skill QA testing BSI UII: manual + automated testing, dari analisa kode sampai bug ticket. Namespace `qabsi:` (seperti `superpowers:`).

## Skill (5)

| Skill | Fungsi |
|---|---|
| `/qabsi:analyze-testing` | Dari nol: clone → PRD → test case → testing → report → bug |
| `/qabsi:testing` | PRD + test case ada → testing → report → bug |
| `/qabsi:prd-generate` | PRD saja |
| `/qabsi:test-case-generate` | Test case saja |
| `/qabsi:security-testing` | Security assessment (OWASP) |

## Install

Plugin `qabsi` = repo ini (punya `.claude-plugin/plugin.json`).

```bash
# symlink repo ke ~/.claude/skills/qabsi (auto-load sebagai plugin `qabsi`)
ln -s "$PWD" ~/.claude/skills/qabsi
```

Restart session / jalankan `/skills` biar skill ke-load. Skill muncul sebagai `/qabsi:testing`, `/qabsi:analyze-testing`, dst.

## Cara Pakai

```
/qabsi:testing — "test app X sesuai test case yang sudah ada"
/qabsi:analyze-testing — "test app Y yang belum ada PRD/test case"
/qabsi:prd-generate — "bikin PRD dari repo Z"
/qabsi:test-case-generate — "bikin test case dari PRD/repo"
/qabsi:security-testing — "security assessment endpoint W"
```

Routing (kondisi mana pakai skill mana) ada di `references/flow.md`.

## Struktur

```
.claude-plugin/plugin.json  # manifest plugin (name: qabsi)
skills/                     # 5 skill
references/                 # rules, flow, skill-tree, setup, testing-module-*, output
references/knowledge/       # 96 modul domain-based
README.md
```

## Prasyarat

- MCP: Chrome DevTools + ClickUp + Confluence (prioritas); Playwright/Postman sesuai kondisi.
- Login GitLab mandiri (repo via URL).
- Login UII Gateway SSO untuk app UII (`uii-gateway-login`).

## Referensi

Lihat `references/rules.md` (standar QA), `references/flow.md` (flow), `qabsi-knowledge-taxonomy-v1.md` (katalog knowledge).
