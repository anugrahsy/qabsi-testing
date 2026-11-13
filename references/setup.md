# Setup and Destinations

## First use

From the AQABSI package root, run the offline preflight at the beginning of every workflow:

```bash
python3 scripts/check_integrations.py --json
```

The command performs no network request unless `--verify` is added. Exit `2` means publication setup is incomplete: communicate the exact missing variable names and setup links immediately, then continue local QA and draft generation. Exit `3` means configuration is invalid. Do not ask the user to paste a token into chat.

Use [`assets/templates/integrations.env.example`](../assets/templates/integrations.env.example) as a names-only reference. Supply real secret values through an approved secret manager or process environment, never a committed `.env` file. Installation itself stays credential-free.

After the offline check, discover available tools/connectors and ask only for decisions that materially affect execution:

1. Authorized repositories/commits and target environment.
2. Test identities/roles and credential-delivery method; never store secret values.
3. Evidence location and retention/redaction policy.
4. Report destination and approved Confluence space/parent.
5. Defect destination and approved ClickUp list/project.
6. Ownership registry containing real platform IDs.

Do not persist these defaults across sessions unless the user explicitly asks. A destination in a ticket is context; external mutation still follows `execution-safety.md` and `integrations.md`.

## Tool fallback

Prefer deterministic project runners. For browser testing, use an available browser automation/DevTools capability and capture tool/version. For API testing, use the project suite, contract tool, or a safe request client. If a named tool is unavailable, report the gap and use an equivalent only when it preserves the required evidence and authorization boundary.

## Publication behavior

Artifact generation is local and dry-run. Before publishing, show destination, title/task count, deduplication result, assignees, sensitive-data review, and exact actions. On partial failure, report completed IDs and do not repeat successful mutations blindly.

When configuration is complete, verify identity and destination with bounded read-only calls:

```bash
python3 scripts/check_integrations.py --verify --json
```

Build and review a no-network publication plan first:

```bash
python3 scripts/publish_artifacts.py \
  --confluence-draft .aqabsi-output/confluence-draft.json \
  --clickup-draft .aqabsi-output/clickup-drafts.json
```

Live publication requires explicit provider selection, `--execute`, and a non-secret authorization reference. The authorization reference identifies the approved change or user instruction; it is not a token.
