#!/usr/bin/env python3
"""Report AQABSI Confluence and ClickUp readiness without exposing secrets."""

from __future__ import annotations

import argparse
import json
import os
from typing import Sequence

from integration_config import build_readiness, load_integration_config, redact
from integration_http import verify_clickup, verify_confluence


def _human_message(payload: dict[str, object]) -> str:
    lines = [f"AQABSI integration preflight ({payload.get('mode', 'offline')})"]
    providers = payload["providers"]
    assert isinstance(providers, dict)
    for name, raw in providers.items():
        item = raw if isinstance(raw, dict) else {}
        status = item.get("status", "invalid")
        lines.append(f"- {name}: {status}")
        missing = item.get("missing", [])
        if missing:
            lines.append("  Missing: " + ", ".join(str(value) for value in missing))
        errors = item.get("errors", [])
        for error in errors if isinstance(errors, list) else []:
            lines.append(f"  Error: {error}")
        if status in {"missing", "invalid", "unauthorized", "forbidden", "unreachable"}:
            lines.append(f"  Setup: {item.get('setup_url')}")
        if status == "verified":
            identity = item.get("identity", {})
            destination = item.get("destination", {})
            if isinstance(identity, dict):
                identity_label = identity.get("display_name") or identity.get("id")
                if identity_label:
                    lines.append(f"  Verified identity: {identity_label}")
            if isinstance(destination, dict):
                destination_label = destination.get("name") or destination.get("key") or destination.get("id")
                if destination_label:
                    lines.append(f"  Verified destination: {destination_label}")
        options = item.get("configuration_options", {})
        if status == "missing" and isinstance(options, dict):
            for option, names in options.items():
                if isinstance(names, list):
                    lines.append(
                        f"  If {option}: " + ", ".join(str(name) for name in names)
                    )
        assignment = item.get("assignment", {})
        if isinstance(assignment, dict) and assignment.get("status") == "optional_missing":
            lines.append(
                "  Optional assignment setup: "
                + str(assignment.get("variable"))
                + " (needed to assign tasks automatically)"
            )
    lines.append("Never paste API tokens into chat or commit them to a repository.")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--provider",
        action="append",
        choices=("confluence", "clickup"),
        help="Check only the selected provider; repeat to select both.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Perform bounded read-only provider verification.",
    )
    args = parser.parse_args(argv)

    config = load_integration_config(os.environ)
    payload = build_readiness(config, args.provider)
    if args.verify:
        payload["mode"] = "verify"
        providers = payload["providers"]
        assert isinstance(providers, dict)
        if "confluence" in providers and providers["confluence"].get("status") == "ready":
            providers["confluence"].update(verify_confluence(config.confluence).to_dict())
        if "clickup" in providers and providers["clickup"].get("status") == "ready":
            providers["clickup"].update(verify_clickup(config.clickup).to_dict())
    safe_payload = redact(payload, config.secrets)
    if args.json:
        print(json.dumps(safe_payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        assert isinstance(safe_payload, dict)
        print(_human_message(safe_payload))

    providers = safe_payload["providers"]
    assert isinstance(providers, dict)
    statuses = {
        item.get("status")
        for item in providers.values()
        if isinstance(item, dict)
    }
    if "invalid" in statuses:
        return 3
    if "missing" in statuses:
        return 2
    if statuses - {"ready", "verified"}:
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
