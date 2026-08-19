#!/usr/bin/env python3
"""Governance sweep — run via uv since there's no pip."""
import json, urllib.request, urllib.error, sys, re

def envval(name):
    try:
        env = open("/opt/data/profiles/nura/.env").read()
        m = re.search(rf"^{name}=(.+)$", env, re.M)
        return m.group(1).strip().strip('"').strip("'") if m else ""
    except Exception as e:
        return ""

def get(url, headers=None, timeout=10):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode()[:500]}
    except Exception as e:
        return 0, {"error": str(e)}

key = envval("API_SERVER_KEY")
hdr = {"User-Agent": "NURA-Hermes-Gov/1.0", "Content-Type": "application/json",
       "x-api-key": key, "Authorization": "Bearer " + key}

# Find the live Paperclip server
base = None
for port in [3101, 3100]:
    status, data = get(f"http://127.0.0.1:{port}/api/health")
    if status == 200:
        base = f"http://127.0.0.1:{port}"
        break

if not base:
    print("FATAL: No Paperclip server reachable", file=sys.stderr)
    sys.exit(1)

# Get companies
status, companies_data = get(f"{base}/api/companies", hdr)
if status != 200:
    print(f"FATAL: Cannot list companies (HTTP {status})", file=sys.stderr)
    sys.exit(1)

companies = companies_data if isinstance(companies_data, list) else companies_data.get("companies", companies_data.get("data", []))
target = companies[0] if companies else None
if not target:
    print("FATAL: No companies found", file=sys.stderr)
    sys.exit(1)

cid = target["id"]
cname = target.get("name", "?")
print(f"=== NURA Developer Governance Sweep ===", file=sys.stderr)
print(f"Company: {cname} ({cid})", file=sys.stderr)

# Get agents
status, agents_data = get(f"{base}/api/companies/{cid}/agents", hdr)
agents_list = agents_data if isinstance(agents_data, list) else (agents_data or {}).get("agents", (agents_data or {}).get("data", []))
agent_map = {a.get("id"): a.get("name", a.get("displayName", "?")) for a in agents_list if isinstance(a, dict)}

# Get issues
status, issues_data = get(f"{base}/api/companies/{cid}/issues", hdr)
if status != 200:
    print(f"FATAL: Cannot fetch issues (HTTP {status})", file=sys.stderr)
    sys.exit(1)

issues = issues_data if isinstance(issues_data, list) else issues_data.get("issues", issues_data.get("data", []))
open_statuses = {"todo", "in-progress", "in_progress", "open", "active", "blocked"}

candidates = []
for iss in issues:
    if not isinstance(iss, dict):
        continue
    s = (iss.get("status") or "").lower()
    aid = iss.get("assigneeAgentId") or iss.get("assigneeId") or iss.get("assignee")
    if s in open_statuses and aid:
        candidates.append(iss)

# Audit
violations = []
for iss in candidates:
    iid = iss.get("id") or iss.get("issueId", "?")
    title = iss.get("title", "?")
    s = iss.get("status", "?")
    desc = iss.get("description", "") or ""
    aname = agent_map.get(iss.get("assigneeAgentId") or iss.get("assigneeId", ""), "?")

    # Get comments
    status_c, comments_data = get(f"{base}/api/issues/{iid}/comments", hdr)
    comments = []
    if status_c == 200:
        comments = comments_data if isinstance(comments_data, list) else comments_data.get("comments", comments_data.get("data", []))

    # R1: spec reference
    if not re.search(r'(spec|specification|app.interface.spec|directive)', desc, re.I):
        violations.append(f"ISSUE {iid} \"{title}\" ({aname}, {s}) — R1: no spec/directive reference in description")

    # R2: acceptance criteria
    if not re.search(r'(acceptance criteria|AC\s*[:：]|criteria\s*[:：]|验收)', desc, re.I):
        violations.append(f"ISSUE {iid} \"{title}\" ({aname}, {s}) — R2: no acceptance criteria stated")

    # R3: evidence for non-todo issues
    if s not in ("todo", "backlog", "open"):
        has_ev = any(re.search(r'(test|output|evidence|verified|passed|result)', (c.get("body","") if isinstance(c,dict) else str(c)), re.I) for c in comments)
        if not has_ev:
            violations.append(f"ISSUE {iid} \"{title}\" ({aname}, {s}) — R3: no test evidence in comments")

    # R5: blocked = named blocker + fallback
    if s == "blocked":
        all_text = desc + " " + " ".join((c.get("body","") if isinstance(c,dict) else str(c)) for c in comments)
        has_blocker = bool(re.search(r'(blocker|blocked.by|fallback)', all_text, re.I))
        if not has_blocker:
            violations.append(f"ISSUE {iid} \"{title}\" ({aname}, {s}) — R5: blocked with no named blocker + fallback")

    # R7: secrets check
    all_text = desc + " " + " ".join((c.get("body","") if isinstance(c,dict) else str(c)) for c in comments)
    for pat in [r'(?:api[._-]?key|password|secret|token)\s*[:=]\s*\S{8,}', r'(?:sk|pk)-[A-Za-z0-9_.-]{20,}', r'\b\d{3}-\d{2}-\d{4}\b']:
        if re.search(pat, all_text):
            violations.append(f"ISSUE {iid} \"{title}\" ({aname}, {s}) — R7: potential secret/PHI pattern")
            break

if not violations:
    print("ALL LANES COMPLIANT")
else:
    print(f"\n=== VIOLATIONS ({len(violations)}) ===\n")
    for v in violations:
        print(v)
    print(f"\n--- {len(violations)} total violations across {len(candidates)} active issues ---")
