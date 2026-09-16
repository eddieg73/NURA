"""
Organize the workspace.

1. Move the small loose standalone pages under the master workspace (pages move; databases cannot).
2. Build a complete WORKSPACE MAP section so one page indexes everything.
3. Remove Notion's default onboarding page.
"""
import sys, requests, time, json
sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"
MASTER = "3d8a9b14-e498-8125-a630-f2fcc2bd2354"

# --- small loose pages that are safe to file under the master workspace ---
# (databases CANNOT be moved - verified - so they stay at root and are listed instead)
MOVE = [
    ("f17a9b14-e498-824b-9e70-015d8108c6d3", "Meeting recap"),
    ("3aba9b14-e498-81d4-a3f1-dcdc97ad16f3", "12-Week Plan"),
    ("25529e89-8382-4abf-9567-6ca38b9e60cd", "Project — Raspberry Pi + ESP32 Daily Intel Dashboard"),
    ("3cda9b14-e498-81e4-b9e9-fd6521d0b1a4", "🕵️ OSINT & Intelligence Command"),
]
KEEP_AT_ROOT = [
    "613e14da-104a-470e-af85-799d66eb8ebc",  # Executive Command Center (ops hub, 284 items)
    "3aba9b14-e498-812b-8436-d56f4f806b2e",  # NURA Health Communications Flutter App (106 items)
    "3d6a9b14-e498-81e2-bab7-fc22b42127e9",  # Archive backup
    "384a9b14-e498-8032-9f95-e9dc974a5b57",  # To Do List
    "3d3a9b14-e498-8198-960a-c448cfb96dbd",  # Provider Labs (clinical master)
    "3d2a9b14-e498-812e-bb81-df63db1b22b1",  # Private Clinical Appendix (sensitive)
]

print("=" * 90)
print("STEP 1 — file the loose standalone pages under the master workspace")
print("=" * 90)
moved = []
for pid, label in MOVE:
    r = requests.patch(f"{BASE}/pages/{pid}", headers=H, timeout=30,
                       json={"parent": {"type": "page_id", "page_id": MASTER}})
    ok = r.status_code == 200
    print(f"  {label[:58]:<60} move={r.status_code}")
    if ok:
        moved.append((pid, label))
    else:
        print(f"      {r.text[:160]}")
    time.sleep(0.4)

print("\n" + "=" * 90)
print("STEP 2 — remove Notion's default onboarding page")
print("=" * 90)
w = requests.patch(f"{BASE}/pages/384a9b14-e498-801a-8cac-d9cf84409453",
                   headers=H, timeout=30, json={"in_trash": True})
print(f"  'Welcome to Notion!' -> trash={w.status_code}")

print("\n" + "=" * 90)
print("STEP 3 — build the WORKSPACE MAP section")
print("=" * 90)


def h2(t):
    return {"object": "block", "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": t}}]}}


def h3(t):
    return {"object": "block", "type": "heading_3",
            "heading_3": {"rich_text": [{"type": "text", "text": {"content": t}}]}}


def b(runs):
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": runs}}


def tx(t, bold=False, code=False):
    return {"type": "text", "text": {"content": t}, "annotations": {"bold": bold, "code": code}}


def link(pid, label, note=""):
    runs = [{"type": "mention", "mention": {"type": "page", "page": {"id": pid}}},
            tx(f"  —  {label}" + (f"   {note}" if note else ""))]
    return b(runs)


MAP = [
    h2("🗺️ WORKSPACE MAP — everything, in one place"),
    {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [tx(
        "The workspace root was 15 loose items. This is the index for all of it. "
        "Sections below list every top-level area, every database, and every outstanding cleanup.")]}},

    h3("OPERATIONS — the day-to-day hub"),
    link("613e14da-104a-470e-af85-799d66eb8ebc", "NURATECH AI — Executive Command Center", "[284 items · live]"),
    link("384a9b14-e498-8032-9f95-e9dc974a5b57", "To Do List", "[task capture]"),
    link("3cda9b14-e498-8178-8581-c358f57305a1", "Hermes ↔ ChatGPT — Agent Handoffs", "[27 rows]"),
    link("298d6119-62cf-4233-8717-9a3c1c687080", "MIH Evidence & Policy Registry", "[15 rows]"),

    h3("CLINICAL & PRODUCT"),
    link("3d3a9b14-e498-8198-960a-c448cfb96dbd", "NURA Provider Labs — Master Clinical Intelligence, Radiology & Imaging"),
    link("3aba9b14-e498-812b-8436-d56f4f806b2e", "NURA Health Communications Flutter App", "[106 items]"),
    link("22260907-f18c-4768-95de-052942bdb055", "Flutter Delivery Board — Active", "[10 rows]"),
    link("3d2a9b14-e498-812e-bb81-df63db1b22b1", "Private Clinical Appendix — Cognitive Profile", "[sensitive — restrict]"),

    h3("FILED HERE (moved in during cleanup)"),
]
for pid, label in moved:
    MAP.append(link(pid, label))

MAP += [
    h3("DATABASES AT ROOT — cannot be moved, indexed here instead"),
    {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [tx(
        "Notion's API does not permit moving a database to a new parent "
        "('Parent must be a database_id'). These three stay at root and are linked here.",
        )]}},
    link("d3da9b14-e498-82df-b0d8-014512d331ec", "People", "[6 rows]"),
    link("3cca9b14-e498-800d-83db-f6bd7a245636", "Claude Tasks", "[2 rows]"),
    link("3cda9b14-e498-811d-af0c-ecf7bfed5937", "My links", "[0 rows]"),

    h3("ARCHIVE — historical, do not write to"),
    link("3d6a9b14-e498-81e2-bab7-fc22b42127e9", "Archive — NURATECH Executive Command Center — Backup 2026-09-09", "[74 items]"),

    h3("⚠️ OUTSTANDING CLEANUP — needs your decision"),
    b([tx("Finnish template artifact — ", bold=True),
       tx("145 pages titled 'Aamuyhteenveto – <date>' (Finnish: 'Morning summary'), all last edited 2026-08-30 "
          "in one batch. Parent is a page the integration cannot see. This looks like an imported template, "
          "not your work. Recommend deletion after you confirm.")]),
    b([tx("DUPLICATE life-category trees — ", bold=True),
       tx("Hobbies, Projects, Travel, Admin, Fitness, Learning, Family, Business, Finance, Health all exist TWICE "
          "(20 pages). One set was edited 2026-09-09, the other 2026-08-31 and carries non-Notion ID formats — "
          "a second imported template. Pick the keeper and the other can go.")]),
    b([tx("Skill Registry ×3 — ", bold=True),
       tx("appear in search, all return 404. The integration has no access. Open or delete manually.")]),
    b([tx("4 databases labelled '⛔ SUPERSEDED — (nested content)' — ", bold=True),
       tx("removal is a human-reviewed top-down job; see the consolidation record below.")]),
]

r = requests.patch(f"{BASE}/blocks/{MASTER}/children", headers=H, timeout=40, json={"children": MAP})
print(f"  map appended: {r.status_code}")
g = requests.get(f"{BASE}/blocks/{MASTER}/children?page_size=100", headers=H, timeout=40)
d = g.json()
tot = len(d.get("results", []))
print(f"  master page blocks: {tot} (has_more={d.get('has_more')})")

json.dump({"moved": moved, "master": MASTER}, open("/opt/data/notion_org_done.json", "w"), indent=1)
print(f"\nMASTER -> https://www.notion.so/{MASTER.replace('-','')}")
