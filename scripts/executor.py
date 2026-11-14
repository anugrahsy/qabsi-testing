#!/usr/bin/env python3
"""Deterministic AQABSI API test executor.

Reads a test-run manifest, executes every ``layer == "api"`` test case against a
target base URL using only the Python standard library, and writes a new manifest
with ``actual_result``, ``status``, and ``evidence`` populated from the observed
HTTP response. Pass/fail is never fabricated: status is derived solely from the
observed status code versus the case's expected status or success expectation.

Credentials are read from ``AQABSI_TARGET_BASE_URL`` and ``AQABSI_TEST_TOKEN`` or
from arguments, and are never written to the output manifest.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import socket
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import HTTPRedirectHandler, Request, build_opener

MAX_BODY_BYTES = 2000
EVIDENCE_BODY_LIMIT = 500
RESULT_BODY_LIMIT = 400
HTTP_METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE")


class NoRedirect(HTTPRedirectHandler):
    """Do not follow redirects so the observed status code stays deterministic."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def redact_text(value: Any, secrets: tuple[str, ...] = ()) -> str:
    text = str(value if value is not None else "")
    for secret in sorted({item for item in secrets if item}, key=len, reverse=True):
        text = text.replace(secret, "[REDACTED]")
    text = re.sub(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+", "Bearer [REDACTED]", text)
    text = re.sub(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b", "[REDACTED_JWT]", text)
    return text


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "...[truncated]"


def _decode(raw: bytes) -> str:
    return raw.decode("utf-8", errors="replace").strip()


def _normalize_status(value: Any) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_expected_status(case: dict[str, Any]) -> int | None:
    text = str(case.get("expected_result") or "")
    match = re.search(r"(?i)\bHTTP\s*([1-5]\d{2})\b", text)
    if match:
        return int(match.group(1))
    td = case.get("test_data")
    if isinstance(td, dict):
        return _normalize_status(td.get("expected_status"))
    return None


def resolve_target(case: dict[str, Any]) -> dict[str, Any]:
    """Resolve method, path, body, headers, and expected outcome for a test case."""
    td = case.get("test_data")
    td = td if isinstance(td, dict) else {}
    request = td.get("request") if isinstance(td.get("request"), dict) else {}

    method = td.get("method") or request.get("method")
    path = (
        td.get("path")
        or td.get("url")
        or td.get("endpoint")
        or request.get("path")
        or request.get("url")
        or request.get("endpoint")
    )
    body = request.get("body") if "body" in request else td.get("body")
    headers = request.get("headers") if "headers" in request else td.get("headers")
    expected_status = _normalize_status(
        request.get("expected_status") if "expected_status" in request else td.get("expected_status")
    )
    expected_success = request.get("expected_success") if "expected_success" in request else td.get("expected_success")
    if expected_success is not None and not isinstance(expected_success, bool):
        expected_success = None

    if not method or not path:
        for step in case.get("steps") or []:
            match = re.match(r"^\s*(GET|POST|PUT|PATCH|DELETE)\s+(\S+)", str(step), re.IGNORECASE)
            if match:
                method = method or match.group(1).upper()
                path = path or match.group(2)
                break

    if expected_status is None:
        expected_status = parse_expected_status(case)

    return {
        "method": str(method).upper() if method else None,
        "path": str(path) if path else None,
        "body": body,
        "headers": headers if isinstance(headers, dict) else None,
        "expected_status": expected_status,
        "expected_success": expected_success,
    }


def classify_status(actual_status: int | None, expected_status: int | None, expected_success: bool | None) -> str:
    if actual_status is None:
        return "environment_error"
    if expected_status is not None:
        return "pass" if actual_status == expected_status else "fail"
    if expected_success is True:
        return "pass" if 200 <= actual_status < 400 else "fail"
    if expected_success is False:
        return "pass" if 400 <= actual_status < 600 else "fail"
    return "pass" if 200 <= actual_status < 400 else "fail"


def perform_request(
    target: dict[str, Any],
    base_url: str,
    token: str | None,
    timeout: float,
) -> tuple[int | None, str, str | None]:
    method = target.get("method")
    path = target.get("path")
    if not method or not path:
        return None, "", "No request path could be resolved."
    if method not in HTTP_METHODS:
        return None, "", f"Unsupported HTTP method: {method}"

    url = path if path.startswith(("http://", "https://")) else urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
    headers = dict(target.get("headers") or {})
    if token and not any(key.lower() == "authorization" for key in headers):
        headers["Authorization"] = "Bearer " + token

    data: bytes | None = None
    body = target.get("body")
    if body is not None and method in ("POST", "PUT", "PATCH"):
        if isinstance(body, (dict, list)):
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            headers.setdefault("Content-Type", "application/json")
        elif isinstance(body, str):
            data = body.encode("utf-8")
        else:
            data = str(body).encode("utf-8")

    opener = build_opener(NoRedirect())
    try:
        with opener.open(Request(url, data=data, headers=headers, method=method), timeout=timeout) as response:
            raw = response.read(MAX_BODY_BYTES + 1)
            status = response.getcode()
            return status, _decode(raw[:MAX_BODY_BYTES]), None
    except HTTPError as exc:
        raw = exc.read(MAX_BODY_BYTES)
        return exc.code, _decode(raw[:MAX_BODY_BYTES]), None
    except (URLError, TimeoutError, socket.timeout, OSError) as exc:
        return None, "", str(exc)


def run_case(case: dict[str, Any], base_url: str, token: str | None, timeout: float) -> dict[str, Any]:
    target = resolve_target(case)
    method = target["method"]
    path = target["path"]
    if not method or not path:
        return {
            "status": "blocked",
            "actual_result": "No HTTP request target could be resolved from test_data or steps.",
            "evidence": ["blocked: unresolved request target"],
            "notes": "executor could not determine method/path",
        }

    actual_status, body_text, error = perform_request(target, base_url, token, timeout)
    secrets = (token,) if token else ()
    safe_body = redact_text(body_text, secrets)
    safe_error = redact_text(error, secrets)
    status = classify_status(actual_status, target["expected_status"], target["expected_success"])

    if actual_status is None:
        actual_result = f"Request failed: {safe_error}" if safe_error else "Request failed."
        evidence = [f"{method} {path} -> connection error"]
    else:
        expected_label = f"expected {target['expected_status']}" if target["expected_status"] is not None else "expected success"
        actual_result = f"HTTP {actual_status} ({expected_label})"
        if safe_body:
            actual_result += f": {_truncate(safe_body, RESULT_BODY_LIMIT)}"
        evidence = [f"{method} {path} -> HTTP {actual_status}"]
        if safe_body:
            evidence.append(_truncate(safe_body, EVIDENCE_BODY_LIMIT))

    return {"status": status, "actual_result": actual_result, "evidence": evidence, "notes": "deterministic executor"}


def execute_manifest(data: dict[str, Any], base_url: str, token: str | None, timeout: float) -> dict[str, Any]:
    result = copy.deepcopy(data)
    for case in result.get("test_cases") or []:
        if not isinstance(case, dict) or case.get("layer") != "api":
            continue
        outcome = run_case(case, base_url, token, timeout)
        case["status"] = outcome["status"]
        case["actual_result"] = outcome["actual_result"]
        case["evidence"] = outcome["evidence"]
        note = outcome.get("notes")
        if note:
            existing = str(case.get("notes") or "").strip()
            case["notes"] = (existing + "; " if existing else "") + note
    return result


def _summary(data: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for case in data.get("test_cases") or []:
        if not isinstance(case, dict):
            continue
        status = case.get("status")
        if isinstance(status, str):
            counts[status] = counts.get(status, 0) + 1
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="AQABSI test-run JSON manifest")
    parser.add_argument("--output", type=Path, help="Output manifest path (default: <input>.executed.json)")
    parser.add_argument("--base-url", help="Target base URL (default: AQABSI_TARGET_BASE_URL)")
    parser.add_argument("--token", help="Bearer token (default: AQABSI_TEST_TOKEN); never written to output")
    parser.add_argument("--timeout", type=float, default=8.0, help="Per-request timeout in seconds")
    args = parser.parse_args()

    base_url = (args.base_url or os.environ.get("AQABSI_TARGET_BASE_URL", "")).strip()
    token = args.token if args.token is not None else os.environ.get("AQABSI_TEST_TOKEN", "").strip()
    if not base_url:
        print("AQABSI executor failed: target base URL is required (--base-url or AQABSI_TARGET_BASE_URL).", file=sys.stderr)
        return 2
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"AQABSI executor failed: {exc}", file=sys.stderr)
        return 2

    executed = execute_manifest(data, base_url, token or None, args.timeout)
    output = args.output or Path(str(args.input.with_suffix("")) + ".executed.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(executed, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"schema_version": "1.0", "output": str(output), "counts": _summary(executed)}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
