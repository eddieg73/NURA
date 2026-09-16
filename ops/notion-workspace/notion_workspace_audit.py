"""Audit what actually exists in Notion: databases, project rows, and whether an index exists."""
import sys, requests, json
sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()


def search_all(obj_filter=None):
    out, cursor = [], None
    for _ in range(12):
        body = {
            "page_size": 100,
            "sort": {"direction": "descending", "timestamp": "last_edited_time"},
        }
        if obj_filter:
            body["filter"] = {"value": obj_filter, "property": "object"}
        if cursor:
            body["start_cursor"] = cursor
        r = requests.post("https://api.notion.com/v1/search", headers=H, json=body, timeout=30)
        if r.status_code != 200:
            print(f"  search error {r.status_code}: {r.text[:200]}")
            break
        d = r.json()
        out.extend(d.get("results", []))
        if not d.get("has_more"):
            break
        cursor = d.get("next_cursor")
    return out


def title_of(obj):
    props = obj.get("properties") or {}
    if obj.get("object") == "database" and obj.get("title"):
        return "".join(t.get("plain_text", "") for t in obj["title"])
    for v in props.values():
        if isinstance(v, dict) and v.get("type") == "title":
            return "".join(t.get("plain_text", "") for t in v.get("title", []))
    return "(untitled)"


print("=" * 72)
print("NOTION WORKSPACE AUDIT")
print("=" * 72)

dbs = [o for o in search_all("database") if o.get("object") == "database"]
pages = [o for o in search_all("page") if o.get("object") == "page"]

print(f"\nDATABASES VISIBLE: {len(dbs)}")
for d in sorted(dbs, key=lambda x: title_of(x).lower()):
    print(f"  - {title_of(d):<46} {d['id']}")

print(f"\nTOP-LEVEL / ALL PAGES VISIBLE: {len(pages)}")

# flag anything that looks like an index / map of content
KEY = ("index", "map of content", "moc", "directory", "master", "command center",
       "hub", "overview", "start here", "dashboard", "registry")
print("\nPAGES THAT LOOK LIKE AN INDEX / HUB / DASHBOARD:")
found = []
for p in pages:
    t = title_of(p)
    if any(k in t.lower() for k in KEY):
        found.append((t, p["id"]))
for t, i in sorted(found):
    print(f"  - {t:<52} {i}")
if not found:
    print("  (none)")

with open("/opt/data/notion_audit_raw.json", "w") as f:
    json.dump({"databases": dbs, "pages": pages}, f, indent=1)
print("\nraw -> /opt/data/notion_audit_raw.json")
