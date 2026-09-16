"""Inspect the ambiguous items: orphan row, skill registries, flutter boards, odd DBs, and the project list."""
import sys, requests, json
sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"


def all_rows(db_id, cap=300):
    out, cursor = [], None
    while len(out) < cap:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        r = requests.post(f"{BASE}/databases/{db_id}/query", headers=H, json=body, timeout=40)
        if r.status_code != 200:
            return None, r.status_code, r.text[:200]
        d = r.json()
        out.extend(d.get("results", []))
        if not d.get("has_more"):
            break
        cursor = d.get("next_cursor")
    return out, 200, None


def title_of(row):
    for v in (row.get("properties") or {}).values():
        if isinstance(v, dict) and v.get("type") == "title":
            return "".join(x.get("plain_text", "") for x in v.get("title", [])).strip()
    return ""


def db_info(db_id):
    r = requests.get(f"{BASE}/databases/{db_id}", headers=H, timeout=30)
    if r.status_code != 200:
        return None, r.status_code
    return r.json(), 200


print("=" * 96)
print("1. THE ONE ORPHAN ROW — is 'Medisun Digital Operations & NURA ERP Integration' a rename?")
print("=" * 96)
ra, _, _ = all_rows("9547910e-8975-44b8-b511-2108abfa0d11")
rb, _, _ = all_rows("e90a9b14-e498-83f9-ae0b-810a94157b95")
print("\n  -- A-side ERP-related rows --")
for r in ra or []:
    t = title_of(r)
    if "erp" in t.lower() or "medisun" in t.lower():
        print(f"     A: {t}")
        print(f"        created={r.get('created_time','')[:10]} edited={r.get('last_edited_time','')[:10]} id={r['id']}")
print("\n  -- B-side ERP-related rows --")
for r in rb or []:
    t = title_of(r)
    if "erp" in t.lower() or "medisun" in t.lower():
        print(f"     B: {t}")
        print(f"        created={r.get('created_time','')[:10]} edited={r.get('last_edited_time','')[:10]} id={r['id']}")

print("\n" + "=" * 96)
print("2. SKILL REGISTRY x3 — why did the query fail?")
print("=" * 96)
for sid in ["70986afe-0c3c-4954-9644-ac2525d53b15",
            "10cf4335-b217-4a49-b6d0-a567fe3df2cd",
            "ee46997c-71ff-4fa7-8ce4-bcee1ed0b9e6"]:
    info, code = db_info(sid)
    if info:
        t = "".join(x.get("plain_text", "") for x in info.get("title", []))
        print(f"  {sid[:8]}  {t!r}")
        print(f"     in_trash={info.get('in_trash')}  archived={info.get('archived')}  parent={(info.get('parent') or {}).get('type')}")
        print(f"     props={list((info.get('properties') or {}).keys())[:6]}")
    else:
        print(f"  {sid[:8]}  FAILED {code}")

print("\n" + "=" * 96)
print("3. FLUTTER BOARDS")
print("=" * 96)
for sid in ["2c2be702-682d-473a-ba55-d5520e1dafee", "22260907-f18c-4768-95de-052942bdb055"]:
    rows, code, err = all_rows(sid)
    info, _ = db_info(sid)
    t = "".join(x.get("plain_text", "") for x in (info or {}).get("title", []))
    print(f"  {sid[:8]}  {t!r}  rows={len(rows) if rows is not None else 'FAIL '+str(code)}")
    for r in (rows or [])[:4]:
        print(f"       - {title_of(r)[:70]}")

print("\n" + "=" * 96)
print("4. THE 18 PROJECTS (canonical Executive Projects A) — the project registry source")
print("=" * 96)
for i, r in enumerate(ra or [], 1):
    props = r.get("properties") or {}
    st = ""
    for k in ("Status", "State", "Stage", "Phase"):
        v = props.get(k)
        if isinstance(v, dict):
            t = v.get("type")
            if t == "status" and v.get("status"):
                st = v["status"].get("name")
            elif t == "select" and v.get("select"):
                st = v["select"].get("name")
    due = ""
    v = props.get("Due") or props.get("Due Date")
    if isinstance(v, dict) and v.get("date"):
        due = (v["date"] or {}).get("start") or ""
    print(f"  {i:>2}. {title_of(r)[:62]:<64} {st:<14} {due}")
