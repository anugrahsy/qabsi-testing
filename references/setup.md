# Setup and Destinations

## First use

Discover available tools/connectors and ask only for decisions that materially affect execution:

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
