# Runtime Exploration

Runtime exploration is the evidence-collection phase of vibe testing: reconstruct the as-is product from live application observation plus source code, instead of code alone. The PRD remains the authoritative reference that test cases trace to.

## When to run

- The `analyze-testing` mode is selected and the target UI is reachable through a browser.
- A PRD is missing, stale, or contradicted by the running application.

## Preconditions

- Read [execution-safety.md](execution-safety.md) and [auth-adapter.md](auth-adapter.md) first.
- Confirm scope, target environment, allowed accounts/roles, evidence location, and prohibited actions.
- Confirm the target FE/UI is browser-accessible. If it is not, record runtime exploration as `blocked` and fall back to source-only reconstruction.

## Steps

1. Open the target application with browser automation when available, otherwise a manual browser session with the approved profile.
2. Authenticate per [auth-adapter.md](auth-adapter.md) (`web_login`, `bearer_token`, `basic_auth`, or SSO). For SSO with a self-signed or internal-CA certificate, follow the documented browser trust steps (Advanced → Proceed) without disabling TLS validation.
3. Walk the primary menus and flows: happy path, safe error path, and in-scope state transitions.
4. Record observed behavior, errors, and state. Label each observation `verified`, `inferred`, `assumption`, `open question`, or `recommendation`.
5. Capture sanitized evidence: screenshots (PII masked), network request method/path/status, and console errors. Record timestamp, route/URL, and correlation ID when available.
6. Log observations as evidence sources (`SRC-...`) so requirements can reference executed runtime evidence.

## Safety and privacy

- Do not capture sensitive data or PII; mask or crop screenshots and never save cookies, tokens, sessions, or secrets.
- Respect scope and authorization; do not explore flows or roles outside the approved boundary.
- Do not perform destructive or mutating actions without explicit authorization and a cleanup plan.
- Keep evidence inside the approved workspace; do not upload source, screenshots, or internal data to external services.

## Output

- A runtime exploration note mapping observed behavior to routes/flows and evidence files.
- Discrepancies between UI, API, and code recorded as contradictions, risks, or open questions.
- Evidence sources that feed the PRD evidence hierarchy (`executed runtime evidence`) in [prd-standard.md](prd-standard.md).
