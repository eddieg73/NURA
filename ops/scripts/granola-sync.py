#!/usr/bin/env python3
"""The Granola sync — the daily pull: the new notes → the vault → the Notion mirror.
Silent when the key's the missing or the nothing's the new. The founder's the key gate applies.
"""
import os

def main():
    key_file = "/opt/data/profiles/nura/home/.config/granola/.env"
    key = ""
    for l in open(key_file):
        if l.startswith("GRANOLA_API_KEY="):
            key = l.split("=", 1)[1].strip().strip('"')
            break
    if not key:
        return  # the silent — the key gate's the still open (the founder's the desktop app)
    # The pull via the Granola public API (the https://public-api.granola.ai/v1)
    import json, urllib.request
    req = urllib.request.Request("https://public-api.granola.ai/v1/notes",
                                 headers={"Authorization": f"Bearer {key}",
                                          "User-Agent": "NURA-Hermes/1.0"})
    try:
        d = json.loads(urllib.request.urlopen(req, timeout=20).read())
        notes = d.get("notes", d if isinstance(d, list) else [])
    except Exception:
        return  # the silent — the transient
    if not notes:
        return
    # The stage the new notes for the importer (the vault-first, the Notion-mirror after)
    os.makedirs("/opt/data/profiles/nura/cron/granola-queue", exist_ok=True)
    for n in notes[:10]:
        nid = n.get("id", "n")
        p = f"/opt/data/profiles/nura/cron/granola-queue/{nid}.json"
        if not os.path.exists(p):
            open(p, "w").write(json.dumps(n))
    print(f"granola: {len(notes[:10])} new notes staged for the importer")

if __name__ == "__main__":
    main()
