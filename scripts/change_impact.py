#!/usr/bin/env python3
"""Map changed files to modules and filter affected AQABSI test cases.

Runs ``git diff --name-only`` in the target repository, maps changed file paths
to module/feature names using common backend path conventions, and returns the
test cases in a manifest that are most likely affected by the change.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

MODULE_PATTERNS = (
    (re.compile(r"app/Http/Controllers/([A-Za-z0-9_]+)Controller\.php$"), "controller"),
    (re.compile(r"app/Services/([A-Za-z0-9_]+)Service\.php$"), "service"),
    (re.compile(r"app/Repositories/([A-Za-z0-9_]+)Repository\.php$"), "repository"),
    (re.compile(r"app/Models/([A-Za-z0-9_]+)\.php$"), "model"),
    (re.compile(r"app/Http/Requests/([A-Za-z0-9_]+)Request\.php$"), "request"),
    (re.compile(r"app/Http/Resources/([A-Za-z0-9_]+)Resource\.php$"), "resource"),
    (re.compile(r"app/Http/Middleware/([A-Za-z0-9_]+)\.php$"), "middleware"),
)
ROUTES_FILE = "routes/web.php"


def normalize_module(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def map_file_module(path: str) -> tuple[str | None, str | None]:
    normalized = path.replace("\\", "/")
    for pattern, kind in MODULE_PATTERNS:
        match = pattern.search(normalized)
        if match:
            return normalize_module(match.group(1)), kind
    if normalized.endswith(ROUTES_FILE) or normalized == ROUTES_FILE:
        return "*", "routes"
    if normalized.startswith(("database/", "config/")):
        top = normalized.split("/")[0]
        return normalize_module(top), top
    return None, None


def case_matches(case: dict[str, Any], token: str) -> bool:
    if token == "*":
        return True
    hay = (normalize_module(case.get("module")) + " " + normalize_module(case.get("feature"))).strip()
    if not hay:
        return False
    return token in hay or hay in token


def select_affected_cases(cases: list[dict[str, Any]], changed_files: list[str]) -> list[dict[str, Any]]:
    affects_all = False
    tokens: set[str] = set()
    file_map: dict[str, list[str]] = {}
    for path in changed_files:
        token, _ = map_file_module(path)
        if token == "*":
            affects_all = True
        elif token:
            tokens.add(token)
            file_map.setdefault(token, []).append(path)

    results: list[dict[str, Any]] = []
    for case in cases:
        if not isinstance(case, dict):
            continue
        matched = sorted(token for token in tokens if case_matches(case, token))
        if affects_all or matched:
            results.append(
                {
                    "id": case.get("id"),
                    "module": case.get("module"),
                    "feature": case.get("feature"),
                    "scenario": case.get("scenario"),
                    "layer": case.get("layer"),
                    "status": case.get("status"),
                    "matched_modules": matched,
                    "matched_files": sorted({path for token in matched for path in file_map.get(token, [])}),
                }
            )
    return results


def collect_changed_files(repo: str, base: str | None) -> list[str]:
    if base:
        commands = [["git", "-C", repo, "diff", "--name-only", base]]
    else:
        commands = [
            ["git", "-C", repo, "diff", "--name-only"],
            ["git", "-C", repo, "diff", "--cached", "--name-only"],
        ]
    files: set[str] = set()
    for command in commands:
        proc = subprocess.run(command, capture_output=True, text=True)
        if proc.returncode != 0:
            detail = proc.stderr.strip() or " ".join(command)
            raise RuntimeError(f"git diff failed: {detail}")
        for line in proc.stdout.splitlines():
            line = line.strip()
            if line:
                files.add(line)
    return sorted(files)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."), help="Target repository (default: current directory)")
    parser.add_argument("--manifest", type=Path, required=True, help="AQABSI test-run JSON manifest")
    parser.add_argument("--base", help="Optional git ref to diff against (e.g. main)")
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    args = parser.parse_args()

    try:
        changed = collect_changed_files(str(args.repo), args.base)
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"AQABSI change impact failed: {exc}", file=sys.stderr)
        return 2

    affected = select_affected_cases(data.get("test_cases") or [], changed)
    payload = {
        "schema_version": "1.0",
        "repo": str(args.repo),
        "base": args.base,
        "changed_files": changed,
        "affected_count": len(affected),
        "affected": affected,
    }
    serialized = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    print(serialized, end="")
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
