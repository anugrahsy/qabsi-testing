# GitLab, Confluence, and ClickUp Integration Contract

Artifact generation remains local. The package includes an executable preflight and gated publisher; an official connector may be used instead when available, after checking its current schema and preserving the same authorization and deduplication controls.

Every adapter starts with `dry_run: true`, uses a stable idempotency key, stores no secret values, and reports exactly which external mutations occurred. BSI source and internal-restricted evidence stay on BSI-managed infrastructure; ClickUp receives sanitized metadata and accessible links only.

## Mandatory readiness check

Run this before source discovery so missing setup is visible at the beginning, not after testing finishes:

```bash
python3 scripts/check_integrations.py --json
```

Offline readiness does not prove access. When live publication is in scope and network access is authorized, run `python3 scripts/check_integrations.py --verify --json` to perform bounded read-only identity and destination checks. Missing or invalid publication configuration never blocks local analysis, testing, spreadsheet generation, or draft generation.

Configuration is supplied only through the documented `AQABSI_CONFLUENCE_*`, `AQABSI_CLICKUP_*`, and target test variables (`AQABSI_TARGET_*`, `AQABSI_TEST_*`). Use [`assets/templates/integrations.env.example`](../assets/templates/integrations.env.example) for variable names. Do not paste passwords or token values into chat, source code, command history, PRDs, reports, or committed files.

## Target application authentication

When testing authenticated routes or functional workflows on a target deployment (development, staging, or local test environment), configure test account credentials separately from documentation platforms:

- `AQABSI_TARGET_BASE_URL`: Base URL of the target application (HTTPS or loopback HTTP). Must belong to a non-production development or staging host unless explicit test authorization is provided.
- `AQABSI_TARGET_AUTH_MODE`: Authentication mode (`web_login`, `bearer_token`, `basic_auth`, `sso_manual_handoff`, or `none`).
- `AQABSI_TEST_USERNAME`: Dedicated test account username.
- `AQABSI_TEST_PASSWORD`: Test account password. Transmitted only during verification, redacted from all outputs, logs, artifacts, and receipts.
- `AQABSI_TEST_TOKEN`: API token or Bearer token (when `bearer_token` mode is selected).
- `AQABSI_TARGET_LOGIN_PATH`: Custom login route (defaults to `/login`).

Preflight verifies reachability and performs a single controlled login smoke test. Session cookies and tokens are kept in memory only during testing and never echoed in reports or receipts. For SSO or interactive MFA, use `sso_manual_handoff`.

Single-account credentials enable authenticated functional testing. Multi-role/IDOR testing requires dedicated role credentials; unconfigured roles are marked as blocked rather than guessed.

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

- Cloud uses email plus API token and a numeric Space ID.
- Data Center uses a bearer PAT and Space key.
- The base URL must use HTTPS and may include an approved Confluence context path.

## ClickUp

Only a confirmed `fail` produces a defect draft. `flaky`, `blocked`, `not_run`, and `environment_error` require investigation or test/environment work, not a confirmed product-bug ticket.

Use the generated SHA-256 fingerprint to search existing open/closed tasks. If found, add the new run evidence or reopen according to team policy; otherwise create one task. Store the fingerprint, run ID, test-case ID, source commit/MR, environment, severity, owner team, and Confluence report link. Never create repeated tasks because a retry produced the same failure.

## Failure handling

- `401/403`: stop and request the correct connection or permission; do not bypass.
- Rate limit/transient failure: bounded retry only when the connector documents safe retry semantics.
- Validation failure: keep the local draft and report the rejected fields.
- Attachment quota/full: retain the approved local artifact and link only if recipients can access it.
- Partial publication: report exactly which mutations succeeded and do not repeat them blindly.

## Gated publisher

The default command prints a sanitized plan and performs no network request:

```bash
python3 scripts/publish_artifacts.py \
  --confluence-draft .aqabsi-output/confluence-draft.json \
  --clickup-draft .aqabsi-output/clickup-drafts.json
```

After the plan, destination, identity, assignee IDs, and sensitive-data review are approved, publish one provider at a time:

```bash
python3 scripts/publish_artifacts.py \
  --provider confluence \
  --confluence-draft .aqabsi-output/confluence-draft.json \
  --execute \
  --authorization-reference "<approved-change-reference>" \
  --receipt .aqabsi-output/confluence-publication-receipt.json
```

Replace the provider and draft path for ClickUp. Do not place tokens in `--authorization-reference`. Writes are not retried automatically; use the receipt and provider-side fingerprint/run ID before deciding whether another execution is safe.

Immediately before a live write, the publisher repeats read-only identity and destination verification, including the configured Confluence parent/Space or ClickUp List/Workspace relationship. A valid token for the wrong accessible destination is rejected.

Serialize publication for the same run and destination. AQABSI prevents ordinary replay through exact run markers and fingerprints, but this version does not claim lock-free idempotency for two concurrent publisher processes racing before provider indexing completes. If a previous write returned an ambiguous result or is not yet discoverable through provider search, reconcile its receipt and destination state before replaying it; serialization alone does not guarantee search-index visibility.
