#!/usr/bin/env python3
"""Deterministic professional-quality gates for AQABSI PRDs and test runs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


AMBIGUOUS_PHRASES = (
    "works normally",
    "berjalan normal",
    "user friendly",
    "fast",
    "cepat",
    "secure",
    "aman",
    "as expected",
    "sesuai harapan",
)
SECRET_KEYS = {
    "password",
    "passwd",
    "passphrase",
    "password_confirmation",
    "password_konfirmasi",
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "cookie",
    "secret",
    "api_key",
    "client_secret",
    "otp",
    "otp_code",
    "pin",
    "code",
}
DESTRUCTIVE_PATTERNS = (
    re.compile(r"\bdelete\s+all\b", re.IGNORECASE),
    re.compile(r"\btruncate\b", re.IGNORECASE),
    re.compile(r"\bdrop\s+(?:table|database|schema)\b", re.IGNORECASE),
    re.compile(r"\bwipe\b", re.IGNORECASE),
    re.compile(r"\bhapus\s+semua\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class Finding:
    code: str
    path: str
    message: str
    severity: str = "error"


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _is_ambiguous(value: Any) -> bool:
    text = _normalize(str(value))
    return any(
        re.search(r"(?<!\w)" + re.escape(phrase).replace(r"\ ", r"\s+") + r"(?!\w)", text)
        for phrase in AMBIGUOUS_PHRASES
    )


def _nonblank_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nonblank_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_nonblank_string(item) for item in value)


def _adaptive_outcome(data: dict[str, Any], section_id: str) -> bool:
    for section in data.get("adaptive_sections", []):
        if not isinstance(section, dict) or section.get("id") != section_id:
            continue
        applicability = section.get("applicability")
        if applicability == "not_applicable":
            return _nonblank_string(section.get("rationale")) and _nonblank_string(section.get("reviewer"))
        if applicability in {"required", "optional"}:
            return section.get("content") not in (None, "", [], {})
    return False


def _secret_paths(value: Any, path: str = "") -> Iterable[str]:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_")
            child = f"{path}.{key}" if path else key
            if normalized in SECRET_KEYS or normalized.endswith(("_password", "_token", "_secret", "_otp", "_pin")):
                yield child
            yield from _secret_paths(item, child)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _secret_paths(item, f"{path}[{index}]")
    elif isinstance(value, str):
        if re.search(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+", value) or re.search(
            r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b", value
        ):
            yield path or "$"


def _validate_prd(data: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    requirements = data.get("requirements")
    traceability = data.get("traceability")
    evidence_sources = data.get("evidence_sources", [])
    document = data.get("document")
    required_document_fields = ("title", "version", "status", "business_owner", "technical_owner", "qa_owner", "evidence_cutoff")
    if not isinstance(document, dict) or any(not _nonblank_string(document.get(field)) for field in required_document_fields):
        findings.append(Finding("PRD_DOCUMENT_CONTROL_MISSING", "$.document", "Document control and business/technical/QA ownership are required."))
    if not _nonblank_string(data.get("summary")):
        findings.append(Finding("PRD_SUMMARY_MISSING", "$.summary", "A concise problem/outcome summary is required."))
    scope = data.get("scope")
    scope_present = isinstance(scope, dict) and all(isinstance(scope.get(field), list) for field in ("in_scope", "out_of_scope", "non_goals"))
    if not scope_present and not _adaptive_outcome(data, "scope-boundary"):
        findings.append(Finding("PRD_SCOPE_OUTCOME_MISSING", "$.scope", "Scope boundary is required as a standard or adaptive section."))
    if not data.get("risks") and not _adaptive_outcome(data, "risk-register"):
        findings.append(Finding("PRD_RISK_OUTCOME_MISSING", "$.risks", "Risk analysis is required or must be marked not applicable with review."))
    if not data.get("release_evidence") and not _adaptive_outcome(data, "release-evidence"):
        findings.append(Finding("PRD_RELEASE_EVIDENCE_MISSING", "$.release_evidence", "Release evidence/sign-off outcome is required."))
    if not isinstance(evidence_sources, list) or not evidence_sources:
        findings.append(Finding("PRD_EVIDENCE_LEDGER_MISSING", "$.evidence_sources", "At least one traceable evidence source is required."))
    if not isinstance(requirements, list) or not requirements:
        findings.append(Finding("PRD_REQUIREMENTS_MISSING", "$.requirements", "At least one atomic requirement is required."))
        return findings

    known_sources = {
        source.get("id") for source in evidence_sources if isinstance(source, dict) and source.get("id")
    }
    traced_requirements = {
        row.get("requirement_id") for row in traceability or [] if isinstance(row, dict)
    }
    for index, requirement in enumerate(requirements):
        path = f"$.requirements[{index}]"
        if not isinstance(requirement, dict):
            findings.append(Finding("PRD_REQUIREMENT_INVALID", path, "Requirement must be an object."))
            continue
        requirement_id = requirement.get("id")
        source_ids = requirement.get("source_ids") or []
        if not _nonblank_string(requirement.get("statement")):
            findings.append(Finding("PRD_STATEMENT_MISSING", f"{path}.statement", "Requirement statement must be nonblank."))
        if not _nonblank_string_list(source_ids):
            findings.append(Finding("PRD_SOURCE_MISSING", f"{path}.source_ids", "Requirement must reference evidence."))
        for source_id in source_ids:
            if source_id not in known_sources:
                findings.append(Finding("PRD_SOURCE_UNKNOWN", f"{path}.source_ids", f"Unknown source ID: {source_id}"))
        criteria = requirement.get("acceptance_criteria") or []
        if not criteria:
            findings.append(Finding("PRD_ACCEPTANCE_MISSING", f"{path}.acceptance_criteria", "Observable acceptance criteria are required."))
        if any(_is_ambiguous(item) for item in criteria):
            findings.append(Finding("AMBIGUOUS_ORACLE", f"{path}.acceptance_criteria", "Replace ambiguous language with an observable outcome or threshold."))
        if not _nonblank_string_list(requirement.get("error_behavior")):
            findings.append(Finding("PRD_ERROR_BEHAVIOR_MISSING", f"{path}.error_behavior", "Relevant negative/error behavior is required."))
        if requirement_id not in traced_requirements:
            findings.append(Finding("PRD_TRACEABILITY_MISSING", f"{path}.id", f"{requirement_id or 'Requirement'} is absent from traceability."))
    for index, row in enumerate(traceability or []):
        if not isinstance(row, dict):
            continue
        if not _nonblank_string_list(row.get("source_ids")) or not _nonblank_string_list(row.get("risk_ids")) or not _nonblank_string_list(row.get("test_case_ids")):
            findings.append(Finding("PRD_TRACEABILITY_INCOMPLETE", f"$.traceability[{index}]", "Traceability requires source, risk, and test-case IDs."))
    return findings


def _validate_test_run(data: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    cases = data.get("test_cases")
    if not isinstance(cases, list) or not cases:
        return [Finding("TEST_CASES_MISSING", "$.test_cases", "At least one test case is required.")]

    intents: dict[tuple[str, str, str], str] = {}
    run_authorization = data.get("authorization_record")
    for index, case in enumerate(cases):
        path = f"$.test_cases[{index}]"
        if not isinstance(case, dict):
            findings.append(Finding("TEST_CASE_INVALID", path, "Test case must be an object."))
            continue
        for field in ("requirement_ids", "risk_ids", "source_ids", "module_ids"):
            if not case.get(field):
                findings.append(Finding("TEST_TRACEABILITY_MISSING", f"{path}.{field}", f"{field} must contain at least one ID."))

        expected = case.get("expected_result", "")
        if not expected or _is_ambiguous(expected):
            findings.append(Finding("AMBIGUOUS_ORACLE", f"{path}.expected_result", "Expected result must be specific and observable."))

        intent = (
            _normalize(str(case.get("scenario", ""))),
            _normalize(" | ".join(str(step) for step in case.get("steps", []))),
            _normalize(str(expected)),
        )
        if intent in intents:
            findings.append(Finding("DUPLICATE_TEST_INTENT", path, f"Test intent duplicates {intents[intent]}."))
        else:
            intents[intent] = str(case.get("id", path))

        status = case.get("status")
        if status in {"pass", "fail"} and (
            not _nonblank_string(case.get("actual_result")) or not _nonblank_string_list(case.get("evidence"))
        ):
            findings.append(Finding("EXECUTED_RESULT_WITHOUT_EVIDENCE", path, "Executed verdict requires actual result and sanitized evidence."))
        if status == "not_run" and (case.get("actual_result") or case.get("severity") is not None):
            findings.append(Finding("NOT_RUN_HAS_RESULT", path, "A not_run case cannot have actual result or severity."))

        secret_locations = sorted(set(_secret_paths(case.get("test_data"), f"{path}.test_data")))
        if secret_locations:
            findings.append(Finding("SECRET_LIKE_TEST_DATA", f"{path}.test_data", "Use opaque credential references; secret-like data found at " + ", ".join(secret_locations)))

        steps = "\n".join(str(step) for step in case.get("steps", []))
        destructive = any(pattern.search(steps) for pattern in DESTRUCTIVE_PATTERNS)
        if destructive and not (case.get("authorization_record") or run_authorization):
            findings.append(Finding("DESTRUCTIVE_STEP_WITHOUT_AUTHORIZATION", f"{path}.steps", "Destructive steps require a scoped authorization record."))
        if destructive and not case.get("cleanup"):
            findings.append(Finding("CLEANUP_REQUIRED", f"{path}.cleanup", "Destructive or mutating tests require cleanup/rollback instructions."))
    return findings


def validate_document(data: Any, kind: str) -> list[Finding]:
    if not isinstance(data, dict):
        return [Finding("DOCUMENT_INVALID", "$", "Document must be a JSON object.")]
    if kind == "prd":
        return _validate_prd(data)
    if kind == "test-run":
        return _validate_test_run(data)
    return [Finding("KIND_UNSUPPORTED", "$", f"Unsupported document kind: {kind}")]


def _verdict(findings: list[Finding], kind: str) -> str:
    if findings:
        if kind == "prd" and all(item.code.startswith("PRD_SOURCE") for item in findings):
            return "needs_technical_evidence"
        return "draft_incomplete"
    return "review_ready"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--kind", required=True, choices=("prd", "test-run"))
    parser.add_argument("--format", choices=("human", "json"), default="human")
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"AQABSI quality validation failed: {exc}", file=sys.stderr)
        return 2
    findings = validate_document(data, args.kind)
    payload = {"kind": args.kind, "verdict": _verdict(findings, args.kind), "findings": [asdict(item) for item in findings]}
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"AQABSI quality verdict: {payload['verdict']}")
        for finding in findings:
            print(f"- [{finding.code}] {finding.path}: {finding.message}")
    return 2 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
