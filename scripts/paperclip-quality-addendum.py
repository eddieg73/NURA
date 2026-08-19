import json, urllib.request, urllib.error

def env_file(path, names):
    try:
        for line in open(path):
            for n in names:
                if line.startswith(n + "="):
                    return line.strip().split("=", 1)[1].strip("'\"")
    except OSError:
        pass
    return None

key = env_file("/opt/data/paperclip-runtime/mcp.env", ["PAPERCLIP_API_KEY", "API_KEY"])
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key or "", "Authorization": "Bearer " + (key or "")}
CID = "999ff375-6128-41cf-b6c8-06b98673a29b"
FLORENCE = "e073d73b-d8f0-4044-9b17-c96144ca18bf"

issue = {
    "title": "NUR-109: MY2026 quality playbook — operationalize Medisun 62 addendum (CarePilot + TRC + Solis fax feed)",
    "description": ("Founder 2026-08-02 addendum archived: /opt/data/Obsidian Vault/NURA-OS/MY2026-Quality-"
                    "Addendum.md; playbook patched into hedis-quality-measures.\n"
                    "FLORENCE EXECUTE (population health owner):\n"
                    "1) CAREPILOT: map the 5 problem→solution sets into gap lists + reminder tabs (AWV/"
                    "screening at check-in, recall campaigns, teleretinal, FIT/Cologuard, nurse BP re-"
                    "checks); track the 4 measures (Older Adults, Eye Exams, Colorectal, BP).\n"
                    "2) TRC: 2-day post-discharge milestone tracker (MSO command center) + CPT II 1111F + "
                    "TCM 99495/99496 on post-discharge encounters; ADT feeds via Mirth (NUR-82).\n"
                    "3) SOLIS SUPPLEMENTAL FEED: build the parallel fax lane — Documo outbound fax of "
                    "billing logs + CPT II records to hedisfax@solishealthplans.com (bypass Mirra drops); "
                    "verify delivery status per batch.\n"
                    "4) CHRONIC PROGRAMS: RPM/CCM flags in OpenEMR (CHF weight/BP, CHD post-MI, COPD/"
                    "spiro/pulse-ox, CoCM PHQ-9/GAD-7 — 53+ pts).\n"
                    "5) SDOH: intake screening → Z-codes (Z59.4x, Z59.82) on claims (SNS-E tie, RAF "
                    "uplift).\n"
                    "Evidence: first fax batch receipt + CarePilot gap deltas on this issue."),
    "assigneeAgentId": FLORENCE, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-109 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
