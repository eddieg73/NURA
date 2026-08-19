#!/usr/bin/env python3
"""MCP ADMINISTRATOR — inventory, health, spin-up, teardown, governance."""
import subprocess, json, sys, os, re

HERMES = "/opt/hermes/bin/hermes"
PATH = f"/opt/data/profiles/nura/bin:/opt/data/profiles/nura/.local/bin:/opt/hermes/bin:/opt/hermes/.venv/bin:{os.environ.get('PATH','')}"

def sh(cmd, timeout=18):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, env={**os.environ, "PATH": PATH})
        return r.stdout.strip()
    except Exception as e:
        return f"ERR: {e}"

def inventory():
    out = sh(f"{HERMES} mcp list")
    lanes = []
    for line in out.splitlines():
        m = re.match(r"\s*([\w-]+)\s+(\S+.*?)\s+(\d+|all|[\d]+ selected)?\s*(✓|✗)\s*(enabled|disabled)", line)
        if m:
            lanes.append({"name": m.group(1), "wiring": m.group(2), "status": m.group(4) + " " + m.group(5)})
    return lanes

def test(name):
    out = sh(f"{HERMES} mcp test {name}")
    return out[-80:] if out else "no output"

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "health"
    if action == "inventory":
        print(json.dumps(inventory(), indent=1))
    elif action == "health":
        lanes = inventory()
        report = []
        for l in lanes:
            if l["status"].startswith("✓"):
                r = test(l["name"])
                ok = "Tools discovered" in r or "✓" in r.splitlines()[-1] if r else False
                report.append({"name": l["name"], "status": "OK" if ok else "CHECK", "detail": r[-40:]})
            else:
                report.append({"name": l["name"], "status": "disabled"})
        print(json.dumps(report, indent=1))
    elif action == "spinup" and len(sys.argv) > 2:
        name, cmd, args = sys.argv[2], sys.argv[3], " ".join(sys.argv[4:])
        print(sh(f'echo "Y" | {HERMES} mcp add {name} --command {cmd} --args {args}'))
    elif action == "teardown" and len(sys.argv) > 2:
        print(sh(f"{HERMES} mcp rm {sys.argv[2]}"))
    else:
        print("usage: mcp-admin.py [inventory|health|spinup <name> <cmd> <args...>|teardown <name>]")

if __name__ == "__main__":
    main()
