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
MERIDIAN = "b2c4d576-cc8c-4f45-bcdd-83b16055975d"

issue = {
    "title": "NUR-63: MERIDIAN — NextGen Mirth Connect: the Docker app is READY, build the channels",
    "description": ("Meridian (NextGen Mirth Integration Developer): the Mirth Docker app EXISTS and is ready. "
                    "Evidence: /opt/data/mirth-docker-stack/docker-compose.yml = redis + qdrant + postgres:16 + "
                    "nextgenhealthcare/connect:4.5.2-jdk (the official NextGen Connect image) on :8081 "
                    "(env MIRTH_HTTP_PORT, collision-guarded vs OpenEMR :8080). Channel seeds already in repo: "
                    "channels/channel_adt.json + channel_orm.json + ADT/ORM XML payloads.\n\n"
                    "BUILD:\n"
                    "1) Deploy on 1441409 host: cd /opt/data/mirth-docker-stack && docker compose up -d; verify "
                    "curl -fs http://127.0.0.1:8081 (expect 200) + REST API login (hermes-mirth-connect skill).\n"
                    "2) Channels (per NUR-61/49): ORM^O01 orders->ThaiRIS MWL · ORU^R01 results->OpenEMR · "
                    "ADT^A04/A08 demographics->ThaiRIS/OpenEMR (seeds exist) · DFT^P03 fee sheets->Perfex bridge.\n"
                    "3) Validate with hermes-hl7-simulator (synthetic ADT/ORM/ORU) BEFORE go-live; dead-letter + "
                    "retries + idempotency; channel XML .bak before edits.\n"
                    "4) Coordinate: Frame (RIS MWL), Florence (OpenEMR), Tally (Perfex invoices), Meridian-2 "
                    "(EMR integrations — dedupe decision pending CEO).\n"
                    "Report channel status + test results on this issue. Hermes holds the skills "
                    "(hermes-mirth-connect, hermes-hl7-simulator)."),
    "assigneeAgentId": MERIDIAN, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-63 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
