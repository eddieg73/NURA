import json, urllib.request, urllib.error, re

def envval(name):
    env = open("/opt/data/profiles/nura/.env").read()
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

key = envval("API_SERVER_KEY")
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key, "Authorization": "Bearer " + key}
CID = "999ff375-6128-41cf-b6c8-06b98673a29b"
CTO = "c454a3cb-3516-4046-b60f-03e0b1bea002"

issue = {
    "title": "NUR-114: FOUNDER MATERIAL — IP portfolio, 2026 build progression, device/telemetry lane",
    "description": ("FULL MATERIAL from founder (2026-08-02). CTO review + maintain evidence trail per claim.\n"
                    "=== 1. IP PORTFOLIO ===\n"
                    "- Provisional FILED 2025-06-16: 'NURA Agentic Medical Intelligence Framework' (Nura Tech AI, "
                    "818 Chestnut St Clearwater FL). 22 claims. Vault: NURA-OS/IP/ (Provisional-Patent-2025-06-16.md, "
                    "NURA-Agentic-Framework-Claims.md — condensed digest, NOT attorney substitute).\n"
                    "- Continuation NEEDED for 2026 build deltas: self-hosted offline-first (vs Azure claims), "
                    "OpenEMR/Perfex/Mirth (vs MEDBASE), WENO EPCS (vs DrFirst), NMI (vs FORWARD), telemetry CDS "
                    "(NEWS2 engine + provider gate), device lanes (IHE PCD/11073 SDC/BLE), NURA Capsule hardware "
                    "(embodiment of claims 14-15).\n"
                    "- DISREGARDED (do not file/cite): AHMAS + AHMIS generated drafts (Optimus/Neuralink/ROS filler, "
                    "inflated metrics).\n"
                    "- NURA Capsule/Tag hardware banked: nRF52840 BLE capsule, BOM + drawing spec — continuation-"
                    "worthy for BLE proximity/vitals claims.\n"
                    "- Patent watch LIVE: uspto-ai-patent-watch skill + script uspto-ai-watch.py (49 patents first "
                    "sweep; DIRECT hit US12525343B2 AI routing agent overlaps our routing concept). 6 claim-protection "
                    "lanes added; quarterly sweeps; DIRECT hits -> attorney before building in that space.\n"
                    "=== 2. BUILD STATE PER CLAIM (evidence matrix, vault IP/NURA-Agentic-Framework-Claims.md) ===\n"
                    "- Implemented (original Azure/LangGraph build era): claims 1-8, 11-13, 17-22 core. "
                    "PARTIAL in current self-hosted build: MCP/Hermes orchestration + OpenEMR/Perfex + Mirth live; "
                    "Unity avatar = app spec v2 (SCOPE FREEZE, unbuilt).\n"
                    "- UNBUILT: claim 9/14/15 (BLE triggers + proximity) — NUR-112 device lane Phase 2; "
                    "claim 10 (cross-device session) partial.\n"
                    "- NEW unclaimed: telemetry-cds-engine.py (NEWS2, verified 13/20 synthetic case), "
                    "provider-labs ingest, medical-imaging-vision.py, Gemini in-house lane, n8n webhook live.\n"
                    "=== 3. DEVICE + TELEMETRY (NUR-112 referenced) ===\n"
                    "- medical-device-connectivity skill: IHE PCD DEC (ORU^R01 + 11073 MDC) -> Mirth -> OpenEMR; "
                    "IEEE 11073 SDC/OpenICE for OR/ICU; BLE layer (11073-20601 + app flutter_blue_plus, offline-first).\n"
                    "- telemetry-cds-engine.py: NEWS2 scoring + device red flags + provider gate. Run: "
                    "python3 scripts/telemetry-cds-engine.py.\n"
                    "- SAFETY: no device auto-actions; validation before chart writes; clinical-grade vs "
                    "wellness-grade labeling; PHI Clinic-local.\n"
                    "=== 4. CTO ACTIONS ===\n"
                    "1) Review claims matrix; maintain per-claim implementation evidence (prosecution readiness).\n"
                    "2) Prep continuation notes for attorney (deltas above) before public disclosure of new features.\n"
                    "3) NUR-112 device inventory at 3 clinics (N Miami/Little Haiti/Ft Lauderdale) = unlock.\n"
                    "4) Quarterly patent-watch sweeps; DIRECT overlaps -> attorney + board comment.\n"
                    "5) Keep vault IP/ folder as single source of truth; no fabricated claims/metrics anywhere."),
    "assigneeAgentId": CTO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-114 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
