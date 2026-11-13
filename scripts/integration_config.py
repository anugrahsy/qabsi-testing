#!/usr/bin/env python3
"""Load AQABSI integration settings without persisting or exposing secrets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping
from urllib.parse import urlsplit, urlunsplit


CONFLUENCE_SETUP_URL = "https://id.atlassian.com/manage-profile/security/api-tokens"
CLICKUP_SETUP_URL = "https://app.clickup.com/settings/apps"
LOOPBACK_HOSTS = {"127.0.0.1", "::1", "localhost"}
CONFLUENCE_CONFIGURATION_OPTIONS = {
    "cloud": [
        "AQABSI_CONFLUENCE_BASE_URL",
        "AQABSI_CONFLUENCE_EMAIL",
        "AQABSI_CONFLUENCE_API_TOKEN",
        "AQABSI_CONFLUENCE_SPACE_ID",
        "AQABSI_CONFLUENCE_PARENT_PAGE_ID (optional)",
    ],
    "data_center": [
        "AQABSI_CONFLUENCE_BASE_URL",
        "AQABSI_CONFLUENCE_PAT",
        "AQABSI_CONFLUENCE_SPACE_KEY",
        "AQABSI_CONFLUENCE_PARENT_PAGE_ID (optional)",
    ],
}


@dataclass(frozen=True)
class ConfluenceConfig:
    deployment: str
    base_url: str
    email: str
    api_token: str
    pat: str
    space_id: str
    space_key: str
    parent_page_id: str
    missing: tuple[str, ...]
    errors: tuple[str, ...]

    @property
    def secrets(self) -> tuple[str, ...]:
        return tuple(value for value in (self.api_token, self.pat) if value)


@dataclass(frozen=True)
class ClickUpConfig:
    auth_mode: str
    api_token: str
    workspace_id: str
    list_id: str
    ownership_registry_configured: bool
    missing: tuple[str, ...]
    errors: tuple[str, ...]

    @property
    def secrets(self) -> tuple[str, ...]:
        return (self.api_token,) if self.api_token else ()


TARGET_AUTH_MODES = {
    "web_login",
    "bearer_token",
    "basic_auth",
    "sso_manual_handoff",
    "none",
}
TARGET_SETUP_GUIDANCE = (
    "Akun pengujian target aplikasi belum dikonfigurasi. Siapkan username dan password "
    "melalui secret manager atau environment terminal. Jangan kirim password melalui chat."
)


@dataclass(frozen=True)
class TargetAuthConfig:
    base_url: str
    auth_mode: str
    username: str
    password: str
    token: str
    login_path: str
    missing: tuple[str, ...]
    errors: tuple[str, ...]

    @property
    def secrets(self) -> tuple[str, ...]:
        return tuple(value for value in (self.password, self.token) if value)


@dataclass(frozen=True)
class IntegrationConfig:
    confluence: ConfluenceConfig
    clickup: ClickUpConfig
    target: TargetAuthConfig

    @property
    def secrets(self) -> tuple[str, ...]:
        return self.confluence.secrets + self.clickup.secrets + self.target.secrets


def _value(environ: Mapping[str, str], name: str) -> str:
    return environ.get(name, "").strip()


def _validate_base_url(value: str) -> tuple[str, tuple[str, ...]]:
    if not value:
        return "", ()
    parsed = urlsplit(value)
    errors: list[str] = []
    if not parsed.hostname:
        errors.append("Base URL must include a hostname.")
    if parsed.username or parsed.password:
        errors.append("Base URL must not contain credentials.")
    if parsed.query or parsed.fragment:
        errors.append("Base URL must not contain a query or fragment.")
    if parsed.scheme != "https" and not (
        parsed.scheme == "http" and parsed.hostname in LOOPBACK_HOSTS
    ):
        errors.append("Base URL must use HTTPS; HTTP is allowed only for loopback tests.")
    if parsed.scheme not in {"http", "https"}:
        errors.append("Base URL scheme must be HTTPS.")
    hostname = parsed.hostname or ""
    safe_host = f"[{hostname}]" if ":" in hostname else hostname
    try:
        port = parsed.port
    except ValueError:
        port = None
        errors.append("Base URL contains an invalid port.")
    safe_netloc = safe_host + (f":{port}" if port is not None else "")
    normalized = urlunsplit(
        (parsed.scheme, safe_netloc, parsed.path.rstrip("/"), "", "")
    )
    return normalized, tuple(errors)


def load_integration_config(environ: Mapping[str, str]) -> IntegrationConfig:
    deployment = _value(environ, "AQABSI_CONFLUENCE_DEPLOYMENT").lower()
    base_url, base_errors = _validate_base_url(
        _value(environ, "AQABSI_CONFLUENCE_BASE_URL")
    )
    email = _value(environ, "AQABSI_CONFLUENCE_EMAIL")
    api_token = _value(environ, "AQABSI_CONFLUENCE_API_TOKEN")
    pat = _value(environ, "AQABSI_CONFLUENCE_PAT")
    space_id = _value(environ, "AQABSI_CONFLUENCE_SPACE_ID")
    space_key = _value(environ, "AQABSI_CONFLUENCE_SPACE_KEY")
    parent_page_id = _value(environ, "AQABSI_CONFLUENCE_PARENT_PAGE_ID")

    confluence_missing: list[str] = []
    if not deployment:
        confluence_missing.append("AQABSI_CONFLUENCE_DEPLOYMENT")
    if not base_url:
        confluence_missing.append("AQABSI_CONFLUENCE_BASE_URL")
    if deployment == "cloud":
        for name, value in (
            ("AQABSI_CONFLUENCE_EMAIL", email),
            ("AQABSI_CONFLUENCE_API_TOKEN", api_token),
            ("AQABSI_CONFLUENCE_SPACE_ID", space_id),
        ):
            if not value:
                confluence_missing.append(name)
    elif deployment == "data_center":
        for name, value in (
            ("AQABSI_CONFLUENCE_PAT", pat),
            ("AQABSI_CONFLUENCE_SPACE_KEY", space_key),
        ):
            if not value:
                confluence_missing.append(name)

    confluence_errors = list(base_errors)
    if deployment and deployment not in {"cloud", "data_center"}:
        confluence_errors.append(
            "AQABSI_CONFLUENCE_DEPLOYMENT must be cloud or data_center."
        )

    clickup_token = _value(environ, "AQABSI_CLICKUP_API_TOKEN")
    clickup_auth_mode = _value(environ, "AQABSI_CLICKUP_AUTH_MODE") or "personal"
    clickup_workspace_id = _value(environ, "AQABSI_CLICKUP_WORKSPACE_ID")
    clickup_list_id = _value(environ, "AQABSI_CLICKUP_LIST_ID")
    ownership_registry_configured = bool(
        _value(environ, "AQABSI_OWNERSHIP_REGISTRY")
    )
    clickup_missing = tuple(
        name
        for name, value in (
            ("AQABSI_CLICKUP_API_TOKEN", clickup_token),
            ("AQABSI_CLICKUP_WORKSPACE_ID", clickup_workspace_id),
            ("AQABSI_CLICKUP_LIST_ID", clickup_list_id),
        )
        if not value
    )

    clickup_errors: tuple[str, ...] = ()
    if clickup_auth_mode not in {"personal", "oauth"}:
        clickup_errors = (
            "AQABSI_CLICKUP_AUTH_MODE must be personal or oauth.",
        )

    target_base_url_raw = _value(environ, "AQABSI_TARGET_BASE_URL")
    target_base_url, target_base_errors = _validate_base_url(target_base_url_raw)
    target_auth_mode_raw = _value(environ, "AQABSI_TARGET_AUTH_MODE").lower()
    target_auth_mode = target_auth_mode_raw or "web_login"
    target_username = _value(environ, "AQABSI_TEST_USERNAME")
    target_password = _value(environ, "AQABSI_TEST_PASSWORD")
    target_token = _value(environ, "AQABSI_TEST_TOKEN")
    target_login_path = _value(environ, "AQABSI_TARGET_LOGIN_PATH") or "/login"

    target_missing: list[str] = []
    if not target_base_url:
        target_missing.append("AQABSI_TARGET_BASE_URL")

    target_errors = list(target_base_errors)
    if target_auth_mode not in TARGET_AUTH_MODES:
        target_errors.append(
            f"AQABSI_TARGET_AUTH_MODE must be one of: {', '.join(sorted(TARGET_AUTH_MODES))}."
        )
    elif target_auth_mode in {"web_login", "basic_auth"}:
        if not target_username:
            target_missing.append("AQABSI_TEST_USERNAME")
        if not target_password:
            target_missing.append("AQABSI_TEST_PASSWORD")
    elif target_auth_mode == "bearer_token":
        if not target_token:
            target_missing.append("AQABSI_TEST_TOKEN")
    elif target_auth_mode == "sso_manual_handoff":
        if not target_username:
            target_missing.append("AQABSI_TEST_USERNAME")

    return IntegrationConfig(
        confluence=ConfluenceConfig(
            deployment=deployment,
            base_url=base_url,
            email=email,
            api_token=api_token,
            pat=pat,
            space_id=space_id,
            space_key=space_key,
            parent_page_id=parent_page_id,
            missing=tuple(confluence_missing),
            errors=tuple(confluence_errors),
        ),
        clickup=ClickUpConfig(
            auth_mode=clickup_auth_mode,
            api_token=clickup_token,
            workspace_id=clickup_workspace_id,
            list_id=clickup_list_id,
            ownership_registry_configured=ownership_registry_configured,
            missing=clickup_missing,
            errors=clickup_errors,
        ),
        target=TargetAuthConfig(
            base_url=target_base_url,
            auth_mode=target_auth_mode,
            username=target_username,
            password=target_password,
            token=target_token,
            login_path=target_login_path,
            missing=tuple(target_missing),
            errors=tuple(target_errors),
        ),
    )


def redact(value: object, secrets: Iterable[str]) -> object:
    secret_values = sorted({item for item in secrets if item}, key=len, reverse=True)
    if isinstance(value, str):
        result = value
        for secret in secret_values:
            result = result.replace(secret, "[REDACTED]")
        return result
    if isinstance(value, dict):
        return {key: redact(item, secret_values) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item, secret_values) for item in value]
    if isinstance(value, tuple):
        return tuple(redact(item, secret_values) for item in value)
    return value


def _status(missing: tuple[str, ...], errors: tuple[str, ...]) -> str:
    if errors:
        return "invalid"
    if missing:
        return "missing"
    return "ready"


def build_readiness(
    config: IntegrationConfig, providers: Iterable[str] | None = None
) -> dict[str, object]:
    selected = tuple(providers or ("confluence", "clickup", "target"))
    result: dict[str, object] = {
        "schema_version": "1.0",
        "mode": "offline",
        "providers": {},
    }
    provider_results = result["providers"]
    assert isinstance(provider_results, dict)

    if "confluence" in selected:
        item = config.confluence
        provider_results["confluence"] = {
            "status": _status(item.missing, item.errors),
            "missing": list(item.missing),
            "errors": list(item.errors),
            "destination": {
                "deployment": item.deployment or None,
                "base_url": item.base_url or None,
                "space_id": item.space_id or None,
                "space_key": item.space_key or None,
                "parent_page_id": item.parent_page_id or None,
            },
            "setup_url": CONFLUENCE_SETUP_URL,
            "configuration_options": CONFLUENCE_CONFIGURATION_OPTIONS,
            "secret_delivery": "Use environment variables supplied by an approved secret manager; never paste tokens into chat.",
        }
    if "clickup" in selected:
        item = config.clickup
        provider_results["clickup"] = {
            "status": _status(item.missing, item.errors),
            "missing": list(item.missing),
            "errors": list(item.errors),
            "destination": {
                "auth_mode": item.auth_mode,
                "workspace_id": item.workspace_id or None,
                "list_id": item.list_id or None,
            },
            "setup_url": CLICKUP_SETUP_URL,
            "assignment": {
                "status": (
                    "configured"
                    if item.ownership_registry_configured
                    else "optional_missing"
                ),
                "variable": "AQABSI_OWNERSHIP_REGISTRY",
                "guidance": "Required only for automatic assignee resolution; keep tasks unassigned when mapping is unresolved.",
            },
            "secret_delivery": "Use environment variables supplied by an approved secret manager; never paste tokens into chat.",
        }
    if "target" in selected:
        item = config.target
        provider_results["target"] = {
            "status": _status(item.missing, item.errors),
            "missing": list(item.missing),
            "errors": list(item.errors),
            "destination": {
                "base_url": item.base_url or None,
                "auth_mode": item.auth_mode,
                "username": item.username or None,
                "login_path": item.login_path,
            },
            "setup_guidance": TARGET_SETUP_GUIDANCE,
            "secret_delivery": "Use environment variables supplied by an approved secret manager; never paste passwords or tokens into chat.",
            "authorization_scope": "Single-account credentials enable authenticated functional testing. Multi-role/IDOR testing requires dedicated role credentials; unconfigured roles will be marked as blocked.",
        }
    return result
