"""Append CURRENT DEPLOYED CONFIG to the RADIOLOGY START HERE page."""
import json, subprocess, time, sys
sys.path.insert(0, "/opt/data/scripts")

PAGE = "3d6a9b14-e498-8194-bb79-d799c03c84d5"

def run(*a):
    return subprocess.run(["python3", "/opt/data/scripts/notion_client.py"] + list(a),
                          capture_output=True, text=True)
def t(x): return {"type": "text", "text": {"content": x}}
def h2(x): return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [t(x)]}}
def h3(x): return {"object": "block", "type": "heading_3", "heading_3": {"rich_text": [t(x)]}}
def para(x): return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [t(x)]}}
def bullet(x): return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [t(x)]}}
def callout(x, e="📌"): return {"object": "block", "type": "callout",
    "callout": {"rich_text": [t(x)], "icon": {"type": "emoji", "emoji": e}}}
def code(x): return {"object": "block", "type": "code",
    "code": {"rich_text": [{"type": "text", "text": {"content": x}}], "language": "plain text"}}

b = []
b.append(h2("📡 CURRENT DEPLOYED CONFIGURATION — verified 2026-09-10"))
b.append(callout("This section records what is ACTUALLY RUNNING today, discovered by live inspection of the fleet. It supersedes the target-state description above where the two differ. No credentials appear on this page.", "✅"))

b.append(h3("Fleet map — where each clinical service runs"))
b.append(code(
"""Public endpoint              -> Server            Host
pacs.nuratech.ai             -> clinic            72.61.71.211  (srv1441409)
chatwoot.nuratech.ai         -> clinic            72.61.71.211
carepilot.nuratech.ai        -> CarePilot origin  2.24.107.152  (srv1682494, Debian)
medisun-emr.nuratech.ai      -> lab               72.60.163.140 (srv1030183)
n8n.nuratech.ai              -> lab               72.60.163.140
pay.nuratech.ai              -> edge              195.35.32.113 (srv817449)
app.brawlerzbox.com          -> srv1863412        167.88.45.51
pay.garridoconsultingllc.com -> srv1863412        167.88.45.51"""))

b.append(h3("CLINIC (72.61.71.211) — primary imaging + EMR host"))
b.append(bullet("Orthanc PACS — container radris-stack-orthanc-1 (orthancteam/orthanc:latest-full)"))
b.append(bullet("  • AE title = RADRIS_PACS  ·  DICOM = 4242  ·  REST/UI = 8042  ·  API v30"))
b.append(bullet("  • DICOMweb ENABLED — QIDO-RS at /dicom-web/studies returns 200 (auth required)"))
b.append(bullet("  • Backend = PostgreSQL (orthanc-postgres). Storage dir /var/lib/orthanc/db"))
b.append(bullet("  • Modalities configured: NONE yet  ·  Studies stored: 0  ← Phase A/C not started"))
b.append(bullet("OHIF viewer — container ohif-viewer (ohif/viewer:latest) on :32791"))
b.append(bullet("Mirth / NextGen Connect (OIE fork) — mirth-oie46-mirth-engine-1, image nuratech/connect:4.6.0-nura.1"))
b.append(bullet("  • Ports: 6663→6661, 6669 (HL7 v2 MLLP), 8086→8080 (admin), 8445→8443 (TLS)"))
b.append(bullet("  • Admin REST reached on :8086 (OIE 4.6 API path differs from legacy Mirth)"))
b.append(bullet("OpenEMR — openemr-zklo-openemr-1 (openemr/openemr:latest) + openemr-zklo-mariadb-1"))
b.append(bullet("  • VERSION 8.2.0  ·  published on :32777→80  ·  compose at /docker/openemr-zklo/"))
b.append(bullet("  • Traefik-fronted (TRAEFIK_HOST=srv1441409.hstgr.cloud); DB user openemr, site dir 'default'"))
b.append(bullet("RadRIS app — radris-stack-radris-1 (radris/radris-app:latest) + nginx reverse proxy (80/443)"))
b.append(bullet("NURA RIS — nura-ris-web (nuratech/nura-ris:1.8) on :32790 + nura-ris-db (mariadb:10.11)"))
b.append(bullet("RadAI — nura-radai-registry (postgres:15) + nura-radai-orchestrator (deploy-orchestrator) on :8090"))
b.append(bullet("CarePilot API — carepilot-api:local, healthy, on :8100 (secondary to the CarePilot origin)"))
b.append(bullet("Also on clinic: hermes-gateway (8642), hermes-dashboard (9119), chatwoot (rails/sidekiq/redis)"))

b.append(h3("LAB (72.60.163.140) — FHIR backbone + automation"))
b.append(bullet("Medplum (FHIR R4) — medplum-server on :8103 + medplum-postgres-1 (pg16, 55432) + medplum-redis-1 (56379)"))
b.append(bullet("OHIF viewer — second instance on :8083"))
b.append(bullet("medisun-emr-bot — laravel.test + selenium/standalone-chromium + mysql:8.4 (EMR automation lane)"))
b.append(bullet("n8n — n8n:latest (hosted workflow lane); Dokploy + Traefik (80/443) manage deploys"))
b.append(bullet("Ollama — local model server on :11434 (12 models incl. med42, meditron, biomistral, nomic-embed-text)"))
b.append(callout("LAB IS THE BOTTLENECK: 8 vCPU / 32 GiB but 48 containers with no memory limits → load average ~99 and 94% CPU steal. Ollama inference hangs (HTTP 000 after 90s). Any imaging/ML work placed here will starve. Migration gated (NUR-104).", "⚠️"))

b.append(h3("EDGE (195.35.32.113) — CRM / payments"))
b.append(bullet("medisun-app (perfex-management:3.4.1) on 127.0.0.1:8098 + medisun-db (mysql:8.0) + medisun-cron"))
b.append(bullet("perfex-app (perfex-management:3.4.1) on 127.0.0.1:8099 + perfex-db (mysql:8.0) + perfex-cron"))
b.append(bullet("n8n instances (2). Serves pay.nuratech.ai (Perfex CRM). No PACS/EMR role."))

b.append(h3("srv1863412 (167.88.45.51) — Perfex CRM / payments host (HRT House account)"))
b.append(bullet("nginx + PHP 8.2-FPM + MySQL. Vhosts: app.brawlerzbox.com and pay.garridoconsultingllc.com"))
b.append(bullet("Databases: brawlerzbox (gym/client CRM) + payCRMDB (payments/leads, GoHighLevel-integrated)"))
b.append(bullet("NOT a PACS/EMR host. Confirmed by SSH hostkey (Ubuntu OpenSSH 9.6) — distinct from the CarePilot box (Debian OpenSSH 10.0)."))

b.append(h3("CarePilot origin — srv1682494 (2.24.107.152)"))
b.append(bullet("Laravel app (PHP 8.4.21), TLS cert CN=carepilot.nuratech.ai / SAN carepilot.cloud"))
b.append(bullet("Reachable but NOT yet accessible to ops: no authorized key/credential. Hosting account not yet identified.  ← OPEN ITEM"))

b.append(h3("Deltas vs. the target architecture above"))
b.append(bullet("1. Orthanc AE title is RADRIS_PACS — the plan specifies NURAEDGE01. Decide: rename to NURAEDGE01, or update the plan to RADRIS_PACS."))
b.append(bullet("2. No modality AE/IP allowlist is configured (DicomModalities empty) — Phase C is not done."))
b.append(bullet("3. DICOM 4242 and REST 8042 are bound to 0.0.0.0 (all interfaces). The design rule says they must stay on the imaging VLAN/VPN. ← HARDENING NEEDED"))
b.append(bullet("4. Mirth/OIE has no ThaiRIS MWL channel yet — Phase E not started."))
b.append(bullet("5. Postgres PACS index is present (radris-stack-db-1) but no studies have been stored (0 studies)."))
b.append(bullet("6. Backblaze B2 archive connector is not wired to the imaging stack yet."))
b.append(bullet("7. Enterprise PACS (MEDISUNPACS) is not built — only the clinic/local tier exists."))

blocks = b
for i in range(0, len(blocks), 90):
    out = run("append", PAGE, json.dumps(blocks[i:i+90]))
    try:
        n = len(json.loads(out.stdout).get("results", []))
    except Exception:
        n = "ERR " + out.stdout[:120]
    print(f"chunk {i//90+1}: {n} blocks appended")
time.sleep(1)
rb = run("children", PAGE)
print("page total blocks now:", len(json.loads(rb.stdout).get("results", [])))
