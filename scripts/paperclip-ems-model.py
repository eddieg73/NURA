import json, re, urllib.request, urllib.error

def envval(name):
    env = open("/opt/data/profiles/nura/.env").read()
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

key = envval("API_SERVER_KEY")
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key, "Authorization": "Bearer " + key}
issue_id = "fe997964-f356-417b-8b64-46160a17374b"

body = ("FOUNDER CORRECTION — BUSINESS MODEL (2026-08-02, supersedes earlier framing):\n"
        "NURA EMS is PARTNERSHIP-FIRST: we do NOT displace local EMS/fire — we AUGMENT them under MOU. "
        "We provide the NP or PA + the ambulance OR fly car (ALS SUV quick-response vehicle).\n"
        "Partners: local EMS agencies · fire depts · hospitals.\n"
        "FOUNDER = THE PA PROVIDER: Eddie Garrido, PA-C/EMT-P (FL Paramedic PMD13383) fills the MIH clinical seat. "
        "Org design consequence: the company builds around the founder-provider — President/Ops/Fleet support HIS "
        "clinical operation; the Clinical Lead role becomes backup/second provider, not the lead.\n"
        "Fly car joins the truck spec (same tech stack). Texas 911 outbid = separate later track.")
try:
    req = urllib.request.Request(base + f"/api/issues/{issue_id}/comments",
                                 data=json.dumps({"body": body}).encode(), headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("model correction comment ->", r.status)
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
