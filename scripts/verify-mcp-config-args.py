#!/usr/bin/env python3
"""verify-mcp-config-args.py — read-only defect scan for the Hermes MCP config.

WHY: the 09-12 audits found ~27 MCP lanes parking every cron boot at ~650/h.
Root cause (verified 2026-09-12T20:07Z, dry-run on a config copy):
  Defect A — `args:` stored as a YAML *string* holding a JSON array.
             The literal '[' is passed as argv[1] ->
             `npm error code EINVALIDTAGNAME Invalid tag name "["`.
  Defect B — `command:` holds binary + script path in one space-separated
             string -> FileNotFoundError: 'python3 /opt/data/scripts/...'.

This instrument is READ-ONLY: it never edits the config. Its job is to make
the defect count and the affected lane list a first-class audit output so the
next audit does not have to hand-roll a grep. The fixer lives beside it at
/opt/data/scripts/fix-mcp-args.py (apply = approval-gated: it rewrites the
live MCP config and needs a gateway restart to take effect).

Exit codes: 0 = no defects, 1 = defects present.
Usage: /opt/hermes/.venv/bin/python3 /opt/data/scripts/verify-mcp-config-args.py [config.yaml]
"""
import os
import sys

import yaml

CFG = sys.argv[1] if len(sys.argv) > 1 else "/opt/data/profiles/nura/config.yaml"


def main() -> int:
    if not os.path.exists(CFG):
        print(f"FAIL: config not found: {CFG}")
        return 1
    try:
        with open(CFG, encoding="utf-8") as fh:
            doc = yaml.safe_load(fh) or {}
    except Exception as exc:  # malformed YAML is itself a finding
        print(f"FAIL: config does not parse: {type(exc).__name__}: {exc}")
        return 1

    servers = doc.get("mcp_servers") or doc.get("mcp") or {}
    if not isinstance(servers, dict):
        print(f"FAIL: mcp_servers is {type(servers).__name__}, expected mapping")
        return 1

    enabled = {k: v for k, v in servers.items() if isinstance(v, dict) and v.get("enabled") is not False}

    defect_a, defect_b, no_cmd = [], [], []
    for name, cfg in sorted(enabled.items()):
        args = cfg.get("args")
        # A non-empty string that looks like a JSON array is the defect.
        if isinstance(args, str) and args.strip() not in ("", "[]"):
            defect_a.append((name, args.strip()[:60]))
        cmd = cfg.get("command")
        if isinstance(cmd, str) and " " in cmd.strip():
            defect_b.append((name, cmd.strip()[:60]))
        if not cmd and not cfg.get("url"):
            no_cmd.append(name)

    print(f"config      : {CFG}")
    print(f"servers     : {len(servers)} total / {len(enabled)} enabled")
    print(f"defect A    : {len(defect_a)}  (args stored as a quoted string -> EINVALIDTAGNAME)")
    for n, v in defect_a:
        print(f"              - {n}: args: '{v}'")
    print(f"defect B    : {len(defect_b)}  (command holds binary + path -> FileNotFoundError)")
    for n, v in defect_b:
        print(f"              - {n}: command: {v}")
    print(f"unstartable : {len(no_cmd)}  (enabled, no command and no url)")
    if no_cmd:
        print(f"              {' '.join(no_cmd)}")

    if defect_a or defect_b:
        print()
        print(f"VERDICT: {len(defect_a) + len(defect_b)} malformed lane(s) -> these park deterministically")
        print("         each cron boot. Fixer: /opt/data/scripts/fix-mcp-args.py")
        print("         APPLY IS GATED (rewrites live MCP config; needs gateway restart).")
        return 1
    print()
    print("VERDICT: no args/command defects — lanes that still park fail for another reason.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
