import importlib
import io
import json
import os
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


class PublisherHandler(BaseHTTPRequestHandler):
    def _handle(self):
        size = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(size) if size else b""
        body = json.loads(raw.decode("utf-8")) if raw else None
        request = {
            "method": self.command,
            "path": self.path,
            "authorization": self.headers.get("Authorization"),
            "body": body,
        }
        self.server.requests.append(request)
        status, response = self.server.dispatch(request)
        encoded = json.dumps(response).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    do_GET = _handle
    do_POST = _handle
    do_PUT = _handle

    def log_message(self, format, *args):
        return


class FakePublisherServer:
    def __init__(self, dispatch):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), PublisherHandler)
        self.server.dispatch = dispatch
        self.server.requests = []
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    @property
    def base_url(self):
        return f"http://127.0.0.1:{self.server.server_port}"

    @property
    def requests(self):
        return self.server.requests

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


class PublishArtifactsTest(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(SCRIPTS))

    def tearDown(self):
        if sys.path and sys.path[0] == str(SCRIPTS):
            sys.path.pop(0)

    def load_modules(self):
        try:
            return (
                importlib.import_module("integration_config"),
                importlib.import_module("publish_artifacts"),
            )
        except ModuleNotFoundError:
            self.fail("publish_artifacts module is not implemented")

    def write_drafts(self, root: Path, *, dry_run=True, tasks=None):
        confluence = root / "confluence-draft.json"
        clickup = root / "clickup-drafts.json"
        confluence.write_text(
            json.dumps(
                {
                    "dry_run": dry_run,
                    "publication_requires_authorization": True,
                    "idempotency_key": "AQABSI-RUN-001",
                    "suggested_title": "QA Report — AQABSI-RUN-001",
                    "body_format": "markdown",
                    "body": "# QA Report\n\n<script>unsafe()</script>\n\n- Safe item",
                    "target_space": None,
                    "parent_page_id": None,
                }
            ),
            encoding="utf-8",
        )
        clickup.write_text(
            json.dumps(
                {
                    "dry_run": dry_run,
                    "publication_requires_authorization": True,
                    "tasks": tasks or [],
                }
            ),
            encoding="utf-8",
        )
        return confluence, clickup

    def task(self, fingerprint="a" * 64, *, assignee_id=None, name="Defect one"):
        return {
            "fingerprint": fingerprint,
            "external_key": f"AQABSI-{fingerprint[:12]}",
            "name": name,
            "description_markdown": "**Actual:** observable failure",
            "owner_team": "backend",
            "assignee_id": assignee_id,
            "severity": "high",
            "source_run_id": "AQABSI-RUN-001",
            "action": "create_or_update_by_fingerprint",
        }

    def test_dry_run_builds_plan_without_credentials_or_network(self):
        _, publisher = self.load_modules()
        with tempfile.TemporaryDirectory() as tmp:
            confluence, clickup = self.write_drafts(
                Path(tmp), tasks=[self.task()]
            )
            with mock.patch.object(
                publisher, "request_json", side_effect=AssertionError("network used")
            ):
                plan = publisher.build_publication_plan(
                    confluence, clickup, ("confluence", "clickup")
                )

        self.assertTrue(plan["dry_run"])
        self.assertEqual(plan["providers"]["confluence"]["actions"], 1)
        self.assertEqual(plan["providers"]["clickup"]["actions"], 1)
        self.assertEqual(plan["network_mutations"], 0)
        self.assertEqual(
            plan["providers"]["confluence"]["deduplication"], "not_checked"
        )
        self.assertEqual(
            plan["providers"]["clickup"]["tasks"][0]["assignment_status"],
            "unresolved",
        )
        self.assertIn("body_preview", plan["providers"]["confluence"])

    def test_live_mode_rejects_missing_authorization_and_non_draft_input(self):
        config_module, publisher = self.load_modules()
        with tempfile.TemporaryDirectory() as tmp:
            confluence, clickup = self.write_drafts(Path(tmp), tasks=[self.task()])
            config = config_module.load_integration_config(
                {
                    "AQABSI_CLICKUP_API_TOKEN": "private-token",
                    "AQABSI_CLICKUP_WORKSPACE_ID": "901",
                    "AQABSI_CLICKUP_LIST_ID": "list-42",
                }
            )
            draft = json.loads(clickup.read_text())
            with self.assertRaisesRegex(publisher.PublicationError, "authorization"):
                publisher.publish_clickup(draft, config.clickup, None)

            non_draft = json.loads(clickup.read_text())
            non_draft["dry_run"] = False
            with self.assertRaisesRegex(publisher.PublicationError, "dry_run"):
                publisher.publish_clickup(
                    non_draft, config.clickup, "APPROVED-001"
                )

    def test_malformed_clickup_assignee_is_rejected_before_network(self):
        config_module, publisher = self.load_modules()
        config = config_module.load_integration_config(
            {
                "AQABSI_CLICKUP_API_TOKEN": "private-token",
                "AQABSI_CLICKUP_WORKSPACE_ID": "901",
                "AQABSI_CLICKUP_LIST_ID": "list-42",
            }
        )
        draft = {
            "dry_run": True,
            "publication_requires_authorization": True,
            "tasks": [self.task(assignee_id="not-numeric")],
        }
        with mock.patch.object(
            publisher, "request_json", side_effect=AssertionError("network used")
        ):
            with self.assertRaisesRegex(publisher.PublicationError, "assignee"):
                publisher.publish_clickup(draft, config.clickup, "APPROVED-001")

    def test_malformed_ownership_registry_is_rejected_before_network(self):
        config_module, publisher = self.load_modules()
        config = config_module.load_integration_config(
            {
                "AQABSI_CLICKUP_API_TOKEN": "private-token",
                "AQABSI_CLICKUP_WORKSPACE_ID": "901",
                "AQABSI_CLICKUP_LIST_ID": "list-42",
            }
        )
        draft = {
            "dry_run": True,
            "publication_requires_authorization": True,
            "tasks": [self.task()],
        }
        with mock.patch.object(
            publisher, "request_json", side_effect=AssertionError("network used")
        ):
            with self.assertRaisesRegex(publisher.PublicationError, "teams"):
                publisher.publish_clickup(
                    draft,
                    config.clickup,
                    "APPROVED-001",
                    {"teams": []},
                )
            with self.assertRaisesRegex(publisher.PublicationError, "clickup_user_id"):
                publisher.publish_clickup(
                    draft,
                    config.clickup,
                    "APPROVED-001",
                    {"teams": {"backend": {}}},
                )

    def test_confluence_data_center_creates_then_updates_same_page(self):
        config_module, publisher = self.load_modules()
        state = {"page": None, "version": 0}

        def dispatch(request):
            if request["method"] == "GET" and request["path"] == "/confluence/rest/api/user/current":
                return 200, {"username": "qa-user", "displayName": "QA User"}
            if request["method"] == "GET" and request["path"] == "/confluence/rest/api/space/QA":
                return 200, {"id": "space-1", "key": "QA", "name": "Quality"}
            if request["method"] == "GET" and request["path"].startswith(
                "/confluence/rest/api/content/search?"
            ):
                results = []
                if state["page"]:
                    results.append(
                        {
                            "id": state["page"],
                            "version": {"number": state["version"]},
                            "space": {"key": "QA"},
                            "body": {
                                "storage": {
                                    "value": "<p>AQABSI-RUN-ID: AQABSI-RUN-001</p>"
                                }
                            },
                        }
                    )
                return 200, {"results": results}
            if request["method"] == "POST" and request["path"] == "/confluence/rest/api/content":
                state["page"] = "page-1"
                state["version"] = 1
                return 200, {"id": "page-1", "_links": {"webui": "/display/QA/page-1"}}
            if request["method"] == "PUT" and request["path"] == "/confluence/rest/api/content/page-1":
                state["version"] = request["body"]["version"]["number"]
                return 200, {"id": "page-1", "_links": {"webui": "/display/QA/page-1"}}
            return 404, {"message": "missing"}

        with tempfile.TemporaryDirectory() as tmp, FakePublisherServer(dispatch) as server:
            confluence, _ = self.write_drafts(Path(tmp))
            draft = json.loads(confluence.read_text())
            config = config_module.load_integration_config(
                {
                    "AQABSI_CONFLUENCE_DEPLOYMENT": "data_center",
                    "AQABSI_CONFLUENCE_BASE_URL": server.base_url + "/confluence",
                    "AQABSI_CONFLUENCE_PAT": "private-pat",
                    "AQABSI_CONFLUENCE_SPACE_KEY": "QA",
                }
            )
            created = publisher.publish_confluence(
                draft, config.confluence, "APPROVED-001"
            )
            draft["suggested_title"] = "Corrected QA report title"
            draft["body"] = "# Updated report\n\nNew evidence body"
            updated = publisher.publish_confluence(
                draft, config.confluence, "APPROVED-001"
            )

        self.assertEqual(created.status, "created")
        self.assertEqual(updated.status, "updated")
        self.assertEqual(state["version"], 2)
        self.assertEqual(
            len([item for item in server.requests if item["method"] == "POST"]), 1
        )
        write_bodies = [
            item["body"] for item in server.requests if item["method"] in {"POST", "PUT"}
        ]
        serialized = json.dumps(write_bodies)
        self.assertIn("&lt;script&gt;unsafe()&lt;/script&gt;", serialized)
        self.assertNotIn("<script>unsafe()</script>", serialized)
        put_request = next(
            item for item in server.requests if item["method"] == "PUT"
        )
        updated_storage = put_request["body"]["body"]["storage"]["value"]
        self.assertIsInstance(updated_storage, str)
        self.assertIn("Updated report", updated_storage)
        self.assertIn("AQABSI-RUN-ID: AQABSI-RUN-001", updated_storage)

    def test_confluence_cloud_create_uses_verified_space_and_run_marker(self):
        config_module, publisher = self.load_modules()

        def dispatch(request):
            if request["path"] == "/wiki/rest/api/user/current":
                return 200, {"accountId": "acct-7", "displayName": "QA User"}
            if request["path"] == "/wiki/api/v2/spaces/123":
                return 200, {"id": "123", "key": "QA", "name": "Quality"}
            if request["method"] == "GET" and request["path"].startswith(
                "/wiki/rest/api/content/search?"
            ):
                return 200, {"results": []}
            if request["method"] == "POST" and request["path"] == "/wiki/api/v2/pages":
                return 200, {"id": "page-cloud-1", "_links": {"webui": "/spaces/QA/pages/1"}}
            return 404, {"message": "missing"}

        with tempfile.TemporaryDirectory() as tmp, FakePublisherServer(dispatch) as server:
            confluence, _ = self.write_drafts(Path(tmp))
            config = config_module.load_integration_config(
                {
                    "AQABSI_CONFLUENCE_DEPLOYMENT": "cloud",
                    "AQABSI_CONFLUENCE_BASE_URL": server.base_url + "/wiki",
                    "AQABSI_CONFLUENCE_EMAIL": "qa@example.test",
                    "AQABSI_CONFLUENCE_API_TOKEN": "cloud-secret",
                    "AQABSI_CONFLUENCE_SPACE_ID": "123",
                }
            )
            result = publisher.publish_confluence(
                json.loads(confluence.read_text()),
                config.confluence,
                "APPROVED-001",
            )

        self.assertEqual(result.status, "created")
        self.assertEqual(result.external_id, "page-cloud-1")
        post = next(item for item in server.requests if item["method"] == "POST")
        self.assertEqual(post["body"]["spaceId"], "123")
        self.assertIn("AQABSI-RUN-ID: AQABSI-RUN-001", post["body"]["body"]["value"])
        search = next(
            item
            for item in server.requests
            if item["method"] == "GET" and "/content/search?" in item["path"]
        )
        self.assertIn("AQABSI-RUN-ID", search["path"])
        self.assertIn("space+%3D+%22QA%22", search["path"])
        self.assertNotIn("space+%3D+%22123%22", search["path"])

    def test_clickup_creates_then_skips_existing_fingerprint(self):
        config_module, publisher = self.load_modules()
        state = {"tasks": []}

        def dispatch(request):
            if request["method"] == "GET" and request["path"] == "/api/v2/user":
                return 200, {"user": {"id": 7, "username": "QA User"}}
            if request["method"] == "GET" and request["path"] == "/api/v2/list/list-42":
                return 200, {
                    "id": "list-42",
                    "name": "Defects",
                    "space": {"id": "space-7"},
                }
            if request["method"] == "GET" and request["path"] == "/api/v2/team/901/space?archived=true":
                return 200, {"spaces": [{"id": "space-7", "name": "Engineering"}]}
            if request["method"] == "GET":
                return 200, {"tasks": state["tasks"], "last_page": True}
            if request["method"] == "POST":
                task = {
                    "id": "task-1",
                    "name": request["body"]["name"],
                    "description": request["body"]["description"],
                    "url": "https://app.clickup.com/t/task-1",
                }
                state["tasks"].append(task)
                return 200, task
            return 404, {"message": "missing"}

        with FakePublisherServer(dispatch) as server:
            config = config_module.load_integration_config(
                {
                    "AQABSI_CLICKUP_API_TOKEN": "private-token",
                    "AQABSI_CLICKUP_WORKSPACE_ID": "901",
                    "AQABSI_CLICKUP_LIST_ID": "list-42",
                }
            )
            draft = {
                "dry_run": True,
                "publication_requires_authorization": True,
                "tasks": [self.task()],
            }
            with mock.patch.object(
                publisher, "CLICKUP_API_BASE", server.base_url + "/api/v2"
            ):
                created = publisher.publish_clickup(
                    draft, config.clickup, "APPROVED-001"
                )
                existing = publisher.publish_clickup(
                    draft, config.clickup, "APPROVED-001"
                )

        self.assertEqual(created[0].status, "created")
        self.assertEqual(existing[0].status, "existing")
        self.assertEqual(
            len([item for item in server.requests if item["method"] == "POST"]), 1
        )

    def test_clickup_publication_blocks_wrong_workspace_before_write(self):
        config_module, publisher = self.load_modules()

        def dispatch(request):
            if request["path"] == "/api/v2/user":
                return 200, {"user": {"id": 7, "username": "QA User"}}
            if request["path"] == "/api/v2/list/list-42":
                return 200, {
                    "id": "list-42",
                    "name": "Defects",
                    "space": {"id": "space-999"},
                }
            if request["path"] == "/api/v2/team/901/space?archived=true":
                return 200, {"spaces": [{"id": "space-7", "name": "Engineering"}]}
            return 500, {"message": "write must not run"}

        with FakePublisherServer(dispatch) as server:
            config = config_module.load_integration_config(
                {
                    "AQABSI_CLICKUP_API_TOKEN": "private-token",
                    "AQABSI_CLICKUP_WORKSPACE_ID": "901",
                    "AQABSI_CLICKUP_LIST_ID": "list-42",
                }
            )
            draft = {
                "dry_run": True,
                "publication_requires_authorization": True,
                "tasks": [self.task()],
            }
            with mock.patch.object(
                publisher, "CLICKUP_API_BASE", server.base_url + "/api/v2"
            ):
                with self.assertRaisesRegex(
                    publisher.PublicationError, "verification failed"
                ):
                    publisher.publish_clickup(
                        draft, config.clickup, "APPROVED-001"
                    )

        self.assertEqual(
            [item for item in server.requests if item["method"] == "POST"], []
        )

    def test_clickup_partial_failure_preserves_success_and_stops_provider(self):
        config_module, publisher = self.load_modules()
        state = {"posts": 0}

        def dispatch(request):
            if request["method"] == "GET" and request["path"] == "/api/v2/user":
                return 200, {"user": {"id": 7, "username": "QA User"}}
            if request["method"] == "GET" and request["path"] == "/api/v2/list/list-42":
                return 200, {
                    "id": "list-42",
                    "name": "Defects",
                    "space": {"id": "space-7"},
                }
            if request["method"] == "GET" and request["path"] == "/api/v2/team/901/space?archived=true":
                return 200, {"spaces": [{"id": "space-7", "name": "Engineering"}]}
            if request["method"] == "GET":
                return 200, {"tasks": [], "last_page": True}
            if request["method"] == "POST":
                state["posts"] += 1
                if state["posts"] == 1:
                    return 200, {"id": "task-1", "url": "https://app.clickup.com/t/task-1"}
                return 500, {"message": "provider failed private-token"}
            return 404, {"message": "missing"}

        with FakePublisherServer(dispatch) as server:
            config = config_module.load_integration_config(
                {
                    "AQABSI_CLICKUP_API_TOKEN": "private-token",
                    "AQABSI_CLICKUP_WORKSPACE_ID": "901",
                    "AQABSI_CLICKUP_LIST_ID": "list-42",
                }
            )
            draft = {
                "dry_run": True,
                "publication_requires_authorization": True,
                "tasks": [
                    self.task("a" * 64, name="First"),
                    self.task("b" * 64, name="Second"),
                    self.task("c" * 64, name="Must not run"),
                ],
            }
            with mock.patch.object(
                publisher, "CLICKUP_API_BASE", server.base_url + "/api/v2"
            ):
                results = publisher.publish_clickup(
                    draft, config.clickup, "APPROVED-001"
                )

        self.assertEqual([item.status for item in results], ["created", "unknown"])
        self.assertEqual(results[0].external_id, "task-1")
        self.assertTrue(results[1].reconciliation_required)
        self.assertNotIn("private-token", json.dumps([item.to_dict() for item in results]))
        self.assertEqual(state["posts"], 2)

    def test_clickup_pagination_bound_fails_closed(self):
        config_module, publisher = self.load_modules()
        config = config_module.load_integration_config(
            {
                "AQABSI_CLICKUP_API_TOKEN": "private-token",
                "AQABSI_CLICKUP_WORKSPACE_ID": "901",
                "AQABSI_CLICKUP_LIST_ID": "list-42",
            }
        )

        def dispatch(request):
            return 200, {
                "tasks": [
                    {"id": f"task-{len(server.requests)}", "description": ""}
                ],
                "last_page": False,
            }

        with FakePublisherServer(dispatch) as server:
            with mock.patch.object(
                publisher, "CLICKUP_API_BASE", server.base_url + "/api/v2"
            ):
                tasks, error = publisher._list_clickup_tasks(
                    config.clickup, {"Authorization": "private-token"}
                )

        self.assertEqual(tasks, [])
        self.assertIsNotNone(error)
        self.assertIn("incomplete", error.error.lower())

    def test_existing_clickup_fingerprint_without_task_id_fails_closed(self):
        config_module, publisher = self.load_modules()

        def dispatch(request):
            if request["path"] == "/api/v2/user":
                return 200, {"user": {"id": 7, "username": "QA User"}}
            if request["path"] == "/api/v2/list/list-42":
                return 200, {
                    "id": "list-42",
                    "name": "Defects",
                    "space": {"id": "space-7"},
                }
            if request["path"] == "/api/v2/team/901/space?archived=true":
                return 200, {"spaces": [{"id": "space-7", "name": "Engineering"}]}
            if request["method"] == "GET":
                return 200, {
                    "tasks": [
                        {"description": f"AQABSI-FINGERPRINT: {'a' * 64}"}
                    ],
                    "last_page": True,
                }
            return 500, {"message": "write must not run"}

        with FakePublisherServer(dispatch) as server:
            config = config_module.load_integration_config(
                {
                    "AQABSI_CLICKUP_API_TOKEN": "private-token",
                    "AQABSI_CLICKUP_WORKSPACE_ID": "901",
                    "AQABSI_CLICKUP_LIST_ID": "list-42",
                }
            )
            draft = {
                "dry_run": True,
                "publication_requires_authorization": True,
                "tasks": [self.task()],
            }
            with mock.patch.object(
                publisher, "CLICKUP_API_BASE", server.base_url + "/api/v2"
            ):
                results = publisher.publish_clickup(
                    draft, config.clickup, "APPROVED-001"
                )

        self.assertEqual(results[0].status, "failed")
        self.assertEqual(results[0].action, "search")
        self.assertEqual(
            [item for item in server.requests if item["method"] == "POST"], []
        )

    def test_malformed_create_response_is_not_reported_as_success(self):
        config_module, publisher = self.load_modules()

        def dispatch(request):
            if request["method"] == "GET" and request["path"] == "/api/v2/user":
                return 200, {"user": {"id": 7, "username": "QA User"}}
            if request["method"] == "GET" and request["path"] == "/api/v2/list/list-42":
                return 200, {
                    "id": "list-42",
                    "name": "Defects",
                    "space": {"id": "space-7"},
                }
            if request["method"] == "GET" and request["path"] == "/api/v2/team/901/space?archived=true":
                return 200, {"spaces": [{"id": "space-7", "name": "Engineering"}]}
            if request["method"] == "GET":
                return 200, {"tasks": [], "last_page": True}
            return 200, {"message": "login page"}

        with FakePublisherServer(dispatch) as server:
            config = config_module.load_integration_config(
                {
                    "AQABSI_CLICKUP_API_TOKEN": "private-token",
                    "AQABSI_CLICKUP_WORKSPACE_ID": "901",
                    "AQABSI_CLICKUP_LIST_ID": "list-42",
                }
            )
            draft = {
                "dry_run": True,
                "publication_requires_authorization": True,
                "tasks": [self.task()],
            }
            with mock.patch.object(
                publisher, "CLICKUP_API_BASE", server.base_url + "/api/v2"
            ):
                results = publisher.publish_clickup(
                    draft, config.clickup, "APPROVED-001"
                )

        self.assertEqual(results[0].status, "unknown")
        self.assertIsNone(results[0].external_id)
        self.assertTrue(results[0].reconciliation_required)

    def test_malformed_confluence_search_fails_closed_without_write(self):
        config_module, publisher = self.load_modules()

        def dispatch(request):
            if request["path"] == "/confluence/rest/api/user/current":
                return 200, {"username": "qa-user", "displayName": "QA User"}
            if request["path"] == "/confluence/rest/api/space/QA":
                return 200, {"id": "space-1", "key": "QA", "name": "Quality"}
            if request["method"] == "GET":
                return 200, {"message": "login page"}
            return 500, {"message": "write must not run"}

        with tempfile.TemporaryDirectory() as tmp, FakePublisherServer(dispatch) as server:
            confluence, _ = self.write_drafts(Path(tmp))
            config = config_module.load_integration_config(
                {
                    "AQABSI_CONFLUENCE_DEPLOYMENT": "data_center",
                    "AQABSI_CONFLUENCE_BASE_URL": server.base_url + "/confluence",
                    "AQABSI_CONFLUENCE_PAT": "private-pat",
                    "AQABSI_CONFLUENCE_SPACE_KEY": "QA",
                }
            )
            result = publisher.publish_confluence(
                json.loads(confluence.read_text()),
                config.confluence,
                "APPROVED-001",
            )

        self.assertEqual(result.status, "failed")
        self.assertEqual(result.action, "search")
        self.assertEqual(
            [item for item in server.requests if item["method"] in {"POST", "PUT"}],
            [],
        )

    def test_null_confluence_search_candidate_fails_closed_without_write(self):
        config_module, publisher = self.load_modules()

        def dispatch(request):
            if request["path"] == "/confluence/rest/api/user/current":
                return 200, {"username": "qa-user", "displayName": "QA User"}
            if request["path"] == "/confluence/rest/api/space/QA":
                return 200, {"id": "space-1", "key": "QA", "name": "Quality"}
            if request["method"] == "GET":
                return 200, {"results": [None]}
            return 500, {"message": "write must not run"}

        with tempfile.TemporaryDirectory() as tmp, FakePublisherServer(dispatch) as server:
            confluence, _ = self.write_drafts(Path(tmp))
            config = config_module.load_integration_config(
                {
                    "AQABSI_CONFLUENCE_DEPLOYMENT": "data_center",
                    "AQABSI_CONFLUENCE_BASE_URL": server.base_url + "/confluence",
                    "AQABSI_CONFLUENCE_PAT": "private-pat",
                    "AQABSI_CONFLUENCE_SPACE_KEY": "QA",
                }
            )
            result = publisher.publish_confluence(
                json.loads(confluence.read_text()),
                config.confluence,
                "APPROVED-001",
            )

        self.assertEqual(result.status, "failed")
        self.assertEqual(
            [item for item in server.requests if item["method"] in {"POST", "PUT"}],
            [],
        )

    def test_confluence_run_marker_prefix_collision_fails_closed(self):
        config_module, publisher = self.load_modules()

        def dispatch(request):
            if request["path"] == "/confluence/rest/api/user/current":
                return 200, {"username": "qa-user", "displayName": "QA User"}
            if request["path"] == "/confluence/rest/api/space/QA":
                return 200, {"id": "space-1", "key": "QA", "name": "Quality"}
            if request["method"] == "GET":
                return 200, {
                    "results": [
                        {
                            "id": "page-other",
                            "version": {"number": 1},
                            "space": {"key": "QA"},
                            "body": {
                                "storage": {
                                    "value": "<p>AQABSI-RUN-ID: AQABSI-RUN-0010</p>"
                                }
                            },
                        }
                    ]
                }
            return 500, {"message": "write must not run"}

        with tempfile.TemporaryDirectory() as tmp, FakePublisherServer(dispatch) as server:
            confluence, _ = self.write_drafts(Path(tmp))
            config = config_module.load_integration_config(
                {
                    "AQABSI_CONFLUENCE_DEPLOYMENT": "data_center",
                    "AQABSI_CONFLUENCE_BASE_URL": server.base_url + "/confluence",
                    "AQABSI_CONFLUENCE_PAT": "private-pat",
                    "AQABSI_CONFLUENCE_SPACE_KEY": "QA",
                }
            )
            result = publisher.publish_confluence(
                json.loads(confluence.read_text()),
                config.confluence,
                "APPROVED-001",
            )

        self.assertEqual(result.status, "failed")
        self.assertIn("exact run marker", result.error)
        self.assertEqual(
            [item for item in server.requests if item["method"] in {"POST", "PUT"}],
            [],
        )

    def test_clickup_missing_tasks_collection_fails_closed_without_write(self):
        config_module, publisher = self.load_modules()

        def dispatch(request):
            if request["path"] == "/api/v2/user":
                return 200, {"user": {"id": 7, "username": "QA User"}}
            if request["path"] == "/api/v2/list/list-42":
                return 200, {
                    "id": "list-42",
                    "name": "Defects",
                    "space": {"id": "space-7"},
                }
            if request["path"] == "/api/v2/team/901/space?archived=true":
                return 200, {"spaces": [{"id": "space-7", "name": "Engineering"}]}
            if request["method"] == "GET":
                return 200, {"message": "login page"}
            return 500, {"message": "write must not run"}

        with FakePublisherServer(dispatch) as server:
            config = config_module.load_integration_config(
                {
                    "AQABSI_CLICKUP_API_TOKEN": "private-token",
                    "AQABSI_CLICKUP_WORKSPACE_ID": "901",
                    "AQABSI_CLICKUP_LIST_ID": "list-42",
                }
            )
            draft = {
                "dry_run": True,
                "publication_requires_authorization": True,
                "tasks": [self.task()],
            }
            with mock.patch.object(
                publisher, "CLICKUP_API_BASE", server.base_url + "/api/v2"
            ):
                results = publisher.publish_clickup(
                    draft, config.clickup, "APPROVED-001"
                )

        self.assertEqual(results[0].status, "failed")
        self.assertEqual(results[0].action, "search")
        self.assertEqual(
            [item for item in server.requests if item["method"] == "POST"], []
        )

    def test_clickup_malformed_task_entry_fails_closed_without_write(self):
        config_module, publisher = self.load_modules()

        def dispatch(request):
            if request["path"] == "/api/v2/user":
                return 200, {"user": {"id": 7, "username": "QA User"}}
            if request["path"] == "/api/v2/list/list-42":
                return 200, {
                    "id": "list-42",
                    "name": "Defects",
                    "space": {"id": "space-7"},
                }
            if request["path"] == "/api/v2/team/901/space?archived=true":
                return 200, {"spaces": [{"id": "space-7", "name": "Engineering"}]}
            if request["method"] == "GET":
                return 200, {"tasks": [None], "last_page": True}
            return 500, {"message": "write must not run"}

        with FakePublisherServer(dispatch) as server:
            config = config_module.load_integration_config(
                {
                    "AQABSI_CLICKUP_API_TOKEN": "private-token",
                    "AQABSI_CLICKUP_WORKSPACE_ID": "901",
                    "AQABSI_CLICKUP_LIST_ID": "list-42",
                }
            )
            draft = {
                "dry_run": True,
                "publication_requires_authorization": True,
                "tasks": [self.task()],
            }
            with mock.patch.object(
                publisher, "CLICKUP_API_BASE", server.base_url + "/api/v2"
            ):
                results = publisher.publish_clickup(
                    draft, config.clickup, "APPROVED-001"
                )

        self.assertEqual(results[0].status, "failed")
        self.assertEqual(results[0].action, "search")
        self.assertEqual(
            [item for item in server.requests if item["method"] == "POST"], []
        )

    def test_draft_parent_is_verified_before_confluence_write(self):
        config_module, publisher = self.load_modules()

        def dispatch(request):
            if request["path"] == "/wiki/rest/api/user/current":
                return 200, {"accountId": "acct-7", "displayName": "QA User"}
            if request["path"] == "/wiki/api/v2/spaces/123":
                return 200, {"id": "123", "key": "QA", "name": "Quality"}
            if request["path"] == "/wiki/api/v2/pages/draft-parent":
                return 200, {
                    "id": "draft-parent",
                    "spaceId": "999",
                    "title": "Wrong space",
                }
            return 500, {"message": "write must not run"}

        with tempfile.TemporaryDirectory() as tmp, FakePublisherServer(dispatch) as server:
            confluence, _ = self.write_drafts(Path(tmp))
            draft = json.loads(confluence.read_text())
            draft["parent_page_id"] = "draft-parent"
            config = config_module.load_integration_config(
                {
                    "AQABSI_CONFLUENCE_DEPLOYMENT": "cloud",
                    "AQABSI_CONFLUENCE_BASE_URL": server.base_url + "/wiki",
                    "AQABSI_CONFLUENCE_EMAIL": "qa@example.test",
                    "AQABSI_CONFLUENCE_API_TOKEN": "cloud-secret",
                    "AQABSI_CONFLUENCE_SPACE_ID": "123",
                }
            )
            with self.assertRaisesRegex(
                publisher.PublicationError, "verification failed"
            ):
                publisher.publish_confluence(
                    draft, config.confluence, "APPROVED-001"
                )

        self.assertEqual(
            [item for item in server.requests if item["method"] in {"POST", "PUT"}],
            [],
        )

    def test_dry_run_plan_redacts_configured_secrets_from_preview(self):
        _, publisher = self.load_modules()
        token = "configured-cloud-secret"
        with tempfile.TemporaryDirectory() as tmp:
            confluence, _ = self.write_drafts(Path(tmp))
            draft = json.loads(confluence.read_text())
            draft["body"] = f"# QA report\n\nObserved accidental value: {token}"
            confluence.write_text(json.dumps(draft), encoding="utf-8")
            stdout = io.StringIO()
            with mock.patch.dict(
                os.environ,
                {
                    "AQABSI_CONFLUENCE_DEPLOYMENT": "cloud",
                    "AQABSI_CONFLUENCE_BASE_URL": "https://docs.example.test/wiki",
                    "AQABSI_CONFLUENCE_EMAIL": "qa@example.test",
                    "AQABSI_CONFLUENCE_API_TOKEN": token,
                    "AQABSI_CONFLUENCE_SPACE_ID": "123",
                },
                clear=True,
            ), redirect_stdout(stdout):
                code = publisher.main(
                    ["--confluence-draft", str(confluence)]
                )

        self.assertEqual(code, 0)
        self.assertNotIn(token, stdout.getvalue())
        self.assertIn("[REDACTED]", stdout.getvalue())

    def test_cli_uses_ownership_registry_environment_when_flag_is_absent(self):
        config_module, publisher = self.load_modules()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, clickup = self.write_drafts(root, tasks=[self.task()])
            registry = root / "ownership.json"
            registry.write_text(
                json.dumps({"teams": {"backend": {"clickup_user_id": "77"}}}),
                encoding="utf-8",
            )
            config = config_module.load_integration_config(
                {
                    "AQABSI_CLICKUP_API_TOKEN": "private-token",
                    "AQABSI_CLICKUP_WORKSPACE_ID": "901",
                    "AQABSI_CLICKUP_LIST_ID": "list-42",
                }
            )
            verified = publisher.ProviderVerification(
                "verified", identity={"id": "qa"}, destination={"id": "list-42"}
            )
            stdout = io.StringIO()
            with mock.patch.dict(
                os.environ,
                {
                    "AQABSI_CLICKUP_API_TOKEN": "private-token",
                    "AQABSI_CLICKUP_WORKSPACE_ID": "901",
                    "AQABSI_CLICKUP_LIST_ID": "list-42",
                    "AQABSI_OWNERSHIP_REGISTRY": str(registry),
                },
                clear=True,
            ), mock.patch.object(
                publisher, "load_integration_config", return_value=config
            ), mock.patch.object(
                publisher, "verify_clickup", return_value=verified
            ), mock.patch.object(
                publisher,
                "publish_clickup",
                return_value=[
                    publisher.MutationResult(
                        "clickup", "created", "create", external_id="task-1"
                    )
                ],
            ) as publish_mock, redirect_stdout(stdout):
                code = publisher.main(
                    [
                        "--provider",
                        "clickup",
                        "--clickup-draft",
                        str(clickup),
                        "--execute",
                        "--authorization-reference",
                        "APPROVED-001",
                    ]
                )

        self.assertEqual(code, 0)
        self.assertEqual(publish_mock.call_args.args[3], registry)

    def test_existing_receipt_blocks_before_any_network_or_mutation(self):
        _, publisher = self.load_modules()
        with tempfile.TemporaryDirectory() as tmp:
            confluence, _ = self.write_drafts(Path(tmp))
            receipt = Path(tmp) / "receipt.json"
            receipt.write_text("existing", encoding="utf-8")
            with mock.patch.object(
                publisher,
                "request_json",
                side_effect=AssertionError("network used before receipt validation"),
            ):
                stdout = io.StringIO()
                stderr = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    code = publisher.main(
                        [
                            "--provider",
                            "confluence",
                            "--confluence-draft",
                            str(confluence),
                            "--execute",
                            "--authorization-reference",
                            "APPROVED-001",
                            "--receipt",
                            str(receipt),
                        ]
                    )

        self.assertEqual(code, 2)
        self.assertIn("already exists", stderr.getvalue())

    def test_cli_emits_partial_receipt_when_later_provider_raises(self):
        config_module, publisher = self.load_modules()
        with tempfile.TemporaryDirectory() as tmp:
            confluence, clickup = self.write_drafts(
                Path(tmp), tasks=[self.task()]
            )
            verified = publisher.ProviderVerification(
                "verified", identity={"id": "qa"}, destination={"id": "dest"}
            )
            config = config_module.load_integration_config(
                {
                    "AQABSI_CONFLUENCE_DEPLOYMENT": "cloud",
                    "AQABSI_CONFLUENCE_BASE_URL": "https://docs.example.test/wiki",
                    "AQABSI_CONFLUENCE_EMAIL": "qa@example.test",
                    "AQABSI_CONFLUENCE_API_TOKEN": "cloud-secret",
                    "AQABSI_CONFLUENCE_SPACE_ID": "123",
                    "AQABSI_CLICKUP_API_TOKEN": "private-token",
                    "AQABSI_CLICKUP_WORKSPACE_ID": "901",
                    "AQABSI_CLICKUP_LIST_ID": "list-42",
                }
            )
            stdout = io.StringIO()
            stderr = io.StringIO()
            with mock.patch.object(
                publisher, "load_integration_config", return_value=config
            ), mock.patch.object(
                publisher, "verify_confluence", return_value=verified
            ), mock.patch.object(
                publisher, "verify_clickup", return_value=verified
            ), mock.patch.object(
                publisher,
                "publish_confluence",
                return_value=publisher.MutationResult(
                    "confluence", "created", "create", external_id="page-1"
                ),
            ), mock.patch.object(
                publisher,
                "publish_clickup",
                side_effect=publisher.PublicationError("later provider rejected"),
            ), redirect_stdout(stdout), redirect_stderr(stderr):
                code = publisher.main(
                    [
                        "--provider",
                        "confluence",
                        "--provider",
                        "clickup",
                        "--confluence-draft",
                        str(confluence),
                        "--clickup-draft",
                        str(clickup),
                        "--execute",
                        "--authorization-reference",
                        "APPROVED-001",
                    ]
                )

        self.assertEqual(code, 4)
        receipt = json.loads(stdout.getvalue())
        self.assertEqual(receipt["status"], "partial_failure")
        self.assertEqual(receipt["mutations"][0]["external_id"], "page-1")


if __name__ == "__main__":
    unittest.main()
