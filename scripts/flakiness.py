#!/usr/bin/env python3
"""Detect flaky AQABSI API test cases through bounded deterministic re-execution.

Reads a manifest, re-runs every ``api``-layer case whose status is ``fail``,
``flaky``, or ``environment_error`` up to N times (default 3), and reclassifies
it: consistent failure stays ``fail``, partial success becomes ``flaky``, and a
case whose earlier failure never reproduces is marked ``pass`` (for environment
errors) or ``flaky`` (for transient test/environment issues). Never fabricates a
pass; never writes tokens to the output manifest.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from pathlib import Path
from typing import Any

from executor import classify_status, perform_request, resolve_target

RETRY_STATUSES = {"fail", "flaky", "environment_error"}


def classify_flakiness(original_status: str, passes: int, attempts: int) -> tuple[str, str]:
    if passes <= 0:
        return "fail", "Consistent failure across re-runs."
    if passes < attempts:
        return "flaky", f"{passes}/{attempts} re-runs passed; behavior is inconsistent."
    if original_status == "environment_error":
        return "pass", "All re-runs passed; the earlier environment failure did not reproduce."
    return "flaky", "All re-runs passed; the earlier failure did not reproduce (transient test/environment issue)."


def run_attempts(
    case: dict[str, Any],
    base_url: str,
    token: str | None,
    attempts: int,
    timeout: float,
) -> tuple[int, list[int | None], str | None]:
    target = resolve_target(case)
    if not target["method"] or not target["path"]:
        return 0, [], "unresolvable request target"
    passes = 0
    observations: list[int | None] = []
    for _ in range(attempts):
        actual_status, _, _ = perform_request(target, base_url, token, timeout)
        status = classify_status(actual_status, target["expected_status"], target["expected_success"])
        if status == "pass":
            passes += 1
        observations.append(actual_status)
    return passes, observations, None


def analyze_manifest(
    data: dict[str, Any],
    base_url: str,
    token: str | None,
    attempts: int,
    timeout: float,
) -> tuple[dict[str, Any], dict[str, int]]:
    result = copy.deepcopy(data)
    summary: dict[str, int] = {"fail": 0, "flaky": 0, "pass": 0, "environment_error": 0, "unresolved": 0}
    for case in result.get("test_cases") or []:
        if not isinstance(case, dict):
            continue
        if case.get("status") not in RETRY_STATUSES or case.get("layer") != "api":
            continue
        passes, observations, error = run_attempts(case, base_url, token, attempts, timeout)
        if error:
            summary["unresolved"] += 1
            continue
        environment_errors = sum(1 for status in observations if status is None)
        original = str(case["status"])
        if environment_errors == len(observations):
            final = "environment_error"
            note = "Re-runs could not reach the target; the environment failure persisted."
        else:
            final, note = classify_flakiness(original, passes, attempts)

        case["status"] = final
        case["actual_result"] = f"{passes}/{attempts} re-runs passed; observed statuses: {observations}"
        evidence = list(case.get("evidence") or [])
        evidence.append(f"flakiness check: {passes}/{attempts} passed, statuses {observations}")
        case["evidence"] = evidence
        existing = str(case.get("notes") or "").strip()
        case["notes"] = (existing + "; " if existing else "") + note
        summary[final] += 1
    return result, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="AQABSI test-run JSON manifest")
    parser.add_argument("--output", type=Path, help="Output manifest path (default: <input>.flaky.json)")
    parser.add_argument("--attempts", type=int, default=3, help="Re-run count per case (default: 3)")
    parser.add_argument("--base-url", help="Target base URL (default: AQABSI_TARGET_BASE_URL)")
    parser.add_argument("--token", help="Bearer token (default: AQABSI_TEST_TOKEN); never written to output")
    parser.add_argument("--timeout", type=float, default=8.0, help="Per-request timeout in seconds")
    args = parser.parse_args()

    if args.attempts < 1:
        print("AQABSI flakiness failed: --attempts must be at least 1.", file=sys.stderr)
        return 2
    base_url = (args.base_url or os.environ.get("AQABSI_TARGET_BASE_URL", "")).strip()
    token = args.token if args.token is not None else os.environ.get("AQABSI_TEST_TOKEN", "").strip()
    if not base_url:
        print("AQABSI flakiness failed: target base URL is required (--base-url or AQABSI_TARGET_BASE_URL).", file=sys.stderr)
        return 2
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"AQABSI flakiness failed: {exc}", file=sys.stderr)
        return 2

    analyzed, summary = analyze_manifest(data, base_url, token or None, args.attempts, args.timeout)
    output = args.output or Path(str(args.input.with_suffix("")) + ".flaky.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(analyzed, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"schema_version": "1.0", "attempts": args.attempts, "output": str(output), "summary": summary}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
