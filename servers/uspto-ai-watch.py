#!/usr/bin/env python3
"""USPTO AI-patent watch — queries Google Patents for filings similar to NURA's stack.
Output: data/patent-watch.json + prints newest results. Lane verified 2026-08-02 (PatentsView DNS dead; Google Patents XHR works).
"""
import json, time, urllib.request, urllib.parse
from pathlib import Path

QUERIES = [
    "ambient clinical scribe AI",
    "clinical AI documentation HIPAA",
    "medical voice assistant healthcare AI",
    "AI receptionist appointment scheduling healthcare",
    "FHIR AI coding",
    "medical LLM documentation",
    "healthcare agent workflow automation",
    "telehealth AI dialer",
    "HCC RAF risk adjustment coding AI",
    "patient communication AI platform",
]

def fetch(q):
    gurl = "https://patents.google.com/xhr/query?url=q%3D" + urllib.parse.quote(q) + "&exp="
    req = urllib.request.Request(gurl, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def main():
    seen, rows = {}, []
    for q in QUERIES:
        try:
            gd = fetch(q)
            res = gd.get("results", {}).get("cluster", [{}])[0].get("result", [])
            for r0 in res[:5]:
                p = r0.get("patent", {})
                pid = p.get("publication_number", "")
                if not pid or pid in seen:
                    continue
                seen[pid] = True
                rows.append({"number": pid, "title": (p.get("title") or "")[:110],
                             "assignee": (p.get("assignee") or "")[:60],
                             "date": p.get("publication_date", "?")[:10],
                             "query": q, "url": "https://patents.google.com/patent/" + pid})
        except Exception as e:
            print("query err:", q, str(e)[:80])
        time.sleep(0.7)
    rows.sort(key=lambda x: x["date"], reverse=True)
    Path("/opt/data/profiles/nura/data/patent-watch.json").write_text(json.dumps({"updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "count": len(rows), "patents": rows}, indent=1))
    print("patents found:", len(rows))
    for r0 in rows[:12]:
        print("-", r0["date"], "|", r0["number"], "|", r0["title"])

if __name__ == "__main__":
    main()
