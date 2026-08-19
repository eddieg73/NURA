#!/usr/bin/env python3
"""NURA Mission Control lite — static status page from live state. Stdlib only."""
import json, os, re, subprocess, datetime, html

OUT = "/opt/data/profiles/nura/mission-control/index.html"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15).stdout.strip()
    except Exception:
        return "unavailable"

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M UTC")
gw = sh("curl -s -m 5 http://127.0.0.1:8642/health | head -c 120")
lanes = re.findall(r"^  ([\w-]+):\n((?:    .*\n?)*)", sh("grep -n '^  [\\w-]*:' /opt/data/profiles/nura/config.yaml | head -1") or "")
cfg = open("/opt/data/profiles/nura/config.yaml").read()
m = re.search(r"mcp_servers:\n(.*?)(?=\n\w[\w_]*:)", cfg, re.S)
enabled = []
if m:
    for e in re.finditer(r"^  ([\w-]+):\n((?:    .*\n?)*)", m.group(1), re.M):
        if "enabled: false" not in e.group(2):
            enabled.append(e.group(1))
disk = sh("df -h /opt/data | tail -1")
mem = sh("free -h | awk 'NR==2{print $3\"/\"$2\" avail:\"$7}'")
swap = sh("free -h | awk 'NR==3{print $3\"/\"$2}'")
git = sh("git -C /opt/data/home/nura-clinical-platform log --oneline -1 2>/dev/null")
notes = sh("ls -t /opt/data/profiles/nura/../../home/nura-clinical-platform/data/daily-notes/*.md 2>/dev/null | head -3") or sh("ls -t /opt/data/home/nura-clinical-platform/data/daily-notes/*.md 2>/dev/null | head -3")
crons = sh("ls /opt/data/profiles/nura/cron 2>/dev/null | wc -l")

rows = "".join(f"<tr><td>{html.escape(l)}</td><td style='color:#0a8'>&#9679;</td></tr>" for l in sorted(enabled))
body = f"""<!doctype html><html><head><meta charset="utf-8"><title>NURA Mission Control</title>
<style>body{{font-family:system-ui;background:#0b0f14;color:#d7e0ea;padding:2rem;max-width:900px;margin:auto}}
h1{{color:#4fc3f7}}table{{width:100%;border-collapse:collapse}}td{{padding:.4rem;border-bottom:1px solid #223}}
.g{{color:#4caf50}}.r{{color:#ef5350}}.card{{background:#111820;padding:1rem;border-radius:8px;margin:.6rem 0}}</style></head><body>
<h1>&#x1F6E1; NURA Mission Control</h1><p>Generated {now}</p>
<div class="card"><b>Gateway:</b> <span class="g">{html.escape(gw)}</span></div>
<div class="card"><b>Resources:</b> disk {html.escape(disk)} · RAM {html.escape(mem)} · swap {html.escape(swap)}</div>
<div class="card"><b>Repo:</b> {html.escape(git)} · <b>cron jobs:</b> {html.escape(crons)}</div>
<div class="card"><b>MCP lanes ({len(enabled)}):</b><table>{rows}</table></div>
<div class="card"><b>Latest notes:</b><pre>{html.escape(notes)}</pre></div>
</body></html>"""
open(OUT, "w").write(body)
print("")  # silent for cron no_agent mode
