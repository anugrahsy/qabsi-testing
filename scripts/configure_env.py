#!/usr/bin/env python3
"""Safely write AQABSI configuration values into the gitignored .env.

The skill's preflight collects ALL data up front (target account, Confluence,
ClickUp) and persists secret values here — never into PRDs, manifests, reports,
memory, or committed files.

Usage:
    python3 scripts/configure_env.py '{"AQABSI_TEST_USERNAME":"...", "AQABSI_TEST_PASSWORD":"..."}'
    python3 scripts/configure_env.py --stdin   # reads JSON object from stdin
    python3 scripts/configure_env.py @/tmp/values.json  # reads JSON from a file path

Only the *names* of the keys written are printed. Values are never echoed.
"""
import json
import os
import stat
import sys

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")

VALID_KEYS = {
    "AQABSI_CONFLUENCE_DEPLOYMENT", "AQABSI_CONFLUENCE_BASE_URL",
    "AQABSI_CONFLUENCE_EMAIL", "AQABSI_CONFLUENCE_API_TOKEN", "AQABSI_CONFLUENCE_PAT",
    "AQABSI_CONFLUENCE_SPACE_ID", "AQABSI_CONFLUENCE_SPACE_KEY", "AQABSI_CONFLUENCE_PARENT_PAGE_ID",
    "AQABSI_CLICKUP_AUTH_MODE", "AQABSI_CLICKUP_API_TOKEN",
    "AQABSI_CLICKUP_WORKSPACE_ID", "AQABSI_CLICKUP_LIST_ID",
    "AQABSI_TARGET_BASE_URL", "AQABSI_TARGET_AUTH_MODE",
    "AQABSI_TEST_USERNAME", "AQABSI_TEST_PASSWORD", "AQABSI_TEST_TOKEN",
    "AQABSI_TARGET_LOGIN_PATH", "AQABSI_OWNERSHIP_REGISTRY",
}


def parse_existing(path):
    """Return an ordered list of (kind, key, raw_line) preserving comments/blank lines."""
    entries = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f.read().splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    entries.append(("comment", None, line))
                    continue
                if "=" in line:
                    key = line.split("=", 1)[0].strip()
                    entries.append(("kv", key, line))
                else:
                    entries.append(("comment", None, line))
    return entries


def encode_value(value):
    value = str(value)
    if value == "" or any(ch in value for ch in (" ", "#", '"', "'", "=")):
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return value


def load_values(argv):
    if not argv:
        print("error: no values supplied", file=sys.stderr)
        return None, 2
    arg = argv[0]
    try:
        if arg == "--stdin":
            raw = sys.stdin.read()
        elif arg.startswith("@"):
            with open(arg[1:], "r", encoding="utf-8") as f:
                raw = f.read()
        else:
            raw = arg
        data = json.loads(raw)
    except Exception as e:  # noqa: BLE001
        print(f"error: cannot parse values as JSON: {e}", file=sys.stderr)
        return None, 2
    if not isinstance(data, dict):
        print("error: values must be a JSON object of KEY -> value", file=sys.stderr)
        return None, 2
    return data, 0


def main(argv):
    data, code = load_values(argv)
    if data is None:
        return code

    bad = [k for k in data if k not in VALID_KEYS]
    if bad:
        print("error: unknown variable(s): " + ", ".join(sorted(bad)), file=sys.stderr)
        print("allowed: " + ", ".join(sorted(VALID_KEYS)), file=sys.stderr)
        return 2

    entries = parse_existing(ENV_PATH)
    by_key = {k: v for kind, k, v in entries if kind == "kv"}

    written = []
    for key, value in data.items():
        line = f"{key}={encode_value(value)}"
        if key in by_key:
            for i, (kind, k, _v) in enumerate(entries):
                if kind == "kv" and k == key:
                    entries[i] = ("kv", key, line)
                    break
        else:
            entries.append(("kv", key, line))
        written.append(key)

    os.makedirs(os.path.dirname(ENV_PATH), exist_ok=True)
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        for _kind, _key, line in entries:
            f.write(line + "\n")
    try:
        os.chmod(ENV_PATH, stat.S_IRUSR | stat.S_IWUSR)  # 0600
    except OSError:
        pass

    # Print names only — never values.
    print("configured " + ", ".join(sorted(written)) + " in " + ENV_PATH)
    print("reminder: .env is gitignored; values never go into PRDs/reports/memory.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
