# Evidence, Redaction, and Privacy

Evidence must make a result reproducible without turning QA artifacts into a new data leak.

## Evidence by layer

- Unit/component/integration: command, tool/version, exit code, relevant assertion, and artifact path.
- API/contract: sanitized request shape, response status/body fragment, correlation ID, and schema result.
- Browser/E2E/manual: numbered steps, viewport/browser, screenshot/video, console/network observation, and timestamp.
- Performance: workload model, duration, concurrency/RPS, percentiles, errors, resource metrics, and abort threshold.
- Security: authorized scope, exact reproduction, sanitized proof, impact, affected role/resource, and remediation verification.

## Redact before persistence or publication

Passwords, bearer/API/refresh/reset tokens, cookies, session IDs, private keys, secrets, connection strings, internal credentials, and sensitive headers must be removed. Minimize names, emails, phone numbers, identifiers, financial/health/education data, source snippets, internal URLs, and database records to what is necessary for reproduction.

Prefer synthetic test data. When personal data is unavoidable, follow the authorized storage, access, retention, and deletion policy. Do not upload an artifact merely because a connector accepts it.

## Evidence integrity

- Preserve original local evidence only in an approved restricted location.
- Publish sanitized derivatives.
- Record capture time, run ID, test-case ID, source commit, environment, and tool.
- Do not edit evidence in a way that changes the represented outcome.
- Mark unavailable or incomplete evidence; never create substitute evidence.

The artifact generator performs baseline secret redaction. Human review is still required because context-specific personal and confidential data cannot be recognized perfectly.
