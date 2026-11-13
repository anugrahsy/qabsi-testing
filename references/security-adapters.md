# AQABSI Security Adapter Contract

Security work is permissioned by level. The default is read-only source triage. `dry_run: true` means no target request, scan, model call, source upload, publication, or ticket mutation occurred.

| Level | Required authority | Allowed engine | Output classification |
|---|---|---|---|
| Guidance/source triage | Supplied repository read scope | Cloudflare security-audit guidance | `needs_validation`, `hardening_recommendation`, or `untested` |
| Full source audit | Explicit comprehensive audit request and isolated workspace | Cloudflare six-phase workflow | Independently verified structured findings |
| Local/CI scan | Explicit scan authorization, disposable checkout, approved Docker/model budget | Strix OSS/local skills | `confirmed`, `needs_validation`, `rejected`, or `hardening_recommendation` |
| Staging active validation | Written target, technique, account, rate, data, cleanup, expiry, and stop contact | Selected Strix web/API skills | Reproduced bounded findings |

Production active testing and managed Strix cloud are disabled by default. Never upload BSI source, prompts containing source, internal URLs, evidence, identities, or findings to an external model/service without information-security and data-governance approval.

## Authorization gate

An active authorization record must include approver identity, authority reference, target allowlist, environment, allowed techniques, accounts/roles, rate ceiling, data/cleanup rules, start/expiry, and revocation/stop contact. Missing or expired fields fail closed.

## Normalization

Normalize every result with `schemas/security-finding.schema.json`. Scanner output alone is not `confirmed`; reproduce or independently verify the data flow and impact. Only `confirmed` findings may receive defect severity and a ClickUp defect draft. CVSS 4.0 is recorded only when supported; BSI business priority remains `unmapped` until an approved matrix exists.

## CI safety

Start with `AQABSI_SECURITY_DRY_RUN=true`. Resolve the real merge-request target branch, preserve scanner completion/budget status, sanitize artifacts, verify internal TLS with an approved CA bundle, and never disable certificate validation. The example template is opt-in and manual.
