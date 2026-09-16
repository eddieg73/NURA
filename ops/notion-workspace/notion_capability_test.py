"""Test whether the integration can (a) create a page at workspace root and (b) move a database's parent."""
import sys, requests, json
sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"

print("=" * 80)
print("TEST A — create a page at WORKSPACE ROOT")
print("=" * 80)
r = requests.post(f"{BASE}/pages", headers=H, timeout=30, json={
    "parent": {"type": "workspace", "workspace": True},
    "properties": {"title": [{"text": {"content": "__probe_workspace_root__"}}]},
    "icon": {"type": "emoji", "emoji": "🧪"},
})
print(f"  status {r.status_code}")
print(f"  {r.text[:400]}")
probe_id = None
if r.status_code == 200:
    probe_id = r.json()["id"]
    print(f"  created {probe_id}")

print("\n" + "=" * 80)
print("TEST B — move a database to a new parent page")
print("=" * 80)
# do this against the dead 0-row Flutter board
DEAD = "2c2be702-682d-473a-ba55-d5520e1dafee"
PARENT = "613e14da-104a-470e-af85-799d66eb8ebc"  # Executive Command Center
r2 = requests.patch(f"{BASE}/databases/{DEAD}", headers=H, timeout=30,
                    json={"parent": {"type": "page_id", "page_id": PARENT}})
print(f"  status {r2.status_code}")
print(f"  {r2.text[:400]}")

print("\n" + "=" * 80)
print("TEST C — rename a database title")
print("=" * 80)
r3 = requests.patch(f"{BASE}/databases/{DEAD}", headers=H, timeout=30,
                    json={"title": [{"type": "text", "text": {"content": "__probe_rename__"}}]})
print(f"  status {r3.status_code}")
print(f"  {r3.text[:200]}")

print("\n" + "=" * 80)
print("CLEANUP")
print("=" * 80)
if probe_id:
    rd = requests.patch(f"{BASE}/pages/{probe_id}", headers=H, timeout=30,
                        json={"in_trash": True})
    print(f"  probe page trashed: {rd.status_code}")
if r3.status_code == 200:
    r4 = requests.patch(f"{BASE}/databases/{DEAD}", headers=H, timeout=30,
                        json={"title": [{"type": "text", "text": {"content": "Flutter Delivery Board"}}]})
    print(f"  title restored: {r4.status_code}")
