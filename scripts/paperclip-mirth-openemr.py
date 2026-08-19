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
MERIDIAN = "b2c4d576-1a4e-4f95-9b7f-1e94d2b8c1a3"

issue = {
    "title": "NUR-82: MIRTH <-> OPENEMR — deploy ADT/ORM channels + HL7 wiring",
    "description": ("Founder 2026-08-02: connect Mirth to OpenEMR.\n"
                    "STATE (verified): Mirth MCP lane built (mirth_status/channel deploy/HL7 send/logs via "
                    ":8081/api; wrapper scripts/mirth-mcp-wrapper.sh) but MIRTH_USER/MIRTH_PASS NOT in .env; "
                    "channels designed + saved (imaging-stack/mirth-channels/: channel_adt.json, channel_orm.json, "
                    "channel_adt_poller.xml + payloads); design doc openemr-hl7-forwarding.md; OpenEMR lane in "
                    "mock mode (OAuth pending).\n"
                    "MERIDIAN EXECUTE:\n"
                    "1) DEPLOY channels on Mirth Connect (host 1441409): ADT (A01/A02/A03/A08 patient "
                    "demographics OpenEMR->Mirth->consumers) + ORM (orders -> ThaiRIS worklist) + ORU (results "
                    "back to OpenEMR) + ADT poller (verify file/DB poller vs listener mode).\n"
                    "2) CONFIGURE OpenEMR side: HL7 module enabled (OpenEMR native hl7 or file-based via "
                    "document root), listening port, site id; map OpenEMR facility/physician IDs in channel "
                    "transformers (segment maps, PID->OpenEMR patient match by MRN).\n"
                    "3) TEST: send synthetic ADT A01 (test patient) + ORM order -> confirm Mirth received + "
                    "OpenEMR created/updated patient; verify via Mirth logs + OpenEMR UI/API; evidence on this "
                    "issue (channel stats, message IDs).\n"
                    "4) SECURITY: PHI stays inside 1441409 (Mirth+OpenEMR co-located); Mirth admin on "
                    "localhost; no PHI to external lanes.\n"
                    "BLOCKERS: MIRTH_USER/MIRTH_PASS drop; OpenEMR OAuth drop (for API verification); Docker "
                    "ruling NUR-68 (host container access). Sequence after NUR-68."),
    "assigneeAgentId": MERIDIAN, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-82 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
