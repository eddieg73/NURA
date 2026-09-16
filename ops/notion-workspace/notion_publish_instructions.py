"""Correct the stale Skill Registry claim on the master page, and publish the Notion AI instructions as a page."""
import sys, requests, time
sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"
MASTER = "3d8a9b14-e498-8125-a630-f2fcc2bd2354"


def all_blocks(pid):
    out, cur = [], None
    while True:
        b = {"page_size": 100}
        if cur:
            b["start_cursor"] = cur
        r = requests.get(f"{BASE}/blocks/{pid}/children", headers=H, params=b, timeout=40)
        if r.status_code != 200:
            return out
        d = r.json()
        out += d.get("results", [])
        if not d.get("has_more"):
            return out
        cur = d.get("next_cursor")


print("=" * 86)
print("STEP 1 — correct the Skill Registry claim (it is NOT a ghost)")
print("=" * 86)
fixed = 0
for blk in all_blocks(MASTER):
    t = blk.get("type")
    if t not in ("paragraph", "bulleted_list_item"):
        continue
    txt = "".join(x.get("plain_text", "") for x in blk[t].get("rich_text", []))
    if "Skill Registry" in txt and ("404" in txt or "cannot read" in txt or "ghost" in txt.lower()):
        new = ("Skill Registry — CORRECTED: it is NOT a ghost. The API cannot query it "
               "(returns 404) but it contains 30+ real rows, one per skill category (crm, devops, "
               "productivity, health, research, creative, …). Notion AI can see it. "
               "DO NOT DELETE — it is live content.")
        r = requests.patch(f"{BASE}/blocks/{blk['id']}", headers=H, timeout=30,
                           json={t: {"rich_text": [{"type": "text", "text": {"content": new}}]}})
        print(f"  corrected block {blk['id'][:8]}: {r.status_code}")
        fixed += 1
        time.sleep(0.3)
if not fixed:
    print("  (no matching block found)")

print("\n" + "=" * 86)
print("STEP 2 — publish the cleanup instructions as a Notion page")
print("=" * 86)
r = requests.post(f"{BASE}/pages", headers=H, timeout=40, json={
    "parent": {"type": "page_id", "page_id": MASTER},
    "icon": {"type": "emoji", "emoji": "🤖"},
    "properties": {"title": [{"text": {"content":
        "📋 NOTION AI CLEANUP INSTRUCTIONS — paste into Notion AI"}}]},
})
if r.status_code != 200:
    print(f"  create failed {r.status_code}: {r.text[:250]}")
    raise SystemExit(1)
INSTR = r.json()["id"]
print(f"  created page {INSTR}")


def h2(t):
    return {"object": "block", "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": t}}]}}


def h3(t):
    return {"object": "block", "type": "heading_3",
            "heading_3": {"rich_text": [{"type": "text", "text": {"content": t}}]}}


def p(t):
    return {"object": "block", "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": t}}]}}


def b(t):
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": t}}]}}


def n(t):
    return {"object": "block", "type": "numbered_list_item",
            "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": t}}]}}


blocks = [
    {"object": "block", "type": "callout", "callout": {
        "icon": {"type": "emoji", "emoji": "🎯"},
        "rich_text": [{"type": "text", "text": {"content":
            "Select this page, copy it, and paste it to Notion AI. Then work one task at a time."}}]}},

    h2("WHY THIS EXISTS"),
    p("An audit found 912 objects (883 pages, 29 databases) with four structural problems. They could not "
      "be fixed by API: Notion's API cannot re-parent pages OR databases. A page move returns HTTP 200 "
      "and silently does nothing. You are being asked because you CAN move things."),

    h2("GROUND RULES — read first"),
    n("Verify every move: after moving anything, open it and confirm it really moved. Do not trust a success message."),
    n("Never mass-delete without showing me first. For any deletion over 10 items, list them and wait."),
    n("Do not touch anything in the DO NOT TOUCH list below."),
    n("Work one task at a time and report after each."),
    n("If content looks like real personal or business records, stop and ask."),

    h2("TASK 1 — Review the imported Finnish template (145 pages)"),
    p("145 pages titled 'Aamuyhteenveto – <date>' (Finnish: morning summary), plus a database "
      "'Aamuyhteenvedon keskus'. All 145 were last edited 2026-08-30 in a single batch — the signature "
      "of a template import."),
    n("Open 'Aamuyhteenvedon keskus' and read 5–6 of the pages at random."),
    n("Tell me: is this an imported template, or my own real journal entries?"),
    n("If they contain my own writing — STOP, do not delete, report back."),
    n("If empty or obviously template filler, list all 145 and ask me to confirm before deleting."),
    p("Also: this tree's parent is a page the API could not see. If you can see it, tell me what it is — "
      "it may reveal a second workspace."),

    h2("TASK 2 — Deduplicate the life-category pages (20 → 10)"),
    p("These ten categories each exist TWICE — one copy from 2026-08-31, one from 2026-09-09."),
    b("Admin · Business · Family · Finance · Fitness · Health · Hobbies · Learning · Projects · Travel"),
    p("For each pair: compare contents. One empty → archive the empty one. Both have content → copy the "
      "unique material from the smaller into the larger, then archive the smaller. Both full and "
      "different → STOP and ask me."),
    p("Full ID table for all 20 pages is in the repo: ops/notion-workspace/02-NOTION-AI-CLEANUP-INSTRUCTIONS.md"),
    p("Report the outcome for all ten before moving on."),

    h2("TASK 3 — Organize the workspace root"),
    p("14 items sit loose at the workspace root. Keep 'NURATECH — MASTER WORKSPACE' at the root — it is "
      "the index for everything else."),
    h3("Move these UNDER 'NURATECH — MASTER WORKSPACE'"),
    b("Meeting recap"),
    b("12-Week Plan"),
    b("Project — Raspberry Pi + ESP32 Daily Intel Dashboard"),
    b("🕵️ OSINT & Intelligence Command"),
    b("Private Clinical Appendix — Cognitive Profile"),
    b("If you can move databases too: People, Claude Tasks, My links"),
    h3("LEAVE AT THE ROOT (they are hubs themselves)"),
    b("NURATECH AI — Executive Command Center"),
    b("To Do List"),
    b("NURA Health Communications Flutter App"),
    b("NURA Provider Labs — Master Clinical Intelligence, Radiology & Imaging"),
    b("Archive — NURATECH Executive Command Center — Backup 2026-09-09"),
    p("After each move, open the item and confirm it really moved."),

    h2("TASK 4 — Resolve the four ⛔ SUPERSEDED databases (top-down, one at a time)"),
    p("Each is a duplicate of a live database, but sits atop a NESTED tree — deleting one deletes its "
      "child pages and child databases with it. This is why the API could not do it."),
    n("Open the superseded database and list EVERY child page and child database beneath its rows."),
    n("For each, confirm an equivalent exists in the live replacement."),
    n("All duplicated → delete it. Anything unique → tell me, do not delete, do not merge silently."),
    p("Check first: the superseded Executive Projects holds a 'Medisun Digital Operations & NURA ERP "
      "Integration' project and an 'Untitled' child database. Confirm both exist in the live set."),
    p("Live replacements: Executive Projects 9547910e · Organizations c20a9b14 · Medisun Completed Work "
      "8aca9b14 · Prehospital c28d624e (full IDs in the repo file)."),

    h2("TASK 5 — Verify and finish"),
    n("Confirm 'NURATECH — MASTER WORKSPACE' is at the root and readable top to bottom."),
    n("Confirm the workspace root holds only the intended items."),
    n("Update the OUTSTANDING CLEANUP section of the Master Workspace page."),
    n("Report what you changed, with counts."),

    h2("🚫 DO NOT TOUCH"),
    b("NURATECH AI — Executive Command Center (284 items) — the live operations hub"),
    b("NURATECH — MASTER WORKSPACE — the index; add to it, don't restructure it"),
    b("The Skill Registry — unreadable to the API but contains 30+ REAL ROWS, one per skill category. "
      "DO NOT DELETE. It is live content, not a ghost."),
    b("Private Clinical Appendix — Cognitive Profile — sensitive health data; move if asked, never share or export"),
    b("Anything marked ⛔ SUPERSEDED — leave alone until Task 4 says otherwise"),
    b("Archive — NURATECH Executive Command Center — Backup 2026-09-09 — a deliberate backup"),
    b("The live Master Tasks & Commitments and Executive Projects — canonical writes must keep working"),

    h2("ALREADY FIXED — no action needed"),
    b("33 databases → 29. Five leaf duplicates removed; canonical set verified intact by row count."),
    b("Notion's default 'Welcome to Notion!' page removed."),
    b("A single Master Workspace index page built covering every project, database, area and open item."),
]

CH = 40
for i in range(0, len(blocks), CH):
    rr = requests.patch(f"{BASE}/blocks/{INSTR}/children", headers=H, timeout=40,
                        json={"children": blocks[i:i + CH]})
    print(f"  appended {min(i+CH, len(blocks))}/{len(blocks)}: {rr.status_code}")
    time.sleep(0.4)

print(f"\n  INSTRUCTIONS PAGE -> https://www.notion.so/{INSTR.replace('-','')}")
