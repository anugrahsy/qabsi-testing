#!/usr/bin/env python3
"""Generate deterministic, sanitized QABSI reporting artifacts from a run manifest."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape as xml_escape


STATUSES = ("pass", "fail", "blocked", "skipped", "not_run", "flaky", "environment_error")
PRIORITIES = ("critical", "high", "medium", "low")
SEVERITIES = ("critical", "high", "medium", "low", "info")
ENVIRONMENTS = ("local", "test", "development", "staging", "production")
LAYERS = ("static", "unit", "component", "integration", "contract", "api", "e2e", "exploratory", "regression", "smoke", "security", "accessibility", "compatibility", "data", "migration", "resilience", "observability", "performance", "load", "stress", "endurance", "scalability", "reliability", "usability", "localization")
SECRET_KEYS = {
    "password",
    "passwd",
    "passphrase",
    "password_confirmation",
    "password_konfirmasi",
    "confirmation_password",
    "token",
    "access_token",
    "refresh_token",
    "authorization_code",
    "verification_code",
    "mfa_code",
    "otp",
    "otp_code",
    "recovery_code",
    "code",
    "pin",
    "authorization",
    "cookie",
    "set_cookie",
    "secret",
    "api_key",
    "client_secret",
    "session_id",
}
CSV_COLUMNS = (
    "Test Case ID",
    "Requirement IDs",
    "Risk IDs",
    "Module",
    "Feature",
    "Layer",
    "Scenario",
    "Preconditions",
    "Test Steps",
    "Test Data",
    "Expected Result",
    "Actual Result",
    "Status",
    "Priority",
    "Severity",
    "Evidence",
    "Owner Team",
    "Notes",
)


class ManifestError(ValueError):
    pass


def _require(mapping: dict[str, Any], key: str, context: str) -> Any:
    if key not in mapping or mapping[key] in (None, ""):
        raise ManifestError(f"{context}.{key} is required")
    return mapping[key]


def validate_manifest(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ManifestError("manifest must be a JSON object")
    for key in ("run_id", "schema_version", "title", "module", "environment", "started_at", "source", "test_cases"):
        _require(data, key, "manifest")
    if data["schema_version"] != "1.0":
        raise ManifestError("manifest.schema_version must be 1.0")
    if data["environment"] not in ENVIRONMENTS:
        raise ManifestError(f"manifest.environment must be one of {', '.join(ENVIRONMENTS)}")
    if not isinstance(data["source"], dict):
        raise ManifestError("manifest.source must be an object")
    _require(data["source"], "repository", "manifest.source")
    _require(data["source"], "commit_sha", "manifest.source")
    if not isinstance(data["test_cases"], list):
        raise ManifestError("manifest.test_cases must be an array")

    ids: set[str] = set()
    required_case_fields = (
        "id",
        "module",
        "feature",
        "layer",
        "scenario",
        "preconditions",
        "steps",
        "test_data",
        "expected_result",
        "actual_result",
        "status",
        "priority",
        "severity",
        "evidence",
        "owner_team",
    )
    for index, case in enumerate(data["test_cases"]):
        context = f"manifest.test_cases[{index}]"
        if not isinstance(case, dict):
            raise ManifestError(f"{context} must be an object")
        for key in required_case_fields:
            if key in ("actual_result", "evidence", "severity"):
                if key not in case:
                    raise ManifestError(f"{context}.{key} is required")
            else:
                _require(case, key, context)
        if case["id"] in ids:
            raise ManifestError(f"duplicate test case id: {case['id']}")
        ids.add(case["id"])
        if case["status"] not in STATUSES:
            raise ManifestError(f"{context}.status must be one of {', '.join(STATUSES)}")
        if case["priority"] not in PRIORITIES:
            raise ManifestError(f"{context}.priority must be one of {', '.join(PRIORITIES)}")
        if case["layer"] not in LAYERS:
            raise ManifestError(f"{context}.layer must be one of {', '.join(LAYERS)}")
        severity = case.get("severity")
        if severity is not None and severity not in SEVERITIES:
            raise ManifestError(f"{context}.severity must be null or one of {', '.join(SEVERITIES)}")
        for list_key in ("preconditions", "steps", "evidence"):
            if not isinstance(case[list_key], list):
                raise ManifestError(f"{context}.{list_key} must be an array")
    return data


def _secret_key(key: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_")
    return (
        normalized in SECRET_KEYS
        or normalized.endswith("_password")
        or normalized.endswith("_token")
        or normalized.endswith("_secret")
        or normalized.endswith("_otp")
        or normalized.endswith("_pin")
        or normalized.endswith("_verification_code")
    )


def redact_string(value: str) -> str:
    value = re.sub(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+", "Bearer [REDACTED]", value)
    value = re.sub(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b", "[REDACTED_JWT]", value)
    value = re.sub(
        r"(?i)(password(?:[_-]?(?:confirmation|konfirmasi))?|passwd|token|api[_-]?key|secret|otp|verification[_-]?code|mfa[_-]?code|recovery[_-]?code)(\s*[:=]\s*)([^\s,;]+)",
        lambda match: f"{match.group(1)}{match.group(2)}[REDACTED]",
        value,
    )
    return value


def sanitize(value: Any, parent_key: str = "") -> Any:
    if _secret_key(parent_key):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {key: sanitize(item, key) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize(item, parent_key) for item in value]
    if isinstance(value, str):
        return redact_string(value)
    return value


def _compact(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "\n".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def case_to_row(case: dict[str, Any]) -> dict[str, str]:
    return {
        "Test Case ID": case["id"],
        "Requirement IDs": _compact(case.get("requirement_ids", [])),
        "Risk IDs": _compact(case.get("risk_ids", [])),
        "Module": case["module"],
        "Feature": case["feature"],
        "Layer": case["layer"],
        "Scenario": case["scenario"],
        "Preconditions": _compact(case["preconditions"]),
        "Test Steps": _compact(case["steps"]),
        "Test Data": _compact(case["test_data"]),
        "Expected Result": case["expected_result"],
        "Actual Result": case["actual_result"],
        "Status": case["status"],
        "Priority": case["priority"],
        "Severity": case.get("severity") or "",
        "Evidence": _compact(case["evidence"]),
        "Owner Team": case["owner_team"],
        "Notes": case.get("notes", ""),
    }


def _summary(cases: list[dict[str, Any]]) -> dict[str, int]:
    counts = {status: 0 for status in STATUSES}
    for case in cases:
        counts[case["status"]] += 1
    return counts


def build_markdown(data: dict[str, Any]) -> str:
    counts = _summary(data["test_cases"])
    source = data["source"]
    lines = [
        f"# QA Report — {data['title']}",
        "",
        "## Run information",
        "",
        f"- Run ID: `{data['run_id']}`",
        f"- Module: {data['module']}",
        f"- Environment: {data['environment']}",
        f"- Target: {data.get('target') or 'Not recorded'}",
        f"- Repository: {source['repository']}",
        f"- Commit: `{source['commit_sha']}`",
        f"- Merge request: {source.get('merge_request_url') or 'Not recorded'}",
        f"- Started: {data['started_at']}",
        f"- Finished: {data.get('finished_at') or 'Not finished'}",
        "",
        "## Summary",
        "",
        "| Total | Pass | Fail | Blocked | Skipped | Not run | Flaky | Environment error |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
        f"| {len(data['test_cases'])} | {counts['pass']} | {counts['fail']} | {counts['blocked']} | {counts['skipped']} | {counts['not_run']} | {counts['flaky']} | {counts['environment_error']} |",
        "",
        "## Test cases",
        "",
        "| ID | Requirements | Layer | Scenario | Expected | Actual | Status | Severity | Owner |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for case in data["test_cases"]:
        clean = lambda text: str(text).replace("|", "\\|").replace("\n", "<br>")
        lines.append(
            "| " + " | ".join(
                clean(value)
                for value in (
                    case["id"],
                    ", ".join(case.get("requirement_ids", [])) or "—",
                    case["layer"],
                    case["scenario"],
                    case["expected_result"],
                    case["actual_result"],
                    case["status"],
                    case.get("severity") or "—",
                    case["owner_team"],
                )
            ) + " |"
        )
    lines.extend(["", "## Limitations", ""])
    limitations = data.get("limitations") or ["No limitations were recorded."]
    lines.extend(f"- {item}" for item in limitations)
    lines.extend(
        [
            "",
            "## Publication state",
            "",
            "This artifact is a sanitized draft. Publishing and assignment require explicit authorization.",
            "",
        ]
    )
    return "\n".join(lines)


def write_csv(path: Path, cases: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(case_to_row(case) for case in cases)


def _column_letter(index: int) -> str:
    result = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def _zip_write(archive: zipfile.ZipFile, name: str, content: str) -> None:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(info, content.encode("utf-8"))


def write_xlsx(path: Path, cases: list[dict[str, Any]]) -> None:
    rows = [list(CSV_COLUMNS)] + [[case_to_row(case)[column] for column in CSV_COLUMNS] for case in cases]
    sheet_rows: list[str] = []
    for row_index, row in enumerate(rows, start=1):
        cells = []
        for column_index, value in enumerate(row, start=1):
            reference = f"{_column_letter(column_index)}{row_index}"
            style = "1" if row_index == 1 else "0"
            status_column_index = CSV_COLUMNS.index("Status") + 1
            if row_index > 1 and column_index == status_column_index:
                style = {"pass": "2", "fail": "3"}.get(str(value), "4")
            escaped = xml_escape(str(value), {'"': "&quot;"})
            cells.append(f'<c r="{reference}" t="inlineStr" s="{style}"><is><t xml:space="preserve">{escaped}</t></is></c>')
        sheet_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')
    last_row = max(2, len(rows))
    last_column = _column_letter(len(CSV_COLUMNS))
    widths = [16, 24, 20, 20, 20, 15, 36, 34, 42, 36, 42, 42, 18, 14, 14, 32, 18, 28]
    columns = "".join(f'<col min="{i}" max="{i}" width="{width}" customWidth="1"/>' for i, width in enumerate(widths, start=1))
    status_list = ",".join(STATUSES)
    status_column = _column_letter(CSV_COLUMNS.index("Status") + 1)
    sheet = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'
        f'<cols>{columns}</cols><sheetData>{"".join(sheet_rows)}</sheetData>'
        f'<autoFilter ref="A1:{last_column}{last_row}"/>'
        f'<dataValidations count="1"><dataValidation type="list" allowBlank="0" sqref="{status_column}2:{status_column}1048576"><formula1>"{status_list}"</formula1></dataValidation></dataValidations>'
        '</worksheet>'
    )
    styles = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><color rgb="FFFFFFFF"/><sz val="11"/><name val="Calibri"/></font></fonts>'
        '<fills count="5"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF1F4E78"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFC6EFCE"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFFFC7CE"/></patternFill></fill></fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="5"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf><xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf><xf numFmtId="0" fontId="0" fillId="3" borderId="0" xfId="0"/><xf numFmtId="0" fontId="0" fillId="4" borderId="0" xfId="0"/><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>'
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
        '</styleSheet>'
    )
    with zipfile.ZipFile(path, "w") as archive:
        _zip_write(archive, "[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>')
        _zip_write(archive, "_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        _zip_write(archive, "xl/workbook.xml", '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Test Cases" sheetId="1" r:id="rId1"/></sheets></workbook>')
        _zip_write(archive, "xl/_rels/workbook.xml.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
        _zip_write(archive, "xl/styles.xml", styles)
        _zip_write(archive, "xl/worksheets/sheet1.xml", sheet)


def defect_fingerprint(data: dict[str, Any], case: dict[str, Any]) -> str:
    source = data["source"]
    components = (
        data["environment"],
        source["repository"],
        case["module"],
        case["feature"],
        case["id"],
        re.sub(r"\s+", " ", case["actual_result"].strip().lower()),
    )
    return hashlib.sha256("|".join(components).encode()).hexdigest()


def build_clickup_drafts(data: dict[str, Any]) -> dict[str, Any]:
    tasks = []
    for case in data["test_cases"]:
        if case["status"] != "fail":
            continue
        fingerprint = defect_fingerprint(data, case)
        tasks.append(
            {
                "fingerprint": fingerprint,
                "external_key": f"QABSI-{fingerprint[:12]}",
                "name": f"[BUG][{(case.get('severity') or 'untriaged').upper()}] {case['scenario']}",
                "description_markdown": "\n".join(
                    [
                        f"**Test case:** {case['id']}",
                        f"**Requirements:** {', '.join(case.get('requirement_ids', [])) or 'Not linked'}",
                        f"**Environment:** {data['environment']}",
                        f"**Expected:** {case['expected_result']}",
                        f"**Actual:** {case['actual_result']}",
                        "**Steps:**",
                        *[f"{index}. {step}" for index, step in enumerate(case["steps"], start=1)],
                        f"**Evidence:** {', '.join(case['evidence']) or 'Not recorded'}",
                        f"**Source commit:** {data['source']['commit_sha']}",
                    ]
                ),
                "owner_team": case["owner_team"],
                "assignee_id": None,
                "severity": case.get("severity"),
                "source_run_id": data["run_id"],
                "action": "create_or_update_by_fingerprint",
            }
        )
    return {"dry_run": True, "publication_requires_authorization": True, "tasks": tasks}


def generate(input_path: Path, output_dir: Path) -> None:
    raw = json.loads(input_path.read_text(encoding="utf-8"))
    validated = validate_manifest(raw)
    data = sanitize(validated)
    if output_dir.exists():
        raise ManifestError(f"output directory already exists; choose a new path: {output_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}-", dir=output_dir.parent))
    try:
        report = build_markdown(data)
        (temporary / "sanitized-run.json").write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (temporary / "qa-report.md").write_text(report, encoding="utf-8")
        write_csv(temporary / "test-cases.csv", data["test_cases"])
        write_xlsx(temporary / "test-cases.xlsx", data["test_cases"])
        confluence = {
            "dry_run": True,
            "publication_requires_authorization": True,
            "idempotency_key": data["run_id"],
            "target_space": None,
            "parent_page_id": None,
            "suggested_title": f"QA Report — {data['run_id']} — {data['title']}",
            "body_format": "markdown",
            "body": report,
        }
        (temporary / "confluence-draft.json").write_text(json.dumps(confluence, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (temporary / "clickup-drafts.json").write_text(json.dumps(build_clickup_drafts(data), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(output_dir)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="QABSI test-run JSON manifest")
    parser.add_argument("output", type=Path, help="New output directory")
    args = parser.parse_args()
    try:
        generate(args.input.resolve(), args.output.resolve())
    except (OSError, json.JSONDecodeError, ManifestError) as exc:
        print(f"QABSI artifact generation failed: {exc}", file=sys.stderr)
        return 2
    print(f"Generated sanitized QABSI artifacts in {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
