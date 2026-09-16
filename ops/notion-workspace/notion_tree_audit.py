"""
Full Notion workspace audit: every page and database, its parent chain, and what is
actually unorganized (loose at root, orphaned, or stranded under a trashed ancestor).
"""
import sys, requests, json, time
from collections import defaultdict, Counter
sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"

STOP = {"something went wrong", ""}


def search_all(obj_filter, cap=1200):
    out, cur = [], None
    while len(out) < cap:
        body = {"page_size": 100,
                "sort": {"direction": "descending", "timestamp": "last_edited_time"}}
        if obj_filter:
            body["filter"] = {"value": obj_filter, "property": "object"}
        if cur:
            body["start_cursor"] = cur
        r = requests.post(f"{BASE}/search", headers=H, json=body, timeout=40)
        if r.status_code != 200:
            print(f"  search {r.status_code}: {r.text[:160]}")
            break
        d = r.json()
        out.extend(d.get("results", []))
        if not d.get("has_more"):
            break
        cur = d.get("next_cursor")
    return out


def title_of(o):
    if o.get("object") == "database" and o.get("title"):
        return "".join(x.get("plain_text", "") for x in o["title"]).strip()
    for v in (o.get("properties") or {}).values():
        if isinstance(v, dict) and v.get("type") == "title":
            t = "".join(x.get("plain_text", "") for x in v.get("title", [])).strip()
            if t:
                return t
    return "(untitled)"


print("enumerating workspace...")
pages = search_all("page")
dbs = search_all("database")
print(f"  pages={len(pages)}  databases={len(dbs)}")

# ---- build a title map so parents can be named ----
titles = {}
for o in pages + dbs:
    titles[o["id"]] = title_of(o)

records = []
for o in pages + dbs:
    p = o.get("parent") or {}
    pt = p.get("type")
    pid = None
    if pt == "page_id":
        pid = p.get("page_id")
    elif pt == "database_id":
        pid = p.get("database_id")
    elif pt == "workspace":
        pid = None
    records.append({
        "id": o["id"],
        "kind": o.get("object"),
        "title": title_of(o),
        "parent_type": pt,
        "parent_id": pid,
        "edited": (o.get("last_edited_time") or "")[:10],
        "trashed": o.get("in_trash", False),
    })

by_id = {r["id"]: r for r in records}


def root_of(rec, depth=0):
    """Walk to the top-level ancestor. Returns (root_id, root_title, depth) or a marker."""
    seen = set()
    cur = rec
    d = 0
    while True:
        pid = cur["parent_id"]
        if pid is None:
            return (cur["id"], cur["title"], d)
        if pid in seen or d > 40:
            return ("CYCLE", "(cycle)", d)
        seen.add(pid)
        nxt = by_id.get(pid)
        if nxt is None:
            return (pid, titles.get(pid, "(parent not visible)"), d)
        cur = nxt
        d += 1


print("resolving ancestry...")
for r in records:
    rid, rtitle, depth = root_of(r)
    r["root_id"] = rid
    r["root_title"] = rtitle
    r["depth"] = depth

live = [r for r in records if not r["trashed"]]
dead = [r for r in records if r["trashed"]]

print("\n" + "=" * 96)
print(f"WORKSPACE STRUCTURE   live={len(live)}   in-trash={len(dead)}")
print("=" * 96)

roots = defaultdict(list)
for r in live:
    roots[(r["root_id"], r["root_title"])].append(r)

print(f"\nTOP-LEVEL GROUPS: {len(roots)}\n")
ordered = sorted(roots.items(), key=lambda kv: -len(kv[1]))
for (rid, rtitle), items in ordered:
    ndb = sum(1 for i in items if i["kind"] == "database")
    npg = sum(1 for i in items if i["kind"] == "page")
    top = [i for i in items if i["depth"] == 0]
    mark = "ROOT-LOOSE" if any(i["parent_type"] == "workspace" for i in top) else "grouped"
    print(f"  [{len(items):>4} items | {ndb:>2} db, {npg:>4} pg]  {rtitle[:58]:<60} {mark}")
    print(f"        root id {rid}")

print("\n" + "=" * 96)
print("LOOSE AT WORKSPACE ROOT (top-level, no organizing parent)")
print("=" * 96)
loose = [r for r in live if r["parent_type"] == "workspace"]
for r in sorted(loose, key=lambda x: (x["kind"], x["title"].lower())):
    print(f"  {r['kind']:<9} {r['title'][:62]:<64} {r['id']}")
print(f"\n  total loose: {len(loose)}")

print("\n" + "=" * 96)
print("ORPHANED / STRANDED (parent not visible to the integration)")
print("=" * 96)
orphans = [r for r in live if r["root_id"] == "CYCLE" or r["root_title"] == "(parent not visible)"]
for r in sorted(orphans, key=lambda x: x["title"].lower())[:30]:
    print(f"  {r['kind']:<9} {r['title'][:58]:<60} parent={r['parent_id']}")
print(f"\n  total orphaned: {len(orphans)}")

print("\n" + "=" * 96)
print("DEPTH DISTRIBUTION (how deep content sits)")
print("=" * 96)
dep = Counter(r["depth"] for r in live)
for k in sorted(dep):
    print(f"  depth {k:>2}: {dep[k]}")

json.dump({"records": records, "root_count": len(roots)},
          open("/opt/data/notion_tree_audit.json", "w"), indent=1)
print("\n-> /opt/data/notion_tree_audit.json")
