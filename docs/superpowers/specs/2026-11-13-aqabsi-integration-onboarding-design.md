# AQABSI Integration Onboarding and Safe Publisher Design

## Intent

AQABSI must detect Confluence and ClickUp readiness at the beginning of every workflow, explain missing setup before a long test run, and provide an authorized path from sanitized drafts to live external records. Installation remains credential-free because repository installers cannot safely infer organization URLs, destinations, deployment types, identities, or authorization.

## Goals

- Make integration preflight mandatory before testing while allowing local analysis and draft generation when integrations are unavailable.
- Report each provider as `ready`, `missing`, `invalid`, `verified`, `unauthorized`, `forbidden`, or `unreachable` without revealing secret values.
- Support ClickUp personal tokens and deployment-aware Confluence Cloud or Data Center authentication.
- Publish existing Confluence and ClickUp drafts only after an explicit live flag, authorization reference, destination review, and identity resolution.
- Prevent duplicate pages/tasks and record partial success so retries do not blindly repeat completed mutations.
- Keep the package framework-neutral and team-neutral for all BSI UII teams.

## Non-goals

- AQABSI does not collect tokens in chat, write them to repository files, generate a real credential file, or inspect browser cookies.
- AQABSI does not hardcode a person, team, Confluence space, parent page, ClickUp Workspace, or ClickUp List.
- AQABSI does not automatically publish merely because credentials exist.
- AQABSI does not configure OAuth applications, organization secret stores, or platform permissions.
- AQABSI does not attach internal-restricted source or raw evidence to ClickUp.

## Approaches considered

1. **Documentation-only onboarding.** Smallest change, but agents can skip prose and users receive the setup warning only after artifacts are generated.
2. **Executable preflight plus gated publisher.** Selected because it produces machine-readable readiness, protects secrets, supports deterministic testing, and makes live mutation an explicit second step.
3. **Plaintext `credentials.json` with automatic publication.** Rejected because it normalizes long-lived secret storage and turns credential presence into implicit mutation authority.

## Configuration contract

Secrets are accepted only from environment variables or an environment supplied by an approved secret manager. AQABSI never prints their values.

Common provider variables:

- `AQABSI_CONFLUENCE_DEPLOYMENT`: `cloud` or `data_center`.
- `AQABSI_CONFLUENCE_BASE_URL`: HTTPS origin including any Confluence context path.
- `AQABSI_CONFLUENCE_SPACE_ID`: required for Cloud.
- `AQABSI_CONFLUENCE_SPACE_KEY`: required for Data Center.
- `AQABSI_CONFLUENCE_PARENT_PAGE_ID`: optional approved parent.
- `AQABSI_CONFLUENCE_EMAIL` and `AQABSI_CONFLUENCE_API_TOKEN`: Cloud basic-auth pair.
- `AQABSI_CONFLUENCE_PAT`: Data Center bearer token.
- `AQABSI_CLICKUP_API_TOKEN`: ClickUp personal or OAuth access token.
- `AQABSI_CLICKUP_AUTH_MODE`: `personal` (default) or `oauth`.
- `AQABSI_CLICKUP_WORKSPACE_ID`: approved Workspace used for identity/destination checks.
- `AQABSI_CLICKUP_LIST_ID`: approved defect List.
- `AQABSI_OWNERSHIP_REGISTRY`: path to a reviewed JSON mapping that contains platform user IDs but no tokens.

Configuration may include non-secret provider URLs and destination IDs in team/project profiles later, but this delivery reads the explicit environment contract so a first-use check behaves consistently across Codex, Claude Code, Antigravity, CI, and terminals.

## Preflight behavior

`scripts/check_integrations.py` performs an offline check by default and a read-only API verification only with `--verify`. It returns human-readable guidance or JSON suitable for an agent. Missing setup identifies exact variable names and safe next steps; it never suggests pasting a token into chat.

The root skill runs preflight before source discovery. Missing publication integrations do not block code analysis, test design, authorized testing, or local artifact generation. They block only the affected live publication action.

## Publication behavior

`scripts/publish_artifacts.py` consumes generated draft files. Without `--execute`, it prints a sanitized publication plan and performs no network mutation. Live execution requires:

- `--execute`;
- a non-empty `--authorization-reference`;
- provider selection;
- complete verified provider configuration;
- `dry_run: true` source drafts;
- resolved destination IDs and resolved numeric ClickUp assignee IDs when assignment is requested.

Confluence Cloud uses the v2 pages API with Cloud basic authentication. Data Center uses the content REST API with a bearer PAT. The publisher searches the approved destination for the run page before create and updates the matching page when present. Markdown is converted to a safe, deterministic Confluence storage subset; raw HTML from the draft is escaped.

ClickUp searches the approved List for the AQABSI fingerprint before creating a confirmed defect. Existing fingerprints are skipped and returned as existing records. Only generated eligible tasks are accepted; unresolved assignees remain unassigned rather than guessed.

## Security and failure handling

- HTTPS is mandatory except explicit loopback-only test transport.
- Tokens are never included in CLI output, exceptions, artifacts, publication receipts, or test fixtures.
- Timeouts are bounded; TLS verification remains enabled; redirects to a different origin are rejected.
- `401`, `403`, validation errors, rate limits, and network failures are classified distinctly.
- Writes are not automatically retried. A publication receipt records each success, existing match, skip, and failure.
- A partial failure stops the affected provider and preserves completed external IDs.
- ClickUp receives sanitized defect metadata and accessible links, not raw restricted evidence.

## First-use experience

The README and skill show this sequence:

```text
install AQABSI
→ run integration preflight
→ configure missing variables through an approved secret channel
→ verify read-only access
→ run QA and generate drafts
→ review destinations, identities, and mutation plan
→ explicitly authorize and execute publication
```

Installation never claims Confluence or ClickUp is connected. A successful preflight identifies the authenticated account and destination without displaying credentials. ClickUp verification confirms that the configured List's Space belongs to the configured Workspace; Confluence verification confirms the Space and effective parent page used by the mutation.

## Verification

- Unit tests cover missing/invalid configuration, secret redaction, provider status classification, dry-run no-network behavior, authorization gating, Confluence create/update, ClickUp create/deduplication, and partial failure receipts using local fake HTTP services.
- Existing package, quality, and artifact-generation tests continue to pass.
- Package validation rejects credential templates containing secret values and ensures the root skill routes through integration preflight.
