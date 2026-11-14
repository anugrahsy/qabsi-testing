#!/usr/bin/env python3
"""Generate deterministic, sanitized AQABSI reporting artifacts from a run manifest."""

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
DOMAINS = ("BE", "FE", "both")
FE_LAYERS = {"component", "e2e", "accessibility", "usability", "compatibility"}


def resolve_domain(case: dict[str, Any]) -> str:
    """Resolve the backend/frontend domain, honouring an explicit field when present."""
    explicit = case.get("domain") or case.get("tag")
    if isinstance(explicit, str) and explicit.strip():
        lowered = explicit.strip().lower()
        if lowered == "both":
            return "both"
        if lowered in ("be", "fe"):
            return lowered.upper()
    if case.get("layer") in FE_LAYERS:
        return "FE"
    return "BE"
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
    "Domain",
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
    for optional_list in ("access_control_matrix", "security_findings"):
        if optional_list in data and not isinstance(data[optional_list], list):
            raise ManifestError(f"manifest.{optional_list} must be an array")
    for index, finding in enumerate(data.get("security_findings", [])):
        context = f"manifest.security_findings[{index}]"
        if not isinstance(finding, dict):
            raise ManifestError(f"{context} must be an object")
        for key in ("id", "title", "classification", "source_engine", "target", "business_priority", "evidence", "reproduction", "authorization", "data_classification", "clickup_eligible"):
            if key not in finding:
                raise ManifestError(f"{context}.{key} is required")
        if type(finding["clickup_eligible"]) is not bool:
            raise ManifestError(f"{context}.clickup_eligible must be a boolean")
        if finding["classification"] == "confirmed" and finding["clickup_eligible"]:
            for key in ("expected_result", "actual_result", "error_location"):
                value = finding.get(key)
                if not isinstance(value, str) or not value.strip():
                    raise ManifestError(f"{context}.{key} is required for ClickUp-eligible confirmed findings")
            for key in ("evidence", "reproduction"):
                values = finding.get(key)
                if not isinstance(values, list) or not values or not all(isinstance(item, str) and item.strip() for item in values):
                    raise ManifestError(f"{context}.{key} requires nonblank entries for ClickUp-eligible confirmed findings")
            authorization = finding.get("authorization")
            if not isinstance(authorization, dict) or not isinstance(authorization.get("authority_reference"), str) or not authorization["authority_reference"].strip():
                raise ManifestError(f"{context}.authorization.authority_reference is required for ClickUp-eligible confirmed findings")

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
        "Domain": resolve_domain(case),
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


def build_coverage_matrix(data: dict[str, Any]) -> dict[str, Any]:
    requirement_ids = sorted(
        {item for case in data["test_cases"] for item in case.get("requirement_ids", [])}
    )
    matrix = {req: {status: 0 for status in STATUSES} for req in requirement_ids}
    for case in data["test_cases"]:
        for req in case.get("requirement_ids", []):
            if req in matrix:
                matrix[req][case["status"]] += 1
    return {"requirements": requirement_ids, "matrix": matrix}


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
        "| ID | Requirements | Layer | Domain | Scenario | Expected | Actual | Status | Severity | Owner |",
        "|---|---|---|---|---|---|---|---|---|---|",
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
                    resolve_domain(case),
                    case["scenario"],
                    case["expected_result"],
                    case["actual_result"],
                    case["status"],
                    case.get("severity") or "—",
                    case["owner_team"],
                )
            ) + " |"
        )

    failed_cases = [case for case in data["test_cases"] if case["status"] == "fail"]
    lines.extend(["", "## Failed test case execution logs", ""])
    if failed_cases:
        for case in failed_cases:
            lines.extend(
                [
                    f"### {case['id']} — {case['scenario']}",
                    "",
                    f"**Domain:** {resolve_domain(case)}",
                    f"**Priority / severity:** {case['priority']} / {case.get('severity') or '—'}",
                    f"**Expected:** {case['expected_result']}",
                    f"**Actual result:** {case['actual_result']}",
                    "",
                    "**Steps:**",
                    "",
                    *[f"{index}. {step}" for index, step in enumerate(case["steps"], start=1)],
                    "",
                    "**Evidence:**",
                ]
            )
            if case["evidence"]:
                lines.extend(f"- {item}" for item in case["evidence"])
            else:
                lines.append("- Not recorded")
            lines.append("")
    else:
        lines.append("No failed test case was recorded for this run.")

    coverage = build_coverage_matrix(data)
    lines.extend(["", "## Coverage matrix", ""])
    if coverage["requirements"]:
        lines.append("| Requirement | " + " | ".join(STATUSES) + " |")
        lines.append("|---|" + "---|" * len(STATUSES))
        for req in coverage["requirements"]:
            row = coverage["matrix"][req]
            lines.append("| " + req + " | " + " | ".join(str(row[status]) for status in STATUSES) + " |")
    else:
        lines.append("No requirement traceability was recorded for this run.")

    access_rows = data.get("access_control_matrix") or []
    lines.extend(["", "## Access-control matrix", ""])
    if access_rows:
        lines.extend(
            [
                "| Role | Action | Resource | Expected | Actual | Status | Test case | Error location |",
                "|---|---|---|---|---|---|---|---|",
            ]
        )
        for row in access_rows:
            clean = lambda text: str(text or "—").replace("|", "\\|").replace("\n", "<br>")
            lines.append(
                "| "
                + " | ".join(
                    clean(row.get(key))
                    for key in ("role", "action", "resource", "expected", "actual", "status", "test_case_id", "error_location")
                )
                + " |"
            )
    else:
        lines.append("No access-control matrix was recorded for this run.")

    security_findings = data.get("security_findings") or []
    lines.extend(["", "## Security and access-control findings", ""])
    if security_findings:
        lines.extend(
            [
                "| ID | Classification | Finding | Target | Expected | Actual | Error location | Evidence |",
                "|---|---|---|---|---|---|---|---|",
            ]
        )
        for finding in security_findings:
            clean = lambda text: str(text or "—").replace("|", "\\|").replace("\n", "<br>")
            lines.append(
                "| "
                + " | ".join(
                    clean(value)
                    for value in (
                        finding.get("id"),
                        finding.get("classification"),
                        finding.get("title"),
                        finding.get("target"),
                        finding.get("expected_result"),
                        finding.get("actual_result"),
                        finding.get("error_location"),
                        ", ".join(finding.get("evidence", [])),
                    )
                )
                + " |"
            )
    else:
        lines.append("No normalized security finding was recorded for this run.")
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


def build_confluence_body(data: dict[str, Any]) -> str:
    """Defects-only Confluence body: publish only failed cases so reviewers see what to fix.

    Full results (pass + fail + blocked + not_run) remain in the local dashboard,
    CSV, and XLSX artifacts. This mirrors the ClickUp drafts, which already filter
    to ``status == "fail"`` only.
    """
    counts = _summary(data["test_cases"])
    source = data["source"]
    failed_cases = [case for case in data["test_cases"] if case["status"] == "fail"]
    lines = [
        f"# QA Report (Defect) — {data['title']}",
        "",
        "## Run information",
        "",
        f"- Run ID: `{data['run_id']}`",
        f"- Module: {data['module']}",
        f"- Environment: {data['environment']}",
        f"- Target: {data.get('target') or 'Not recorded'}",
        f"- Repository: {source['repository']}",
        f"- Commit: `{source['commit_sha']}`",
        f"- Started: {data['started_at']}",
        f"- Finished: {data.get('finished_at') or 'Not finished'}",
        "",
        "## Summary (defects only)",
        "",
        f"- Total test cases: {len(data['test_cases'])}",
        f"- Failed (perlu diperbaiki): {counts['fail']}",
        f"- Pass: {counts['pass']} | Blocked: {counts['blocked']} | Not run: {counts['not_run']} | Skipped: {counts['skipped']} | Flaky: {counts['flaky']} | Environment error: {counts['environment_error']}",
        "",
        "> Halaman ini hanya memuat hal yang perlu diperbaiki (test case gagal + security finding terkonfirmasi). Hasil lengkap (pass + fail + blocked + not_run) tersedia di dashboard & spreadsheet lokal.",
        "",
        "## Failed test case execution logs",
        "",
    ]
    if failed_cases:
        for case in failed_cases:
            lines.extend(
                [
                    f"### {case['id']} — {case['scenario']}",
                    "",
                    f"**Domain:** {resolve_domain(case)}",
                    f"**Layer:** {case['layer']}",
                    f"**Feature:** {case['feature']}",
                    f"**Priority / severity:** {case['priority']} / {case.get('severity') or '—'}",
                    f"**Expected:** {case['expected_result']}",
                    f"**Actual result:** {case['actual_result']}",
                    "",
                    "**Steps:**",
                    "",
                    *[f"{index}. {step}" for index, step in enumerate(case["steps"], start=1)],
                    "",
                    "**Evidence:**",
                    *([f"- {item}" for item in case["evidence"]] or ["- Not recorded"]),
                    "",
                    f"**Owner team:** {case['owner_team']}",
                    "",
                ]
            )
    else:
        lines.append("No failed test case was recorded for this run.")

    security_findings = data.get("security_findings") or []
    lines.extend(["", "## Security and access-control findings", ""])
    if security_findings:
        lines.extend(
            [
                "| ID | Classification | Finding | Target | Expected | Actual | Error location | Evidence |",
                "|---|---|---|---|---|---|---|---|",
            ]
        )
        for finding in security_findings:
            clean = lambda text: str(text or "—").replace("|", "\\|").replace("\n", "<br>")
            lines.append(
                "| "
                + " | ".join(
                    clean(value)
                    for value in (
                        finding.get("id"),
                        finding.get("classification"),
                        finding.get("title"),
                        finding.get("target"),
                        finding.get("expected_result"),
                        finding.get("actual_result"),
                        finding.get("error_location"),
                        ", ".join(finding.get("evidence", [])),
                    )
                )
                + " |"
            )
    else:
        lines.append("No normalized security finding was recorded for this run.")
    lines.extend(
        [
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


def _worksheet_xml(columns_list: list[str], data_rows: list[list[Any]], status_column_name: str | None = None) -> str:
    rows = [columns_list] + data_rows
    sheet_rows: list[str] = []
    for row_index, row in enumerate(rows, start=1):
        cells = []
        for column_index, value in enumerate(row, start=1):
            reference = f"{_column_letter(column_index)}{row_index}"
            style = "1" if row_index == 1 else "0"
            status_column_index = columns_list.index(status_column_name) + 1 if status_column_name in columns_list else -1
            if row_index > 1 and column_index == status_column_index:
                style = {"pass": "2", "fail": "3"}.get(str(value), "4")
            escaped = xml_escape(str(value), {'"': "&quot;"})
            cells.append(f'<c r="{reference}" t="inlineStr" s="{style}"><is><t xml:space="preserve">{escaped}</t></is></c>')
        sheet_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')
    last_row = max(2, len(rows))
    last_column = _column_letter(len(columns_list))
    widths = [min(50, max(14, len(column) + 4)) for column in columns_list]
    columns = "".join(f'<col min="{i}" max="{i}" width="{width}" customWidth="1"/>' for i, width in enumerate(widths, start=1))
    validation = ""
    if status_column_name in columns_list:
        status_list = ",".join(STATUSES)
        status_column = _column_letter(columns_list.index(status_column_name) + 1)
        validation = f'<dataValidations count="1"><dataValidation type="list" allowBlank="0" sqref="{status_column}2:{status_column}1048576"><formula1>"{status_list}"</formula1></dataValidation></dataValidations>'
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'
        f'<cols>{columns}</cols><sheetData>{"".join(sheet_rows)}</sheetData>'
        f'<autoFilter ref="A1:{last_column}{last_row}"/>'
        f'{validation}'
        '</worksheet>'
    )


def write_xlsx(path: Path, data: dict[str, Any]) -> None:
    cases = data["test_cases"]
    test_rows = [[case_to_row(case)[column] for column in CSV_COLUMNS] for case in cases]
    security_columns = [
        "Finding ID", "Title", "Classification", "Target", "Weakness", "Expected Result",
        "Actual Result", "Error Location", "Evidence", "Owner Team", "ClickUp Eligible",
    ]
    security_rows = [
        [
            finding.get("id", ""), finding.get("title", ""), finding.get("classification", ""),
            finding.get("target", ""), finding.get("weakness", ""), finding.get("expected_result", ""),
            finding.get("actual_result", ""), finding.get("error_location", ""),
            _compact(finding.get("evidence", [])), finding.get("owner_team", ""),
            str(bool(finding.get("clickup_eligible"))).lower(),
        ]
        for finding in data.get("security_findings", [])
    ]
    counts = _summary(cases)
    requirement_ids = sorted({item for case in cases for item in case.get("requirement_ids", [])})
    risk_ids = sorted({item for case in cases for item in case.get("risk_ids", [])})
    access_rows = data.get("access_control_matrix", [])
    coverage_rows = [
        ["Total test cases", len(cases)],
        ["Requirements covered", len(requirement_ids)],
        ["Risks covered", len(risk_ids)],
        ["Access-control checks", len(access_rows)],
        ["Security findings", len(data.get("security_findings", []))],
        *[[f"Status: {status}", count] for status, count in counts.items()],
    ]
    sheets = [
        ("Test Cases", _worksheet_xml(list(CSV_COLUMNS), test_rows, "Status")),
        ("Security Findings", _worksheet_xml(security_columns, security_rows)),
        ("Coverage Summary", _worksheet_xml(["Metric", "Value"], coverage_rows)),
    ]
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
        worksheet_types = "".join(f'<Override PartName="/xl/worksheets/sheet{index}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for index in range(1, len(sheets) + 1))
        _zip_write(archive, "[Content_Types].xml", f'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>{worksheet_types}<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>')
        _zip_write(archive, "_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        workbook_sheets = "".join(f'<sheet name="{xml_escape(name)}" sheetId="{index}" r:id="rId{index}"/>' for index, (name, _) in enumerate(sheets, start=1))
        _zip_write(archive, "xl/workbook.xml", f'<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>{workbook_sheets}</sheets></workbook>')
        relationships = "".join(f'<Relationship Id="rId{index}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{index}.xml"/>' for index in range(1, len(sheets) + 1))
        relationships += f'<Relationship Id="rId{len(sheets) + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        _zip_write(archive, "xl/_rels/workbook.xml.rels", f'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{relationships}</Relationships>')
        _zip_write(archive, "xl/styles.xml", styles)
        for index, (_, sheet_xml) in enumerate(sheets, start=1):
            _zip_write(archive, f"xl/worksheets/sheet{index}.xml", sheet_xml)


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
                "external_key": f"AQABSI-{fingerprint[:12]}",
                "name": f"[BUG][{resolve_domain(case)}][{(case.get('severity') or 'untriaged').upper()}] {case['scenario']}",
                "description_markdown": "\n".join(
                    [
                        f"**Test case:** {case['id']}",
                        f"**Domain:** {resolve_domain(case)}",
                        f"**Requirements:** {', '.join(case.get('requirement_ids', [])) or 'Not linked'}",
                        f"**Environment:** {data['environment']}",
                        f"**Priority / severity:** {case['priority']} / {case.get('severity') or '—'}",
                        f"**Expected:** {case['expected_result']}",
                        "",
                        "**Execution log:**",
                        "",
                        "**Steps:**",
                        *[f"{index}. {step}" for index, step in enumerate(case["steps"], start=1)],
                        "",
                        f"**Actual result:** {case['actual_result']}",
                        "",
                        "**Evidence:**",
                        *([f"- {item}" for item in case["evidence"]] or ["- Not recorded"]),
                        "",
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
    for finding in data.get("security_findings", []):
        if finding.get("classification") != "confirmed" or not finding.get("clickup_eligible"):
            continue
        fingerprint = hashlib.sha256(
            "|".join(
                (
                    data["environment"],
                    data["source"]["repository"],
                    str(finding.get("id", "")),
                    str(finding.get("target", "")),
                    str(finding.get("actual_result", "")),
                )
            ).encode()
        ).hexdigest()
        tasks.append(
            {
                "fingerprint": fingerprint,
                "external_key": f"AQABSI-SEC-{fingerprint[:12]}",
                "finding_id": finding.get("id"),
                "name": f"[SECURITY][{resolve_domain(finding)}][{str(finding.get('business_priority', 'unmapped')).upper()}] {finding.get('title', 'Confirmed security finding')}",
                "description_markdown": "\n".join(
                    [
                        f"**Finding:** {finding.get('id', 'Not recorded')}",
                        f"**Classification:** {finding.get('classification')}",
                        f"**Domain:** {resolve_domain(finding)}",
                        f"**Target:** {finding.get('target', 'Not recorded')}",
                        f"**Expected:** {finding.get('expected_result', 'Not recorded')}",
                        f"**Actual:** {finding.get('actual_result', 'Not recorded')}",
                        f"**Error location:** {finding.get('error_location', 'Needs validation')}",
                        f"**Evidence:** {', '.join(finding.get('evidence', [])) or 'Not recorded'}",
                        f"**Source commit:** {data['source']['commit_sha']}",
                    ]
                ),
                "owner_team": finding.get("owner_team"),
                "assignee_id": None,
                "severity": finding.get("business_priority"),
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
        write_xlsx(temporary / "test-cases.xlsx", data)
        confluence = {
            "dry_run": True,
            "publication_requires_authorization": True,
            "idempotency_key": data["run_id"],
            "target_space": None,
            "parent_page_id": None,
            "suggested_title": f"QA Report — {data['run_id']} — {data['title']}",
            "body_format": "markdown",
            "body": build_confluence_body(data),
        }
        (temporary / "confluence-draft.json").write_text(json.dumps(confluence, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (temporary / "clickup-drafts.json").write_text(json.dumps(build_clickup_drafts(data), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(output_dir)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="AQABSI test-run JSON manifest")
    parser.add_argument("output", type=Path, help="New output directory")
    args = parser.parse_args()
    try:
        generate(args.input.resolve(), args.output.resolve())
    except (OSError, json.JSONDecodeError, ManifestError) as exc:
        print(f"AQABSI artifact generation failed: {exc}", file=sys.stderr)
        return 2
    print(f"Generated sanitized AQABSI artifacts in {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
