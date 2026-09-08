#!/usr/bin/env python3
"""CarePilot backend test — verifies safety, RBAC, MCP surface, and capability engines.
Run the server (background) then this. Read side + enforced writes + propose-only."""
import requests, time, sys
BASE="http://127.0.0.1:8000"
role=lambda r:{"X-Role":r}
def ok(n,c): print(("  PASS " if c else "  FAIL ")+n); return c
def wait():
    for _ in range(15):
        try:
            if requests.get(BASE+"/health",timeout=2).status_code==200: return True
        except: time.sleep(1)
    return False
def run():
    print("CarePilot full-stack backend test")
    if not wait(): print("  FAIL server not ready"); return 1
    p=[]
    # health + capability count
    h=requests.get(BASE+"/health").json(); p.append(ok("health + capabilities=39",h.get("capabilities")==39))
    # READ surface
    p.append(ok("search patients", requests.get(BASE+"/api/patients/search?q=Cleo",headers=role("read_only")).status_code==200))
    p.append(ok("V28 risk aligned", requests.get(BASE+"/api/risk-scores").status_code==200))
    p.append(ok("HEDIS measure", requests.get(BASE+"/api/measure/HEDIS%20HbA1c").status_code==200))
    p.append(ok("CCM candidates (2+ conditions, not enrolled)", len(requests.get(BASE+"/api/ccm/candidates").json()["candidates"])>=1))
    p.append(ok("med-safety alerts", requests.get(BASE+"/api/medication-alerts").status_code==200))
    p.append(ok("pharmacy economics", requests.get(BASE+"/api/pharmacy").status_code==200))
    p.append(ok("utilization", requests.get(BASE+"/api/utilization").status_code==200))
    p.append(ok("claims audit", requests.get(BASE+"/api/claims-audit").status_code==200))
    p.append(ok("contract performance", requests.get(BASE+"/api/financial-summary").status_code==200))
    p.append(ok("risk revenue (conservative)", requests.get(BASE+"/api/risk-revenue").status_code==200))
    p.append(ok("audit vault", requests.get(BASE+"/api/audit").status_code==200))
    p.append(ok("provider scorecard", requests.get(BASE+"/api/provider-scorecard").status_code==200))
    p.append(ok("referrals", requests.get(BASE+"/api/referrals").status_code==200))
    p.append(ok("interventions", requests.get(BASE+"/api/interventions").status_code==200))
    # safety boundary
    g=requests.get(BASE+"/api/safety/boundary").json()["guards"]
    p.append(ok("8 safety guards", len(g)>=8 and "no_ai_sign" in g))
    # RBAC
    t=requests.post(BASE+"/api/tasks",headers=role("read_only"),json={"source":"P1","task_type":"gap","title":"x"})
    p.append(ok("read_only write -> 403", t.status_code==403))
    t2=requests.post(BASE+"/api/tasks",headers=role("provider"),json={"source":"P1","task_type":"gap","title":"Follow-up"})
    p.append(ok("provider write -> 200", t2.status_code==200))
    # propose-only
    c=requests.post(BASE+"/api/propose/charge",headers=role("ma"),json={"pid":"P1","amount":150.5,"code":"99490"}).json()
    p.append(ok("propose charge -> human", c.get("status")=="PROPOSED" and c.get("needs")=="human_confirmation"))
    o=requests.post(BASE+"/api/propose/outreach",headers=role("nurse"),json={"pid":"P1","draft":"Hi"}).json()
    p.append(ok("propose outreach -> consent+human send", o.get("status")=="DRAFT" and "twilio" in o.get("via","")))
    # n8n contract
    l=requests.post(BASE+"/api/labs/review-task",json={"run_ref":"R1","event_id":"E1","patient_ref":"PR1","draft_ref":"D1"})
    p.append(ok("n8n review-task contract", l.status_code==200 and l.json().get("ok")))
    # TCM orchestration
    p.append(ok("TCM cohorts (5)", len(requests.get(BASE+"/api/tcm/cohorts").json()["cohorts"])>=5))
    p.append(ok("TCM cases (discharge+admit)", len(requests.get(BASE+"/api/tcm/cases").json()["cases"])>=2))
    pid=requests.get(BASE+"/api/tcm/cases?trigger=discharge").json()["cases"][0]["patient_id"]
    p.append(ok("TCM admission checklist (8 docs)", len(requests.get(BASE+f"/api/tcm/{pid}/checklist").json()["checklist"])>=8))
    p.append(ok("TCM per-step alert ladder (8 steps)", len(requests.get(BASE+f"/api/tcm/{pid}/steps").json()["steps"])>=8))
    p.append(ok("TCM care team (case mgr + CP-NP + hospital nurse)", len(requests.get(BASE+f"/api/tcm/{pid}/care-team").json()["care_team"])>=3))
    p.append(ok("TCM home-health arranged", requests.get(BASE+f"/api/tcm/{pid}/home-health").json()["home_health"] is not None))
    p.append(ok("integrations (eMedical/Ensure/Mirth)", len(requests.get(BASE+"/api/integrations").json()["integrations"])>=3))
    # TCM lifecycle (CEO/HMO/IPA)
    p.append(ok("TCM event feed (admit/discharge/er)", len(requests.get(BASE+"/api/tcm/events").json()["events"])>=3))
    p.append(ok("TCM ingest -> open case + alert + checklist", requests.post(BASE+"/api/tcm/ingest",json={"event":"admit","patient_ref":"MRN-004","source":"mirth_adt"}).json()["result"].get("fired")==["tcm_case_opened","care_team_alerted","checklist_seeded"]))
    p.append(ok("TCM risk-stratify (cohort+band)", len(requests.get(BASE+f"/api/tcm/{pid}/stratify").json()["cohorts"])>=1))
    p.append(ok("TCM readmission-risk (band)", requests.get(BASE+f"/api/tcm/{pid}/readmission-risk").json()["band"] in ("low","medium","high","very_high")))
    p.append(ok("TCM bh-sdoh", "behavioral_risk" in requests.get(BASE+f"/api/tcm/{pid}/bh-sdoh").json()))
    p.append(ok("TCM placement", requests.get(BASE+f"/api/tcm/{pid}/placement").json()["placements"]!=[]))
    p.append(ok("TCM SLA breaches", len(requests.get(BASE+"/api/tcm/sla").json()["breaches"])>=1))
    p.append(ok("TCM billing (99495/99496)", len(requests.get(BASE+f"/api/tcm/{pid}/billing").json()["billing"])>=2))
    p.append(ok("TCM cost-avoidance (assumption-anchored)", requests.get(BASE+"/api/tcm/cost-avoidance").json()["cost_avoidance_usd"]>0))
    p.append(ok("TCM quality metrics", requests.get(BASE+"/api/tcm/quality").json()["tcm_cases"]>=3))
    p.append(ok("TCM executive board", requests.get(BASE+"/api/tcm/board").json()["members_in_transition"]>=3))
    print(f"\n{sum(p)}/{len(p)} passed")
    return 0 if all(p) else 1
if __name__=="__main__": sys.exit(run())
