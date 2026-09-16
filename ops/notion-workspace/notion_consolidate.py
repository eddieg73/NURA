"""
1. Make every link bullet self-describing (mention + explicit name text).
2. Consolidate: trash the five superseded duplicates, with a restore manifest.
"""
import sys, requests, json, time
sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"
PAGE = "3d8a9b14-e498-8125-a630-f2fcc2bd2354"

meta = json.load(open("/opt/data/notion_master_page.json"))
projects = meta["projects"]                 # [(title, page_id, status)]
canon = meta["canonical"]                   # key -> (db_id, label, note)

page_by_id = {p[1]: (p[0], p[2]) for p in projects}
db_by_id = {v[0]: (v[1], v[2]) for v in canon.values()}

print("=" * 84)
print("STEP 1 — make link bullets self-describing")
print("=" * 84)

r = requests.get(f"{BASE}/blocks/{PAGE}/children?page_size=100", headers=H, timeout=40)
blocks = r.json().get("results", [])
fixed = 0
for b in blocks:
    bt = b.get("type")
    if bt != "bulleted_list_item":
        continue
    rt = b[bt].get("rich_text", [])
    if not rt or rt[0].get("type") != "mention":
        continue
    m = rt[0]["mention"]
    kind = m["type"]
    mid = m[kind]["id"]
    if kind == "page" and mid in page_by_id:
        name, st = page_by_id[mid]
        tail = f"  —  {name}" + (f"   [{st}]" if st else "")
    elif kind == "database" and mid in db_by_id:
        name, note = db_by_id[mid]
        tail = f"  —  {name}   ({note})"
    else:
        continue
    new_rt = [rt[0], {"type": "text", "text": {"content": tail}}]
    rr = requests.patch(f"{BASE}/blocks/{b['id']}", headers=H, timeout=30,
                        json={bt: {"rich_text": new_rt}})
    if rr.status_code == 200:
        fixed += 1
    else:
        print(f"    patch {rr.status_code}: {rr.text[:150]}")
    time.sleep(0.3)
print(f"  bullets made self-describing: {fixed}")

print("\n" + "=" * 84)
print("STEP 2 — consolidate: trash superseded duplicates")
print("=" * 84)
manifest = []
for db_id, label, why in meta["superseded"]:
    # capture a full dump BEFORE trashing, so nothing is unrecoverable
    rows, cursor = [], None
    for _ in range(4):
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        rr = requests.post(f"{BASE}/databases/{db_id}/query", headers=H, json=body, timeout=40)
        if rr.status_code != 200:
            break
        d = rr.json()
        rows.extend(d.get("results", []))
        if not d.get("has_more"):
            break
        cursor = d.get("next_cursor")

    def t_of(row):
        for v in (row.get("properties") or {}).values():
            if isinstance(v, dict) and v.get("type") == "title":
                return "".join(x.get("plain_text", "") for x in v.get("title", [])).strip()
        return ""

    manifest.append({
        "id": db_id, "label": label, "reason": why,
        "row_count": len(rows),
        "rows": [t_of(x) for x in rows],
    })

    tr = requests.patch(f"{BASE}/databases/{db_id}", headers=H, timeout=30,
                        json={"in_trash": True})
    print(f"  {label:<46} rows={len(rows):<3} trash={tr.status_code}")

with open("/opt/data/notion_superseded_manifest.json", "w") as f:
    json.dump(manifest, f, indent=1)
print("\n  manifest -> /opt/data/notion_superseded_manifest.json")
print(f"  total rows preserved in manifest: {sum(m['row_count'] for m in manifest)}")

print("\n" + "=" * 84)
print("STEP 3 — verify")
print("=" * 84)
for db_id, label, _ in meta["superseded"]:
    rr = requests.get(f"{BASE}/databases/{db_id}", headers=H, timeout=30)
    if rr.status_code == 200:
        print(f"  {label:<46} in_trash={rr.json().get('in_trash')}")
    else:
        print(f"  {label:<46} GET {rr.status_code} (gone/trashed)")
