# Testing Module — Data & Persistence

Index domain data. Detail di `knowledge/data/<file>.md`.

| Modul | Cakupan |
|---|---|
| `data-crud.md` | Create/read/update/delete |
| `data-integrity.md` | Constraints, nullability |
| `data-relationship.md` | Foreign key, cascade, orphan |
| `data-transaction.md` | Commit, rollback, atomicity (ACID) |
| `data-soft-delete.md` | Soft delete, visibility |
| `data-duplicate.md` | Unique constraints |
| `data-migration.md` | Schema/data migration |
| `data-consistency.md` | API vs DB vs cache |
| `data-concurrency.md` | Concurrent updates, isolation |
| `data-seeding.md` | Test fixtures, test data |

`data-transaction` wajib muat commit/rollback; `data-concurrency` muat lost update/race.
