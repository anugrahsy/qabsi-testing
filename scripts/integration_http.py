#!/usr/bin/env python3
"""Safe HTTP boundary for AQABSI integration verification and publishing."""

from __future__ import annotations

import base64
import json
import socket
from dataclasses import dataclass, field
from typing import Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from integration_config import ClickUpConfig, ConfluenceConfig, LOOPBACK_HOSTS, TargetAuthConfig, redact


CLICKUP_API_BASE = "https://api.clickup.com/api/v2"
MAX_RESPONSE_BYTES = 1_048_576


class CrossOriginRedirectError(RuntimeError):
    pass


def _origin(url: str) -> tuple[str, str, int | None]:
    parsed = urlsplit(url)
    return parsed.scheme.lower(), (parsed.hostname or "").lower(), parsed.port


class SameOriginRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        absolute = urljoin(req.full_url, newurl)
        if _origin(req.full_url) != _origin(absolute):
            raise CrossOriginRedirectError("Cross-origin redirect blocked.")
        return super().redirect_request(req, fp, code, msg, headers, absolute)


@dataclass(frozen=True)
class HttpRequest:
    method: str
    url: str
    headers: Mapping[str, str] = field(default_factory=dict)
    body: object | None = None
    timeout: float = 8.0


@dataclass(frozen=True)
class HttpResponse:
    ok: bool
    status_code: int | None
    data: object | None
    category: str
    error: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "status_code": self.status_code,
            "data": self.data,
            "category": self.category,
            "error": self.error,
        }


@dataclass(frozen=True)
class ProviderVerification:
    status: str
    identity: Mapping[str, object] = field(default_factory=dict)
    destination: Mapping[str, object] = field(default_factory=dict)
    errors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "identity": dict(self.identity),
            "destination": dict(self.destination),
            "errors": list(self.errors),
        }


def _decode_body(raw: bytes) -> object:
    text = raw.decode("utf-8", errors="replace")
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"message": text}


def _category(status_code: int) -> str:
    if status_code == 401:
        return "unauthorized"
    if status_code == 403:
        return "forbidden"
    if status_code == 429:
        return "rate_limited"
    if 300 <= status_code < 400:
        return "redirect_blocked"
    if 400 <= status_code < 500:
        return "validation_error"
    return "provider_error"


def request_json(request: HttpRequest, secrets: Iterable[str]) -> HttpResponse:
    secret_values = tuple(value for value in secrets if value)
    body = None
    headers = {"Accept": "application/json", **dict(request.headers)}
    if request.body is not None:
        body = json.dumps(request.body, ensure_ascii=False).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")
    urllib_request = Request(
        request.url,
        data=body,
        headers=headers,
        method=request.method.upper(),
    )
    opener = build_opener(SameOriginRedirectHandler())
    try:
        with opener.open(urllib_request, timeout=request.timeout) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                return HttpResponse(
                    False,
                    response.status,
                    None,
                    "invalid_response",
                    "Provider response exceeded the safe size limit.",
                )
            data = redact(_decode_body(raw), secret_values)
            return HttpResponse(True, response.status, data, "ok")
    except CrossOriginRedirectError:
        return HttpResponse(
            False,
            None,
            None,
            "redirect_blocked",
            "Cross-origin redirect blocked.",
        )
    except HTTPError as exc:
        raw = exc.read(MAX_RESPONSE_BYTES)
        data = redact(_decode_body(raw), secret_values)
        return HttpResponse(
            False,
            exc.code,
            data,
            _category(exc.code),
            f"Provider returned HTTP {exc.code}.",
        )
    except (URLError, TimeoutError, socket.timeout, OSError):
        return HttpResponse(
            False,
            None,
            None,
            "unreachable",
            "Provider could not be reached within the bounded request.",
        )


def _failed_verification(response: HttpResponse) -> ProviderVerification:
    return ProviderVerification(
        status=response.category,
        errors=(response.error or "Provider verification failed.",),
    )

def _mapping(value: object) -> Mapping[str, object]:
    return value if isinstance(value, dict) else {}


def _present_identifier(value: object) -> bool:
    return isinstance(value, (str, int)) and not isinstance(value, bool) and bool(str(value))


def _invalid_response(message: str) -> ProviderVerification:
    return ProviderVerification("invalid_response", errors=(message,))


def verify_confluence(
    config: ConfluenceConfig, parent_page_id: str | None = None
) -> ProviderVerification:
    if config.errors:
        return ProviderVerification("invalid", errors=config.errors)
    if config.missing:
        return ProviderVerification("missing", errors=config.missing)

    if config.deployment == "cloud":
        credentials = base64.b64encode(
            f"{config.email}:{config.api_token}".encode("utf-8")
        ).decode("ascii")
        headers = {"Authorization": f"Basic {credentials}"}
        destination_url = f"{config.base_url}/api/v2/spaces/{quote(config.space_id, safe='')}"
    else:
        headers = {"Authorization": f"Bearer {config.pat}"}
        destination_url = f"{config.base_url}/rest/api/space/{quote(config.space_key, safe='')}"

    identity_response = request_json(
        HttpRequest(
            method="GET",
            url=f"{config.base_url}/rest/api/user/current",
            headers=headers,
        ),
        config.secrets,
    )
    if not identity_response.ok:
        return _failed_verification(identity_response)
    destination_response = request_json(
        HttpRequest(method="GET", url=destination_url, headers=headers),
        config.secrets,
    )
    if not destination_response.ok:
        return _failed_verification(destination_response)

    effective_parent = parent_page_id or config.parent_page_id
    parent_data: Mapping[str, object] = {}
    if effective_parent:
        if config.deployment == "cloud":
            parent_url = (
                f"{config.base_url}/api/v2/pages/"
                f"{quote(effective_parent, safe='')}"
            )
        else:
            parent_url = (
                f"{config.base_url}/rest/api/content/"
                f"{quote(effective_parent, safe='')}?expand=space"
            )
        parent_response = request_json(
            HttpRequest(method="GET", url=parent_url, headers=headers), config.secrets
        )
        if not parent_response.ok:
            return _failed_verification(parent_response)
        parent_data = _mapping(parent_response.data)

    identity_data = _mapping(identity_response.data)
    destination_data = _mapping(destination_response.data)
    identity_id = identity_data.get("accountId") or identity_data.get("username")
    if not _present_identifier(identity_id):
        return _invalid_response("Confluence identity response did not contain an account ID.")
    if config.deployment == "cloud":
        destination_id = destination_data.get("id")
        if not _present_identifier(destination_id):
            return _invalid_response("Confluence Space response did not contain an ID.")
        if str(destination_id) != config.space_id:
            return ProviderVerification(
                "destination_mismatch",
                errors=("Confluence returned a different Space than configured.",),
            )
        if effective_parent and (
            str(parent_data.get("id")) != effective_parent
            or str(parent_data.get("spaceId")) != config.space_id
        ):
            return ProviderVerification(
                "destination_mismatch",
                errors=("Confluence parent page is outside the configured Space.",),
            )
    else:
        destination_key = destination_data.get("key")
        if not _present_identifier(destination_key):
            return _invalid_response("Confluence Space response did not contain a key.")
        if str(destination_key) != config.space_key:
            return ProviderVerification(
                "destination_mismatch",
                errors=("Confluence returned a different Space than configured.",),
            )
        parent_space_key = _mapping(parent_data.get("space")).get("key")
        if effective_parent and (
            str(parent_data.get("id")) != effective_parent
            or str(parent_space_key) != config.space_key
        ):
            return ProviderVerification(
                "destination_mismatch",
                errors=("Confluence parent page is outside the configured Space.",),
            )
    return ProviderVerification(
        status="verified",
        identity={
            "id": identity_id,
            "display_name": identity_data.get("displayName"),
        },
        destination={
            "id": destination_data.get("id"),
            "key": destination_data.get("key"),
            "name": destination_data.get("name"),
            "parent_page_id": effective_parent or None,
        },
    )


def verify_clickup(
    config: ClickUpConfig, api_base: str | None = None
) -> ProviderVerification:
    if config.errors:
        return ProviderVerification("invalid", errors=config.errors)
    if config.missing:
        return ProviderVerification("missing", errors=config.missing)
    resolved_api_base = api_base or CLICKUP_API_BASE
    authorization = (
        f"Bearer {config.api_token}"
        if config.auth_mode == "oauth"
        else config.api_token
    )
    headers = {"Authorization": authorization}
    user_response = request_json(
        HttpRequest(method="GET", url=f"{resolved_api_base}/user", headers=headers),
        config.secrets,
    )
    if not user_response.ok:
        return _failed_verification(user_response)
    list_response = request_json(
        HttpRequest(
            method="GET",
            url=f"{resolved_api_base}/list/{quote(config.list_id, safe='')}",
            headers=headers,
        ),
        config.secrets,
    )
    if not list_response.ok:
        return _failed_verification(list_response)
    spaces_response = request_json(
        HttpRequest(
            method="GET",
            url=(
                f"{resolved_api_base}/team/"
                f"{quote(config.workspace_id, safe='')}/space?archived=true"
            ),
            headers=headers,
        ),
        config.secrets,
    )
    if not spaces_response.ok:
        return _failed_verification(spaces_response)

    user_data = _mapping(_mapping(user_response.data).get("user"))
    list_data = _mapping(list_response.data)
    spaces_data = _mapping(spaces_response.data)
    user_id = user_data.get("id")
    list_id = list_data.get("id")
    space_id = _mapping(list_data.get("space")).get("id")
    if not _present_identifier(user_id):
        return _invalid_response("ClickUp user response did not contain a user ID.")
    spaces = spaces_data.get("spaces")
    if not _present_identifier(list_id) or not _present_identifier(space_id):
        return _invalid_response(
            "ClickUp List response did not contain List and Space IDs."
        )
    if not isinstance(spaces, list) or any(not isinstance(item, dict) for item in spaces):
        return _invalid_response("ClickUp Workspace response did not contain a Spaces array.")
    workspace_space_ids = {
        str(item.get("id"))
        for item in spaces
        if _present_identifier(item.get("id"))
    }
    if str(list_id) != config.list_id or str(space_id) not in workspace_space_ids:
        return ProviderVerification(
            "destination_mismatch",
            errors=("ClickUp returned a List outside the configured destination.",),
        )
    return ProviderVerification(
        status="verified",
        identity={
            "id": user_id,
            "display_name": user_data.get("username"),
            "email": user_data.get("email"),
        },
        destination={
            "id": list_data.get("id"),
            "name": list_data.get("name"),
            "workspace_id": config.workspace_id,
            "space_id": space_id,
        },
    )


def verify_target_app(config: TargetAuthConfig) -> ProviderVerification:
    parsed = urlsplit(config.base_url)
    hostname = (parsed.hostname or "").lower()
    is_safe_env = (
        hostname in LOOPBACK_HOSTS
        or any(
            tag in hostname
            for tag in (
                "dev",
                "staging",
                "stag",
                "test",
                "local",
                "demo",
                "qa",
                "sandbox",
                "uat",
                "preview",
            )
        )
        or hostname.startswith("10.")
        or hostname.startswith("192.168.")
        or hostname.startswith("172.16.")
    )
    if not is_safe_env:
        return ProviderVerification(
            status="forbidden",
            destination={"base_url": config.base_url, "auth_mode": config.auth_mode},
            errors=(
                "Target host appears to be a production environment. "
                "AQABSI requires an explicit dev/staging environment or verified test authorization.",
            ),
        )

    base_resp = request_json(
        HttpRequest(method="GET", url=config.base_url, timeout=8.0),
        config.secrets,
    )
    if not base_resp.ok and base_resp.category in {"unreachable", "redirect_blocked"}:
        return ProviderVerification(
            status=base_resp.category,
            destination={"base_url": config.base_url, "auth_mode": config.auth_mode},
            errors=(base_resp.error or "Target application could not be reached within the bounded request.",),
        )

    if config.auth_mode == "web_login":
        login_url = urljoin(config.base_url, config.login_path)
        login_resp = request_json(
            HttpRequest(
                method="POST",
                url=login_url,
                body={"username": config.username, "password": config.password},
                timeout=8.0,
            ),
            config.secrets,
        )
        if login_resp.ok:
            return ProviderVerification(
                status="verified",
                identity={"username": config.username},
                destination={
                    "base_url": config.base_url,
                    "auth_mode": config.auth_mode,
                    "login_path": config.login_path,
                },
            )
        if login_resp.category in {"unauthorized", "forbidden"}:
            return ProviderVerification(
                status="unauthorized",
                destination={"base_url": config.base_url, "auth_mode": config.auth_mode},
                errors=("Target application rejected test credentials (HTTP 401/403).",),
            )
        if login_resp.category == "unreachable":
            return ProviderVerification(
                status="unreachable",
                destination={"base_url": config.base_url, "auth_mode": config.auth_mode},
                errors=(login_resp.error or "Login endpoint is unreachable.",),
            )
        return ProviderVerification(
            status="invalid",
            destination={"base_url": config.base_url, "auth_mode": config.auth_mode},
            errors=(login_resp.error or f"Target login returned status {login_resp.status_code}.",),
        )

    if config.auth_mode == "bearer_token":
        probe_resp = request_json(
            HttpRequest(
                method="GET",
                url=config.base_url,
                headers={"Authorization": f"Bearer {config.token}"},
                timeout=8.0,
            ),
            config.secrets,
        )
        if probe_resp.category in {"unauthorized", "forbidden"}:
            return ProviderVerification(
                status=probe_resp.category,
                destination={"base_url": config.base_url, "auth_mode": config.auth_mode},
                errors=("Target application rejected test bearer token.",),
            )
        return ProviderVerification(
            status="verified",
            identity={"auth_mode": "bearer_token"},
            destination={"base_url": config.base_url, "auth_mode": config.auth_mode},
        )

    if config.auth_mode == "sso_manual_handoff":
        return ProviderVerification(
            status="verified",
            identity={"username": config.username, "mode": "sso_manual_handoff"},
            destination={"base_url": config.base_url, "auth_mode": config.auth_mode},
        )

    return ProviderVerification(
        status="verified",
        destination={"base_url": config.base_url, "auth_mode": config.auth_mode},
    )
