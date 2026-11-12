# Output Contract

## Local artifacts

The canonical input is a sanitized run manifest conforming to `../schemas/test-run.schema.json`. Generate:

- `sanitized-run.json` — machine-readable source of report truth.
- `qa-report.md` — human review report.
- `test-cases.csv` — portable tabular export.
- `test-cases.xlsx` — formatted spreadsheet with filter, frozen header, status validation, and wrapped cells.
- `confluence-draft.json` — unpublished report draft.
- `clickup-drafts.json` — deduplicated confirmed-defect drafts only.

## QA report minimum

- Run/ticket, dates, source commit/MR, tester/agent, target and environment.
- Scope, requirements/risks, selected layers, tools/versions, and test data policy.
- Status summary and traceable case details.
- Confirmed defects and separate flaky/environment/blocked outcomes.
- Sanitized evidence and cleanup state.
- Limitations, untested risk, assumptions, and residual risk.

## Spreadsheet columns

Test Case ID, Module, Feature, Layer, Scenario, Preconditions, Test Steps, Test Data, Expected Result, Actual Result, Status, Priority, Severity, Evidence, Owner Team, and Notes.

## Defect draft minimum

Summary/impact, test case and run IDs, source commit/MR, environment, reproducible steps, expected/actual, sanitized evidence, severity rationale, owner team, stable fingerprint, and unresolved assignee reference.

Publishing and assignment follow `integrations.md`; generated payloads are drafts, not proof of external creation.
