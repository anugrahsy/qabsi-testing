# GitLab CI Orchestration

QABSI plans and reports testing; deterministic runners perform it. A practical GitLab flow is:

```text
Merge request or scheduled pipeline
→ change-impact inventory
→ static/unit/component/integration/contract jobs
→ deploy isolated review environment when available
→ API/E2E/accessibility/security jobs authorized for that environment
→ normalize results into test-run JSON
→ generate sanitized artifacts
→ human/authorized publication gate
```

## Pipeline rules

- Merge requests run fast risk-matched checks and produce JUnit/coverage/evidence artifacts.
- Default-branch pipelines run broader regression after merge.
- Scheduled pipelines may run longer security, compatibility, or performance suites within approved scope.
- Production publication/deployment is never inferred from a successful QA artifact job.
- Protect credentials with masked CI variables; do not echo them or store them in artifacts.
- Preserve runner exit codes separately from test verdicts so environment failures are not product failures.

Use `assets/templates/gitlab-ci.qabsi.example.yml` as a blueprint. Adapt runner images, commands, and dependencies to the actual repositories; never paste placeholder commands into a live pipeline unchanged.
