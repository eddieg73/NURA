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
CTO = "c454a3cb-3516-4046-b60f-03e0b1bea002"

issue = {
    "title": "NUR-104: Sovereign stack sequence — Mattermost deploy + vLLM local lane on Lab (air-gap milestone)",
    "description": ("Founder 2026-08-02 one-sheet archived: /opt/data/Obsidian Vault/NURA-OS/Sovereign-Stack-"
                    "OneSheet.md. Map verified: NPM/Paperclip/n8n/MCP/Qdrant/Redis/OpenEMR = LIVE; "
                    "PostgreSQL = NUR-103; Mattermost/vLLM/MeshCentral/AgentZero/HA/Media = NOT deployed.\n"
                    "CTO SEQUENCE:\n"
                    "1) MATTERMOST (priority — human-in-the-loop approvals/alerts per operator charter): "
                    "deploy on 1441409 (docker, localhost-only, TLS via NPM), create approval channels "
                    "(clinical-approvals, ops-alerts), wire Hermes alert/approval routing. Evidence: "
                    "channel + first alert on this issue.\n"
                    "2) VLLM LOCAL LANE (air-gap milestone): Lab 1030183 — vLLM serving quantized "
                    "Llama/MedGemma (serving-llms-vllm skill); local embeddings already live (fastembed "
                    "384d); goal: PHI-capable reasoning WITHOUT cloud. Honest note: today reasoning = "
                    "cloud DeepSeek/Gemini (NON-PHI only); air-gap is a staged migration, not a switch.\n"
                    "3) OPTIONAL BACKLOG: MeshCentral (OOB admin), Agent Zero (skip — Paperclip covers), "
                    "Home Assistant, media/Tandoor (non-clinical).\n"
                    "Evidence per deliverable required."),
    "assigneeAgentId": CTO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-104 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
