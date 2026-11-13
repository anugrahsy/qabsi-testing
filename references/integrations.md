# GitLab, Confluence, and ClickUp Integration Contract

Helpers generate drafts only. Use the available official connector/API after checking its current tool schema and only when the user authorized the exact mutation.

Every adapter starts with `dry_run: true`, uses a stable idempotency key, stores no secret values, and reports exactly which external mutations occurred. BSI source and internal-restricted evidence stay on BSI-managed infrastructure; ClickUp receives sanitized metadata and accessible links only.

## GitLab BSI UII

Treat the service as self-managed until base URL, API version, authentication method, internal CA, project path, MR IID, source/target SHA, pipeline/job IDs, and permissions are verified. Prefer masked/protected CI variables and never disable TLS verification. Adding a job to a target repository is a separate approved change.

## Ownership registry

Maintain an approved mapping outside source code secrets:

```json
{
  "teams": {
    "backend": {"clickup_user_id": "123", "confluence_account_id": "abc"},
    "frontend": {"clickup_user_id": "456", "confluence_account_id": "def"}
  }
}
```

Do not derive assignment from gender, a guessed name, commit authorship, or a Consumer/Maintainer label alone. If a platform user ID is unresolved, leave the draft unassigned and report the mapping gap.

## Confluence

Record deployment type (Cloud/Data Center), base URL, authentication method, space key, parent page, and attachment classification before publication. Use `run_id` as the idempotency key. Search for an existing page/property before create; update the same run page when found. Include scope, source commit/MR, environment, summary, traceability, test results, defects, evidence links, limitations, and publication timestamp. Preserve a link to the sanitized spreadsheet artifact.

## ClickUp

Only a confirmed `fail` produces a defect draft. `flaky`, `blocked`, `not_run`, and `environment_error` require investigation or test/environment work, not a confirmed product-bug ticket.

Use the generated SHA-256 fingerprint to search existing open/closed tasks. If found, add the new run evidence or reopen according to team policy; otherwise create one task. Store the fingerprint, run ID, test-case ID, source commit/MR, environment, severity, owner team, and Confluence report link. Never create repeated tasks because a retry produced the same failure.

## Failure handling

- `401/403`: stop and request the correct connection or permission; do not bypass.
- Rate limit/transient failure: bounded retry only when the connector documents safe retry semantics.
- Validation failure: keep the local draft and report the rejected fields.
- Attachment quota/full: retain the approved local artifact and link only if recipients can access it.
- Partial publication: report exactly which mutations succeeded and do not repeat them blindly.
