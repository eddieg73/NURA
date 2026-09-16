"""Row-level diff between each duplicate DB pair, to find orphans before any consolidation."""
import sys, requests, json
sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"


def all_rows(db_id, cap=400):
    out, cursor = [], None
    while len(out) < cap:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        r = requests.post(f"{BASE}/databases/{db_id}/query", headers=H, json=body, timeout=40)
        if r.status_code != 200:
            return None
        d = r.json()
        out.extend(d.get("results", []))
        if not d.get("has_more"):
            break
        cursor = d.get("next_cursor")
    return out


def row_key(row):
    """Best available human key for a row."""
    props = row.get("properties") or {}
    for name in ("Name", "Task", "Title", "Project", "Item", "Entry", "Title "):
        v = props.get(name)
        if isinstance(v, dict) and v.get("type") == "title":
            t = "".join(x.get("plain_text", "") for x in v.get("title", [])).strip()
            if t:
                return t
    for v in props.values():
        if isinstance(v, dict) and v.get("type") == "title":
            t = "".join(x.get("plain_text", "") for x in v.get("title", [])).strip()
            if t:
                return t
    return None


def row_status(row):
    props = row.get("properties") or {}
    for name in ("Status", "State", "Stage"):
        v = props.get(name)
        if isinstance(v, dict):
            t = v.get("type")
            if t == "status" and v.get("status"):
                return v["status"].get("name")
            if t == "select" and v.get("select"):
                return v["select"].get("name")
    return ""


PAIRS = [
    ("Executive Projects", "9547910e-8975-44b8-b511-2108abfa0d11", "e90a9b14-e498-83f9-ae0b-810a94157b95"),
    ("Master Tasks & Commitments", "d3ff0c00-c629-43dc-b82c-06a28866fcb1", "752a9b14-e498-8309-b369-817c7145b742"),
    ("Medisun Completed Work Register", "8aca9b14-e498-8200-8d00-0149672c0a5f", "44a69385-45ef-47ab-a787-aa6274472081"),
    ("Organizations & Current Roles", "c20a9b14-e498-8333-b554-01413da172df", "116b71cd-76a4-4eef-a1d0-81068e3c6cf4"),
    ("Prehospital & Aeromedical Evidence Board", "cdca9b14-e498-821f-9a92-814495237c4f", "c28d624e-b827-4065-b1fd-200cdf7dd561"),
    ("🧠 Founder Evolution Diary", "3d6a9b14-e498-81e2-bab7-fc22b42127e9_dup", "613e14da-104a-470e-af85-799d66eb8ebc_dup"),
]

report = {}
for name, a_id, b_id in PAIRS:
    if "_dup" in a_id:
        continue  # handled below
    ra, rb = all_rows(a_id), all_rows(b_id)
    if ra is None or rb is None:
        print(f"\n{name}: QUERY FAILED (a={ra is None}, b={rb is None})")
        continue
    ka = {row_key(r) for r in ra if row_key(r)}
    kb = {row_key(r) for r in rb if row_key(r)}
    both = ka & kb
    only_a = ka - kb
    only_b = kb - ka
    report[name] = {"A": len(ra), "B": len(rb), "both": len(both),
                    "only_A": sorted(only_a), "only_B": sorted(only_b)}
    print("\n" + "=" * 90)
    print(f"{name}")
    print(f"  A = {a_id[:8]}  rows={len(ra)}")
    print(f"  B = {b_id[:8]}  rows={len(rb)}")
    print(f"  shared keys : {len(both)}")
    print(f"  ONLY in A   : {len(only_a)}")
    for t in sorted(only_a)[:14]:
        print(f"      A> {t[:78]}")
    if len(only_a) > 14:
        print(f"      ... +{len(only_a)-14} more")
    print(f"  ONLY in B   : {len(only_b)}")
    for t in sorted(only_b)[:14]:
        print(f"      B> {t[:78]}")
    if len(only_b) > 14:
        print(f"      ... +{len(only_b)-14} more")

with open("/opt/data/notion_dup_rows.json", "w") as f:
    json.dump(report, f, indent=1)
print("\n-> /opt/data/notion_dup_rows.json")
