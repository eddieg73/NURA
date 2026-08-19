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
CEO = "f2f6e8a6-6d99-4113-9604-1e8259fc1d83"

issue = {
    "title": "NUR-65: Google Sign-In (SSO) for Perfex + OpenEMR",
    "description": ("Founder 2026-08-02: Google Sign-In for BOTH apps. Skill: google-sso-perfex-openemr.\n"
                    "1) PERFEX (Tally fa200fb7): Google Login module — client ID/secret in .env 0600 "
                    "(GOOGLE_OAUTH_CLIENT_ID/SECRET), redirect https://pay.nuratech.ai/admin/authentication/"
                    "google_callback (match console exactly); test round-trip with 2 accounts.\n"
                    "2) OPENEMR (OpenEMR System Administrator 5e630b7b): OIDC provider config — client registration, "
                    "scopes openid email profile, callback via emr.nuratech.ai; keep local admin break-glass until "
                    "SSO verified for all staff; audit provider=google.\n"
                    "3) GOOGLE CONSOLE (founder drop): create OAuth web clients + consent screen in console.cloud."
                    "google.com (project nuratech-ai); provide client IDs/secrets + exact redirect URIs.\n"
                    "GATES: PHI never leaves apps (tokens authenticate only); SSO round-trip evidence per app; "
                    "founder supplies the console credentials."),
    "assigneeAgentId": CEO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-65 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
