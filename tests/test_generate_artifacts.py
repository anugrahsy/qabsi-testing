import csv
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate_artifacts.py"
FIXTURE = ROOT / "tests" / "fixtures" / "sample-run.json"


class GenerateArtifactsTest(unittest.TestCase):
    def run_generator(self, input_path: Path, output_dir: Path):
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(input_path), str(output_dir)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_generates_sanitized_deterministic_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "artifacts"
            result = self.run_generator(FIXTURE, output_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            expected = {
                "qa-report.md",
                "test-cases.csv",
                "test-cases.xlsx",
                "confluence-draft.json",
                "clickup-drafts.json",
                "sanitized-run.json",
            }
            self.assertEqual({path.name for path in output_dir.iterdir()}, expected)

            combined = "\n".join(
                path.read_text(errors="ignore")
                for path in output_dir.iterdir()
                if path.suffix != ".xlsx"
            )
            self.assertNotIn("SuperSecret!", combined)
            self.assertNotIn("wrong-password", combined)
            self.assertNotIn("eyJhbGciOiJIUzI1NiJ9.secret.signature", combined)
            self.assertIn("[REDACTED]", combined)

            with (output_dir / "test-cases.csv").open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual([row["Test Case ID"] for row in rows], ["TC-AUTH-001", "TC-AUTH-002"])
            self.assertEqual(rows[1]["Requirement IDs"], "FR-AUTH-002")
            self.assertEqual(rows[1]["Status"], "fail")

            with zipfile.ZipFile(output_dir / "test-cases.xlsx") as workbook:
                self.assertIn("xl/worksheets/sheet1.xml", workbook.namelist())
                for name in workbook.namelist():
                    if name.endswith((".xml", ".rels")):
                        ET.fromstring(workbook.read(name))
                sheet = workbook.read("xl/worksheets/sheet1.xml").decode()
                self.assertIn("TC-AUTH-002", sheet)
                self.assertIn("environment_error", sheet)

            clickup = json.loads((output_dir / "clickup-drafts.json").read_text())
            self.assertTrue(clickup["dry_run"])
            self.assertEqual(len(clickup["tasks"]), 1)
            self.assertRegex(clickup["tasks"][0]["fingerprint"], r"^[a-f0-9]{64}$")
            self.assertIsNone(clickup["tasks"][0]["assignee_id"])

            first = (output_dir / "clickup-drafts.json").read_bytes()
            second_dir = Path(tmp) / "second"
            second = self.run_generator(FIXTURE, second_dir)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(first, (second_dir / "clickup-drafts.json").read_bytes())

    def test_rejects_invalid_manifest_without_writing_partial_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid = Path(tmp) / "invalid.json"
            invalid.write_text(json.dumps({"title": "Missing required fields"}))
            output_dir = Path(tmp) / "artifacts"

            result = self.run_generator(invalid, output_dir)

            self.assertEqual(result.returncode, 2)
            self.assertIn("run_id", result.stderr)
            self.assertFalse(output_dir.exists())

    def test_refuses_to_overwrite_existing_output_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "artifacts"
            output_dir.mkdir()
            sentinel = output_dir / "keep.txt"
            sentinel.write_text("preserve me")

            result = self.run_generator(FIXTURE, output_dir)

            self.assertEqual(result.returncode, 2)
            self.assertIn("choose a new path", result.stderr)
            self.assertEqual(sentinel.read_text(), "preserve me")

    def test_not_run_manifest_without_target_creates_no_defect_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = json.loads(FIXTURE.read_text())
            data["target"] = None
            for case in data["test_cases"]:
                case["status"] = "not_run"
                case["actual_result"] = ""
                case["severity"] = None
            manifest = Path(tmp) / "not-run.json"
            manifest.write_text(json.dumps(data))
            output_dir = Path(tmp) / "artifacts"

            result = self.run_generator(manifest, output_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Target: Not recorded", (output_dir / "qa-report.md").read_text())
            drafts = json.loads((output_dir / "clickup-drafts.json").read_text())
            self.assertEqual(drafts["tasks"], [])

    def test_redacts_confirmation_password_and_verification_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = json.loads(FIXTURE.read_text())
            data["test_cases"][0]["test_data"] = {
                "password_konfirmasi": "synthetic-confirmation-secret",
                "code": "synthetic-current-code",
                "otp_code": "synthetic-current-otp",
            }
            manifest = Path(tmp) / "sensitive-fields.json"
            manifest.write_text(json.dumps(data))
            output_dir = Path(tmp) / "artifacts"

            result = self.run_generator(manifest, output_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            combined = "\n".join(
                path.read_text(errors="ignore")
                for path in output_dir.iterdir()
                if path.suffix != ".xlsx"
            )
            self.assertNotIn("synthetic-confirmation-secret", combined)
            self.assertNotIn("synthetic-current-code", combined)
            self.assertNotIn("synthetic-current-otp", combined)
            self.assertGreaterEqual(combined.count("[REDACTED]"), 3)

    def test_security_access_failure_flows_to_report_workbook_and_clickup(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = json.loads(FIXTURE.read_text())
            data["access_control_matrix"] = [
                {
                    "role": "viewer",
                    "action": "DELETE",
                    "resource": "/api/v1/service/{uuid}",
                    "expected": "HTTP 403 and no data mutation",
                    "actual": "HTTP 200 and the record was soft-deleted",
                    "status": "fail",
                    "test_case_id": "TC-AUTH-002",
                    "error_location": "app/Http/Controllers/ServiceController.php:destroy authorization boundary",
                }
            ]
            data["security_findings"] = [
                {
                    "id": "SEC-AUTHZ-001",
                    "title": "Viewer can delete a service record",
                    "classification": "confirmed",
                    "source_engine": "native-test",
                    "target": "DELETE /api/v1/service/{uuid}",
                    "weakness": "CWE-862 Missing Authorization",
                    "cvss_4_vector": None,
                    "cvss_4_score": None,
                    "business_priority": "unmapped",
                    "expected_result": "Viewer receives HTTP 403 and no record changes.",
                    "actual_result": "Viewer receives HTTP 200 and the record is soft-deleted.",
                    "error_location": "app/Http/Controllers/ServiceController.php:destroy authorization boundary",
                    "evidence": ["evidence/SEC-AUTHZ-001-response.json"],
                    "reproduction": ["Authenticate as synthetic viewer", "Send DELETE for the synthetic service UUID"],
                    "authorization": {"authority_reference": "AUTH-SYNTHETIC-001"},
                    "data_classification": "internal_restricted",
                    "owner_team": "backend",
                    "clickup_eligible": True,
                }
            ]
            manifest = Path(tmp) / "security-run.json"
            manifest.write_text(json.dumps(data))
            output_dir = Path(tmp) / "artifacts"

            result = self.run_generator(manifest, output_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            report = (output_dir / "qa-report.md").read_text()
            self.assertIn("Security and access-control findings", report)
            self.assertIn("SEC-AUTHZ-001", report)
            self.assertIn("ServiceController.php:destroy", report)
            confluence = json.loads((output_dir / "confluence-draft.json").read_text())
            self.assertIn("SEC-AUTHZ-001", confluence["body"])
            clickup = json.loads((output_dir / "clickup-drafts.json").read_text())
            security_tasks = [task for task in clickup["tasks"] if task.get("finding_id") == "SEC-AUTHZ-001"]
            self.assertEqual(len(security_tasks), 1)
            self.assertIn("ServiceController.php:destroy", security_tasks[0]["description_markdown"])
            with zipfile.ZipFile(output_dir / "test-cases.xlsx") as workbook:
                workbook_xml = workbook.read("xl/workbook.xml").decode()
                self.assertIn("Test Cases", workbook_xml)
                self.assertIn("Security Findings", workbook_xml)
                self.assertIn("Coverage Summary", workbook_xml)
                self.assertIn("xl/worksheets/sheet2.xml", workbook.namelist())
                self.assertIn("xl/worksheets/sheet3.xml", workbook.namelist())

    def test_unproven_confirmed_security_finding_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = json.loads(FIXTURE.read_text())
            data["security_findings"] = [
                {
                    "id": "SEC-UNPROVEN",
                    "title": "Unproven finding",
                    "classification": "confirmed",
                    "source_engine": "native-test",
                    "target": "DELETE /services/{uuid}",
                    "business_priority": "unmapped",
                    "evidence": ["   "],
                    "reproduction": [],
                    "authorization": None,
                    "data_classification": "internal_restricted",
                    "clickup_eligible": "yes",
                }
            ]
            manifest = Path(tmp) / "unproven.json"
            manifest.write_text(json.dumps(data))
            output_dir = Path(tmp) / "artifacts"

            result = self.run_generator(manifest, output_dir)

            self.assertEqual(result.returncode, 2)
            self.assertIn("security_findings[0]", result.stderr)
            self.assertFalse(output_dir.exists())

    def test_crud_pilot_covers_all_operations_and_remains_not_run(self):
        pilot = ROOT / "examples" / "crud-pilot" / "test-run.json"
        data = json.loads(pilot.read_text())
        module_ids = {module_id for case in data["test_cases"] for module_id in case.get("module_ids", [])}
        self.assertTrue(
            {"api.get_collection", "api.get_detail", "api.post", "api.put", "api.patch", "api.delete"}.issubset(module_ids)
        )
        self.assertTrue(all(case["status"] == "not_run" for case in data["test_cases"]))
        self.assertTrue(all(case["actual_result"] == "" and case["evidence"] == [] for case in data["test_cases"]))

        quality = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_quality.py"), str(pilot), "--kind", "test-run"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(quality.returncode, 0, quality.stdout + quality.stderr)

        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_generator(pilot, Path(tmp) / "artifacts")
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
