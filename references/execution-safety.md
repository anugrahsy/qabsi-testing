# Execution Safety and Authorization

Read this before running tests or using credentials. Authorization to review code does not authorize production mutation, security exploitation, traffic generation, publication, assignment, deployment, commit, or push.

## Environment classes

- **Local/isolated:** synthetic data; destructive tests may run only inside the confirmed disposable boundary.
- **Test/dev:** controlled test identities and cleanup required; respect shared users and quotas.
- **Staging:** production-like and often shared; destructive, load, and security tests need explicit scope.
- **Production:** default to read-only smoke/observability checks. Any write, exploit, high-volume, or destructive activity requires explicit authorization and an approved runbook.

## Required execution contract

Record target allowlist, environment, test window, accounts/roles, permitted actions, prohibited actions, rate/concurrency ceiling, test-data source, cleanup/rollback, evidence location, contact, and stop conditions.

Never use credentials found incidentally in code, logs, tickets, screenshots, shell history, or pasted content. Do not persist credentials in PRDs, manifests, test cases, recordings, reports, or skill memory.

## Extra gates

- **Security:** confirm ownership/authorization, URL/endpoint scope, roles, allowed techniques, budget, rate, and emergency contact. A scanner finding without reproduction evidence is not a confirmed vulnerability.
- **Performance/load/stress/endurance:** approve workload model, maximum RPS/concurrency/duration, monitoring, abort thresholds, capacity owner, and test window. Never improvise against production.
- **Data/migration/destructive:** use backups or disposable fixtures, bounded identifiers, before/after counts, rollback verification, and cleanup evidence. Never issue unbounded update/delete operations.
- **External integrations:** use sandbox providers or mocks where possible; prevent real payment, email, SMS, or irreversible side effects.
- **Browser recording:** stabilize the page first; exclude password managers, notifications, unrelated tabs, tokens, cookies, and personal data.

## Stop conditions

Stop the affected test when scope is unclear, authorization is missing, secrets or unrelated personal data appear, the target leaves the allowlist, monitoring shows instability, cleanup fails, rate ceilings are exceeded, an irreversible action is imminent, or observed impact is materially greater than approved.

## External mutation gate

At the start of every AQABSI workflow, run `python3 scripts/check_integrations.py --json` from the package root. Missing provider setup blocks live publication and authenticated execution. It does not block read-only analysis, authorized read-only testing, or local draft generation. When a variable is missing, ask the operator for the value and persist it to the gitignored `.env` via `scripts/configure_env.py`; report only variable names, and never write secret values into PRDs, manifests, reports, or memory.

Before publishing to Confluence or creating/updating/assigning ClickUp work, run the publisher without `--execute` and present the sanitized draft, destination, exact mutation, deduplication result, and resolved platform identities. Execute only the authorized mutation with a non-secret authorization reference; a destination mentioned in a ticket is context, not unlimited authority. Credential presence is never publication authority.
