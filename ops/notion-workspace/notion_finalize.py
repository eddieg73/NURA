"""
Finalize safely.

The row-title diff was insufficient: these databases are a NESTED TREE
(Organizations -> Medisun Health Group -> child databases), and two of the 'copies'
hold nested child content. Deleting them cascades.

So: keep them, label them unambiguously, and leave the de-duplication of the leaf
databases (which the audit proved carry no children) where it already succeeded.
"""
import sys, requests, time, json
sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"

# copies WITH nested content -> restore + relabel, do not delete
NESTED = [
    ("e90a9b14-e498-83f9-ae0b-810a94157b95", "⛔ SUPERSEDED — Executive Projects (nested content)"),
    ("116b71cd-76a4-4eef-a1d0-81068e3c6cf4", "⛔ SUPERSEDED — Organizations & Current Roles (nested content)"),
    ("44a69385-45ef-47ab-a787-aa6274472081", "⛔ SUPERSEDED — Medisun Completed Work Register (nested content)"),
]

print("=" * 88)
print("STEP 1 — restore + relabel the copies that hold nested content")
print("=" * 88)
for did, newtitle in NESTED:
    requests.patch(f"{BASE}/databases/{did}", headers=H, timeout=30, json={"in_trash": False})
    time.sleep(0.7)
    r = requests.patch(f"{BASE}/databases/{did}", headers=H, timeout=30,
                       json={"title": [{"type": "text", "text": {"content": newtitle}}]})
    g = requests.get(f"{BASE}/databases/{did}", headers=H, timeout=30)
    cur = "".join(x.get("plain_text", "") for x in g.json().get("title", [])) if g.status_code == 200 else "?"
    tr = g.json().get("in_trash") if g.status_code == 200 else "?"
    print(f"  {did[:8]}  rename={r.status_code}  in_trash={tr}")
    print(f"            -> {cur}")

print("\n" + "=" * 88)
print("STEP 2 — confirm the canonical tree is intact")
print("=" * 88)
canon = [
    ("9547910e-8975-44b8-b511-2108abfa0d11", "Executive Projects", 18),
    ("d3ff0c00-c629-43dc-b82c-06a28866fcb1", "Master Tasks & Commitments", 78),
    ("c20a9b14-e498-8333-b554-01413da172df", "Organizations & Current Roles", 9),
    ("8aca9b14-e498-8200-8d00-0149672c0a5f", "Medisun Completed Work Register", 27),
    ("c28d624e-b827-4065-b1fd-200cdf7dd561", "Prehospital & Aeromedical Evidence", 6),
    ("a5dfe5bd-c416-4f4c-b3e9-d6119279ad88", "🧠 Founder Evolution Diary", 10),
]
allok = True
for did, label, expect in canon:
    q = requests.post(f"{BASE}/databases/{did}/query", headers=H, json={"page_size": 100}, timeout=40)
    n = len(q.json().get("results", [])) if q.status_code == 200 else None
    ok = (n == expect)
    if not ok:
        allok = False
    print(f"  {label:<40} rows={str(n):<5} expected={expect:<4} {'OK' if ok else '!! CHECK'}")

print("\n" + "=" * 88)
print("STEP 3 — final live-database count")
print("=" * 88)


def search_all(f, cap=400):
    out, cur = [], None
    while len(out) < cap:
        b = {"page_size": 100, "sort": {"direction": "descending", "timestamp": "last_edited_time"}}
        if f:
            b["filter"] = {"value": f, "property": "object"}
        if cur:
            b["start_cursor"] = cur
        r = requests.post(f"{BASE}/search", headers=H, json=b, timeout=30)
        if r.status_code != 200:
            break
        d = r.json()
        out.extend(d.get("results", []))
        if not d.get("has_more"):
            break
        cur = d.get("next_cursor")
    return out


live = 0
for d in search_all("database"):
    g = requests.get(f"{BASE}/databases/{d['id']}", headers=H, timeout=30)
    if g.status_code == 200 and not g.json().get("in_trash"):
        live += 1
    time.sleep(0.1)
print(f"  live databases: {live}")
json.dump({"nested_kept": NESTED, "canonical": canon, "live_count": live, "all_canonical_ok": allok},
          open("/opt/data/notion_final_state.json", "w"), indent=1)
