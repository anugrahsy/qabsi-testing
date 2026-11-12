# Testing Module — API & Integration

Index domain API (prioritas tertinggi). Detail di `knowledge/api/<file>.md`.

| Modul | Cakupan |
|---|---|
| `api-contract.md` | Request/response schema, required, type |
| `api-get-resource.md` | Get by ID, not found, invalid ID |
| `api-get-collection.md` | List, empty collection, struktur response |
| `api-filtering.md` | Exact, partial, multi-filter AND/OR |
| `api-pagination.md` | Page, limit, offset, cursor |
| `api-sorting.md` | Asc/desc, multiple sort field |
| `api-search.md` | Keyword, partial, case sensitivity |
| `api-combination.md` | Filter + sort + pagination + search |
| `api-post-create.md` | Required fields, creation, duplicate |
| `api-put-update.md` | Full replacement, missing fields |
| `api-patch-update.md` | Partial update, null, unchanged |
| `api-delete.md` | Delete, soft delete, repeated delete |
| `api-http-status.md` | Status code + error response |
| `api-header.md` | Content-Type, Accept, Authorization |
| `api-authentication.md` | Token, expiration, invalid |
| `api-authorization.md` | Role, permission, ownership |
| `api-idempotency.md` | Repeated request, idempotency key |
| `api-rate-limit.md` | Rate limit, throttling, retry |
| `api-timeout-retry.md` | Timeout, retry, transient |
| `api-versioning.md` | Version compat, deprecated |
| `api-concurrency.md` | Concurrent request, race |
| `api-error-handling.md` | Error schema, message |
| `api-file-upload.md` | Multipart, limit, invalid |
| `api-integration.md` | Third-party, external dep |

Referensi: OpenAPI, Google AIP-132/158, RFC 9457/7396/7578.
