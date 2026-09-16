"""Resolve the remaining unknowns: skill registries, empty DBs, loose root DBs, odd DBs."""
import sys, requests
sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"


def probe(db_id, label):
    r = requests.post(f"{BASE}/databases/{db_id}/query", headers=H,
                      json={"page_size": 100}, timeout=30)
    if r.status_code != 200:
        print(f"  {label:<46} QUERY {r.status_code}: {r.text[:120]}")
        return None
    d = r.json()
    n = len(d.get("results", []))
    more = d.get("has_more")
    print(f"  {label:<46} rows={n}{'+' if more else ''}")
    return n


print("=" * 88)
print("SKILL REGISTRIES (3 copies, all under page 3cca9b14)")
print("=" * 88)
for sid, lbl in [("70986afe-0c3c-4954-9644-ac2525d53b15", "Skill Registry #1"),
                 ("10cf4335-b217-4a49-b6d0-a567fe3df2cd", "Skill Registry #2"),
                 ("ee46997c-71ff-4fa7-8ce4-bcee1ed0b9e6", "Skill Registry T2")]:
    probe(sid, lbl)

print("\n" + "=" * 88)
print("EMPTY / DEAD DATABASES")
print("=" * 88)
for sid, lbl in [("2c2be702-682d-473a-ba55-d5520e1dafee", "Flutter Delivery Board (dead)"),
                 ("22260907-f18c-4768-95de-052942bdb055", "Flutter Delivery Board — Active"),
                 ("641a9b14-e498-8304-91ea-81f3f1dfe2cf", "Time Tracking (A)"),
                 ("77a2851a-bf77-4992-8426-32fc18143850", "Time Tracking (B)"),
                 ("3cda9b14-e498-811d-af0c-ecf7bfed5937", "My links"),
                 ("841c0ce6-5aa0-4bfc-a1ae-93ec72d5b2a9", "Software & Tools — Add List"),
                 ("3cca9b14-e498-800d-83db-f6bd7a245636", "Claude Tasks")]:
    probe(sid, lbl)

print("\n" + "=" * 88)
print("ODD / NON-ENGLISH DATABASES")
print("=" * 88)
for sid, lbl in [("d13a9b14-e498-82d1-831e-012fcd04f7fb", "Aamuyhteenvedon keskus (Finnish)"),
                 ("14ea9b14-e498-8274-be6a-010d75d32506", "Posts"),
                 ("733a9b14-e498-824a-9d1a-01988da721a5", "Social Channels"),
                 ("81ca9b14-e498-82d0-85d4-01ee88a1e32e", "Agent's Log")]:
    probe(sid, lbl)

print("\n" + "=" * 88)
print("LOOSE WORKSPACE-ROOT DATABASES")
print("=" * 88)
for sid, lbl in [("384a9b14-e498-8041-a6cf-fc6849b4fc40", "To Do List DB"),
                 ("d3da9b14-e498-82df-b0d8-014512d331ec", "People"),
                 ("3cda9b14-e498-800d-83db-f6bd7a245636", "Claude Tasks (root)")]:
    probe(sid, lbl)

print("\n" + "=" * 88)
print("THE TWO COMPETING EXECUTIVE COMMAND CENTERS")
print("=" * 88)
for pid, lbl in [("613e14da-104a-470e-af85-799d66eb8ebc", "Executive Command Center (LIVE?)"),
                 ("3d6a9b14-e498-81e2-bab7-fc22b42127e9", "Archive — backup 2026-09-09")]:
    r = requests.get(f"{BASE}/pages/{pid}", headers=H, timeout=30)
    if r.status_code == 200:
        d = r.json()
        title = ""
        for v in (d.get("properties") or {}).values():
            if isinstance(v, dict) and v.get("type") == "title":
                title = "".join(x.get("plain_text", "") for x in v.get("title", []))
        print(f"  {lbl}")
        print(f"     id={pid}")
        print(f"     title={title!r}  in_trash={d.get('in_trash')}")
        print(f"     created={d.get('created_time','')[:10]}  edited={d.get('last_edited_time','')[:10]}")
        print(f"     parent={(d.get('parent') or {}).get('type')}")
    else:
        print(f"  {lbl}: GET {r.status_code}")
