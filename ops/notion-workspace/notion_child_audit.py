"""
Safety audit: for every database I trashed, restore it, check whether any of its rows
parent a child page or child database, then decide keep vs re-trash.

A row-title diff cannot detect child content, so this is the check that should have
preceded the first trash.
"""
import sys, requests, time
sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"

TRASHED = [
    ("752a9b14-e498-8309-b369-817c7145b742", "Master Tasks & Commitments (copy)", 57),
    ("44a69385-45ef-47ab-a787-aa6274472081", "Medisun Completed Work Register (copy)", 27),
    ("116b71cd-76a4-4eef-a1d0-81068e3c6cf4", "Organizations & Current Roles (copy)", 9),
    ("c28d624e-b827-4065-b1fd-200cdf7dd561", "Prehospital & Aeromedical Evidence (copy)", 6),
    ("e3ba9b14-e498-83a0-94ab-81d0f6304ba0", "🧠 Founder Evolution Diary (copy)", 10),
    ("2c2be702-682d-473a-ba55-d5520e1dafee", "Flutter Delivery Board (dead, 0 rows)", 0),
    ("77a2851a-bf77-4992-8426-32fc18143850", "Time Tracking (dup empty)", 0),
]


def rows_of(db):
    out, cur = [], None
    while True:
        b = {"page_size": 100}
        if cur:
            b["start_cursor"] = cur
        r = requests.post(f"{BASE}/databases/{db}/query", headers=H, json=b, timeout=40)
        if r.status_code != 200:
            return None
        d = r.json()
        out.extend(d.get("results", []))
        if not d.get("has_more"):
            return out
        cur = d.get("next_cursor")


def title_of(o):
    for v in (o.get("properties") or {}).values():
        if isinstance(v, dict) and v.get("type") == "title":
            return "".join(x.get("plain_text", "") for x in v.get("title", [])).strip()
    return "(untitled)"


print("=" * 92)
print("CHILD-CONTENT AUDIT OF EVERY TRASHED DATABASE")
print("=" * 92)

verdicts = []
for did, label, expected in TRASHED:
    # restore so we can inspect
    requests.patch(f"{BASE}/databases/{did}", headers=H, timeout=30, json={"in_trash": False})
    time.sleep(0.8)
    rows = rows_of(did)
    if rows is None:
        print(f"\n{label}\n   could not query after restore — leaving RESTORED (safe)")
        verdicts.append((label, "RESTORED", "unqueryable"))
        continue

    carriers = []
    for row in rows:
        ch = requests.get(f"{BASE}/blocks/{row['id']}/children?page_size=100", headers=H, timeout=30)
        if ch.status_code != 200:
            continue
        for b in ch.json().get("results", []):
            if b.get("type") in ("child_page", "child_database"):
                kind = b["type"]
                name = (b.get(kind) or {}).get("title", "")
                carriers.append((title_of(row), kind, b["id"], name))
        time.sleep(0.1)

    print(f"\n{label}")
    print(f"   rows={len(rows)}  rows carrying child content = {len(carriers)}")
    for rt, kind, cid, cname in carriers[:10]:
        print(f"      └─ {kind}: {cname[:56]!r}")
        print(f"         under row: {rt[:60]}")
    if len(carriers) > 10:
        print(f"      ... +{len(carriers)-10} more")

    if carriers:
        verdicts.append((label, "KEEP RESTORED", f"{len(carriers)} child items"))
    else:
        requests.patch(f"{BASE}/databases/{did}", headers=H, timeout=30, json={"in_trash": True})
        verdicts.append((label, "RE-TRASHED", "no child content"))

print("\n" + "=" * 92)
print("VERDICTS")
print("=" * 92)
for label, verdict, why in verdicts:
    print(f"  {label:<48} {verdict:<16} {why}")
