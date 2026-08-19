import json, re, urllib.request, urllib.error

env = open("/opt/data/profiles/nura/.env").read()
tok = re.search(r"^NOTION_API_TOKEN=(.+)$", env, re.M).group(1).strip().strip('"').strip("'")

payload = {
    "parent": {"type": "workspace", "workspace": True},
    "properties": {"title": [{"text": {"content": "NURA Hub"}}]},
    "children": [
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "NURA OS Connector Hub"}}]}},
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Mirror + link surface for Hermes digests, board, vault, research. System of record stays Paperclip/Perfex/OpenEMR/Obsidian."}}]}},
    ],
}
req = urllib.request.Request("https://api.notion.com/v1/pages", method="POST",
                             headers={"Authorization": "Bearer " + tok, "Notion-Version": "2022-06-28",
                                      "Content-Type": "application/json"},
                             data=json.dumps(payload).encode())
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.loads(r.read().decode())
        print("create page ->", r.status, "| id:", d.get("id"), "| url:", d.get("url"))
except urllib.error.HTTPError as e:
    print("create ->", e.code, e.read().decode()[:250])
