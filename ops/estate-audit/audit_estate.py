#!/usr/bin/env python3
"""
FULL ESTATE AUDIT — skills, artifacts, plugins, and monitoring coverage.

Purpose: answer three questions with evidence.
  1. WHAT EXISTS       — skills, scripts, plugins, crons, services
  2. WHAT IS BROKEN    — structural defects, missing files, bad frontmatter, syntax errors
  3. WHAT IS UNMONITORED — the real target: systems with no watcher

The third is the one that matters. The a2a lane died for six days not because it was misconfigured
but because nothing watched it. So this audit ends with a coverage map: for every system, is there
a named job that would notice if it stopped?
"""
import json
import os
import re
import subprocess
import sys

PROFILE = "/opt/data/profiles/nura"
SKILLS_DIRS = [f"{PROFILE}/skills", "/opt/data/skills"]
SCRIPTS_DIRS = ["/opt/data/scripts", f"{PROFILE}/scripts", "/opt/data/NURA/scripts"]
CRON = f"{PROFILE}/cron/jobs.json"

out = {}


def sh(cmd, timeout=60):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return ""


# ══════════════════════════════════════════════════════════════════════════
print("=" * 92)
print("1. SKILLS — inventory and structural validation")
print("=" * 92)

skills = []
for base in SKILLS_DIRS:
    if not os.path.isdir(base):
        continue
    for root, dirs, files in os.walk(base):
        if "SKILL.md" in files:
            p = os.path.join(root, "SKILL.md")
            name = os.path.basename(root)
            try:
                txt = open(p, encoding="utf-8", errors="ignore").read()
            except Exception:
                txt = ""
            fm = {}
            m = re.match(r"^---\s*\n(.*?)\n---", txt, re.S)
            if m:
                for line in m.group(1).splitlines():
                    if ":" in line and not line.startswith(" "):
                        k, _, v = line.partition(":")
                        fm[k.strip()] = v.strip()
            skills.append({
                "name": name, "path": p, "bytes": len(txt),
                "has_fm": bool(m),
                "desc": fm.get("description", ""),
                "desc_len": len(fm.get("description", "")),
                "dir": root,
            })

print(f"  skills found (SKILL.md present): {len(skills)}")
no_fm = [s for s in skills if not s["has_fm"]]
no_desc = [s for s in skills if not s["desc"]]
long_desc = [s for s in skills if s["desc_len"] > 160]
tiny = [s for s in skills if s["bytes"] < 400]
print(f"    no YAML frontmatter : {len(no_fm)}")
print(f"    no description      : {len(no_desc)}")
print(f"    description >160ch  : {len(long_desc)}")
print(f"    suspiciously tiny   : {len(tiny)}")
if no_fm:
    print("    -- no frontmatter:")
    for s in no_fm[:8]:
        print(f"       {s['name']}")
if tiny:
    print("    -- tiny (possible stubs/pruned):")
    for s in tiny[:8]:
        print(f"       {s['name']:<44} {s['bytes']}B")

# duplicate basenames = possible collisions
from collections import Counter
dupes = {k: v for k, v in Counter(s["name"] for s in skills).items() if v > 1}
print(f"    duplicate skill names: {len(dupes)}  {list(dupes)[:6]}")
out["skills"] = {"total": len(skills), "no_fm": len(no_fm), "no_desc": len(no_desc),
                 "tiny": len(tiny), "dupes": len(dupes)}

# ── skill directories with NO SKILL.md (orphaned scaffolding)
orphan_dirs = []
for base in SKILLS_DIRS:
    if not os.path.isdir(base):
        continue
    for root, dirs, files in os.walk(base):
        if os.path.basename(root) == "references" or "/references" in root:
            continue
        if not files and not dirs:
            orphan_dirs.append(root)
print(f"    empty directories: {len(orphan_dirs)}")

# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 92)
print("2. ARTIFACTS / SCRIPTS — do they even parse?")
print("=" * 92)
scripts = []
for base in SCRIPTS_DIRS:
    if not os.path.isdir(base):
        continue
    for f in sorted(os.listdir(base)):
        p = os.path.join(base, f)
        if os.path.isfile(p) and (f.endswith(".py") or f.endswith(".sh")):
            scripts.append(p)
print(f"  scripts found: {len(scripts)}")

bad = []
for p in scripts:
    if p.endswith(".py"):
        try:
            r = subprocess.run(["/opt/hermes/.venv/bin/python3", "-m", "py_compile", p],
                               capture_output=True, text=True, timeout=30)
            if r.returncode != 0:
                bad.append((p, (r.stderr or "").strip().splitlines()[-1][:90]))
        except Exception as e:
            bad.append((p, f"compile-exc {e}"))
    else:
        r = subprocess.run(["bash", "-n", p], capture_output=True, text=True, timeout=20)
        if r.returncode != 0:
            bad.append((p, (r.stderr or "").strip()[:90]))
print(f"  SYNTAX ERRORS: {len(bad)}")
for p, e in bad[:15]:
    print(f"    {p.split('/')[-1]:<44} {e}")

# git state of the ops repo
gdirty = sh("cd /opt/data/NURA && git status --porcelain | wc -l")
glast = sh("cd /opt/data/NURA && git log --oneline -1")
print(f"\n  NURA repo: {gdirty} uncommitted changes | HEAD {glast[:70]}")
out["scripts"] = {"total": len(scripts), "syntax_errors": len(bad)}

# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 92)
print("3. PLUGINS / MCP LANES")
print("=" * 92)
import yaml
try:
    cfg = yaml.safe_load(open(f"{PROFILE}/config.yaml"))
except Exception as e:
    cfg = {}
    print("  config.yaml FAILED to parse:", e)
mcp = cfg.get("mcp_servers") or {}
enabled = {k: v for k, v in mcp.items() if isinstance(v, dict) and v.get("enabled")}
print(f"  mcp_servers declared: {len(mcp)}   enabled: {len(enabled)}")
malformed = {k: v for k, v in mcp.items()
             if isinstance(v, dict) and v.get("enabled") and not (v.get("command") or v.get("url"))}
print(f"  enabled but MALFORMED (no command/url): {len(malformed)}  {list(malformed)[:8]}")
plugdir = f"{PROFILE}/plugins"
pcount = len(os.listdir(plugdir)) if os.path.isdir(plugdir) else 0
print(f"  plugins dir entries: {pcount}")
out["plugins"] = {"declared": len(mcp), "enabled": len(enabled), "malformed": len(malformed)}

# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 92)
print("4. CRONS — health and error state")
print("=" * 92)
try:
    j = json.load(open(CRON))
    jobs = j if isinstance(j, list) else j.get("jobs", [])
except Exception as e:
    jobs = []
    print("  jobs.json unreadable:", e)
err = [x for x in jobs if x.get("last_status") == "error"]
off = [x for x in jobs if not x.get("enabled")]
mon = [x for x in jobs if x.get("monitor")]
print(f"  total: {len(jobs)}   enabled: {len(jobs)-len(off)}   disabled: {len(off)}")
print(f"  last_status=error: {len(err)}")
print(f"  monitor-gated (change-only): {len(mon)}")
for x in err[:12]:
    print(f"    ERROR {x.get('name','?')[:44]:<44} {(x.get('schedule') or {}).get('expr','')}")
out["crons"] = {"total": len(jobs), "error": len(err), "monitored": len(mon)}

# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 92)
print("5. MONITORING COVERAGE — the question that actually matters")
print("=" * 92)
jobblob = " ".join(
    ((x.get("name") or "") + " " + (x.get("prompt") or "") + " " + (x.get("prompt_preview") or ""))
    .lower() for x in jobs)

SYSTEMS = {
    "gateway process":        ["gateway"],
    "tailscale / tailnet":    ["tailscale", "tailnet"],
    "qdrant vectors":         ["qdrant"],
    "redis":                  ["redis"],
    "docker fleet":           ["docker", "fleet"],
    "disk / space":           ["disk", "space", "disk-usage"],
    "swap / memory":          ["swap", "memory", "ram"],
    "cron roster health":     ["cron"],
    "backups (B2/restic)":    ["backup", "restic", "b2"],
    "MCP lanes":              ["mcp lane", "mcp_fleet", "mcp"],
    "clinical stack":         ["openemr", "mirth", "fhir", "medplum"],
    "radiology / PACS":       ["pacs", "ris", "dicom"],
    "CaddyOS / proxy":        ["proxy", "nginx", "tls", "ssl", "cert"],
    "Notion sync":            ["notion"],
    "n8n workflows":          ["n8n"],
    "cert expiry":            ["expiry", "cert"],
    "arxiv/agents external":  ["arxiv", "openfda", "bioportal"],
    "deploy/CI":              ["deploy", "build", "upgrade"],
    "email lane":             ["email", "imap", "smtp"],
    "external endpoints":     ["endpoint", "url", "uptime"],
}

print(f"{'SYSTEM':<26}{'MONITORED':<11}{'matched job(s)'}")
print("-" * 92)
uncovered = []
for sysname, kws in SYSTEMS.items():
    hits = [x.get("name") for x in jobs if any(k in jobblob and k in
            ((x.get("name") or "") + " " + (x.get("prompt") or "") + " " +
             (x.get("prompt_preview") or "")).lower() for k in kws)]
    covered = bool(hits)
    if not covered:
        uncovered.append(sysname)
    print(f"{sysname:<26}{('YES' if covered else '** NO **'):<11}"
          f"{(', '.join(hits[:3]) if hits else '-')}")
print("-" * 92)
print(f"\n  UNMONITORED SYSTEMS: {len(uncovered)}")
for u in uncovered:
    print(f"    {u}")
out["uncovered"] = uncovered

# gateway lanes — cross-reference the new watchdog
print("\n  gateway_state.json lanes (from the new lane watchdog):")
r = subprocess.run(["/opt/hermes/.venv/bin/python3",
                    "/opt/data/scripts/lane-state-watchdog.py", "--json"],
                   capture_output=True, text=True, timeout=120)
try:
    d = json.loads(r.stdout)
    for v in d.get("degraded", []):
        print(f"    DEGRADED {v['lane']:<20} {v['state']:<14} {v.get('error') or ''}")
except Exception:
    print("    (watchdog produced no JSON)")

json.dump(out, open("/opt/data/estate_audit.json", "w"), indent=1)
print("\n  -> /opt/data/estate_audit.json")
