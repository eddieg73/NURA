"""Consolidate the last remaining duplicate pair: Founder Evolution Diary (10 rows each)."""
import sys, requests, json, time
sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"


def all_rows(db_id):
    out, cursor = [], None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        r = requests.post(f"{BASE}/databases/{db_id}/query", headers=H, json=body, timeout=40)
        if r.status_code != 200:
            return None, r.status_code
        d = r.json()
        out.extend(d.get("results", []))
        if not d.get("has_more"):
            return out, 200
        cursor = d.get("next_cursor")


def title_of(row):
    for v in (row.get("properties") or {}).values():
        if isinstance(v, dict) and v.get("type") == "title":
            return "".join(x.get("plain_text", "") for x in v.get("title", [])).strip()
    return ""


def db_meta(db_id):
    r = requests.get(f"{BASE}/databases/{db_id}", headers=H, timeout=30)
    if r.status_code != 200:
        return None
    d = r.json()
    return {
        "title": "".join(x.get("plain_text", "") for x in d.get("title", [])),
        "edited": d.get("last_edited_time", "")[:10],
        "trashed": d.get("in_trash"),
        "parent": (d.get("parent") or {}).get("page_id") or (d.get("parent") or {}).get("type"),
    }


PAIRS = [
    ("Founder Evolution Diary",
     "e3ba9b14-e498-83a0-94ab-81d0f6304ba0",
     "a5dfe5bd-c416-4f4c-b3e9-d6119279ad88"),
]

for name, a_id, b_id in PAIRS:
    print("=" * 86)
    print(name)
    print("=" * 86)
    ma, mb = db_meta(a_id), db_meta(b_id)
    print(f"  A {a_id[:8]}  {ma}")
    print(f"  B {b_id[:8]}  {mb}")
    ra, ca = all_rows(a_id)
    rb, cb = all_rows(b_id)
    print(f"  rows A={len(ra) if ra is not None else 'ERR'+str(ca)}  "
          f"B={len(rb) if rb is not None else 'ERR'+str(cb)}")
    if ra is None or rb is None:
        continue
    ka = {title_of(x) for x in ra if title_of(x)}
    kb = {title_of(x) for x in rb if title_of(x)}
    print(f"  shared={len(ka & kb)}  only A={len(ka - kb)}  only B={len(kb - ka)}")
    for t in sorted(ka - kb):
        print(f"     A> {t[:72]}")
    for t in sorted(kb - ka):
        print(f"     B> {t[:72]}")

    # keep the one whose parent is the LIVE Executive Command Center (613e14da)
    live = "613e14da"
    keep, drop = (a_id, b_id) if live in str(ma["parent"]) else (b_id, a_id)
    print(f"\n  KEEP {keep[:8]} (parent is the live command center)")
    print(f"  DROP {drop[:8]}")

    if len(ka - kb) or len(kb - ka):
        print("  !! non-identical — NOT auto-trashing, needs review")
        continue

    drop_rows, _ = all_rows(drop)
    manifest = {"id": drop, "label": name, "reason": "identical duplicate of " + keep,
                "row_count": len(drop_rows), "rows": [title_of(x) for x in drop_rows]}
    existing = json.load(open("/opt/data/notion_superseded_manifest.json"))
    existing.append(manifest)
    json.dump(existing, open("/opt/data/notion_superseded_manifest.json", "w"), indent=1)

    rr = requests.patch(f"{BASE}/databases/{drop}", headers=H, timeout=30, json={"in_trash": True})
    print(f"  trashed: {rr.status_code}   (rows preserved in manifest: {len(drop_rows)})")
    time.sleep(0.4)
