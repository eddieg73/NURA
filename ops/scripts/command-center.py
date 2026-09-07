#!/usr/bin/env python3
"""NURA Command Center (NOC) — ONE glance for every system, Network-Admin style.
Reads live fleet state and renders: (1) a served status page, (2) a daily Notion snapshot.
Healthy/stable = SILENT. Only real problems surface as signal. Stdlib + requests.
Run: python3 command-center.py [--notion] [--emit-json]
"""
import json, os, re, subprocess, datetime, html, sys, socket
from zoneinfo import ZoneInfo

PROFILE = "/opt/data/profiles/nura"
OUT = f"{PROFILE}/mission-control/index.html"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
OUT_JSON = "/opt/data/nura-command-center-state.json"

def sh(cmd, t=12):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=t).stdout.strip()
    except Exception:
        return "unavailable"

def ok(cond): return "🟢" if cond else "🔴"

# ---- live state collection -------------------------------------------------
def cron_fleet():
    """Return (total, ok, error, paused) from the live cron jobs DB (authoritative).
    error = enabled jobs whose LAST RUN was an error (paused jobs are QUARANTINED, not erroring)."""
    raw = sh("export PATH=/opt/data/profiles/nura/bin:/opt/data/profiles/nura/.local/bin:/opt/hermes/bin:/opt/hermes/.venv/bin:$PATH; timeout 60 hermes cron list --json 2>/dev/null")
    try:
        jobs = json.loads(raw) if raw.startswith("[") or raw.startswith("{") else []
        if isinstance(jobs, dict): jobs = jobs.get("jobs", jobs.get("data", []))
    except Exception:
        jobs = []
    if not jobs:
        # fallback: read the jobs DB directly
        for p in [f"{PROFILE}/cron/jobs.json", "/opt/data/cron/jobs.json"]:
            try:
                d = json.load(open(p))
                jobs = d if isinstance(d, list) else d.get("jobs", d.get("items", []))
                if jobs: break
            except Exception:
                pass
    total = len(jobs)
    paused = sum(1 for j in jobs if j.get("paused_at"))
    # erroring = enabled (not paused) jobs whose last run errored
    err = sum(1 for j in jobs if j.get("last_status") == "error" and not j.get("paused_at"))
    return (total, total - err - paused, err, paused)

def fleet_state():
    """Disk / RAM / swap / load on this host."""
    disk = sh("df -h /opt/data | tail -1").split()
    mem = sh("free -h | awk 'NR==2{print $3\"/\"$2}'")
    swap = sh("free -h | awk 'NR==3{print $3\"/\"$2}'")
    load = sh("cut -d' ' -f1-3 /proc/loadavg")
    return disk, mem, swap, load

def services():
    """Docker containers health (any host we can reach)."""
    out = sh("docker ps --format '{{.Names}} {{.Status}}' 2>/dev/null | head -40")
    return [l for l in out.splitlines() if l.strip()]

def gateways():
    """What's actually serving on key ports."""
    probes = [("gateway", 8642), ("mission-control", 4100), ("carepilot-app", 8000)]
    res = []
    for name, port in probes:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(2)
        up = s.connect_ex(("127.0.0.1", port)) == 0; s.close()
        res.append((name, up, port))
    return res

def alerts():
    """Distill any actual problems from the state (the ONLY thing that should ever be loud)."""
    a = []
    t, e, err, paused = 0, 0, 0, 0
    try:
        t, e, err, paused = cron_fleet()
    except Exception:
        pass
    if err: a.append(f"{err}/{t} cron jobs ERRORING (last_status=error)")
    disk = sh("df -h /opt/data | tail -1").split()
    if len(disk) >= 5:
        pct = int(disk[4].rstrip("%"))
        if pct >= 85: a.append(f"DISK at {pct}% (headroom rule breached)")
    for name, up, port in gateways():
        if not up and name in ("gateway",): a.append(f"GATEWAY DOWN on :{port}")
    return a

# Founder-gated items: paused-on-auth crons + Notion Master Tasks flagged for founder. NOT errors.
def needs_eddie():
    n = []
    # 1) paused-on-auth crons (quarantined, waiting on @csuite)
    raw = sh("export PATH=/opt/data/profiles/nura/bin:/opt/data/profiles/nura/.local/bin:/opt/hermes/bin:/opt/hermes/.venv/bin:$PATH; timeout 60 hermes cron list --json 2>/dev/null")
    try:
        jobs = json.loads(raw) if raw.startswith("[") or raw.startswith("{") else []
        if isinstance(jobs, dict): jobs = jobs.get("jobs", jobs.get("data", []))
    except Exception:
        jobs = []
    if not jobs:
        for p in [f"{PROFILE}/cron/jobs.json", "/opt/data/cron/jobs.json"]:
            try:
                d = json.load(open(p)); jobs = d if isinstance(d, list) else d.get("jobs", d.get("items", []))
                if jobs: break
            except Exception: pass
    for j in jobs:
        if j.get("paused_at") and j.get("last_status") == "error":
            n.append(f"Re-auth paused job: '{j.get('name','job')}' (external auth — eMedical/Solis)")

    # 2) Notion Master Tasks — tasks needing founder (Founder Gate / Doing / Blocked / Waiting)
    try:
        tok = notion_token()
        if tok:
            import requests
            H = {"Authorization": f"Bearer {tok}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
            db = "d3ff0c00-c629-43dc-b82c-06a28866fcb1"  # Master Tasks & Commitments
            r = requests.post(f"https://api.notion.com/v1/databases/{db}/query", headers=H,
                              json={"page_size":100}, timeout=20)
            for o in r.json().get("results", []):
                pr = o.get("properties", {})
                st = ((pr.get("Status") or {}).get("select") or {}).get("name","")
                fg = ((pr.get("Founder Gate") or {}).get("select") or {}).get("name","")
                task = "".join(x.get("plain_text","") for x in (pr.get("Task") or {}).get("title",[])) or \
                       "".join(x.get("plain_text","") for x in (pr.get("Name") or {}).get("title",[]))
                if fg or st in ("Blocked","Waiting"):
                    n.append(f"[Founder] {task[:70]} (status={st}, gate={fg or 'none'})")
    except Exception:
        pass
    return n

# ---- render -----------------------------------------------------------------
def render_html(state):
    now = datetime.datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %H:%M %Z")
    d = state["disk"]; disk_str = " ".join(d) if d else "unavailable"
    rows = "".join(f"<tr><td>{html.escape(n)}</td><td>{'🟢' if up else '🔴'}</td><td>:{p}</td></tr>"
                   for n, up, p in state["gateways"])
    svc = "".join(f"<tr><td>{html.escape(s)}</td></tr>" for s in state["services"]) or "<tr><td>docker unavailable</td></tr>"
    al = "".join(f"<li style='color:#ef5350'>{html.escape(x)}</li>" for x in state["alerts"]) or "<li style='color:#4caf50'>All clear — no actionable problems.</li>"
    ne = "".join(f"<li style='color:#f0b429'>{html.escape(x)}</li>" for x in state.get("needs_eddie", [])) or "<li style='color:#4a9'>No founder-gated items waiting.</li>"
    body = f"""<!doctype html><html><head><meta charset="utf-8"><title>NURA Command Center</title>
<style>body{{font-family:ui-monospace,monospace;background:#0b0f14;color:#d7e0ea;padding:2rem;max-width:1100px;margin:auto}}
h1{{color:#4fc3f7;font-size:1.4rem}}h2{{color:#8ab;font-size:1rem;margin-top:1.6rem}}
table{{width:100%;border-collapse:collapse}}td{{padding:.4rem;border-bottom:1px solid #1c2630;font-size:.85rem}}
.card{{background:#111820;padding:1rem;border-radius:8px;margin:.6rem 0}}
.g{{color:#4caf50}}.r{{color:#ef5350}}.y{{color:#f0b429}}</style></head><body>
<h1>🛡 NURA Command Center</h1><p>Generated {now} · gateway:{'🟢' if state['gw_ok'] else '🔴'}</p>
<div class="card"><b>Resources:</b> disk {html.escape(disk_str)} · RAM {html.escape(state['mem'])} · swap {html.escape(state['swap'])} · load {html.escape(state['load'])}</div>
<div class="card"><b>Cron fleet:</b> {state['cron_total']} jobs · {state['cron_ok']} ok · <span class="{'r' if state['cron_err'] else 'g'}">{state['cron_err']} error</span> · {state['cron_paused']} paused</div>
<h2>🔥 Actionable Alerts</h2><ul>{al}</ul>
<h2>⏳ NEEDS EDDIE</h2><ul>{ne}</ul>
<h2>🧪 Gateway / Surfaces</h2><table>{rows}</table>
<h2>📦 Docker Services (this host)</h2><table>{svc}</table>
<h2>🧠 MCP lanes ({state['mcp_count']})</h2><p>{html.escape(', '.join(state['mcp_lanes'][:40]))}</p>
</body></html>"""
    open(OUT, "w").write(body)
    return OUT

NURA_OPS_DASHBOARD = "3c2a9b14-e498-81fb-96db-d4a35ba1eec3"  # 🛰️ NURA Ops Dashboard (shared w/ ChatGPT)

def notion_token():
    """Resolve the Notion token the way the canonical scripts do (auth.json CLI token first)."""
    try:
        d = json.load(open(f"{PROFILE}/home/.config/notion/auth.json"))
        if d:
            return list(d.values())[0]
    except Exception:
        pass
    for p in [f"{PROFILE}/.env", f"{PROFILE}/home/.secrets/notion-nuratech-coder.env"]:
        if os.path.exists(p):
            for line in open(p, errors="ignore"):
                if line.startswith("NOTION_API_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None

def daily_notion(md, title="Daily Ops Snapshot"):
    """Append a titled snapshot block to the shared NURA Ops Dashboard. Silent on failure."""
    tok = notion_token()
    if not tok:
        return "no token"
    try:
        import requests, uuid
        H = {"Authorization": f"Bearer {tok}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
        now = datetime.datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %H:%M %Z")
        rich = [{"type": "text", "text": {"content": f"🛡 {title} · {now}\n{md}"}}]
        r = requests.patch(f"https://api.notion.com/v1/blocks/{NURA_OPS_DASHBOARD}/children",
                          headers=H, json={"children": [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": rich}}]}, timeout=15)
        return (r.status_code, r.text[:100])
    except Exception as e:
        return str(e)[:100]

def mcp_lanes():
    """Top-level MCP servers listed in config.yaml (under mcp_servers:)."""
    try:
        cfg = open(f"{PROFILE}/config.yaml").read()
    except Exception:
        return []
    m = re.search(r"mcp_servers:\n(.*?)(?=\n\w[\w_]*:)", cfg, re.S)
    if not m:
        return []
    # any line that's exactly two-space indent + word + colon at the top of mcp_servers
    return [l.strip() for l in re.findall(r"^  ([\w-]+):", m.group(1), re.M)]

def build():
    ctot, cok, cerr, cpa = cron_fleet()
    disk, mem, swap, load = fleet_state()
    gws = gateways()
    mlanes = mcp_lanes()
    st = {
        "disk": disk, "mem": mem, "swap": swap, "load": load,
        "cron_total": ctot, "cron_ok": cok, "cron_err": cerr, "cron_paused": cpa,
        "services": services(), "gateways": gws,
        "gw_ok": any(up for n, up, p in gws if n == "gateway"),
        "mcp_lanes": mlanes,
        "mcp_count": len(mlanes),
        "alerts": alerts(),
        "needs_eddie": needs_eddie(),
    }
    st["mcp_lanes"] = [l.strip() for l in st["mcp_lanes"] if l.strip()]
    open(OUT_JSON, "w").write(json.dumps(st, default=str))
    path = render_html(st)
    return st, path

if __name__ == "__main__":
    st, path = build()
    if "--emit-json" in sys.argv:
        print(json.dumps(st, default=str))
    else:
        print("")  # silent for no_agent cron; real signal only if alerts
        if "--notion" in sys.argv and st["alerts"]:
            md = "\n".join("🔴 " + a for a in st["alerts"])
            r = daily_notion(md)
            if r: print("notion:", r)
