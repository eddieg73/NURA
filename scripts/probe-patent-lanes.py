import json, urllib.request, urllib.parse, time

def q(base, params):
    url = base + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "NURA-PatentWatch/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

# Probe 1: PatentsView API (official USPTO data partner)
try:
    query = {"_text_any": {"patent_abstract": ["clinical AI documentation"]}}
    d = q("https://search.patentsview.org/api/v1/patent/",
          {"q": json.dumps(query), "f": json.dumps(["patent_id", "patent_title", "patent_date"]),
           "o": json.dumps({"patent_date": "desc"}), "s": "3"})
    pats = d.get("patents", [])
    print("PatentsView results:", len(pats))
    for p in pats[:3]:
        print("-", p.get("patent_id"), "|", p.get("patent_date"), "|", (p.get("patent_title") or "")[:70])
except Exception as e:
    print("PatentsView ERR:", str(e)[:150])

time.sleep(1)
# Probe 2: Google Patents page fetch (fallback lane)
try:
    gurl = "https://patents.google.com/xhr/query?url=q%3D" + urllib.parse.quote("clinical AI scribe") + "&exp="
    req = urllib.request.Request(gurl, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        gd = json.loads(r.read())
    res = gd.get("results", {}).get("cluster", [{}])[0].get("result", [])
    print("Google Patents results:", len(res))
    for r0 in res[:3]:
        print("-", r0.get("patent", {}).get("publication_number"), "|", (r0.get("patent", {}).get("title") or "")[:70])
except Exception as e:
    print("GooglePatents ERR:", str(e)[:150])
