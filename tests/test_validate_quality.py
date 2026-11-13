import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_quality.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_quality", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def professional_run():
    return {
        "schema_version": "1.0",
        "run_id": "AQABSI-QUALITY-001",
        "title": "Synthetic login quality fixture",
        "module": "authentication",
        "environment": "test",
        "target": "https://test.example.invalid",
        "started_at": "2026-11-13T09:00:00+07:00",
        "source": {"repository": "synthetic/service", "commit_sha": "0123456789abcdef"},
        "authorization_record": None,
        "test_cases": [
            {
                "id": "TC-AUTH-001",
                "title": "Valid user receives an authenticated session",
                "requirement_ids": ["FR-AUTH-001"],
                "risk_ids": ["RISK-AUTH-SESSION"],
                "source_ids": ["SRC-API-LOGIN"],
                "module_ids": ["authentication.login"],
                "role": "registered_user",
                "state": "logged_out",
                "module": "Authentication",
                "feature": "Login",
                "layer": "api",
                "technique": "scenario",
                "scenario": "Submit valid credentials once",
                "preconditions": ["Synthetic active account exists"],
                "steps": ["POST the synthetic credential reference to /login"],
                "test_data": {"credential_ref": "vault://qa/login-valid"},
                "data_classification": "synthetic",
                "expected_result": "HTTP 200 returns the documented session envelope and writes one login audit event.",
                "actual_result": "",
                "status": "not_run",
                "priority": "critical",
                "priority_rationale": "Authentication is required by all protected journeys.",
                "severity": None,
                "evidence": [],
                "evidence_requirements": ["Sanitized response and audit correlation ID"],
                "cleanup": ["Revoke any session created by the test"],
                "automation_suitability": "high",
                "target_adapter": "native-api",
                "owner_team": "identity-platform",
            }
        ],
    }


def professional_prd():
    return {
        "schema_version": "1.0",
        "document": {
            "title": "Synthetic authentication PRD",
            "version": "1.0",
            "status": "in_review",
            "business_owner": "product-identity",
            "technical_owner": "identity-platform",
            "qa_owner": "qa-platform",
            "reviewers": ["security-platform"],
            "evidence_cutoff": "2026-11-13T09:00:00+07:00",
            "source_commits": ["0123456789abcdef"],
        },
        "quality_verdict": "review_ready",
        "summary": "Provide a documented login contract for synthetic test users and protected journeys.",
        "scope": {"in_scope": ["Login API"], "out_of_scope": ["SSO"], "non_goals": ["Production identity migration"]},
        "evidence_sources": [
            {"id": "SRC-API-LOGIN", "type": "api_contract", "location": "openapi:/login", "classification": "verified", "confidence": "high", "sensitivity": "internal_restricted"}
        ],
        "requirements": [
            {
                "id": "FR-AUTH-001",
                "statement": "The login endpoint shall issue the documented session envelope for a valid synthetic account.",
                "priority": "must",
                "evidence_type": "verified",
                "source": "SRC-API-LOGIN",
                "source_ids": ["SRC-API-LOGIN"],
                "confidence": "high",
                "acceptance_criteria": ["Given an active synthetic account, one valid login returns HTTP 200 and one auditable session."],
                "error_behavior": ["Invalid credentials return the documented generic authentication error without a session."],
            }
        ],
        "business_rules": [],
        "risks": [{"id": "RISK-AUTH-SESSION", "impact": "high", "mitigation": "Traceable session tests"}],
        "release_evidence": ["Approved quality report and residual-risk review"],
        "open_questions": [],
        "traceability": [{"requirement_id": "FR-AUTH-001", "source_ids": ["SRC-API-LOGIN"], "risk_ids": ["RISK-AUTH-SESSION"], "test_case_ids": ["TC-AUTH-001"]}],
    }


class ValidateQualityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_validator()

    def codes(self, data, kind):
        return {finding.code for finding in self.validator.validate_document(data, kind)}

    def test_review_ready_prd_and_not_run_plan_are_accepted(self):
        self.assertEqual(self.validator.validate_document(professional_prd(), "prd"), [])
        self.assertEqual(self.validator.validate_document(professional_run(), "test-run"), [])

    def test_adaptive_prd_does_not_require_a_fixed_section_order(self):
        prd = professional_prd()
        prd.pop("scope")
        prd["prd_profile"] = "api-change"
        prd["adaptive_sections"] = [
            {"id": "scope-boundary", "title": "Scope boundary", "applicability": "required", "content": {"in": ["Login API"], "out": ["SSO"]}},
            {"id": "contract-impact", "title": "Contract impact", "applicability": "required", "content": {"breaking_change": False}},
            {"id": "ui-journey", "title": "UI journey", "applicability": "not_applicable", "rationale": "API-only change", "reviewer": "qa-platform"},
        ]

        self.assertEqual(self.validator.validate_document(prd, "prd"), [])

        schema = json.loads((ROOT / "schemas" / "prd.schema.json").read_text())
        self.assertTrue(schema["additionalProperties"])
        self.assertNotIn("scope", schema["required"])
        self.assertIn("adaptive_sections", schema["properties"])

    def test_prd_rejects_missing_traceability_and_ambiguous_oracle(self):
        prd = professional_prd()
        prd["traceability"] = []
        prd["requirements"][0]["acceptance_criteria"] = ["Login works normally and is fast."]

        codes = self.codes(prd, "prd")

        self.assertIn("PRD_TRACEABILITY_MISSING", codes)
        self.assertIn("AMBIGUOUS_ORACLE", codes)

    def test_prd_rejects_missing_professional_outcomes_and_unknown_sources(self):
        prd = {
            "requirements": [
                {
                    "id": "FR-MINIMAL-001",
                    "statement": "A minimal statement",
                    "source_ids": ["MISSING-SOURCE"],
                    "acceptance_criteria": ["HTTP 200 returns one documented record."],
                }
            ],
            "traceability": [{"requirement_id": "FR-MINIMAL-001"}],
        }

        codes = self.codes(prd, "prd")

        self.assertIn("PRD_DOCUMENT_CONTROL_MISSING", codes)
        self.assertIn("PRD_EVIDENCE_LEDGER_MISSING", codes)
        self.assertIn("PRD_SOURCE_UNKNOWN", codes)
        self.assertIn("PRD_SCOPE_OUTCOME_MISSING", codes)
        self.assertIn("PRD_RISK_OUTCOME_MISSING", codes)
        self.assertIn("PRD_RELEASE_EVIDENCE_MISSING", codes)
        self.assertIn("PRD_ERROR_BEHAVIOR_MISSING", codes)

    def test_test_run_rejects_duplicate_intent_and_unproven_result(self):
        run = professional_run()
        duplicate = copy.deepcopy(run["test_cases"][0])
        duplicate["id"] = "TC-AUTH-002"
        run["test_cases"].append(duplicate)
        run["test_cases"][0]["status"] = "pass"

        codes = self.codes(run, "test-run")

        self.assertIn("DUPLICATE_TEST_INTENT", codes)
        self.assertIn("EXECUTED_RESULT_WITHOUT_EVIDENCE", codes)

    def test_executed_result_rejects_blank_actual_and_evidence(self):
        run = professional_run()
        case = run["test_cases"][0]
        case["status"] = "pass"
        case["actual_result"] = "   "
        case["evidence"] = ["", "   "]

        self.assertIn("EXECUTED_RESULT_WITHOUT_EVIDENCE", self.codes(run, "test-run"))

    def test_indonesian_measurable_oracle_does_not_match_aman_substring(self):
        run = professional_run()
        run["test_cases"][0]["expected_result"] = "Halaman menampilkan HTTP 403 tanpa perubahan data."
        self.assertNotIn("AMBIGUOUS_ORACLE", self.codes(run, "test-run"))

        run["test_cases"][0]["expected_result"] = "Fitur berjalan normal dan aman."
        self.assertIn("AMBIGUOUS_ORACLE", self.codes(run, "test-run"))

    def test_test_run_rejects_secret_like_test_data(self):
        run = professional_run()
        run["test_cases"][0]["test_data"] = {
            "nested": {"password_konfirmasi": "plain-secret"},
            "authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.secret.signature",
        }

        codes = self.codes(run, "test-run")

        self.assertIn("SECRET_LIKE_TEST_DATA", codes)

    def test_destructive_step_requires_authorization_and_cleanup(self):
        run = professional_run()
        run["test_cases"][0]["steps"] = ["Delete all records from the shared table"]
        run["test_cases"][0]["cleanup"] = []

        codes = self.codes(run, "test-run")

        self.assertIn("DESTRUCTIVE_STEP_WITHOUT_AUTHORIZATION", codes)
        self.assertIn("CLEANUP_REQUIRED", codes)

    def test_cli_emits_machine_readable_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "run.json"
            run = professional_run()
            run["test_cases"][0]["status"] = "fail"
            path.write_text(json.dumps(run))

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(path), "--kind", "test-run", "--format", "json"],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["verdict"], "draft_incomplete")
            self.assertTrue(any(item["code"] == "EXECUTED_RESULT_WITHOUT_EVIDENCE" for item in payload["findings"]))


if __name__ == "__main__":
    unittest.main()
