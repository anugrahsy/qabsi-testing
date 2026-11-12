---
name: testing
description: Use when PRD and test cases already exist and QA needs to execute detailed testing against them, then produce a report and bug tickets.
---

# Testing

## Overview
Testing dengan PRD + test case sudah ada. Fokus eksekusi detail + report + bug ticket.

## When to Use
- PRD sudah ada (dibuat sendiri atau dari PM).
- Test case sudah ada.
- Tinggal testing.

## Core Pattern
1. Baca ticket: link API contract, target web (mis. `gateway-dev.uii.ac.id`), PRD/test case.
2. Testing detail sesuai test case. Enrich pakai knowledge module relevan — lihat `../../references/skill-tree.md`.
3. Rekam bug (video), report → Confluence, bug ticket → ClickUp + assign dari contract Consumer/Maintainer.

## Common Mistakes
- Mengarang hasil test.
- Skip kombinasi parameter (filter + sort + pagination + search) — lihat `api-combination`.

Detail: `../../references/flow.md`.
