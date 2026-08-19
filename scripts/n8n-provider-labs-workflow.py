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

nb = env_file("/opt/data/profiles/nura/.env", ["N8N_BASE_URL"]) or "https://n8n.nuratech.ai"
nk = env_file("/opt/data/profiles/nura/.env", ["N8N_API_KEY"])

workflow = {
    "name": "Provider Labs Ingest Webhook",
    "nodes": [
        {"parameters": {"path": "provider-labs-ingest", "responseMode": "responseNode", "options": {}},
         "id": "webhook-1", "name": "Webhook", "type": "n8n-nodes-base.webhook",
         "typeVersion": 2, "position": [0, 0], "webhookId": "provider-labs-ingest"},
        {"parameters": {"command": "python3 /opt/data/profiles/nura/scripts/provider-labs-ingest.py --all --queue 2>&1 | head -c 1500",
                         "executeOnce": False},
         "id": "cmd-1", "name": "Run Ingest", "type": "n8n-nodes-base.executeCommand",
         "typeVersion": 1, "position": [200, 0]},
        {"parameters": {"options": {}},
         "id": "resp-1", "name": "Respond to Webhook", "type": "n8n-nodes-base.respondToWebhook",
         "typeVersion": 1, "position": [400, 0]}
    ],
    "connections": {
        "Webhook": {"main": [[{"node": "Run Ingest", "type": "main", "index": 0}]]},
        "Run Ingest": {"main": [[{"node": "Respond to Webhook", "type": "main", "index": 0}]]}
    },
    "settings": {"executionOrder": "v1"},
    "active": True,
    "tags": [{"name": "provider-labs"}],
}

try:
    req = urllib.request.Request(f"{nb}/api/v1/workflows", data=json.dumps(workflow).encode(),
                                 headers={"X-N8N-API-KEY": nk, "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read())
        print("WORKFLOW ->", r.status, d.get("id"), "|", d.get("name"), "| active:", d.get("active"))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:250])
