import importlib
import json
import os
import threading
import subprocess
import sys
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_integrations.py"
SCRIPTS = ROOT / "scripts"


class FakeHandler(BaseHTTPRequestHandler):
    routes: dict[tuple[str, str], tuple[int, dict[str, str], object]] = {}
    requests: list[dict[str, object]] = []

    def do_GET(self):
        type(self).requests.append(
            {"method": "GET", "path": self.path, "authorization": self.headers.get("Authorization")}
        )
        status, headers, body = type(self).routes.get(
            ("GET", self.path), (404, {}, {"message": "missing"})
        )
        encoded = json.dumps(body).encode("utf-8")
        self.send_response(status)
        for key, value in headers.items():
            self.send_header(key, value)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format, *args):
        return


class FakeServer:
    def __init__(self, routes):
        handler = type("ConfiguredHandler", (FakeHandler,), {})
        handler.routes = routes
        handler.requests = []
        self.handler = handler
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    @property
    def base_url(self):
        return f"http://127.0.0.1:{self.server.server_port}"

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


class IntegrationPreflightTest(unittest.TestCase):
    def run_cli(self, *args: str, environment: dict[str, str] | None = None):
        env = {"PATH": os.environ.get("PATH", ""), "PYTHONPATH": str(SCRIPTS)}
        env.update(environment or {})
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def load_config_module(self):
        sys.path.insert(0, str(SCRIPTS))
        try:
            return importlib.import_module("integration_config")
        except ModuleNotFoundError:
            self.fail("integration_config module is not implemented")
        finally:
            if sys.path[0] == str(SCRIPTS):
                sys.path.pop(0)

    def load_http_module(self):
        sys.path.insert(0, str(SCRIPTS))
        try:
            return importlib.import_module("integration_http")
        except ModuleNotFoundError:
            self.fail("integration_http module is not implemented")
        finally:
            if sys.path[0] == str(SCRIPTS):
                sys.path.pop(0)

    def test_empty_environment_reports_both_providers_missing(self):
        result = self.run_cli("--json")

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertTrue(result.stdout.strip(), "preflight did not emit JSON")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["mode"], "offline")
        self.assertEqual(payload["providers"]["confluence"]["status"], "missing")
        self.assertEqual(payload["providers"]["clickup"]["status"], "missing")
        self.assertIn(
            "AQABSI_CONFLUENCE_DEPLOYMENT",
            payload["providers"]["confluence"]["missing"],
        )
        self.assertIn(
            "AQABSI_CLICKUP_API_TOKEN",
            payload["providers"]["clickup"]["missing"],
        )
        confluence_options = payload["providers"]["confluence"][
            "configuration_options"
        ]
        self.assertIn(
            "AQABSI_CONFLUENCE_API_TOKEN",
            confluence_options["cloud"],
        )
        self.assertIn("AQABSI_CONFLUENCE_PAT", confluence_options["data_center"])
        self.assertNotIn("token value", result.stdout.lower())
        self.assertEqual(
            payload["providers"]["clickup"]["assignment"]["status"],
            "optional_missing",
        )
        self.assertEqual(
            payload["providers"]["clickup"]["assignment"]["variable"],
            "AQABSI_OWNERSHIP_REGISTRY",
        )

    def test_clickup_provider_is_ready_without_exposing_token(self):
        token = "private-clickup-value"
        result = self.run_cli(
            "--provider",
            "clickup",
            "--json",
            environment={
                "AQABSI_CLICKUP_API_TOKEN": token,
                "AQABSI_CLICKUP_WORKSPACE_ID": "901",
                "AQABSI_CLICKUP_LIST_ID": "list-42",
            },
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(token, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        provider = payload["providers"]["clickup"]
        self.assertEqual(provider["status"], "ready")
        self.assertEqual(provider["destination"]["workspace_id"], "901")
        self.assertEqual(provider["destination"]["list_id"], "list-42")
        self.assertNotIn("api_token", json.dumps(provider).lower())

    def test_confluence_deployment_requires_provider_specific_fields(self):
        cases = [
            (
                {
                    "AQABSI_CONFLUENCE_DEPLOYMENT": "cloud",
                    "AQABSI_CONFLUENCE_BASE_URL": "https://docs.example.test/wiki",
                    "AQABSI_CONFLUENCE_EMAIL": "qa@example.test",
                    "AQABSI_CONFLUENCE_API_TOKEN": "cloud-secret",
                    "AQABSI_CONFLUENCE_SPACE_ID": "123",
                },
                "space_id",
                "123",
            ),
            (
                {
                    "AQABSI_CONFLUENCE_DEPLOYMENT": "data_center",
                    "AQABSI_CONFLUENCE_BASE_URL": "https://docs.example.test/confluence",
                    "AQABSI_CONFLUENCE_PAT": "dc-secret",
                    "AQABSI_CONFLUENCE_SPACE_KEY": "QA",
                },
                "space_key",
                "QA",
            ),
        ]

        for environment, destination_key, expected in cases:
            with self.subTest(deployment=environment["AQABSI_CONFLUENCE_DEPLOYMENT"]):
                result = self.run_cli(
                    "--provider", "confluence", "--json", environment=environment
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)["providers"]["confluence"]
                self.assertEqual(payload["status"], "ready")
                self.assertEqual(payload["destination"][destination_key], expected)
                for value in environment.values():
                    if "secret" in value:
                        self.assertNotIn(value, result.stdout + result.stderr)

    def test_non_https_non_loopback_url_is_invalid(self):
        result = self.run_cli(
            "--provider",
            "confluence",
            "--json",
            environment={
                "AQABSI_CONFLUENCE_DEPLOYMENT": "cloud",
                "AQABSI_CONFLUENCE_BASE_URL": "http://docs.example.test/wiki",
                "AQABSI_CONFLUENCE_EMAIL": "qa@example.test",
                "AQABSI_CONFLUENCE_API_TOKEN": "cloud-secret",
                "AQABSI_CONFLUENCE_SPACE_ID": "123",
            },
        )

        self.assertEqual(result.returncode, 3)
        provider = json.loads(result.stdout)["providers"]["confluence"]
        self.assertEqual(provider["status"], "invalid")
        self.assertIn("HTTPS", " ".join(provider["errors"]))
        self.assertNotIn("cloud-secret", result.stdout + result.stderr)

    def test_invalid_base_url_never_echoes_embedded_credentials(self):
        result = self.run_cli(
            "--provider",
            "confluence",
            "--json",
            environment={
                "AQABSI_CONFLUENCE_DEPLOYMENT": "cloud",
                "AQABSI_CONFLUENCE_BASE_URL": "https://qa:dummy-password@docs.example.test/wiki",
                "AQABSI_CONFLUENCE_EMAIL": "qa@example.test",
                "AQABSI_CONFLUENCE_API_TOKEN": "cloud-secret",
                "AQABSI_CONFLUENCE_SPACE_ID": "123",
            },
        )

        self.assertEqual(result.returncode, 3)
        self.assertNotIn("qa", json.loads(result.stdout)["providers"]["confluence"]["destination"]["base_url"])
        self.assertNotIn("dummy-password", result.stdout + result.stderr)
        self.assertNotIn("cloud-secret", result.stdout + result.stderr)

    def test_redact_scrubs_secret_substrings_in_nested_values(self):
        module = self.load_config_module()
        secret = "sensitive-value"
        source = {
            "header": f"Bearer {secret}",
            "nested": [secret, {"message": f"rejected {secret}"}],
        }

        result = module.redact(source, [secret])

        serialized = json.dumps(result)
        self.assertNotIn(secret, serialized)
        self.assertEqual(result["header"], "Bearer [REDACTED]")
        self.assertEqual(result["nested"][0], "[REDACTED]")

    def test_verify_confluence_cloud_reads_identity_and_destination(self):
        routes = {
            ("GET", "/wiki/rest/api/user/current"): (
                200,
                {},
                {"accountId": "acct-7", "displayName": "QA User"},
            ),
            ("GET", "/wiki/api/v2/spaces/123"): (
                200,
                {},
                {"id": "123", "key": "QA", "name": "Quality"},
            ),
        }
        with FakeServer(routes) as server:
            config_module = self.load_config_module()
            http_module = self.load_http_module()
            token = "cloud-private-value"
            config = config_module.load_integration_config(
                {
                    "AQABSI_CONFLUENCE_DEPLOYMENT": "cloud",
                    "AQABSI_CONFLUENCE_BASE_URL": server.base_url + "/wiki",
                    "AQABSI_CONFLUENCE_EMAIL": "qa@example.test",
                    "AQABSI_CONFLUENCE_API_TOKEN": token,
                    "AQABSI_CONFLUENCE_SPACE_ID": "123",
                }
            )

            result = http_module.verify_confluence(config.confluence)

        self.assertEqual(result.status, "verified")
        self.assertEqual(result.identity["display_name"], "QA User")
        self.assertEqual(result.destination["name"], "Quality")
        self.assertNotIn(token, json.dumps(result.to_dict()))
        self.assertTrue(
            all(
                str(item["authorization"]).startswith("Basic ")
                for item in server.handler.requests
            )
        )

    def test_cli_verify_reports_verified_confluence(self):
        routes = {
            ("GET", "/wiki/rest/api/user/current"): (
                200,
                {},
                {"accountId": "acct-7", "displayName": "QA User"},
            ),
            ("GET", "/wiki/api/v2/spaces/123"): (
                200,
                {},
                {"id": "123", "key": "QA", "name": "Quality"},
            ),
        }
        with FakeServer(routes) as server:
            result = self.run_cli(
                "--provider",
                "confluence",
                "--verify",
                "--json",
                environment={
                    "AQABSI_CONFLUENCE_DEPLOYMENT": "cloud",
                    "AQABSI_CONFLUENCE_BASE_URL": server.base_url + "/wiki",
                    "AQABSI_CONFLUENCE_EMAIL": "qa@example.test",
                    "AQABSI_CONFLUENCE_API_TOKEN": "cloud-private-value",
                    "AQABSI_CONFLUENCE_SPACE_ID": "123",
                },
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        provider = json.loads(result.stdout)["providers"]["confluence"]
        self.assertEqual(provider["status"], "verified")
        self.assertEqual(provider["identity"]["display_name"], "QA User")
        self.assertNotIn("cloud-private-value", result.stdout + result.stderr)

    def test_human_verify_output_names_mode_identity_and_destination(self):
        routes = {
            ("GET", "/wiki/rest/api/user/current"): (
                200,
                {},
                {"accountId": "acct-7", "displayName": "QA User"},
            ),
            ("GET", "/wiki/api/v2/spaces/123"): (
                200,
                {},
                {"id": "123", "key": "QA", "name": "Quality"},
            ),
        }
        with FakeServer(routes) as server:
            result = self.run_cli(
                "--provider",
                "confluence",
                "--verify",
                environment={
                    "AQABSI_CONFLUENCE_DEPLOYMENT": "cloud",
                    "AQABSI_CONFLUENCE_BASE_URL": server.base_url + "/wiki",
                    "AQABSI_CONFLUENCE_EMAIL": "qa@example.test",
                    "AQABSI_CONFLUENCE_API_TOKEN": "cloud-private-value",
                    "AQABSI_CONFLUENCE_SPACE_ID": "123",
                },
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("(verify)", result.stdout)
        self.assertIn("QA User", result.stdout)
        self.assertIn("Quality", result.stdout)
        self.assertNotIn("Setup:", result.stdout)

    def test_confluence_parent_must_belong_to_configured_space(self):
        routes = {
            ("GET", "/wiki/rest/api/user/current"): (
                200,
                {},
                {"accountId": "acct-7", "displayName": "QA User"},
            ),
            ("GET", "/wiki/api/v2/spaces/123"): (
                200,
                {},
                {"id": "123", "key": "QA", "name": "Quality"},
            ),
            ("GET", "/wiki/api/v2/pages/parent-1"): (
                200,
                {},
                {"id": "parent-1", "spaceId": "999", "title": "Wrong space"},
            ),
        }
        with FakeServer(routes) as server:
            config_module = self.load_config_module()
            http_module = self.load_http_module()
            config = config_module.load_integration_config(
                {
                    "AQABSI_CONFLUENCE_DEPLOYMENT": "cloud",
                    "AQABSI_CONFLUENCE_BASE_URL": server.base_url + "/wiki",
                    "AQABSI_CONFLUENCE_EMAIL": "qa@example.test",
                    "AQABSI_CONFLUENCE_API_TOKEN": "cloud-private-value",
                    "AQABSI_CONFLUENCE_SPACE_ID": "123",
                    "AQABSI_CONFLUENCE_PARENT_PAGE_ID": "parent-1",
                }
            )
            result = http_module.verify_confluence(config.confluence)

        self.assertEqual(result.status, "destination_mismatch")

    def test_verify_clickup_reads_user_and_list(self):
        routes = {
            ("GET", "/api/v2/user"): (
                200,
                {},
                {"user": {"id": 7, "username": "QA User", "email": "qa@example.test"}},
            ),
            ("GET", "/api/v2/list/list-42"): (
                200,
                {},
                {"id": "list-42", "name": "Defects", "space": {"id": "space-7"}},
            ),
            ("GET", "/api/v2/team/901/space?archived=true"): (
                200,
                {},
                {"spaces": [{"id": "space-7", "name": "Engineering"}]},
            ),
        }
        with FakeServer(routes) as server:
            config_module = self.load_config_module()
            http_module = self.load_http_module()
            token = "clickup-private-value"
            config = config_module.load_integration_config(
                {
                    "AQABSI_CLICKUP_API_TOKEN": token,
                    "AQABSI_CLICKUP_WORKSPACE_ID": "901",
                    "AQABSI_CLICKUP_LIST_ID": "list-42",
                }
            )
            with mock.patch.object(http_module, "CLICKUP_API_BASE", server.base_url + "/api/v2"):
                result = http_module.verify_clickup(config.clickup)

        self.assertEqual(result.status, "verified")
        self.assertEqual(result.identity["id"], 7)
        self.assertEqual(result.destination["name"], "Defects")
        self.assertNotIn(token, json.dumps(result.to_dict()))
        self.assertTrue(
            all(item["authorization"] == token for item in server.handler.requests)
        )

    def test_verification_rejects_malformed_identity_or_wrong_workspace(self):
        malformed_routes = {
            ("GET", "/api/v2/user"): (200, {}, {"message": "login page"}),
            ("GET", "/api/v2/list/list-42"): (
                200,
                {},
                {"id": "list-42", "name": "Defects", "space": {"id": "space-7"}},
            ),
            ("GET", "/api/v2/team/901/space?archived=true"): (
                200,
                {},
                {"spaces": [{"id": "space-7", "name": "Engineering"}]},
            ),
        }
        with FakeServer(malformed_routes) as server:
            config_module = self.load_config_module()
            http_module = self.load_http_module()
            config = config_module.load_integration_config(
                {
                    "AQABSI_CLICKUP_API_TOKEN": "private-token",
                    "AQABSI_CLICKUP_WORKSPACE_ID": "901",
                    "AQABSI_CLICKUP_LIST_ID": "list-42",
                }
            )
            with mock.patch.object(
                http_module, "CLICKUP_API_BASE", server.base_url + "/api/v2"
            ):
                malformed = http_module.verify_clickup(config.clickup)

        wrong_workspace_routes = {
            ("GET", "/api/v2/user"): (
                200,
                {},
                {"user": {"id": 7, "username": "QA User"}},
            ),
            ("GET", "/api/v2/list/list-42"): (
                200,
                {},
                {"id": "list-42", "name": "Defects", "space": {"id": "space-999"}},
            ),
            ("GET", "/api/v2/team/901/space?archived=true"): (
                200,
                {},
                {"spaces": [{"id": "space-7", "name": "Engineering"}]},
            ),
        }
        with FakeServer(wrong_workspace_routes) as server:
            with mock.patch.object(
                http_module, "CLICKUP_API_BASE", server.base_url + "/api/v2"
            ):
                wrong_workspace = http_module.verify_clickup(config.clickup)

        self.assertEqual(malformed.status, "invalid_response")
        self.assertEqual(wrong_workspace.status, "destination_mismatch")

    def test_verification_classifies_unauthorized_forbidden_and_unreachable(self):
        config_module = self.load_config_module()
        http_module = self.load_http_module()
        for status_code, expected in ((401, "unauthorized"), (403, "forbidden")):
            with self.subTest(status_code=status_code), FakeServer(
                {
                    ("GET", "/api/v2/user"): (
                        status_code,
                        {},
                        {"message": "denied private-token-value"},
                    )
                }
            ) as server:
                config = config_module.load_integration_config(
                    {
                        "AQABSI_CLICKUP_API_TOKEN": "private-token-value",
                        "AQABSI_CLICKUP_WORKSPACE_ID": "901",
                        "AQABSI_CLICKUP_LIST_ID": "list-42",
                    }
                )
                with mock.patch.object(http_module, "CLICKUP_API_BASE", server.base_url + "/api/v2"):
                    result = http_module.verify_clickup(config.clickup)
                self.assertEqual(result.status, expected)
                self.assertNotIn("private-token-value", json.dumps(result.to_dict()))

        config = config_module.load_integration_config(
            {
                "AQABSI_CLICKUP_API_TOKEN": "private-token-value",
                "AQABSI_CLICKUP_WORKSPACE_ID": "901",
                "AQABSI_CLICKUP_LIST_ID": "list-42",
            }
        )
        with mock.patch.object(http_module, "CLICKUP_API_BASE", "http://127.0.0.1:1/api/v2"):
            result = http_module.verify_clickup(config.clickup)
        self.assertEqual(result.status, "unreachable")
        self.assertNotIn("private-token-value", json.dumps(result.to_dict()))

    def test_cross_origin_redirect_is_blocked_without_forwarding_authorization(self):
        http_module = self.load_http_module()
        with FakeServer({("GET", "/capture"): (200, {}, {"ok": True})}) as target:
            with FakeServer(
                {
                    ("GET", "/redirect"): (
                        302,
                        {"Location": target.base_url + "/capture"},
                        {"redirect": True},
                    )
                }
            ) as source:
                response = http_module.request_json(
                    http_module.HttpRequest(
                        method="GET",
                        url=source.base_url + "/redirect",
                        headers={"Authorization": "private-token-value"},
                    ),
                    ["private-token-value"],
                )

        self.assertFalse(response.ok)
        self.assertEqual(response.category, "redirect_blocked")
        self.assertEqual(target.handler.requests, [])
        self.assertNotIn("private-token-value", json.dumps(response.to_dict()))


if __name__ == "__main__":
    unittest.main()
