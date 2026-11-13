#!/usr/bin/env python3
"""Plan or explicitly publish sanitized AQABSI drafts to Confluence and ClickUp."""

from __future__ import annotations

import argparse
import base64
import html
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence
from urllib.parse import quote, urlencode

from integration_config import (
    ClickUpConfig,
    ConfluenceConfig,
    load_integration_config,
    redact,
)
from integration_http import (
    HttpRequest,
    ProviderVerification,
    request_json,
    verify_clickup,
    verify_confluence,
)


CLICKUP_API_BASE = "https://api.clickup.com/api/v2"
FINGERPRINT = re.compile(r"^[a-f0-9]{64}$")
IDEMPOTENCY_KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$")
RUN_MARKER_ELEMENT = re.compile(
    r"<p>\s*AQABSI-RUN-ID:\s*([A-Za-z0-9][A-Za-z0-9._:-]{0,199})\s*</p>"
)


class PublicationError(ValueError):
    pass


@dataclass(frozen=True)
class MutationResult:
    provider: str
    status: str
    action: str
    external_id: str | None = None
    url: str | None = None
    fingerprint: str | None = None
    error: str | None = None
    reconciliation_required: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "provider": self.provider,
            "status": self.status,
            "action": self.action,
            "external_id": self.external_id,
            "url": self.url,
            "fingerprint": self.fingerprint,
            "error": self.error,
            "reconciliation_required": self.reconciliation_required,
        }


def _load_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PublicationError(f"Invalid draft {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PublicationError(f"Invalid draft {path}: root must be an object.")
    return value


def _validate_draft(draft: Mapping[str, object], provider: str) -> None:
    if draft.get("dry_run") is not True:
        raise PublicationError(f"{provider} input must have dry_run: true.")
    if draft.get("publication_requires_authorization") is not True:
        raise PublicationError(
            f"{provider} input must require publication authorization."
        )


def _require_authorization(reference: str | None) -> str:
    if not reference or not reference.strip():
        raise PublicationError(
            "Live publication requires a non-empty authorization reference."
        )
    return reference.strip()


def _require_verified(provider: str, result: ProviderVerification) -> None:
    if result.status != "verified":
        detail = "; ".join(result.errors) or result.status
        raise PublicationError(f"{provider} verification failed: {detail}")


def build_publication_plan(
    confluence_draft_path: Path | None,
    clickup_draft_path: Path | None,
    providers: Iterable[str],
    config: object | None = None,
    ownership_registry: Mapping[str, object] | Path | None = None,
) -> dict[str, object]:
    selected = tuple(dict.fromkeys(providers))
    if not selected:
        raise PublicationError("Select at least one publication provider.")
    plan: dict[str, object] = {
        "schema_version": "1.0",
        "dry_run": True,
        "network_mutations": 0,
        "providers": {},
    }
    provider_plan = plan["providers"]
    assert isinstance(provider_plan, dict)
    if "confluence" in selected:
        if confluence_draft_path is None:
            raise PublicationError("Confluence draft path is required.")
        draft = _load_json(confluence_draft_path)
        _validate_draft(draft, "Confluence")
        confluence_config = getattr(config, "confluence", None)
        configured_parent = getattr(confluence_config, "parent_page_id", None) or None
        draft_parent = draft.get("parent_page_id") or None
        if configured_parent and draft_parent and str(configured_parent) != str(draft_parent):
            raise PublicationError(
                "Confluence draft parent_page_id conflicts with the configured parent."
            )
        destination = {
            "deployment": getattr(confluence_config, "deployment", None) or None,
            "base_url": getattr(confluence_config, "base_url", None) or None,
            "space_id": getattr(confluence_config, "space_id", None) or None,
            "space_key": getattr(confluence_config, "space_key", None) or None,
            "parent_page_id": configured_parent or draft_parent,
        }
        body = draft.get("body")
        provider_plan["confluence"] = {
            "actions": 1,
            "operation": "create_or_update_by_run_id",
            "title": draft.get("suggested_title"),
            "idempotency_key": draft.get("idempotency_key"),
            "destination": destination,
            "deduplication": "not_checked",
            "body_preview": str(body)[:240] if isinstance(body, str) else None,
        }
    if "clickup" in selected:
        if clickup_draft_path is None:
            raise PublicationError("ClickUp draft path is required.")
        draft = _load_json(clickup_draft_path)
        _validate_draft(draft, "ClickUp")
        tasks = draft.get("tasks")
        if not isinstance(tasks, list):
            raise PublicationError("ClickUp draft tasks must be an array.")
        registry = _load_registry(ownership_registry)
        task_plan: list[dict[str, object]] = []
        for raw in tasks:
            if not isinstance(raw, dict):
                raise PublicationError("Every ClickUp task draft must be an object.")
            assignee = _resolved_assignee(raw, registry)
            task_plan.append(
                {
                    "name": raw.get("name"),
                    "fingerprint": raw.get("fingerprint"),
                    "owner_team": raw.get("owner_team"),
                    "resolved_assignee_id": assignee,
                    "assignment_status": "resolved" if assignee is not None else "unresolved",
                    "deduplication": "not_checked",
                }
            )
        clickup_config = getattr(config, "clickup", None)
        provider_plan["clickup"] = {
            "actions": len(tasks),
            "operation": "create_or_reuse_by_fingerprint",
            "fingerprints": [
                task.get("fingerprint")
                for task in tasks
                if isinstance(task, dict)
            ],
            "destination": {
                "auth_mode": getattr(clickup_config, "auth_mode", None) or None,
                "workspace_id": getattr(clickup_config, "workspace_id", None) or None,
                "list_id": getattr(clickup_config, "list_id", None) or None,
            },
            "tasks": task_plan,
        }
    return plan


def _inline_markup(value: str) -> str:
    escaped = html.escape(value, quote=False)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    return escaped


def markdown_to_storage(markdown: str) -> str:
    """Convert a safe report-oriented Markdown subset to Confluence storage XHTML."""
    lines = markdown.splitlines()
    output: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            level = len(heading.group(1))
            output.append(f"<h{level}>{_inline_markup(heading.group(2))}</h{level}>")
            index += 1
            continue
        if line.startswith("|" ) and index + 1 < len(lines) and re.match(
            r"^\|?\s*:?-{3,}", lines[index + 1]
        ):
            header_cells = [cell.strip() for cell in line.strip("|").split("|")]
            output.append("<table><tbody><tr>" + "".join(
                f"<th>{_inline_markup(cell)}</th>" for cell in header_cells
            ) + "</tr>")
            index += 2
            while index < len(lines) and lines[index].startswith("|"):
                cells = [cell.strip() for cell in lines[index].strip("|").split("|")]
                output.append("<tr>" + "".join(
                    f"<td>{_inline_markup(cell)}</td>" for cell in cells
                ) + "</tr>")
                index += 1
            output.append("</tbody></table>")
            continue
        if re.match(r"^-\s+", line):
            output.append("<ul>")
            while index < len(lines) and re.match(r"^-\s+", lines[index]):
                item = re.sub(r"^-\s+", "", lines[index])
                output.append(f"<li>{_inline_markup(item)}</li>")
                index += 1
            output.append("</ul>")
            continue
        if re.match(r"^\d+\.\s+", line):
            output.append("<ol>")
            while index < len(lines) and re.match(r"^\d+\.\s+", lines[index]):
                item = re.sub(r"^\d+\.\s+", "", lines[index])
                output.append(f"<li>{_inline_markup(item)}</li>")
                index += 1
            output.append("</ol>")
            continue
        output.append(f"<p>{_inline_markup(line)}</p>")
        index += 1
    return "".join(output)


def _confluence_headers(config: ConfluenceConfig) -> dict[str, str]:
    if config.deployment == "cloud":
        encoded = base64.b64encode(
            f"{config.email}:{config.api_token}".encode("utf-8")
        ).decode("ascii")
        return {"Authorization": f"Basic {encoded}"}
    return {"Authorization": f"Bearer {config.pat}"}


def _join_web_url(base_url: str, path: object) -> str | None:
    if not isinstance(path, str) or not path:
        return None
    if path.startswith("http://") or path.startswith("https://"):
        return path
    parsed = re.match(r"^(https?://[^/]+)", base_url)
    return (parsed.group(1) if parsed else base_url) + "/" + path.lstrip("/")


def _validate_confluence_publication(
    draft: Mapping[str, object], config: ConfluenceConfig
) -> tuple[str, str, str, str | None]:
    _validate_draft(draft, "Confluence")
    if config.errors:
        raise PublicationError(
            "Invalid Confluence configuration: " + "; ".join(config.errors)
        )
    if config.missing:
        raise PublicationError(
            "Missing Confluence configuration: " + ", ".join(config.missing)
        )
    title = draft.get("suggested_title")
    body = draft.get("body")
    idempotency_key = draft.get("idempotency_key")
    if not isinstance(title, str) or not title.strip():
        raise PublicationError("Confluence draft title is required.")
    if not isinstance(body, str):
        raise PublicationError("Confluence draft body must be Markdown text.")
    if not isinstance(idempotency_key, str) or not IDEMPOTENCY_KEY.fullmatch(
        idempotency_key
    ):
        raise PublicationError(
            "Confluence idempotency_key must be a stable printable run ID."
        )
    draft_parent = draft.get("parent_page_id")
    if draft_parent is not None and not isinstance(draft_parent, (str, int)):
        raise PublicationError("Confluence parent_page_id must be a string or integer.")
    normalized_draft_parent = str(draft_parent) if draft_parent not in {None, ""} else None
    if (
        config.parent_page_id
        and normalized_draft_parent
        and config.parent_page_id != normalized_draft_parent
    ):
        raise PublicationError(
            "Confluence draft parent_page_id conflicts with the configured parent."
        )
    effective_parent = config.parent_page_id or normalized_draft_parent
    return title, body, idempotency_key, effective_parent


def publish_confluence(
    draft: Mapping[str, object],
    config: ConfluenceConfig,
    authorization_reference: str | None,
    verification: ProviderVerification | None = None,
) -> MutationResult:
    _require_authorization(authorization_reference)
    title, body, idempotency_key, parent_id = _validate_confluence_publication(
        draft, config
    )
    if verification is None:
        verification = verify_confluence(config, parent_page_id=parent_id)
    _require_verified("Confluence", verification)
    verified_parent = verification.destination.get("parent_page_id")
    if (str(verified_parent) if verified_parent else None) != parent_id:
        raise PublicationError(
            "Confluence verification did not cover the effective parent page."
        )
    marker = f"AQABSI-RUN-ID: {idempotency_key}"
    storage = f"<p>{html.escape(marker)}</p>" + markdown_to_storage(body)
    headers = _confluence_headers(config)

    verified_space_key = verification.destination.get("key")
    if not isinstance(verified_space_key, str) or not verified_space_key:
        raise PublicationError("Confluence verification did not return a Space key.")
    cql = (
        f'space = "{verified_space_key}" AND type = page '
        f'AND text ~ "\\"{marker}\\""'
    )
    search_url = f"{config.base_url}/rest/api/content/search?" + urlencode(
        {"cql": cql, "expand": "version,body.storage,space"}
    )
    if config.deployment == "cloud":
        collection_url = f"{config.base_url}/api/v2/pages"
    else:
        collection_url = f"{config.base_url}/rest/api/content"

    search = request_json(
        HttpRequest("GET", search_url, headers=headers), config.secrets
    )
    if not search.ok:
        return MutationResult(
            "confluence", "failed", "search", error=search.error
        )
    if not isinstance(search.data, dict) or not isinstance(
        search.data.get("results"), list
    ):
        return MutationResult(
            "confluence",
            "failed",
            "search",
            error="Confluence search response did not contain a results array.",
        )
    results = search.data["results"]
    if any(not isinstance(item, dict) for item in results):
        return MutationResult(
            "confluence",
            "failed",
            "search",
            error="Confluence search returned a malformed page candidate.",
        )
    exact_matches: list[Mapping[str, object]] = []
    for candidate in results:
        candidate_body = candidate.get("body")
        storage_value = None
        if isinstance(candidate_body, dict):
            candidate_storage = candidate_body.get("storage")
            if isinstance(candidate_storage, dict):
                storage_value = candidate_storage.get("value")
        candidate_space = candidate.get("space")
        candidate_space_key = (
            candidate_space.get("key") if isinstance(candidate_space, dict) else None
        )
        if candidate_space_key != verified_space_key or not isinstance(
            storage_value, str
        ):
            return MutationResult(
                "confluence",
                "failed",
                "search",
                error="Confluence search candidate lacked exact Space/body evidence.",
            )
        marker_values = RUN_MARKER_ELEMENT.findall(storage_value)
        if marker_values != [idempotency_key]:
            return MutationResult(
                "confluence",
                "failed",
                "search",
                error="Confluence fuzzy search candidate did not contain the exact run marker.",
            )
        exact_matches.append(candidate)
    if len(exact_matches) > 1:
        return MutationResult(
            "confluence",
            "failed",
            "search",
            error="Confluence idempotency search returned multiple matching pages.",
        )
    existing = exact_matches[0] if exact_matches else None

    if config.deployment == "cloud":
        payload: dict[str, object] = {
            "spaceId": config.space_id,
            "status": "current",
            "title": title,
            "body": {"representation": "storage", "value": storage},
        }
        if parent_id:
            payload["parentId"] = str(parent_id)
        if isinstance(existing, dict):
            if not existing.get("id"):
                return MutationResult(
                    "confluence", "failed", "search", error="Confluence match has no page ID."
                )
            page_id = str(existing["id"])
            version = existing.get("version", {})
            version_number = version.get("number") if isinstance(version, dict) else None
            if not isinstance(version_number, int) or isinstance(version_number, bool):
                return MutationResult(
                    "confluence",
                    "failed",
                    "search",
                    error="Confluence match has no valid version number.",
                )
            payload["id"] = page_id
            payload["version"] = {"number": version_number + 1}
            response = request_json(
                HttpRequest("PUT", f"{collection_url}/{quote(page_id, safe='')}", headers, payload),
                config.secrets,
            )
            action = "update"
            status = "updated"
        else:
            response = request_json(
                HttpRequest("POST", collection_url, headers, payload), config.secrets
            )
            action = "create"
            status = "created"
    else:
        payload = {
            "type": "page",
            "title": title,
            "space": {"key": config.space_key},
            "body": {"storage": {"value": storage, "representation": "storage"}},
        }
        if parent_id:
            payload["ancestors"] = [{"id": str(parent_id)}]
        if isinstance(existing, dict):
            if not existing.get("id"):
                return MutationResult(
                    "confluence", "failed", "search", error="Confluence match has no page ID."
                )
            page_id = str(existing["id"])
            version = existing.get("version", {})
            version_number = version.get("number") if isinstance(version, dict) else None
            if not isinstance(version_number, int) or isinstance(version_number, bool):
                return MutationResult(
                    "confluence",
                    "failed",
                    "search",
                    error="Confluence match has no valid version number.",
                )
            payload["version"] = {"number": version_number + 1}
            response = request_json(
                HttpRequest("PUT", f"{collection_url}/{quote(page_id, safe='')}", headers, payload),
                config.secrets,
            )
            action = "update"
            status = "updated"
        else:
            response = request_json(
                HttpRequest("POST", collection_url, headers, payload), config.secrets
            )
            action = "create"
            status = "created"

    if not response.ok:
        return _write_failure("confluence", action, response)
    data = response.data if isinstance(response.data, dict) else {}
    if not data.get("id"):
        return MutationResult(
            "confluence",
            "unknown",
            action,
            error="Confluence write response did not contain a page ID.",
            reconciliation_required=True,
        )
    links = data.get("_links", {})
    webui = links.get("webui") if isinstance(links, dict) else None
    return MutationResult(
        "confluence",
        status,
        action,
        external_id=str(data.get("id")) if data.get("id") is not None else None,
        url=_join_web_url(config.base_url, webui),
    )


def _clickup_headers(config: ClickUpConfig) -> dict[str, str]:
    value = (
        f"Bearer {config.api_token}"
        if config.auth_mode == "oauth"
        else config.api_token
    )
    return {"Authorization": value}


def _load_registry(value: Mapping[str, object] | Path | None) -> Mapping[str, object]:
    if value is None:
        return {}
    registry = _load_json(value) if isinstance(value, Path) else value
    teams = registry.get("teams", {})
    if not isinstance(teams, dict):
        raise PublicationError("Ownership registry field 'teams' must be an object.")
    for team, mapping in teams.items():
        if not isinstance(team, str) or not isinstance(mapping, dict):
            raise PublicationError(
                "Every ownership registry team must map to an object."
            )
        if "clickup_user_id" in mapping:
            candidate = mapping.get("clickup_user_id")
            if isinstance(candidate, bool) or not str(candidate).isdigit():
                raise PublicationError(
                    f"Ownership registry clickup_user_id for team {team!r} must be numeric."
                )
    return registry


def _resolved_assignee(
    task: Mapping[str, object], registry: Mapping[str, object]
) -> int | None:
    candidate = task.get("assignee_id")
    if candidate is None:
        teams = registry.get("teams", {})
        owner = task.get("owner_team")
        if isinstance(teams, dict) and isinstance(owner, str):
            mapping = teams.get(owner)
            if isinstance(mapping, dict):
                if "clickup_user_id" not in mapping:
                    raise PublicationError(
                        f"Ownership registry team {owner!r} is missing clickup_user_id."
                    )
                candidate = mapping.get("clickup_user_id")
    if candidate is None or candidate == "":
        return None
    if isinstance(candidate, bool) or not str(candidate).isdigit():
        raise PublicationError("ClickUp assignee IDs must be numeric platform IDs.")
    return int(candidate)


def _prepare_clickup_publication(
    draft: Mapping[str, object],
    config: ClickUpConfig,
    ownership_registry: Mapping[str, object] | Path | None,
) -> list[tuple[Mapping[str, object], int | None]]:
    _validate_draft(draft, "ClickUp")
    if config.errors:
        raise PublicationError(
            "Invalid ClickUp configuration: " + "; ".join(config.errors)
        )
    if config.missing:
        raise PublicationError(
            "Missing ClickUp configuration: " + ", ".join(config.missing)
        )
    tasks = draft.get("tasks")
    if not isinstance(tasks, list):
        raise PublicationError("ClickUp draft tasks must be an array.")
    registry = _load_registry(ownership_registry)
    prepared: list[tuple[Mapping[str, object], int | None]] = []
    for raw in tasks:
        if not isinstance(raw, dict):
            raise PublicationError("Every ClickUp task draft must be an object.")
        fingerprint = raw.get("fingerprint")
        if not isinstance(fingerprint, str) or not FINGERPRINT.fullmatch(fingerprint):
            raise PublicationError("Every ClickUp task requires a SHA-256 fingerprint.")
        if raw.get("action") != "create_or_update_by_fingerprint":
            raise PublicationError("Unsupported ClickUp draft action.")
        prepared.append((raw, _resolved_assignee(raw, registry)))
    return prepared


def _priority(severity: object) -> int | None:
    return {"critical": 1, "urgent": 1, "high": 2, "medium": 3, "low": 4}.get(
        str(severity).lower()
    )


def _write_failure(
    provider: str,
    action: str,
    response: object,
    *,
    fingerprint: str | None = None,
    error: str | None = None,
) -> MutationResult:
    category = getattr(response, "category", "invalid_response")
    ambiguous = category in {"unreachable", "provider_error", "invalid_response"}
    return MutationResult(
        provider,
        "unknown" if ambiguous else "failed",
        action,
        fingerprint=fingerprint,
        error=error or getattr(response, "error", None) or "Provider write failed.",
        reconciliation_required=ambiguous,
    )


def _find_fingerprint(tasks: Sequence[object], fingerprint: str) -> Mapping[str, object] | None:
    marker = f"AQABSI-FINGERPRINT: {fingerprint}"
    for raw in tasks:
        if not isinstance(raw, dict):
            continue
        if marker in str(raw.get("description", "")):
            return raw
    return None


def _list_clickup_tasks(
    config: ClickUpConfig, headers: Mapping[str, str]
) -> tuple[list[object], MutationResult | None]:
    collected: list[object] = []
    for page in range(50):
        query = urlencode(
            {"include_closed": "true", "page": page, "subtasks": "true"}
        )
        url = (
            f"{CLICKUP_API_BASE}/list/{quote(config.list_id, safe='')}/task?{query}"
        )
        response = request_json(HttpRequest("GET", url, headers=headers), config.secrets)
        if not response.ok:
            return [], MutationResult(
                "clickup", "failed", "search", error=response.error
            )
        if not isinstance(response.data, dict) or "tasks" not in response.data:
            return [], MutationResult(
                "clickup",
                "failed",
                "search",
                error="ClickUp search response did not contain a tasks array.",
            )
        data = response.data
        tasks = data["tasks"]
        if not isinstance(tasks, list):
            return [], MutationResult(
                "clickup", "failed", "search", error="ClickUp returned invalid tasks data."
            )
        for task in tasks:
            if (
                not isinstance(task, dict)
                or not task.get("id")
                or not isinstance(task.get("description"), str)
            ):
                return [], MutationResult(
                    "clickup",
                    "failed",
                    "search",
                    error="ClickUp search returned a malformed task entry.",
                )
        collected.extend(tasks)
        if data.get("last_page") is True or not tasks:
            return collected, None
    return [], MutationResult(
        "clickup",
        "failed",
        "search",
        error="ClickUp deduplication search was incomplete at the safety page limit.",
    )


def publish_clickup(
    draft: Mapping[str, object],
    config: ClickUpConfig,
    authorization_reference: str | None,
    ownership_registry: Mapping[str, object] | Path | None = None,
    verification: ProviderVerification | None = None,
) -> list[MutationResult]:
    _require_authorization(authorization_reference)
    prepared = _prepare_clickup_publication(draft, config, ownership_registry)

    if verification is None:
        verification = verify_clickup(config, api_base=CLICKUP_API_BASE)
    _require_verified("ClickUp", verification)

    headers = _clickup_headers(config)
    existing_tasks, search_error = _list_clickup_tasks(config, headers)
    if search_error:
        return [search_error]
    results: list[MutationResult] = []
    for task, assignee in prepared:
        fingerprint = str(task["fingerprint"])
        existing = _find_fingerprint(existing_tasks, fingerprint)
        if existing is not None:
            if not existing.get("id"):
                results.append(
                    MutationResult(
                        "clickup",
                        "failed",
                        "search",
                        fingerprint=fingerprint,
                        error="ClickUp fingerprint match did not contain a task ID.",
                    )
                )
                break
            results.append(
                MutationResult(
                    "clickup",
                    "existing",
                    "reuse",
                    external_id=str(existing.get("id")) if existing.get("id") else None,
                    url=str(existing.get("url")) if existing.get("url") else None,
                    fingerprint=fingerprint,
                )
            )
            continue
        description = str(task.get("description_markdown", "")).rstrip()
        description += f"\n\nAQABSI-FINGERPRINT: {fingerprint}"
        payload: dict[str, object] = {
            "name": str(task.get("name", "AQABSI confirmed defect")),
            "description": description,
            "tags": ["aqabsi", "defect"],
            "priority": _priority(task.get("severity")),
        }
        if assignee is not None:
            payload["assignees"] = [assignee]
        url = f"{CLICKUP_API_BASE}/list/{quote(config.list_id, safe='')}/task"
        response = request_json(
            HttpRequest("POST", url, headers=headers, body=payload), config.secrets
        )
        if not response.ok:
            results.append(
                _write_failure(
                    "clickup", "create", response, fingerprint=fingerprint
                )
            )
            break
        data = response.data if isinstance(response.data, dict) else {}
        if not data.get("id"):
            results.append(
                MutationResult(
                    "clickup",
                    "unknown",
                    "create",
                    fingerprint=fingerprint,
                    error="ClickUp create response did not contain a task ID.",
                    reconciliation_required=True,
                )
            )
            break
        created = {
            "id": data.get("id"),
            "url": data.get("url"),
            "description": description,
        }
        existing_tasks.append(created)
        results.append(
            MutationResult(
                "clickup",
                "created",
                "create",
                external_id=str(data.get("id")) if data.get("id") else None,
                url=str(data.get("url")) if data.get("url") else None,
                fingerprint=fingerprint,
            )
        )
    return results


def _write_output(payload: object, output: Path | None) -> None:
    serialized = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    print(serialized, end="")
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        try:
            with output.open("x", encoding="utf-8") as handle:
                handle.write(serialized)
        except FileExistsError as exc:
            raise PublicationError(f"Receipt already exists: {output}") from exc


def _ensure_output_available(output: Path | None) -> None:
    if output is not None and output.exists():
        raise PublicationError(f"Receipt already exists: {output}")


def _receipt(
    status: str,
    authorization: str,
    mutations: Sequence[MutationResult],
    error: str | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": "1.0",
        "dry_run": False,
        "status": status,
        "authorization_reference": authorization,
        "mutations": [item.to_dict() for item in mutations],
    }
    if error:
        payload["error"] = error
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", action="append", choices=("confluence", "clickup"))
    parser.add_argument("--confluence-draft", type=Path)
    parser.add_argument("--clickup-draft", type=Path)
    parser.add_argument("--ownership-registry", type=Path)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--authorization-reference")
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args(argv)

    selected = tuple(args.provider or ())
    if not selected:
        selected = tuple(
            provider
            for provider, path in (
                ("confluence", args.confluence_draft),
                ("clickup", args.clickup_draft),
            )
            if path is not None
        )
    config = load_integration_config(os.environ)
    mutations: list[MutationResult] = []
    authorization = ""
    try:
        _ensure_output_available(args.receipt)
        registry_path = args.ownership_registry
        if registry_path is None and os.environ.get("AQABSI_OWNERSHIP_REGISTRY", "").strip():
            registry_path = Path(os.environ["AQABSI_OWNERSHIP_REGISTRY"].strip())
        plan = build_publication_plan(
            args.confluence_draft,
            args.clickup_draft,
            selected,
            config,
            registry_path,
        )
        if not args.execute:
            _write_output(redact(plan, config.secrets), args.receipt)
            return 0
        if not args.provider:
            raise PublicationError("Live mode requires explicit --provider selection.")
        authorization = _require_authorization(args.authorization_reference)
        confluence_draft = (
            _load_json(args.confluence_draft) if "confluence" in selected else None
        )
        clickup_draft = (
            _load_json(args.clickup_draft) if "clickup" in selected else None
        )
        verifications: dict[str, ProviderVerification] = {}
        confluence_parent: str | None = None
        if confluence_draft is not None:
            _, _, _, confluence_parent = _validate_confluence_publication(
                confluence_draft, config.confluence
            )
        if clickup_draft is not None:
            _prepare_clickup_publication(clickup_draft, config.clickup, registry_path)
        if confluence_draft is not None:
            verifications["confluence"] = verify_confluence(
                config.confluence, parent_page_id=confluence_parent
            )
            _require_verified("Confluence", verifications["confluence"])
        if clickup_draft is not None:
            verifications["clickup"] = verify_clickup(
                config.clickup, api_base=CLICKUP_API_BASE
            )
            _require_verified("ClickUp", verifications["clickup"])
        if "confluence" in selected:
            mutations.append(
                publish_confluence(
                    confluence_draft,
                    config.confluence,
                    authorization,
                    verification=verifications["confluence"],
                )
            )
            if mutations[-1].status in {"failed", "unknown"}:
                status = "partial_failure"
                safe_receipt = redact(
                    _receipt(status, authorization, mutations), config.secrets
                )
                _write_output(safe_receipt, args.receipt)
                return 4
        if "clickup" in selected:
            mutations.extend(
                publish_clickup(
                    clickup_draft,
                    config.clickup,
                    authorization,
                    registry_path,
                    verification=verifications["clickup"],
                )
            )
        status = (
            "partial_failure"
            if any(item.status in {"failed", "unknown"} for item in mutations)
            else "completed"
        )
        receipt = _receipt(status, authorization, mutations)
        safe_receipt = redact(receipt, config.secrets)
        _write_output(safe_receipt, args.receipt)
        return 4 if status == "partial_failure" else 0
    except PublicationError as exc:
        safe_error = str(redact(str(exc), config.secrets))
        if mutations:
            safe_receipt = redact(
                _receipt(
                    "partial_failure",
                    authorization,
                    mutations,
                    error=safe_error,
                ),
                config.secrets,
            )
            try:
                _write_output(safe_receipt, args.receipt)
            except PublicationError:
                pass
            print(
                f"AQABSI publication stopped after partial success: {safe_error}",
                file=sys.stderr,
            )
            return 4
        print(f"AQABSI publication blocked: {safe_error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
