#!/usr/bin/env python3
"""
Repackage the reviewed plugin as a patched release.

Includes only source-controlled content: NO node_modules, NO dist, NO .env.
Bumps the version to 0.2.1 to signal the bind-host security fix, and records it in CHANGELOG.
"""
import json
import os
import zipfile

SRC = "/opt/data/openemr_plugin_review"
OUT = "/opt/data/NURA/ops/openemr-plugin/NURA_OpenEMR_Plugin_v0.2.1-patched.zip"
SKIP_DIRS = {"node_modules", "dist", ".git", "coverage"}

# --- bump versions ---------------------------------------------------------
pj = os.path.join(SRC, "package.json")
d = json.load(open(pj))
old_pkg = d["version"]
d["version"] = "0.2.1"
json.dump(d, open(pj, "w"), indent=2)
open(pj, "a").write("\n")

cpj = os.path.join(SRC, ".codex-plugin", "plugin.json")
c = json.load(open(cpj))
old_codex = c["version"]
c["version"] = "0.2.1"
json.dump(c, open(cpj, "w"), indent=2)
open(cpj, "a").write("\n")

# --- changelog -------------------------------------------------------------
cl = os.path.join(SRC, "CHANGELOG.md")
prev = open(cl).read() if os.path.exists(cl) else "# Changelog\n"
entry = (
    "## 0.2.1 — 2026-09-13\n\n"
    "### Security\n"
    "- **Bind host no longer defaults to `0.0.0.0`.** The server previously listened on every\n"
    "  interface while `.mcp.json` advertised `http://127.0.0.1:8787/mcp` and the README instructed a\n"
    "  local connection. With the development default `AUTH_MODE=passthrough` — which accepts any\n"
    "  bearer token — a wide bind exposed the complete MCP tool surface to every reachable interface\n"
    "  (verified: a dummy bearer returned HTTP 200 with the tool list, and the port answered on the\n"
    "  host's LAN address). `BIND_HOST` now defaults to `127.0.0.1`; external exposure requires an\n"
    "  explicit `BIND_HOST`. Malformed values are rejected at startup and never executed.\n"
    "- Added 3 regression tests: loopback default, explicit override, malformed value rejected.\n\n"
    "### Documentation\n"
    "- `.env.example` documents `BIND_HOST` and the passthrough exposure consideration.\n\n"
    "### Not changed\n"
    "- No functional or clinical behaviour change. Read-only boundary, auth model, token exchange,\n"
    "  and audit output are untouched.\n\n"
)
open(cl, "w").write(prev.rstrip() + "\n\n" + entry)

print(f"  package.json  {old_pkg} -> 0.2.1")
print(f"  plugin.json   {old_codex} -> 0.2.1")
print("  CHANGELOG.md  entry added")

# --- zip -------------------------------------------------------------------
os.makedirs(os.path.dirname(OUT), exist_ok=True)
n = 0
skipped = 0
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(SRC):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for f in sorted(files):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, SRC)
            if f == ".env" or f.endswith(".log") or f == "package-lock.json.orig":
                skipped += 1
                continue
            z.write(p, rel)
            n += 1
            print(f"    + {rel}")
print(f"\n  wrote {OUT}")
print(f"  entries: {n}  skipped: {skipped}  bytes: {os.path.getsize(OUT):,}")
