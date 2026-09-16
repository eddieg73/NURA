#!/usr/bin/env python3
"""
MCP config repair — 2026-09-12 incident-commander audit.

Defect A: `args:` stored as a YAML *string* containing a JSON array
          -> the string (including the literal '[') is passed as argv[1]
          -> `npm error code EINVALIDTAGNAME Invalid tag name "["`
Defect B: `command:` holds command + path in one space-separated string
          -> FileNotFoundError: 'python3 /opt/data/scripts/dsh-mcp.py'

Fix rewrites ONLY the affected lines, byte-for-byte elsewhere (comments preserved).
"""
import json, os, re, shutil, sys, time, yaml

CFG = "/opt/data/profiles/nura/config.yaml"
stamp = time.strftime("%Y%m%d_%H%M%S")
BAK = f"{CFG}.bak-mcpargs-{stamp}"

lines = open(CFG, encoding="utf-8").read().splitlines(keepends=True)
orig = list(lines)

ARGS_RE = re.compile(r"^(?P<ind>\s+)args:\s*'(?P<val>.*)'\s*$")
CMD_RE = re.compile(r"^(?P<ind>\s+)command:\s*(?P<bin>python3|node|npx|uvx)\s+(?P<rest>\S.*?)\s*$")

def yaml_list(indent, items):
    out = [f"{indent}args:\n"]
    for it in items:
        safe = it.replace("'", "''")
        out.append(f"{indent}  - '{safe}'\n")
    return out

changes = []
for i, ln in enumerate(lines):
    m = ARGS_RE.match(ln)
    if m:
        ind, val = m.group("ind"), m.group("val")
        # YAML single-quoted: backslash is literal. Undo \" -> " then parse JSON.
        try:
            parsed = json.loads(val.replace('\\"', '"'))
        except Exception:
            try:
                parsed = json.loads(val)
            except Exception as e:
                print(f"  SKIP line {i+1}: cannot parse {val[:50]!r} ({e})")
                continue
        if not isinstance(parsed, list):
            print(f"  SKIP line {i+1}: not a list")
            continue
        if all(isinstance(x, str) for x in parsed):
            new = yaml_list(ind, parsed)
            changes.append((i + 1, ln.rstrip("\n"), "".join(new).rstrip("\n")))
            lines[i:i + 1] = new
            continue
    m2 = CMD_RE.match(ln)
    if m2:
        ind, binn, rest = m2.group("ind"), m2.group("bin"), m2.group("rest")
        # only split when the next non-blank sibling is NOT already an args: line
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        if nxt.startswith("args:"):
            continue
        new = [f"{ind}command: {binn}\n", f"{ind}args:\n", f"{ind}  - '{rest}'\n"]
        changes.append((i + 1, ln.rstrip("\n"), "".join(new).rstrip("\n")))
        lines[i:i + 1] = new

if not changes:
    print("No changes needed.")
    sys.exit(0)

new_text = "".join(lines)

# validate BEFORE touching the original
try:
    d = yaml.safe_load(new_text)
except Exception as e:
    print(f"ABORT — repaired text does not parse: {e}")
    sys.exit(2)

bad = []
for name, c in d.get("mcp_servers", {}).items():
    if isinstance(c, dict):
        a = c.get("args")
        if isinstance(a, str):
            bad.append(name)
        cmd = c.get("command")
        if isinstance(cmd, str) and " " in cmd:
            bad.append(f"{name}:command")
if bad:
    print(f"ABORT — still malformed after repair: {bad}")
    sys.exit(2)

shutil.copy2(CFG, BAK)
tmp = CFG + ".tmp-repair"
with open(tmp, "w", encoding="utf-8") as f:
    f.write(new_text)
os.replace(tmp, CFG)

print(f"backup      : {BAK}")
print(f"lines fixed : {len(changes)}")
for ln_no, old, new in changes:
    print(f"  L{ln_no}: {old.strip()[:72]}")
print(f"\nre-parse OK  : {len(d['mcp_servers'])} servers, 0 malformed args/command")
