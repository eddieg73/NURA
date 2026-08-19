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

NAMES = {
    "f2f6e8a6-6d99-4113-9604-1e8259fc1d83": "Atlas",          # CEO
    "0f81f292-5eea-4c6d-b64b-10b3345d29dd": "Orion",          # CTO
    "084cd44f-6570-4370-b8f0-fe66ec8b8baf": "Iris",           # CMO
    "fd71784f-fd2": "Midas",                                   # RCM Billing Lead / CFO
    "c5c0e478-cf2": "Nova",                                    # Customer Success
    "5fe33426-cf1": "Harmony",                                 # HR Ops
    "1e6eb308-19f": "Sentinel",                                # Infrastructure SRE
    "7cb8ee83-aca": "Helm",                                    # Docker Platform
    "0de3968c-edc": "Relay",                                   # GoHighLevel
    "5bbe99fe-bdb": "Beacon",                                  # Mobile Release/Store
    "f0550226-f05": "Pixel",                                   # Doximity Flutter Lead
    "e97ce372-ed4": "Forge",                                   # Doximity Backend
    "ff52997d-6b4": "Pulse",                                   # Wearables/Bluetooth
    "e4a5c397-665": "Weaver",                                  # Integrations Specialist
    "c454a3cb-351": "Canvas",                                  # Flutter Mobile Lead
    "6f0816a7-1bb": "Vigil",                                   # Compliance SecOps
    "b2c4d576-cc8": "Meridian",                                # NextGen Mirth Dev
    "fa200fb7-6520-4553-ad62-701b6c0febd5": "Tally",           # Perfex CRM Developer
    "e073d73b-d8f0-4044-9b17-c96144ca18bf": "Florence",        # OpenEMR Concierge Dev
    "877154cd-fffc-49e9-a6f2-fd60b8ed906a": "Loom",            # Workflow Automation Dev
    "0a57c77a-59f3-4575-8f89-84bd96c43cf7": "Frame",           # RIS/PACS Admin
    "973f42d4-18b2-4c89-b1c2-82c3680c84fd": "Bridge",          # MCP Integrations Dev
    "bc49f6db-433b-418b-b8f1-c923f59be16c": "Meridian 2",      # EMR Integrations Dev (rename pending dedupe)
    "32bdda92-e393-4311-bdf2-3a4d4346ee2c": "Echo",            # Twilio & VoIP Engineer
    "b327bcaf-c5eb-4fc1-bc94-3c30669145ab": "Ink",             # Documo & Fax Engineer
    "1f0c5310-7e8d-48eb-842e-0e9ca2651dc5": "Nexus",           # App Integrator
    "8112eff3-e59f-4ffd-9c14-4c526aef543b": "Reel",            # NURA Media Agent
}

ok = fail = 0
for aid, name in NAMES.items():
    try:
        req = urllib.request.Request(base + f"/api/agents/{aid}",
                                     data=json.dumps({"name": name}).encode(),
                                     headers=hdr, method="PATCH")
        with urllib.request.urlopen(req, timeout=8) as r:
            d = json.loads(r.read())
            got = d.get("name", "?")
            ok += 1 if got == name else 0
            print(f"{ok}. {name} <- {got}")
    except Exception as e:
        fail += 1
        print(f"FAIL {aid}: {str(e)[:80]}")
print(f"RENAMED {ok}/{len(NAMES)} (fail {fail})")
