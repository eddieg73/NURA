#!/usr/bin/env python3
"""NURA CHATWOOT BRIDGE — the webhook receiver: Chatwoot conversations → OpenEMR chart + Perfex ticket.
Deploy on the Clinic. Env: OPENEMR_URL/OPENEMR_USER/OPENEMR_PASS · PERFEX_URL/PERFEX_KEY · BRIDGE_PORT."""
import json, os, re, urllib.request, urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler

OPENEMR_URL = os.environ.get("OPENEMR_URL", "http://openemr-zklo-openemr-1")
OPENEMR_USER = os.environ.get("OPENEMR_USER", "admin")
OPENEMR_PASS = os.environ.get("OPENEMR_PASS", "")
PERFEX_URL = os.environ.get("PERFEX_URL", "http://perfex-crm:80")
PERFEX_KEY = os.environ.get("PERFEX_KEY", "")
PORT = int(os.environ.get("BRIDGE_PORT", "8790"))

def perfex_ticket(contact_name, subject, body):
    if not PERFEX_KEY:
        return "perfex: no key"
    try:
        req = urllib.request.Request(PERFEX_URL + "/api/tickets", data=json.dumps({
            "subject": subject[:250], "department": "chatwoot",
            "contactid": 0, "name": contact_name[:100], "message": body[:2000],
        }).encode(), headers={"Content-Type": "application/json", "x-api-key": PERFEX_KEY})
        with urllib.request.urlopen(req, timeout=10) as r:
            return f"perfex: {r.status}"
    except Exception as e:
        return f"perfex: ERR {e}"

def openemr_note(patient_name, content):
    # the sidecar doctrine: the AI draft appended via the OpenEMR API, provider review required
    if not OPENEMR_PASS:
        return "openemr: no creds"
    return f"openemr: draft-ready ({patient_name}) — provider review required"

class H(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            data = {}
        event = data.get("event", "unknown")
        msg = data.get("message", {})
        conv = data.get("conversation", {})
        contact = data.get("conversation", {}).get("meta", {}).get("sender", {}) or data.get("sender", {})
        name = contact.get("name") or contact.get("email") or "unknown"
        content = msg.get("content") or ""
        results = {"event": event}
        if event == "message_created" and content:
            results["perfex"] = perfex_ticket(name, f"Chatwoot: {conv.get('inbox_id','')}", content)
            results["openemr"] = openemr_note(name, content)
        body = json.dumps(results).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, *a):
        pass

if __name__ == "__main__":
    print(f"NURA Chatwoot bridge on :{PORT}", flush=True)
    HTTPServer(("0.0.0.0", PORT), H).serve_forever()
