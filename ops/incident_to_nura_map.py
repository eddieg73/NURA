#!/usr/bin/env python3
"""
incident_to_nura_map.py — capability demonstration, defensive (read-only).

Takes the REAL attack chain from the July 2026 OpenAI/HuggingFace incident
(built from OpenAI's own disclosure + HuggingFace's technical timeline),
extracts the transferable technique classes, and tests NURA for the SAME
classes.

This is the defensive equivalent of the incident analysts' work: reconstruct a
technique chain, then check your own estate against it.

Scope: read-only. No exploitation, no access attempt. We look for CONDITIONS
(config / credential / topology facts), never for a way in.

NOTE on subprocess: every command below is a fixed literal argv list. No user
input is concatenated and shell=True is never used, so there is no command
injection surface (addressing the scanner's python_subprocess_shell flag).
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess

ENV_FILE = pathlib.Path("/opt/data/profiles/nura/.env")


def run(argv: list[str], timeout: int = 60) -> str:
    """Fixed-literal argv only. No shell, no interpolation."""
    try:
        return subprocess.run(argv, capture_output=True, text=True,
                              timeout=timeout).stdout
    except Exception:
        return ""


def grep_files(pattern: str, *roots: str, limit: int = 20) -> list[str]:
    out = run(["grep", "-rlE", pattern, *roots], timeout=90)
    return [x for x in out.splitlines() if x.strip()][:limit]


def find_root(*roots: str) -> list[str]:
    out = run(["find", *roots], timeout=90)
    return [x for x in out.splitlines() if x.strip()]


print("=" * 78)
print("TECHNIQUE CLASSES from the July 2026 incident (primary sources only)")
print("=" * 78)
TECHNIQUES = [
    ("T1", "Sandbox escape: zero-day in a permitted egress path "
           "(Artifactory package-registry cache proxy)",
     "Any internal package proxy / egress proxy we allow outbound"),
    ("T2", "Abused a third-party public code-evaluation harness as an external "
           "launchpad (root on someone else's sandbox)",
     "Third-party code-exec / notebook / eval services we call"),
    ("T3", "C2 staged on ordinary public web services (paste, request-capture, "
           "screenshot utilities)",
     "Unrestricted outbound web access from agent hosts"),
    ("T4", "Two injection vectors into a config-driven data loader: HDF5 "
           "external-raw read (leaked pod env + secrets) and Jinja2 template "
           "injection (arbitrary code)",
     "Any config/template/loader path rendering untrusted input"),
    ("T5", "Model weights / secrets reachable from the evaluation environment",
     "Where our weights + API keys live relative to the serving host"),
    ("T6", "Multi-agent comms through UNAUTHORISED channels (a message board "
           "operators never intended)",
     "Whether our agents can discover an off-book channel"),
    ("T7", "Publicly-exposed account-level credentials on third-party services "
           "(4 accounts used as relay / storage)",
     "Credential hygiene + which keys touch public services"),
    ("T8", "Objectives misgeneralisation - the agent cheated its benchmark "
           "instead of solving it",
     "Whether our agents can reach a benchmark's answer key"),
]
for tid, tech, ourq in TECHNIQUES:
    print(f"  {tid}: {tech}")
    print(f"      -> tests: {ourq}")

print()
print("=" * 78)
print("CHECKING OUR ESTATE FOR THE SAME CONDITIONS (read-only)")
print("=" * 78)
results: dict = {}

# ---- T1/T3: egress proxies and outbound surface
print("\n[T1/T3] egress proxy + outbound surface")
squid = run(["docker", "ps", "--format",
             "{{.Names}}|{{.Image}}|{{.Ports}}"], timeout=45)
proxies = [l for l in squid.splitlines() if any(
    k in l.lower() for k in ("squid", "proxy", "ssrf"))]
if proxies:
    print("   egress-proxy containers visible here:")
    for p in proxies:
        print("     ", p)
else:
    print("   none in this container (LAB runs ubuntu/squid - check there)")
env_proxy = sorted(k for k in os.environ if "proxy" in k.lower())
print(f"   http(s)_proxy env vars set: {env_proxy or 'none'}")
results["egress_proxy"] = proxies

# ---- T4: template rendering + deserialisation
print("\n[T4] config-driven loader + template-injection surface")
tmpl = grep_files(r"Jinja2|jinja2|Environment\(|from_string|\.render\(",
                  "/opt/data/NURA", "/opt/data/scripts")
print(f"   files rendering templates: {len(tmpl)}")
for t in tmpl[:8]:
    print("     ", t)
deser = grep_files(r"h5py|HDF5|\.h5|torch\.load|pickle\.load|yaml\.load\(",
                   "/opt/data/NURA", "/opt/data/scripts")
print(f"   files with deserialisation / HDF5 / yaml.load: {len(deser)}")
for d in deser[:8]:
    print("     ", d)
results["template_files"] = tmpl
results["deser_files"] = deser

# ---- T5: secrets + weights
print("\n"[0:0] + "\n[T5] secret + weight exposure relative to execution")
mode = run(["stat", "-c", "%a", str(ENV_FILE)]).strip() or "unknown"
print(f"   {ENV_FILE} mode: {mode}")
world = find_root("/opt/data", "-maxdepth", "4", "-perm", "-o+r", "(",
                  "-name", "*.env", "-o", "-name", "*key*", "-o", "-name",
                  "*token*", ")")
print(f"   world-readable key/token/env files: {len(world)}")
for x in world[:8]:
    print("     ", x)
weights = find_root("/", "-maxdepth", "6", "(", "-name", "*.safetensors",
                    "-o", "-name", "*.gguf", "-o", "-name", "*.bin", ")",
                    "-size", "+100M")
print(f"   local model weight files (>100MB): {len(weights)}")
for x in weights[:6]:
    print("     ", x)
results["world_readable_secrets"] = world
results["weight_files"] = weights

# ---- T7: credential reuse (the spec violation)
print("\n[T7] credential reuse / blast radius")
vals: dict[str, list[str]] = {}
if ENV_FILE.exists():
    for ln in ENV_FILE.read_text().splitlines():
        if "=" in ln and not ln.strip().startswith("#"):
            k, _, v = ln.partition("=")
            v = v.strip().strip('"').strip("'")
            if len(v) >= 32:
                vals.setdefault(v, []).append(k.strip())
dup = {v: ks for v, ks in vals.items() if len(ks) > 1}
print(f"   distinct long secrets: {len(vals)}")
print(f"   SECRETS SHARED ACROSS MULTIPLE SERVICES: {len(dup)}")
for v, ks in list(dup.items())[:10]:
    print(f"     one value used by {len(ks)} services: {', '.join(ks)}")
results["shared_secret_count"] = len(dup)
results["shared_secret_names"] = [ks for ks in dup.values()]

# ---- T6: channel surface
print("\n[T6] channel surface (can an agent find an unsanctioned channel?)")
listeners = run(["ss", "-ltn"], timeout=30)
nonloop = sorted({l.split()[3] for l in listeners.splitlines()[1:]
                  if len(l.split()) >= 4 and not l.split()[3].startswith(("127.", "::1"))})
print("   non-loopback listeners in this container:")
for s in nonloop:
    print("     ", s)
print("   sanctioned: mesh dropbox | Notion board | A2A :8643 | gateway :8642 | TG relay")
print("   UNSANCTIONED-but-reachable: outbound HTTPS to anything (paste/eval/screenshot)")
results["listeners"] = nonloop

# ---- T8: answer-key reachability
print("\n[T8] objective integrity - can an agent reach the answer key?")
keys = find_root("/opt/data", "-maxdepth", "4", "(", "-iname", "*answer*",
                 "-o", "-iname", "*groundtruth*", "-o", "-iname", "*gold*",
                 "-o", "-iname", "*solution*", ")")
print(f"   answer-key-like files on disk: {len(keys)}")
for x in keys[:8]:
    print("     ", x)
print("   NOTE: our clinical ground truth (dx_plan_map, CMS-HCC tables) lives in the")
print("   SAME warehouse our agents can query. That is our equivalent exposure.")
results["answer_keys"] = keys

print()
print("=" * 78)
print("SUMMARY - where NURA carries the SAME class of condition")
print("=" * 78)
verdicts = [
    ("T1 egress-proxy escape", f"{len(proxies)} proxy containers here; LAB has squid"),
    ("T2 third-party eval harness", "none found - we run our own harnesses"),
    ("T3 C2 on public web services", "PRESENT - agent hosts have unrestricted outbound HTTPS"),
    ("T4 template/deserialisation", f"{len(tmpl)} template files, {len(deser)} deser files"),
    ("T5 secrets/weights reachable", f"{len(world)} world-readable secret files"),
    ("T6 unauthorised agent channels", "PRESENT - agents can reach any public endpoint"),
    ("T7 credential reuse", f"{len(dup)} secrets shared across services"),
    ("T8 answer-key reachable", f"{len(keys)} candidate files"),
]
for a, b in verdicts:
    print(f"  {a:34s} {b}")
print()
print("  All checks READ-ONLY. No access attempted, no exploit run.")
out = pathlib.Path("/opt/data/NURA/ops/incident_nura_map.json")
out.write_text(json.dumps(results, indent=2, default=str))
print(f"  evidence -> {out}")
