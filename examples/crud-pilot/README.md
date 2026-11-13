# Synthetic CRUD Forward-Test Pilot

This example models a generic BSI-style service/endpoint resource without private source or business data. It demonstrates adaptive PRD composition and professional cases for GET collection/detail, POST, PUT, PATCH, DELETE, validation, duplicates, transactions, UUID lookup, role-based access, concurrency, audit, and cleanup.

All cases intentionally remain `not_run`. The files prove generation, validation, sanitization, and coverage behavior; they do not claim a deployed application passed. Replace synthetic sources and requirements only after selecting an authorized real module and pinning its repository revision.

Validate and generate:

```bash
python3 scripts/validate_quality.py examples/crud-pilot/prd-crud.json --kind prd
python3 scripts/validate_quality.py examples/crud-pilot/test-run.json --kind test-run
python3 scripts/generate_artifacts.py examples/crud-pilot/test-run.json .aqabsi-output/crud-pilot
```
