#!/usr/bin/env python3
"""Launch the official Hostinger MCP with a token from the active Hermes .env."""

from __future__ import annotations

import os
from pathlib import Path


def _read_secret(path: Path, name: str) -> str | None:
    if not path.exists():
        return None
    for raw_line in path.read_text(errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == name:
            value = value.strip().strip('"').strip("'")
            return value or None
    return None


hermes_home = Path(os.environ.get("HERMES_HOME", "/opt/data"))
token = os.environ.get("HOSTINGER_API_TOKEN") or _read_secret(
    hermes_home / ".env", "HOSTINGER_API_TOKEN"
)
if not token:
    raise SystemExit("HOSTINGER_API_TOKEN is not configured in the active Hermes secret store")

environment = os.environ.copy()
environment["HOSTINGER_API_TOKEN"] = token

binary = hermes_home / "mcp-installs" / "hostinger-api" / "node_modules" / ".bin" / "hostinger-vps-mcp"
if not binary.is_file():
    raise SystemExit(f"Pinned Hostinger VPS MCP binary is missing: {binary}")

os.execvpe(str(binary), [str(binary)], environment)
