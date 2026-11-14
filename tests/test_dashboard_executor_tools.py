import csv
import importlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
FIXTURE = ROOT / "tests" / "fixtures" / "sample-run.json"


def load_module(name):
    sys.path.insert(0, str(SCRIPTS))
    try:
        return importlib.import_module(name)
    finally:
        if sys.path and sys.path[0] == str(SCRIPTS):
            sys.path.pop(0)


class GenerateDashboardTest(unittest.TestCase):
    def test_generates_self_contained_sanitized_dashboard(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "dashboard"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "generate_dashboard.py"),
                    str(FIXTURE),
                    str(output_dir),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual({path.name for path in output_dir.iterdir()}, {"dashboard.html"})
            html = (output_dir / "dashboard.html").read_text(encoding="utf-8")
            self.assertIn("Coverage matrix", html)
            self.assertIn("FR-AUTH-001", html)
            self.assertIn("TC-AUTH-002", html)
            self.assertIn("Summary", html)
            self.assertIn("Log Report", html)
            self.assertIn("Domain", html)
            self.assertIn("ev-line", html)
            self.assertIn("domain-be", html)
            self.assertIn("case-row", html)
            self.assertIn("detail-row", html)
            self.assertIn("caret", html)
            self.assertIn("actual-box", html)
            self.assertIn("Execution log / Evidence", html)
            self.assertNotIn("SuperSecret!", html)
            self.assertNotIn("wrong-password", html)
            self.assertNotIn("eyJhbGciOiJIUzI1NiJ9.secret.signature", html)
            self.assertNotIn("__AQABSI_DATA__", html)


class ExecutorTest(unittest.TestCase):
    def test_classify_status_is_deterministic(self):
        executor = load_module("executor")
        self.assertEqual(executor.classify_status(200, 200, None), "pass")
        self.assertEqual(executor.classify_status(200, 401, None), "fail")
        self.assertEqual(executor.classify_status(401, None, None), "fail")
        self.assertEqual(executor.classify_status(301, None, None), "pass")
        self.assertEqual(executor.classify_status(None, None, None), "environment_error")
        self.assertEqual(executor.classify_status(401, None, False), "pass")
        self.assertEqual(executor.classify_status(200, None, False), "fail")

    def test_resolve_target_from_steps_and_expected_status(self):
        executor = load_module("executor")
        case = {
            "steps": ["POST /api/v1/login"],
            "test_data": {},
            "expected_result": "HTTP 200 returns an authenticated session.",
        }
        target = executor.resolve_target(case)
        self.assertEqual(target["method"], "POST")
        self.assertEqual(target["path"], "/api/v1/login")
        self.assertEqual(target["expected_status"], 200)

    def test_redact_text_removes_bearer_and_jwt(self):
        executor = load_module("executor")
        redacted = executor.redact_text(
            "Authorization: Bearer secret-token body eyJhbGciOiJIUzI1NiJ9.secret.signature",
            ("secret-token",),
        )
        self.assertNotIn("secret-token", redacted)
        self.assertIn("[REDACTED]", redacted)


class FlakinessTest(unittest.TestCase):
    def test_classify_flakiness_outcomes(self):
        flakiness = load_module("flakiness")
        self.assertEqual(flakiness.classify_flakiness("fail", 0, 3), ("fail", "Consistent failure across re-runs."))
        self.assertEqual(flakiness.classify_flakiness("fail", 1, 3)[0], "flaky")
        self.assertEqual(flakiness.classify_flakiness("fail", 3, 3)[0], "flaky")
        self.assertEqual(flakiness.classify_flakiness("environment_error", 3, 3)[0], "pass")


class ChangeImpactTest(unittest.TestCase):
    def test_map_file_module_by_path_convention(self):
        change_impact = load_module("change_impact")
        self.assertEqual(change_impact.map_file_module("app/Http/Controllers/BusinessProcessController.php")[0], "businessprocess")
        self.assertEqual(change_impact.map_file_module("app/Services/AuthService.php")[0], "auth")
        self.assertEqual(change_impact.map_file_module("app/Repositories/ServiceRepository.php")[0], "service")
        self.assertEqual(change_impact.map_file_module("routes/web.php")[0], "*")
        self.assertEqual(change_impact.map_file_module("README.md")[0], None)

    def test_select_affected_cases_by_module_and_routes(self):
        change_impact = load_module("change_impact")
        cases = [
            {"id": "TC-1", "module": "Business Process", "feature": "Create"},
            {"id": "TC-2", "module": "Authentication", "feature": "Login"},
        ]
        affected = change_impact.select_affected_cases(
            cases, ["app/Http/Controllers/BusinessProcessController.php"]
        )
        self.assertEqual([item["id"] for item in affected], ["TC-1"])
        self.assertEqual(affected[0]["matched_modules"], ["businessprocess"])

        all_affected = change_impact.select_affected_cases(cases, ["routes/web.php"])
        self.assertEqual(len(all_affected), 2)


class GenerateArtifactsDomainTest(unittest.TestCase):
    def run_generator(self, output_dir):
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "generate_artifacts.py"),
                str(FIXTURE),
                str(output_dir),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_domain_and_inline_execution_logs_are_rendered(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "artifacts"
            result = self.run_generator(output_dir)
            self.assertEqual(result.returncode, 0, result.stderr)

            with (output_dir / "test-cases.csv").open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["Domain"], "FE")  # e2e layer
            self.assertEqual(rows[1]["Domain"], "BE")  # api layer

            clickup = json.loads((output_dir / "clickup-drafts.json").read_text())
            task = clickup["tasks"][0]
            self.assertIn("[BE]", task["name"])
            self.assertIn("Execution log", task["description_markdown"])
            self.assertIn("Actual result", task["description_markdown"])
            self.assertIn("evidence/TC-AUTH-002-response.json", task["description_markdown"])

            confluence = json.loads((output_dir / "confluence-draft.json").read_text())
            self.assertIn("Failed test case execution logs", confluence["body"])
            self.assertIn("**Domain:** BE", confluence["body"])

            report = (output_dir / "qa-report.md").read_text()
            self.assertIn("Failed test case execution logs", report)
            self.assertIn("| Domain |", report)

    def test_resolve_domain_honours_explicit_field_and_layer(self):
        generate_artifacts = load_module("generate_artifacts")
        self.assertEqual(generate_artifacts.resolve_domain({"layer": "api"}), "BE")
        self.assertEqual(generate_artifacts.resolve_domain({"layer": "e2e"}), "FE")
        self.assertEqual(generate_artifacts.resolve_domain({"layer": "unit"}), "BE")
        self.assertEqual(generate_artifacts.resolve_domain({"layer": "api", "domain": "FE"}), "FE")
        self.assertEqual(generate_artifacts.resolve_domain({"layer": "api", "tag": "both"}), "both")


if __name__ == "__main__":
    unittest.main()
