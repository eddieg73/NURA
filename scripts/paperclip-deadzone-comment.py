import json, re, urllib.request, urllib.error

def envval(name):
    env = open("/opt/data/profiles/nura/.env").read()
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

key = envval("API_SERVER_KEY")
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key, "Authorization": "Bearer " + key}
issue_id = "49b440e3-c2e8-4426-a7d2-c1835344d0bd"

body = ("FOUNDER-ADDED SPEC (2026-08-02, from his Colibrì research):\n"
        "- Target hardware: modest CPU + 25GB RAM + 1GB/s virtual NVMe — that is the SPEC for the demo box.\n"
        "- Model: GLM-5.2 = 744B params / 1.5TB FP16; Colibrì runs the INT4 package (~370GB on disk).\n"
        "- Mechanism: MoE expert streaming — only the 8+1 active experts per token load into RAM; single C file "
        "expert-selection code, minimal deps.\n"
        "- Trade-off acknowledged: steep speed penalty = offline/batch tier, never real-time chat.\n"
        "Requirement added: the demo box must have >=25GB RAM + NVMe (1GB/s class). If no clinic machine qualifies, "
        "the Lab (32GB RAM) is the fallback demo box; OLMoE 7B remains the small-box first test.")
try:
    req = urllib.request.Request(base + f"/api/issues/{issue_id}/comments",
                                 data=json.dumps({"body": body}).encode(), headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("comment ->", r.status)
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
