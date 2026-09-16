"""Full Notion inventory: every database with row count, last edit, and parent."""
import sys, requests, datetime, json
sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"


def title_of(obj):
    if obj.get("object") == "database" and obj.get("title"):
        return "".join(t.get("plain_text", "") for t in obj["title"])
    for v in (obj.get("properties") or {}).values():
        if isinstance(v, dict) and v.get("type") == "title":
            return "".join(t.get("plain_text", "") for t in v.get("title", []))
    return "(untitled)"


def search_all(obj_filter, cap=600):
    out, cursor = [], None
    while len(out) < cap:
        body = {"page_size": 100,
                "sort": {"direction": "descending", "timestamp": "last_edited_time"}}
        if obj_filter:
            body["filter"] = {"value": obj_filter, "property": "object"}
        if cursor:
            body["start_cursor"] = cursor
        r = requests.post(f"{BASE}/search", headers=H, json=body, timeout=30)
        if r.status_code != 200:
            break
        d = r.json()
        out.extend(d.get("results", []))
        if not d.get("has_more"):
            break
        cursor = d.get("next_cursor")
    return out


def db_rows(db_id):
    try:
        r = requests.post(f"{BASE}/databases/{db_id}/query", headers=H,
                          json={"page_size": 100}, timeout=30)
        if r.status_code != 200:
            return None, None
        d = r.json()
        return len(d.get("results", [])), d.get("has_more")
    except Exception:
        return None, None


def parent_desc(obj):
    p = obj.get("parent") or {}
    t = p.get("type")
    if t == "workspace":
        return "WORKSPACE-ROOT"
    if t == "page_id":
        return f"page:{p.get('page_id')}"
    if t == "database_id":
        return f"db:{p.get('database_id')}"
    return str(t)


dbs = search_all("database")
pages = search_all("page")

print("=" * 100)
print(f"DATABASES: {len(dbs)}   PAGES: {len(pages)}")
print("=" * 100)

rows = []
for d in dbs:
    n, more = db_rows(d["id"])
    rows.append({
        "title": title_of(d),
        "id": d["id"],
        "rows": n,
        "has_more": bool(more),
        "edited": d.get("last_edited_time", "")[:16],
        "parent": parent_desc(d),
    })

rows.sort(key=lambda r: (r["title"].lower(), -(r["rows"] or 0)))
print(f"\n{'DATABASE':<50} {'ROWS':>5}  {'LAST EDITED':<17} PARENT")
print("-" * 100)
for r in rows:
    flag = ">" if r["has_more"] else " "
    print(f"{r['title'][:49]:<50} {str(r['rows']):>4}{flag}  {r['edited']:<17} {r['parent']}")

# group by title to expose duplicates
from collections import defaultdict
by_title = defaultdict(list)
for r in rows:
    by_title[r["title"]].append(r)

print("\n" + "=" * 100)
print("DUPLICATE TITLES")
print("=" * 100)
dupes = {k: v for k, v in by_title.items() if len(v) > 1}
for t, group in sorted(dupes.items()):
    print(f"\n{t}  ({len(group)} copies)")
    for g in sorted(group, key=lambda x: -(x["rows"] or 0)):
        print(f"   {g['rows']:>4} rows  {g['edited']}  {g['id']}")
if not dupes:
    print("  (none)")

with open("/opt/data/notion_inventory.json", "w") as f:
    json.dump({"databases": rows, "page_count": len(pages)}, f, indent=1)
print("\n-> /opt/data/notion_inventory.json")
