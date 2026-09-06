#!/usr/bin/env python3
"""CarePilot backend test — verifies safety boundary + RBAC enforcements with real HTTP calls.
RUN: start the app (background), then run this. Uses only the READ side + enforced writes."""
import requests, time, sys

BASE = "http://127.0.0.1:8000"
role_h = lambda r: {"X-Role": r}

def ok(name, cond):
    print(("  PASS " if cond else "  FAIL ") + name)
    return cond

def wait_ready():
    for _ in range(15):
        try:
            if requests.get(BASE+"/health", timeout=2).status_code == 200:
                return True
        except Exception:
            time.sleep(1)
    return False

def run():
    print("CarePilot backend safety/RBAC test")
    if not wait_ready():
        print("  FAIL server not ready"); return 1
    passed = []
    # READ tools
    passed.append(ok("search_patients[read] 200",
        requests.get(BASE+"/api/patients/search?q=demo", headers=role_h("read_only")).status_code == 200))
    passed.append(ok("work_queue[read] 200",
        requests.get(BASE+"/api/work-queue", headers=role_h("read_only")).status_code == 200))
    # safety boundary present
    g = requests.get(BASE+"/api/safety/boundary").json()["guards"]
    passed.append(ok("safety boundary has 8 guards", len(g) >= 8 and "no_ai_sign" in g))
    # RBAC: read_only cannot write task -> 403
    t = requests.post(BASE+"/api/tasks", headers=role_h("read_only"),
        json={"source":"P0001","task_type":"gap","title":"x","owner":"y"})
    passed.append(ok("read_only write -> 403", t.status_code == 403))
    # provider CAN write task -> 200
    t2 = requests.post(BASE+"/api/tasks", headers=role_h("provider"),
        json={"source":"P0001","task_type":"gap","title":"Follow-up","owner":"nurse-2"})
    passed.append(ok("provider write -> 200", t2.status_code == 200))
    # propose-only charge -> human confirmation, not auto-bill
    c = requests.post(BASE+"/api/propose/charge", headers=role_h("ma"),
        json={"pid":"P0001","amount":150.5,"code":"99490"}).json()
    passed.append(ok("propose charge -> PROPOSED/human", c.get("status")=="PROPOSED" and c.get("needs")=="human_confirmation"))
    # propose-only enrollment
    e = requests.post(BASE+"/api/propose/enrollment", headers=role_h("ma"),
        json={"pid":"P0001","program":"TCM"}).json()
    passed.append(ok("propose enrollment -> PROPOSED/human", e.get("status")=="PROPOSED"))
    # n8n contract endpoint (opaque refs, no PHI)
    l = requests.post(BASE+"/api/labs/review-task", json={"run_ref":"R1","event_id":"E1","patient_ref":"PR1","draft_ref":"D1"})
    passed.append(ok("n8n review-task contract -> ok", l.status_code==200 and l.json().get("ok")))
    print(f"\n{sum(passed)}/{len(passed)} passed")
    return 0 if all(passed) else 1

if __name__ == "__main__":
    sys.exit(run())
