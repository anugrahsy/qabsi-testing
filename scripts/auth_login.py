#!/usr/bin/env python3
"""Log in to a target application and persist session cookies without echoing secrets.

Supports ``web_login`` (form username/password) and ``basic_auth``. Credentials are
read from ``AQABSI_TARGET_BASE_URL``, ``AQABSI_TEST_USERNAME``, and
``AQABSI_TEST_PASSWORD`` or from arguments. Session cookies are saved to a cookie
jar file; passwords and tokens are never printed or written to any file.
"""

from __future__ import annotations

import argparse
import base64
import http.cookiejar
import json
import os
import socket
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPCookieProcessor, HTTPRedirectHandler, Request, build_opener


class SameOriginRedirect(HTTPRedirectHandler):
    """Follow only same-origin redirects so credentials are never forwarded cross-origin."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        origin = urlsplit(req.full_url).netloc
        target = urlsplit(urljoin(req.full_url, newurl)).netloc
        if origin != target:
            return None
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _status_of(code: int | None) -> str:
    if code is None:
        return "unreachable"
    if code in (401, 403):
        return "unauthorized"
    if 200 <= code < 400:
        return "ok"
    return "error"


def login(base_url: str, username: str, password: str, mode: str, login_path: str, probe_path: str, cookie_file: Path) -> dict[str, object]:
    jar = http.cookiejar.MozillaCookieJar()
    opener = build_opener(HTTPCookieProcessor(jar), SameOriginRedirect())
    headers = {"Accept": "application/json"}

    if mode == "web_login":
        login_url = urljoin(base_url.rstrip("/") + "/", login_path.lstrip("/"))
        body = json.dumps({"username": username, "password": password}, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
        request = Request(login_url, data=body, headers=headers, method="POST")
    else:
        token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
        headers["Authorization"] = "Basic " + token
        request = Request(urljoin(base_url.rstrip("/") + "/", probe_path.lstrip("/")), headers=headers, method="GET")

    try:
        with opener.open(request, timeout=8.0) as response:
            code = response.getcode()
            response.read(1024)
    except HTTPError as exc:
        code = exc.code
        exc.read(1024)
    except (URLError, TimeoutError, socket.timeout, OSError) as exc:
        return {
            "schema_version": "1.0",
            "status": "unreachable",
            "mode": mode,
            "base_url": base_url,
            "login_path": login_path,
            "cookie_file": str(cookie_file),
            "status_code": None,
            "message": f"Target could not be reached: {exc}",
        }

    status = _status_of(code)
    cookie_file.parent.mkdir(parents=True, exist_ok=True)
    jar.filename = str(cookie_file)
    jar.save(ignore_discard=True, ignore_expires=True)
    return {
        "schema_version": "1.0",
        "status": status,
        "mode": mode,
        "base_url": base_url,
        "login_path": login_path,
        "cookie_file": str(cookie_file),
        "status_code": code,
        "message": "Session cookies saved." if status == "ok" else f"Login returned HTTP {code}.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("web_login", "basic_auth"), default="web_login")
    parser.add_argument("--base-url", help="Target base URL (default: AQABSI_TARGET_BASE_URL)")
    parser.add_argument("--username", help="Test username (default: AQABSI_TEST_USERNAME)")
    parser.add_argument("--password", help="Test password (default: AQABSI_TEST_PASSWORD)")
    parser.add_argument("--login-path", help="Login route (default: AQABSI_TARGET_LOGIN_PATH or /login)")
    parser.add_argument("--probe-path", default="/", help="Probe path for basic_auth (default: /)")
    parser.add_argument("--cookie-jar", type=Path, default=Path("aqabsi-cookies.txt"), help="Cookie jar output path")
    args = parser.parse_args()

    base_url = (args.base_url or os.environ.get("AQABSI_TARGET_BASE_URL", "")).strip()
    username = (args.username or os.environ.get("AQABSI_TEST_USERNAME", "")).strip()
    password = args.password if args.password is not None else os.environ.get("AQABSI_TEST_PASSWORD", "").strip()
    login_path = (args.login_path or os.environ.get("AQABSI_TARGET_LOGIN_PATH", "") or "/login").strip()

    if not base_url:
        print("AQABSI auth login failed: target base URL is required.", file=sys.stderr)
        return 2
    if not username or not password:
        print("AQABSI auth login failed: username and password are required.", file=sys.stderr)
        return 2

    payload = login(base_url, username, password, args.mode, login_path, args.probe_path, args.cookie_jar)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["status"] == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
