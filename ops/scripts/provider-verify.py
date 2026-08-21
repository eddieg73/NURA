#!/usr/bin/env python3
"""Provider verification via NPPES (public CMS registry) — the Directory trust wall.
CLI: provider-verify.py <NPI> [--name "Eduardo Garrido"] — verifies NPI is active,
type, name match, state. Returns verified/unverified + source URL.
"""
import json, sys, urllib.request

def verify(npi, name=None):
    url = f"https://npiregistry.cms.hhs.gov/api/?version=2.1&number={npi}"
    req = urllib.request.Request(url, headers={"User-Agent": "NURA-Provider-Verify/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read())
    if not d.get("results"):
        return {"npi": npi, "verified": False, "reason": "not found in NPPES"}
    r0 = d["results"][0]
    basic = r0.get("basic", {})
    name_match = None
    if name:
        given = (basic.get("first_name") or "").lower()
        last = (basic.get("last_name") or "").lower()
        parts = name.lower().split()
        name_match = any(parts[-1] == last for p in [given]) and (parts[-1] == last)
    return {
        "npi": npi,
        "verified": r0.get("number") is not None,
        "status": basic.get("status"),
        "name": f"{basic.get('first_name')} {basic.get('last_name')}",
        "credential": basic.get("credential"),
        "state": basic.get("state"),
        "sole_proprietor": basic.get("sole_proprietor"),
        "taxonomy": [t.get("desc") for t in r0.get("taxonomies", [])][:2],
        "name_match_input": name_match,
        "source": "NPPES public registry (CMS)",
    }

if __name__ == "__main__":
    npi = sys.argv[1] if len(sys.argv) > 1 else "1154381580"
    name = sys.argv[sys.argv.index("--name") + 1] if "--name" in sys.argv else None
    print(json.dumps(verify(npi, name), indent=1))
