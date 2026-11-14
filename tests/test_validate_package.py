import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_package.py"


class ValidatePackageTest(unittest.TestCase):
    def run_validator(self, root: Path):
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(root)],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_repository_package_is_valid(self):
        result = self.run_validator(ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("AQABSI package valid", result.stdout)

    def test_repository_uses_canonical_aqabsi_identity(self):
        skill = (ROOT / "SKILL.md").read_text()
        openai = (ROOT / "agents" / "openai.yaml").read_text()
        plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
        ignored = (ROOT / ".gitignore").read_text().splitlines()

        self.assertIn("name: aqabsi-testing", skill)
        self.assertIn("AQABSI — AI QA BSI", skill)
        self.assertIn("$aqabsi-testing", openai)
        self.assertEqual(plugin["name"], "aqabsi")
        self.assertEqual(plugin["version"], "2.2.0")
        self.assertEqual(plugin["interface"]["displayName"], "AQABSI — AI QA BSI")
        self.assertIn(".aqabsi-output/", ignored)

    def test_first_use_preflight_reports_exact_missing_configuration(self):
        env = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("AQABSI_CONFLUENCE_")
            and not key.startswith("AQABSI_CLICKUP_")
        }
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_integrations.py"), "--json"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 2, result.stderr)
        payload = json.loads(result.stdout)
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

    def test_integration_template_contains_names_only_and_no_secret_values(self):
        template = ROOT / "assets" / "templates" / "integrations.env.example"
        values = {}
        for raw_line in template.read_text().splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            name, value = line.split("=", 1)
            values[name] = value

        self.assertEqual(values["AQABSI_CONFLUENCE_API_TOKEN"], "")
        self.assertEqual(values["AQABSI_CONFLUENCE_PAT"], "")
        self.assertEqual(values["AQABSI_CLICKUP_API_TOKEN"], "")
        self.assertEqual(values["AQABSI_CLICKUP_AUTH_MODE"], "personal")
        self.assertEqual(values["AQABSI_TEST_PASSWORD"], "")
        self.assertEqual(values["AQABSI_TEST_TOKEN"], "")
        self.assertEqual(values["AQABSI_TARGET_AUTH_MODE"], "web_login")

    def test_validator_rejects_secret_valued_integration_template(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "package"
            shutil.copytree(
                ROOT,
                root,
                ignore=shutil.ignore_patterns(".git", ".superpowers", "__pycache__", "*.pyc"),
            )
            template = root / "assets" / "templates" / "integrations.env.example"
            template.write_text(
                template.read_text().replace(
                    "AQABSI_CLICKUP_API_TOKEN=",
                    "AQABSI_CLICKUP_API_TOKEN=secret-value",
                )
            )

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("secret variable must not contain a value", result.stderr)

    def test_validator_requires_preflight_before_source_discovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "package"
            shutil.copytree(
                ROOT,
                root,
                ignore=shutil.ignore_patterns(".git", ".superpowers", "__pycache__", "*.pyc"),
            )
            skill = root / "SKILL.md"
            skill.write_text(
                skill.read_text().replace(
                    "python3 scripts/check_integrations.py --json",
                    "preflight intentionally removed",
                )
            )

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("integration preflight before source discovery", result.stderr)

    def test_public_package_contains_no_team_specific_branding(self):
        team_code = "e" + "a"
        blocked = re.compile(rf"(?i)(?<![a-z0-9]){team_code}(?![a-z0-9])|{team_code}-angular-lumen|svc-{team_code}|gateway-{team_code}")
        findings = []
        for path in ROOT.rglob("*"):
            if not path.is_file() or any(part in {".git", ".superpowers", "__pycache__"} for part in path.parts):
                continue
            if path.suffix.lower() not in {".md", ".json", ".yaml", ".yml", ".py"}:
                continue
            if blocked.search(path.read_text(encoding="utf-8", errors="ignore")):
                findings.append(str(path.relative_to(ROOT)))
        self.assertEqual(findings, [], "team-specific branding found in: " + ", ".join(findings))

    def test_validator_rejects_team_specific_branding_regression(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "package"
            shutil.copytree(
                ROOT,
                root,
                ignore=shutil.ignore_patterns(".git", ".superpowers", "__pycache__", "*.pyc"),
            )
            readme = root / "README.md"
            team_code = "E" + "A"
            readme.write_text(readme.read_text() + f"\nTeam {team_code} only.\n")

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("team-specific branding", result.stderr)

    def test_validator_rejects_legacy_product_name_in_file_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "package"
            shutil.copytree(
                ROOT,
                root,
                ignore=shutil.ignore_patterns(".git", ".superpowers", "__pycache__", "*.pyc"),
            )
            legacy_name = "q" + "absi"
            (root / f"legacy-{legacy_name}.md").write_text("# Legacy package file\n")

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("legacy AQABSI identity", result.stderr)

    def test_validator_rejects_legacy_product_name_in_public_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "package"
            shutil.copytree(
                ROOT,
                root,
                ignore=shutil.ignore_patterns(".git", ".superpowers", "__pycache__", "*.pyc"),
            )
            legacy_name = ("q" + "absi").upper()
            readme = root / "references" / "flow.md"
            readme.write_text(readme.read_text() + f"\nLegacy product label: {legacy_name}.\n")

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("legacy AQABSI identity", result.stderr)

    def test_metadata_mismatch_is_rejected_by_validator(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            legacy_name = "q" + "absi"
            (root / "agents").mkdir()
            (root / ".claude-plugin").mkdir()
            (root / "references" / "knowledge").mkdir(parents=True)
            (root / "SKILL.md").write_text(
                "---\nname: aqabsi-testing\ndescription: Canonical fixture.\n---\n"
                "# AQABSI — AI QA BSI\n"
            )
            (root / "agents" / "openai.yaml").write_text(
                f'interface:\n  display_name: "Wrong"\n  default_prompt: "Use ${legacy_name}-testing."\n'
            )
            (root / ".claude-plugin" / "plugin.json").write_text(
                json.dumps(
                    {
                        "name": legacy_name,
                        "version": "1.0.0",
                        "interface": {"displayName": legacy_name.upper()},
                    }
                )
            )
            (root / ".gitignore").write_text(f".{legacy_name}-output/\n")

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("canonical skill metadata", result.stderr)

    def test_broken_local_markdown_link_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SKILL.md").write_text(
                "---\nname: broken-skill\ndescription: Broken fixture for validation.\n---\n"
                "Read [missing](references/missing.md).\n"
            )
            result = self.run_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("references/missing.md", result.stderr)

    def test_registry_covers_core_modules_and_bsi_stack_families(self):
        registry = json.loads((ROOT / "config" / "module-registry.json").read_text())
        module_ids = {module["id"] for module in registry["modules"]}
        stack_ids = {profile["id"] for profile in registry["stack_profiles"]}

        self.assertTrue(
            {
                "authentication.login",
                "api.get_collection",
                "api.get_detail",
                "api.post",
                "api.put",
                "api.patch",
                "api.delete",
            }.issubset(module_ids)
        )
        self.assertTrue(
            {
                "angular",
                "react-next",
                "vue-nuxt",
                "laravel",
                "lumen",
                "go",
                "java-spring",
                "dotnet",
                "node",
                "python",
                "unknown-web",
                "unknown-service",
            }.issubset(stack_ids)
        )
        self.assertEqual(len(module_ids), len(registry["modules"]))
        self.assertEqual(len(stack_ids), len(registry["stack_profiles"]))

    def test_lower_profile_cannot_weaken_organization_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "package"
            shutil.copytree(
                ROOT,
                root,
                ignore=shutil.ignore_patterns(".git", ".superpowers", "__pycache__", "*.pyc"),
            )
            project = root / "config" / "profiles" / "project-example.json"
            data = json.loads(project.read_text())
            data["policy_overrides"] = {"data_egress": {"allow_managed_external": True}}
            project.write_text(json.dumps(data))

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("cannot weaken organization policy", result.stderr)

    def test_lower_profile_cannot_lower_default_data_classification(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "package"
            shutil.copytree(
                ROOT,
                root,
                ignore=shutil.ignore_patterns(".git", ".superpowers", "__pycache__", "*.pyc"),
            )
            project = root / "config" / "profiles" / "project-example.json"
            data = json.loads(project.read_text())
            data["policy_overrides"] = {"data_egress": {"default_classification": "public"}}
            project.write_text(json.dumps(data))

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("cannot weaken organization policy data_egress.default_classification", result.stderr)

    def test_third_party_lock_and_templates_are_fail_closed(self):
        lock = json.loads((ROOT / "config" / "third-party-skills.lock.json").read_text())
        pins = {item["repository"]: item["commit"] for item in lock["sources"]}
        self.assertEqual(pins["cloudflare/security-audit-skill"], "c1c8a8c1471069fb0e188eeaff69b8e8db6564a8")
        self.assertEqual(pins["obra/superpowers"], "22f0b463e7a5e579904dd6211a520321035526f7")
        self.assertEqual(pins["e2e-inc/e2e"], "79f70ae419adb0f4c2df8d374c1b7d9e3851726d")
        self.assertEqual(pins["usestrix/strix"], "928b1ca66ea5a00e7fe83f0fce84c7d557ff8091")

        strix = next(item for item in lock["sources"] if item["repository"] == "usestrix/strix")
        self.assertNotIn("managed-pentesting-with-strix", strix["skills"])
        self.assertTrue(strix["managed_cloud_disabled"])

        e2e_config = (ROOT / "assets" / "templates" / "e2e-web" / "e2e.config.example.json").read_text()
        ci = (ROOT / "assets" / "templates" / "gitlab-ci.aqabsi-web-security.example.yml").read_text()
        adapters = (ROOT / "references" / "security-adapters.md").read_text()
        combined = "\n".join((e2e_config, ci, adapters))
        self.assertIn("E2E_TELEMETRY_DISABLED", combined)
        self.assertIn("dry_run", combined)
        self.assertNotIn("NODE_TLS_REJECT_UNAUTHORIZED: \"0\"", combined)
        self.assertNotIn("curl -k", combined)


if __name__ == "__main__":
    unittest.main()
