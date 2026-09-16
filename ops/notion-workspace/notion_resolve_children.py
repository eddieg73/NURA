"""Resolve the two copies that carried child content, and compare their children against the live twins."""
import sys, requests, time
sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"


def rows_of(db):
    out, cur = [], None
    while True:
        b = {"page_size": 100}
        if cur:
            b["start_cursor"] = cur
        r = requests.post(f"{BASE}/databases/{db}/query", headers=H, json=b, timeout=40)
        if r.status_code != 200:
            return None, r.status_code, r.text[:160]
        d = r.json()
        out.extend(d.get("results", []))
        if not d.get("has_more"):
            return out, 200, None
        cur = d.get("next_cursor")


def title_of(o):
    for v in (o.get("properties") or {}).values():
        if isinstance(v, dict) and v.get("type") == "title":
            return "".join(x.get("plain_text", "") for x in v.get("title", [])).strip()
    return "(untitled)"


def children_of_tree(db, label):
    rows, code, err = rows_of(db)
    print(f"\n  {label}  ({db[:8]})")
    if rows is None:
        print(f"     QUERY FAILED {code}: {err}")
        return None
    print(f"     rows={len(rows)}")
    found = []
    for row in rows:
        ch = requests.get(f"{BASE}/blocks/{row['id']}/children?page_size=100", headers=H, timeout=30)
        if ch.status_code != 200:
            continue
        for b in ch.json().get("results", []):
            if b.get("type") in ("child_page", "child_database"):
                kind = b["type"]
                found.append((title_of(row), kind, b["id"], (b.get(kind) or {}).get("title", "")))
        time.sleep(0.1)
    for rt, kind, cid, cname in found:
        print(f"     └─ {kind}: {cname[:60]!r}")
        print(f"        under: {rt[:60]}   id={cid}")
    if not found:
        print("     (no child content)")
    return found


print("=" * 92)
print("A. ORGANIZATIONS — copy (116b71cd, restored) vs live (c20a9b14)")
print("=" * 92)
copy_kids = children_of_tree("116b71cd-76a4-4eef-a1d0-81068e3c6cf4", "COPY")
live_kids = children_of_tree("c20a9b14-e498-8333-b554-01413da172df", "LIVE")

print("\n  COMPARISON")
ck = {(k[1], k[3]) for k in (copy_kids or [])}
lk = {(k[1], k[3]) for k in (live_kids or [])}
print(f"     only in COPY: {sorted(ck - lk) if ck - lk else 'none'}")
print(f"     only in LIVE: {sorted(lk - ck) if lk - ck else 'none'}")

print("\n" + "=" * 92)
print("B. MEDISUN COMPLETED WORK — copy (44a69385) vs live (8aca9b14)")
print("=" * 92)
print("  checking the copy's DB state:")
r = requests.get(f"{BASE}/databases/44a69385-45ef-47ab-a787-aa6274472081", headers=H, timeout=30)
if r.status_code == 200:
    j = r.json()
    print(f"     in_trash={j.get('in_trash')}")
    print(f"     parent={j.get('parent')}")
    print(f"     title={''.join(x.get('plain_text','') for x in j.get('title',[]))!r}")
    par = (j.get("parent") or {}).get("page_id")
    if par:
        pg = requests.get(f"{BASE}/pages/{par}", headers=H, timeout=30)
        if pg.status_code == 200:
            pj = pg.json()
            t = ""
            for v in (pj.get("properties") or {}).values():
                if isinstance(v, dict) and v.get("type") == "title":
                    t = "".join(x.get("plain_text", "") for x in v.get("title", []))
            print(f"     parent page title = {t!r}  in_trash={pj.get('in_trash')}")
            print(f"     parent page's parent = {pj.get('parent')}")
else:
    print(f"     GET {r.status_code}: {r.text[:200]}")

print("\n  resolving the ancestor chain to unblock it...")
# walk up: if an ancestor is trashed, restore it
for dbid, lbl in [("44a69385-45ef-47ab-a787-aa6274472081", "Medisun copy (ancestor restore)")]:
    g = requests.get(f"{BASE}/databases/{dbid}", headers=H, timeout=30)
    if g.status_code != 200:
        continue
    par = (g.json().get("parent") or {}).get("page_id")
    if par:
        requests.patch(f"{BASE}/pages/{par}", headers=H, timeout=30, json={"in_trash": False})
        time.sleep(1.0)
        print(f"     restored ancestor page {par[:8]}")
    rr = requests.patch(f"{BASE}/databases/{dbid}", headers=H, timeout=30, json={"in_trash": False})
    time.sleep(0.8)
    rows, code, err = rows_of(dbid)
    print(f"     requery -> {'rows='+str(len(rows)) if rows is not None else f'{code} {err}'}")
