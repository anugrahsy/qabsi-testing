#!/usr/bin/env python3
"""Validate AQABSI frontmatter, local references, JSON, and package invariants."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


FRONTMATTER = re.compile(r"\A---\s*\n(?P<body>.*?)\n---\s*\n", re.DOTALL)
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
CODE_REFERENCE = re.compile(r"`((?:\.\./|references/|assets/|schemas/|scripts/)[^`\s]+\.(?:md|json|yml|yaml|py|csv))`")
BANNED_OPERATIONAL_PLACEHOLDERS = ("template menyusul", "format bebas dulu")
CANONICAL_SKILL_NAME = "aqabsi-testing"
CANONICAL_PLUGIN_NAME = "aqabsi"
CANONICAL_DISPLAY_NAME = "AQABSI — AI QA BSI"
CANONICAL_VERSION = "2.1.0"
LEGACY_IDENTITY_PATTERN = re.compile(r"(?i)(?<![a-z0-9])q" + r"absi(?=$|[^a-z0-9])")
APPROVED_LEGACY_REPOSITORY_SLUG = "anugrahsy/" + "q" + "absi-testing"
PROTECTED_POLICY_VALUES = {
    ("data_egress", "default_classification"): "internal_restricted",
    ("data_egress", "allow_managed_external"): False,
    ("security", "active_testing_requires_authorization"): True,
    ("security", "production_active_testing"): False,
    ("publication", "requires_authorization"): True,
    ("publication", "guess_assignee"): False,
    ("evidence", "executed_verdict_requires_evidence"): True,
}
MISSING = object()
PUBLIC_TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".py"}
INTEGRATION_TEMPLATE = Path("assets/templates/integrations.env.example")
INTEGRATION_SECRET_VARIABLES = {
    "AQABSI_CONFLUENCE_API_TOKEN",
    "AQABSI_CONFLUENCE_PAT",
    "AQABSI_CLICKUP_API_TOKEN",
    "AQABSI_TEST_PASSWORD",
    "AQABSI_TEST_TOKEN",
}
REQUIRED_INTEGRATION_SCRIPTS = {
    "scripts/check_integrations.py",
    "scripts/publish_artifacts.py",
}
PREFLIGHT_COMMAND = "python3 scripts/check_integrations.py --json"
SOURCE_DISCOVERY_MARKER = "Build a source inventory"


def parse_frontmatter(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER.match(text)
    if not match:
        raise ValueError(f"{path}: missing YAML frontmatter")
    fields: dict[str, str] = {}
    for line in match.group("body").splitlines():
        if ":" not in line or line.startswith((" ", "\t")):
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"\'')
    name = fields.get("name", "")
    description = fields.get("description", "")
    if not re.fullmatch(r"[a-z0-9-]{1,63}", name):
        raise ValueError(f"{path}: invalid or missing skill name")
    if not description:
        raise ValueError(f"{path}: missing skill description")
    return name, description


def _clean_target(target: str) -> str:
    target = target.strip().split()[0].strip("<>")
    return target.split("#", 1)[0]


def _nested_value(mapping: object, path: tuple[str, ...]) -> object:
    current = mapping
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return MISSING
        current = current[key]
    return current


def validate_registry_and_profiles(root: Path) -> list[str]:
    errors: list[str] = []
    registry_path = root / "config" / "module-registry.json"
    if not registry_path.is_file():
        return [f"{registry_path}: module registry is required"]
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{registry_path}: invalid module registry: {exc}"]
    modules = registry.get("modules", [])
    stacks = registry.get("stack_profiles", [])
    module_ids = [item.get("id") for item in modules if isinstance(item, dict)]
    stack_ids = [item.get("id") for item in stacks if isinstance(item, dict)]
    if len(module_ids) != len(set(module_ids)):
        errors.append(f"{registry_path}: module IDs must be unique")
    if len(stack_ids) != len(set(stack_ids)):
        errors.append(f"{registry_path}: stack profile IDs must be unique")
    known_modules = set(module_ids)
    for module in modules:
        if not isinstance(module, dict):
            continue
        for related in module.get("related_modules", []):
            if related not in known_modules:
                errors.append(f"{registry_path}: unknown related module {related}")

    profile_dir = root / "config" / "profiles"
    required_profiles = {"organization-bsi", "team-default", "project-example"}
    found_profiles: set[str] = set()
    for profile_path in sorted(profile_dir.glob("*.json")):
        try:
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        profile_id = profile.get("id")
        if profile_id:
            found_profiles.add(profile_id)
        for selected in profile.get("selected_stack_profiles", []):
            if selected not in set(stack_ids):
                errors.append(f"{profile_path}: unknown stack profile {selected}")
        policy_source = profile.get("policy", {}) if profile.get("layer") == "organization" else profile.get("policy_overrides", {})
        for policy_path, required_value in PROTECTED_POLICY_VALUES.items():
            value = _nested_value(policy_source, policy_path)
            if profile.get("layer") == "organization":
                if value != required_value:
                    errors.append(f"{profile_path}: organization policy must set {'.'.join(policy_path)}={required_value}")
            elif value is not MISSING and value != required_value:
                errors.append(f"{profile_path}: cannot weaken organization policy {'.'.join(policy_path)}")
    missing_profiles = required_profiles - found_profiles
    if missing_profiles:
        errors.append(f"{profile_dir}: missing profiles {', '.join(sorted(missing_profiles))}")
    return errors


def validate_organization_neutral_branding(root: Path) -> list[str]:
    """Keep the canonical package neutral across BSI UII teams and projects."""
    team_code = "e" + "a"
    blocked = re.compile(
        rf"(?i)(?<![a-z0-9]){team_code}(?![a-z0-9])|{team_code}-angular-lumen|svc-{team_code}|gateway-{team_code}"
    )
    errors: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in PUBLIC_TEXT_SUFFIXES:
            continue
        if any(part in {".git", ".superpowers", "__pycache__"} for part in path.parts):
            continue
        relative = path.relative_to(root)
        text = path.read_text(encoding="utf-8", errors="ignore")
        if blocked.search(str(relative)) or blocked.search(text):
            errors.append(f"{path}: team-specific branding is not allowed in the BSI UII-wide package")
    return errors


def validate_canonical_product_identity(root: Path) -> list[str]:
    """Reject pre-AQABSI names while the old GitHub repository slug remains approved temporarily."""
    errors: list[str] = []
    ignored_parts = {".git", ".superpowers", "__pycache__"}
    for path in root.rglob("*"):
        if not path.is_file() or ignored_parts.intersection(path.parts):
            continue
        relative = path.relative_to(root)
        if LEGACY_IDENTITY_PATTERN.search(str(relative)):
            errors.append(f"{path}: legacy AQABSI identity is not allowed in package paths")
        if path.suffix.lower() not in PUBLIC_TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        text = text.replace(APPROVED_LEGACY_REPOSITORY_SLUG, "")
        if LEGACY_IDENTITY_PATTERN.search(text):
            errors.append(f"{path}: legacy AQABSI identity is not allowed in public content")
    return errors


def validate_integration_onboarding(root: Path) -> list[str]:
    errors: list[str] = []
    for relative in sorted(REQUIRED_INTEGRATION_SCRIPTS):
        if not (root / relative).is_file():
            errors.append(f"{root / relative}: required integration script is missing")

    template = root / INTEGRATION_TEMPLATE
    if not template.is_file():
        errors.append(f"{template}: names-only integration template is required")
    else:
        values: dict[str, str] = {}
        for line_number, raw_line in enumerate(
            template.read_text(encoding="utf-8").splitlines(), start=1
        ):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                errors.append(f"{template}:{line_number}: expected NAME=value syntax")
                continue
            name, value = line.split("=", 1)
            values[name.strip()] = value.strip()
        for name in sorted(INTEGRATION_SECRET_VARIABLES):
            if name not in values:
                errors.append(f"{template}: required secret variable {name} is missing")
            elif values[name]:
                errors.append(
                    f"{template}: secret variable must not contain a value: {name}"
                )

    skill = root / "SKILL.md"
    if skill.is_file():
        text = skill.read_text(encoding="utf-8")
        command_index = text.find(PREFLIGHT_COMMAND)
        discovery_index = text.find(SOURCE_DISCOVERY_MARKER)
        if (
            command_index < 0
            or discovery_index < 0
            or command_index > discovery_index
        ):
            errors.append(
                f"{skill}: must route through integration preflight before source discovery"
            )
    return errors


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    root_skill = root / "SKILL.md"
    if not root_skill.is_file():
        errors.append(f"{root_skill}: root SKILL.md is required")

    if root_skill.is_file():
        try:
            root_name, _ = parse_frontmatter(root_skill)
            if root_name != CANONICAL_SKILL_NAME:
                errors.append(
                    f"{root_skill}: canonical skill metadata requires name {CANONICAL_SKILL_NAME}"
                )
            root_text = root_skill.read_text(encoding="utf-8")
            if CANONICAL_DISPLAY_NAME not in root_text or f'version: "{CANONICAL_VERSION}"' not in root_text:
                errors.append(
                    f"{root_skill}: canonical skill metadata requires {CANONICAL_DISPLAY_NAME} version {CANONICAL_VERSION}"
                )
        except (OSError, ValueError):
            pass

    openai_path = root / "agents" / "openai.yaml"
    if not openai_path.is_file():
        errors.append(f"{openai_path}: canonical skill metadata file is required")
    else:
        openai_text = openai_path.read_text(encoding="utf-8")
        if CANONICAL_DISPLAY_NAME not in openai_text or f"${CANONICAL_SKILL_NAME}" not in openai_text:
            errors.append(f"{openai_path}: canonical skill metadata is inconsistent")

    plugin_path = root / ".claude-plugin" / "plugin.json"
    if not plugin_path.is_file():
        errors.append(f"{plugin_path}: canonical skill metadata file is required")
    else:
        try:
            plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
            if (
                plugin.get("name") != CANONICAL_PLUGIN_NAME
                or plugin.get("version") != CANONICAL_VERSION
                or plugin.get("interface", {}).get("displayName") != CANONICAL_DISPLAY_NAME
            ):
                errors.append(f"{plugin_path}: canonical skill metadata is inconsistent")
        except (OSError, json.JSONDecodeError, AttributeError):
            pass

    gitignore_path = root / ".gitignore"
    if not gitignore_path.is_file() or ".aqabsi-output/" not in gitignore_path.read_text(encoding="utf-8").splitlines():
        errors.append(f"{gitignore_path}: canonical skill metadata requires .aqabsi-output/")

    skill_files = sorted(root.glob("SKILL.md")) + sorted((root / "skills").glob("*/SKILL.md"))
    for skill_file in skill_files:
        try:
            parse_frontmatter(skill_file)
        except (OSError, ValueError) as exc:
            errors.append(str(exc))

    markdown_files = sorted(root.rglob("*.md"))
    ignored_parts = {".git"}
    for path in markdown_files:
        if ignored_parts.intersection(path.parts):
            continue
        if "docs" in path.parts and "superpowers" in path.parts and "plans" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(root)
        if relative == Path("SKILL.md") or relative.parts[0] in {"skills", "references"}:
            lowered = text.lower()
            for placeholder in BANNED_OPERATIONAL_PLACEHOLDERS:
                if placeholder in lowered:
                    errors.append(f"{path}: unfinished operational placeholder: {placeholder}")
        targets = list(MARKDOWN_LINK.findall(text)) + list(CODE_REFERENCE.findall(text))
        for target in targets:
            cleaned = _clean_target(target)
            if not cleaned or cleaned.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if "*" in cleaned:
                if not list(path.parent.glob(cleaned)):
                    errors.append(f"{path}: missing local reference {target}")
                continue
            if cleaned.startswith(("references/", "assets/", "schemas/", "scripts/", "skills/")):
                resolved = (root / cleaned).resolve()
            else:
                resolved = (path.parent / cleaned).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                errors.append(f"{path}: reference escapes package: {target}")
                continue
            if not resolved.exists():
                errors.append(f"{path}: missing local reference {target}")

    for path in sorted(root.rglob("*.json")):
        if ".git" in path.parts:
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: invalid JSON: {exc}")

    errors.extend(validate_registry_and_profiles(root))
    errors.extend(validate_organization_neutral_branding(root))
    errors.extend(validate_canonical_product_identity(root))
    errors.extend(validate_integration_onboarding(root))

    knowledge = list((root / "references" / "knowledge").glob("*/*.md"))
    if len(knowledge) < 90:
        errors.append(f"{root}: expected at least 90 knowledge modules, found {len(knowledge)}")
    return errors


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]).resolve()
    errors = validate(root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"AQABSI package valid: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
