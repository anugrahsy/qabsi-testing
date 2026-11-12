#!/usr/bin/env python3
"""Validate QABSI frontmatter, local references, JSON, and package invariants."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


FRONTMATTER = re.compile(r"\A---\s*\n(?P<body>.*?)\n---\s*\n", re.DOTALL)
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
CODE_REFERENCE = re.compile(r"`((?:\.\./|references/|assets/|schemas/|scripts/)[^`\s]+\.(?:md|json|yml|yaml|py|csv))`")
BANNED_OPERATIONAL_PLACEHOLDERS = ("template menyusul", "format bebas dulu")


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


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    root_skill = root / "SKILL.md"
    if not root_skill.is_file():
        errors.append(f"{root_skill}: root SKILL.md is required")

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
    print(f"QABSI package valid: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
