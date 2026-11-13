# Isolated AQABSI Web E2E Harness

This template is a contract, not an auto-installer. Copy it into a separate approved QA harness or CI job; do not add dependencies to the target application. Use Node `>=22.20.0`, set `E2E_TELEMETRY_DISABLED=1`, and target only an approved local/review/staging URL.

Required inputs are the target URL, environment, approved test identities through opaque secret references, allowed data mutations, cleanup, evidence directory, rate ceiling, and stop conditions. Exact locator tests must work without a remote model. Agentic model calls remain disabled unless BSI approves an internal endpoint and data flow.

The default is `dry_run: true`. A dry run validates configuration and resolves no credentials. Production, load, destructive, and active security execution are outside this harness.
