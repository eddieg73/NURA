"""
Recover from the cascade.

Trashing the 'Executive Projects (copy)' database cascaded to its row pages and
their child databases, because a project page can parent a database. The row-title
diff could not see that. This restores the copy, enumerates the whole affected
subtree, and reports what must be re-parented or kept.
"""
import sys, requests, json, time
sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"

COPY = "e90a9b14-e498-83f9-ae0b-810a94157b95"   # Executive Projects (copy)
PREH_COPY = "cdca9b14-e498-821f-9a92-814495237c4f"
PREH_LIVE = "c28d624e-b827-4065-b1fd-200cdf7dd561"

print("=" * 86)
print("STEP 1 — restore the ancestor to stop the cascade")
print("=" * 86)
r = requests.patch(f"{BASE}/databases/{COPY}", headers=H, timeout=30, json={"in_trash": False})
print(f"  restore Executive Projects (copy) -> {r.status_code}")
time.sleep(1.5)

print("\n" + "=" * 86)
print("STEP 2 — what lives under that copy? (the cascade's blast radius)")
print("=" * 86)
rows, cursor = [], None
while True:
    body = {"page_size": 100}
    if cursor:
        body["start_cursor"] = cursor
    q = requests.post(f"{BASE}/databases/{COPY}/query", headers=H, json=body, timeout=40)
    if q.status_code != 200:
        print(f"  query {q.status_code}: {q.text[:200]}")
        break
    d = q.json()
    rows.extend(d.get("results", []))
    if not d.get("has_more"):
        break
    cursor = d.get("next_cursor")

print(f"  rows in copy: {len(rows)}")


def t_of(o):
    for v in (o.get("properties") or {}).values():
        if isinstance(v, dict) and v.get("type") == "title":
            return "".join(x.get("plain_text", "") for x in v.get("title", [])).strip()
    return "(untitled)"


affected = []
for row in rows:
    rid = row["id"]
    pr = requests.get(f"{BASE}/pages/{rid}", headers=H, timeout=30)
    trashed = pr.json().get("in_trash") if pr.status_code == 200 else "?"
    ch = requests.get(f"{BASE}/blocks/{rid}/children?page_size=100", headers=H, timeout=30)
    kids = []
    if ch.status_code == 200:
        for b in ch.json().get("results", []):
            if b.get("type") == "child_database":
                kids.append(("DB", b["id"], b["child_database"].get("title", "")))
    if trashed is True or kids:
        affected.append((t_of(row), rid, trashed, kids))
    time.sleep(0.15)

print(f"  rows that were trashed or parent a child DB: {len(affected)}")
for t, rid, tr, kids in affected:
    print(f"\n  • {t[:70]}")
    print(f"      row={rid}  in_trash={tr}")
    for kind, kid, ktitle in kids:
        kr = requests.get(f"{BASE}/databases/{kid}", headers=H, timeout=30)
        kin = kr.json().get("in_trash") if kr.status_code == 200 else "?"
        print(f"      └─ child {kind}: {ktitle!r}  id={kid}  in_trash={kin}")

print("\n" + "=" * 86)
print("STEP 3 — restore the Prehospital DB that actually holds the data")
print("=" * 86)
for did, lbl in [(PREH_COPY, "Prehospital under COPY page"),
                 (PREH_LIVE, "Prehospital under LIVE page")]:
    rr = requests.patch(f"{BASE}/databases/{did}", headers=H, timeout=30, json={"in_trash": False})
    g = requests.get(f"{BASE}/databases/{did}", headers=H, timeout=30)
    state = g.json().get("in_trash") if g.status_code == 200 else "?"
    print(f"  {lbl:<34} restore={rr.status_code}  in_trash={state}")

print("\n" + "=" * 86)
print("STEP 4 — verify both Prehospital DBs now query")
print("=" * 86)
for did, lbl in [(PREH_COPY, "cdca9b14 (copy page)"), (PREH_LIVE, "c28d624e (live page)")]:
    q = requests.post(f"{BASE}/databases/{did}/query", headers=H, json={"page_size": 100}, timeout=40)
    if q.status_code == 200:
        print(f"  {lbl:<28} rows={len(q.json().get('results', []))}")
    else:
        print(f"  {lbl:<28} query {q.status_code}")
