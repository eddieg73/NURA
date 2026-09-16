"""
Build ONE master workspace page at the Notion workspace root.

Structure: a single entry point listing every project and every CANONICAL database,
with superseded copies clearly marked. Nothing is deleted by this script.
"""
import sys, requests, json, time
sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"

# ---- canonical set (verified: superset by row-level diff) ----
CANON = {
    "projects":   ("9547910e-8975-44b8-b511-2108abfa0d11", "Executive Projects", "18 projects"),
    "tasks":      ("d3ff0c00-c629-43dc-b82c-06a28866fcb1", "Master Tasks & Commitments", "78 rows"),
    "medisun":    ("8aca9b14-e498-8200-8d00-0149672c0a5f", "Medisun Completed Work Register", "27 rows"),
    "orgs":       ("c20a9b14-e498-8333-b554-01413da172df", "Organizations & Current Roles", "9 rows"),
    "prehosp":    ("cdca9b14-e498-821f-9a92-814495237c4f", "Prehospital & Aeromedical Evidence Board", "6 rows"),
    "erp":        ("e80e33c7-d5a3-4f4b-a3e5-0c19133a605d", "Nura ERP Build Backlog", "45 rows"),
    "mih":        ("298d6119-62cf-4233-8717-9a3c1c687080", "MIH Evidence & Policy Registry", "15 rows"),
    "handoffs":   ("3cda9b14-e498-8178-8581-c358f57305a1", "Hermes ↔ ChatGPT — Agent Handoffs", "27 rows"),
    "people":     ("d3da9b14-e498-82df-b0d8-014512d331ec", "People", "6 rows"),
    "todo":       ("384a9b14-e498-8041-a6cf-fc6849b4fc40", "To Do List DB", "13 rows"),
    "flutter":    ("22260907-f18c-4768-95de-052942bdb055", "Flutter Delivery Board — Active", "10 rows"),
}

SUPERSEDED = [
    ("e90a9b14-e498-83f9-ae0b-810a94157b95", "Executive Projects (copy)", "17 rows — 16 shared + 1 renamed duplicate"),
    ("752a9b14-e498-8309-b369-817c7145b742", "Master Tasks & Commitments (copy)", "57 rows — strict subset of the 78"),
    ("44a69385-45ef-47ab-a787-aa6274472081", "Medisun Completed Work Register (copy)", "27 rows — identical"),
    ("116b71cd-76a4-4eef-a1d0-81068e3c6cf4", "Organizations & Current Roles (copy)", "9 rows — identical"),
    ("c28d624e-b827-4065-b1fd-200cdf7dd561", "Prehospital & Aeromedical Evidence Board (copy)", "6 rows — identical"),
]


def blocks(chunk):
    r = requests.patch(f"{BASE}/blocks/{PAGE}/children", headers=H,
                       json={"children": chunk}, timeout=40)
    if r.status_code != 200:
        print(f"    append {r.status_code}: {r.text[:250]}")
        return False
    time.sleep(0.35)
    return True


def h2(t):
    return {"object": "block", "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": t}}]}}


def para(runs):
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": runs}}


def text(t, bold=False, code=False):
    return {"type": "text", "text": {"content": t},
            "annotations": {"bold": bold, "code": code}}


def bullet(runs):
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": runs}}


def db_link(db_id, label, meta=""):
    runs = [{"type": "mention", "mention": {"type": "database", "database": {"id": db_id}}},
            text(f"  — {meta}", bold=False)]
    return bullet(runs)


def page_link(page_id, label, meta=""):
    runs = [{"type": "mention", "mention": {"type": "page", "page": {"id": page_id}}},
            text(f"  — {meta}")]
    return bullet(runs)


# ---------- 1. create the master page ----------
print("creating master workspace page at workspace root...")
r = requests.post(f"{BASE}/pages", headers=H, timeout=40, json={
    "parent": {"type": "workspace", "workspace": True},
    "icon": {"type": "emoji", "emoji": "🏛️"},
    "properties": {"title": [{"text": {"content": "NURATECH — MASTER WORKSPACE"}}]},
})
if r.status_code != 200:
    print(f"  FAILED {r.status_code}: {r.text[:400]}")
    raise SystemExit(1)
PAGE = r.json()["id"]
print(f"  created: {PAGE}")

# ---------- 2. fetch the 18 projects ----------
pa = requests.post(f"{BASE}/databases/{CANON['projects'][0]}/query", headers=H,
                   json={"page_size": 100}, timeout=40).json().get("results", [])


def title_of(row):
    for v in (row.get("properties") or {}).values():
        if isinstance(v, dict) and v.get("type") == "title":
            return "".join(x.get("plain_text", "") for x in v.get("title", [])).strip()
    return ""


def status_of(row):
    for k in ("Status", "State", "Stage"):
        v = (row.get("properties") or {}).get(k)
        if isinstance(v, dict):
            t = v.get("type")
            if t == "status" and v.get("status"):
                return v["status"].get("name", "")
            if t == "select" and v.get("select"):
                return v["select"].get("name", "")
    return ""


projects = sorted([(title_of(p), p["id"], status_of(p)) for p in pa], key=lambda x: x[0].lower())
print(f"  projects found: {len(projects)}")

# ---------- 3. write the page ----------
print("writing page content...")
batch = []

batch.append({"object": "block", "type": "callout", "callout": {
    "icon": {"type": "emoji", "emoji": "🎯"},
    "rich_text": [text("This is the single entry point. One workspace, every project, every canonical database. "
                       "Anything marked SUPERSEDED is a copy and is no longer written to.", bold=True)]}})

batch.append(h2("📁 PROJECTS"))
batch.append(para([text(f"{len(projects)} active projects. Each links to its detail page; tasks in Master Tasks & Commitments relate back to these.")]))
for i, (t, pid, st) in enumerate(projects, 1):
    batch.append(page_link(pid, t, st or "—"))

batch.append(h2("🗂️ CANONICAL DATABASES — use these"))
for key, (did, label, meta) in CANON.items():
    batch.append(db_link(did, label, meta))

batch.append(h2("⛔ SUPERSEDED COPIES — do not use or write to"))
batch.append(para([text("These are duplicates found on 2026-09-11. Verified by row-level diff: every row is already "
                        "present in the canonical database above. Renamed and trashed; recoverable from Notion trash for 30 days.")]))
for did, label, meta in SUPERSEDED:
    batch.append(bullet([text(f"{label} — {meta}", bold=False), text(f"  [{did[:8]}]", code=True)]))

batch.append(h2("⚠️ KNOWN GAPS"))
for line in [
    "Skill Registry appears 3× in search but all three return 404 — the integration cannot read them. Needs a human to open or delete them.",
    "Supabase is NOT provisioned. The tech master plan specifies Supabase Postgres + pgvector, but there are no credentials, no CLI and no instance. It is a plan, not a system.",
    "Aamuyhteenvedon keskus (Finnish, 100+ rows) is an unexplained database — flagged for review, not touched.",
]:
    batch.append(bullet([text(line)]))

# chunked append
CH = 40
for i in range(0, len(batch), CH):
    ok = blocks(batch[i:i + CH])
    print(f"  appended {i+len(batch[i:i+CH])}/{len(batch)} blocks  ok={ok}")

with open("/opt/data/notion_master_page.json", "w") as f:
    json.dump({"page_id": PAGE, "projects": projects,
               "canonical": CANON, "superseded": SUPERSEDED}, f, indent=1)

print(f"\nMASTER PAGE = {PAGE}")
print(f"URL = https://www.notion.so/{PAGE.replace('-', '')}")
