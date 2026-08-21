#!/usr/bin/env python3
"""The LVNV/Resurgent litigation tracker — the CourtListener sweep.
The silent when no NEW cases; the alert on the new dockets/opinions mentioning LVNV or Resurgent.
The state file remembers the seen IDs so only the NEW surface.
"""
import json
import os
import sys
import urllib.parse
import urllib.request

STATE = "/opt/data/profiles/nura/cron/lvnv-tracker.state"
OUT = "/opt/data/Obsidian Vault/NURA-OS/Legal/LVNV-Litigation-Log.md"

def fetch(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "NURA-Hermes/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def main():
    seen = set()
    if os.path.exists(STATE):
        seen = set(json.load(open(STATE)))

    new_items = []
    for q in ["LVNV Funding", "Resurgent Capital"]:
        u = ("https://www.courtlistener.com/api/rest/v4/search/"
             f"?q={urllib.parse.quote(q)}&type=o&order_by=dateFiled%20desc")
        try:
            d = fetch(u)
            for r in d.get("results", [])[:12]:
                oid = str(r.get("id"))
                if oid in seen:
                    continue
                # The keep only the recent (the 2026)
                date = str(r.get("dateFiled") or r.get("date_created") or "")[:7]
                if date < "2026":
                    continue
                name = r.get("caseName") or r.get("case_name") or r.get("name", "?")
                court = r.get("court") or r.get("court_id", "?")
                new_items.append(f"{date} | {name} | {court} | courtlistener.com{str(r.get('absolute_url') or '')}")
                seen.add(oid)
        except Exception as e:
            print(f"[warn] {q}: {e}", file=sys.stderr)

    if new_items:
        json.dump(list(seen), open(STATE, "w"))
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with open(OUT, "a") as f:
            for it in new_items:
                f.write(f"- {it}\n")
        print("⚖️ NEW LVNV/RESURGENT LITIGATION: " + "; ".join(new_items[:2]))
    # else silent — no new cases

if __name__ == "__main__":
    main()
