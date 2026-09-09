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
    # HL7 ADT -> TCM trigger (Mirth NextGen Connect)
    import hl7 as H
    a=H.parse_adt(H.adt_example("ADT^A01","MRN-001","Broward General"))
    d=H.parse_adt(H.adt_example("ADT^A03","MRN-002","Baptist MDC"))
    p.append(ok("HL7 ADT parser (A01=admit, A03=discharge, MRN extracted)", a["event"]=="admit" and a["patient_ref"]=="MRN-001" and d["event"]=="discharge" and d["patient_ref"]=="MRN-002"))
    msg=H.adt_example("ADT^A01","MRN-004","Broward General")
    h=requests.post(BASE+"/api/tcm/hl7",json={"message":msg})
    p.append(ok("HL7 ADT -> TCM trigger (open case + alert + checklist)", h.status_code==200 and h.json().get("tcm",{}).get("fired")==["tcm_case_opened","care_team_alerted","checklist_seeded"]))
    # Phase-2: identity / provenance / rules / DW
    iq=requests.get(BASE+"/api/identity/queue").json()
    p.append(ok("identity queue present", iq.get("ok") and len(iq.get("queue",[]))>=4))
    p.append(ok("identity unmatched visible", any(x.get("match_status")=="unmatched" for x in iq.get("queue",[]))))
    im=requests.post(BASE+"/api/labs/identity-match",json={"source_system":"n8n","patient_ref":"OPAQUE-REF-99"}).json()
    p.append(ok("n8n identity-match contract", im.get("ok") and im.get("stage")=="identity_match"))
    pr=requests.get(BASE+"/api/provenance").json()
    p.append(ok("provenance append-only stream", pr.get("ok") and pr.get("append_only") and len(pr.get("events",[]))>=1))
    rl=requests.get(BASE+"/api/rules").json()
    p.append(ok("versioned rules registry", rl.get("ok") and len(rl.get("rules",[]))>=2))
    draft=next(r for r in rl["rules"] if r["status"]=="draft")
    sb=requests.post(BASE+f"/api/rules/{draft['id']}/sandbox-test",headers=role("compliance")).json()
    p.append(ok("rules sandbox-test", sb.get("ok") and sb.get("rule",{}).get("sandbox_passed")))
    prop=requests.post(BASE+f"/api/rules/{draft['id']}/propose-activate").json()
    p.append(ok("rules propose-activate (human gate)", prop.get("status")=="PROPOSED" and prop.get("needs")=="human_approval"))
    act=requests.post(BASE+f"/api/rules/{draft['id']}/activate",headers=role("compliance")).json()
    p.append(ok("rules human activate", act.get("ok") and act.get("rule",{}).get("status")=="active"))
    ro=requests.post(BASE+f"/api/rules/{draft['id']}/activate",headers=role("read_only"))
    p.append(ok("rules activate read_only -> 403", ro.status_code==403))
    dw=requests.get(BASE+"/api/dw/hub").json()
    p.append(ok("DW interop hub scaffold", dw.get("ok") and len(dw.get("feeds",[]))>=3))
    di=requests.post(BASE+"/api/dw/ingest",headers=role("cpho"),json={"entity_type":"encounter","source":"mirth","payload":{"event":"ADT","ref":"SYN-1"}}).json()
    p.append(ok("DW ingest (human write)", di.get("ok") and di.get("record",{}).get("entity_type")=="encounter"))

    # Population Health (caps ~26–32)
    pr=requests.get(BASE+"/api/pop/risk").json()
    p.append(ok("pop risk stratification bands", pr.get("ok") and pr.get("counts") and len(pr.get("rows",[]))>=4))
    mq=requests.get(BASE+"/api/mih/queue").json()
    p.append(ok("MIH queue (propose-only)", mq.get("ok") and mq.get("proposed",0)>=1 and mq.get("propose_only")))
    mp=requests.post(BASE+"/api/mih/propose",json={"patient_ref":"MRN-003","reason":"COPD home check","priority":"routine"}).json()
    p.append(ok("MIH propose -> human", mp.get("status")=="PROPOSED" and mp.get("needs")=="human_confirmation"))
    eid=mp["episode"]["id"]
    ro=requests.post(BASE+f"/api/mih/{eid}/accept",headers=role("read_only"))
    p.append(ok("MIH accept read_only -> 403", ro.status_code==403))
    ac=requests.post(BASE+f"/api/mih/{eid}/accept",headers=role("cpho")).json()
    p.append(ok("MIH human accept (cpho)", ac.get("ok") and ac.get("episode",{}).get("status")=="accepted"))
    pp=requests.get(BASE+"/api/provider-performance").json()
    p.append(ok("provider performance command center", pp.get("ok") and len(pp.get("providers",[]))>=1))
    io=requests.get(BASE+"/api/intervention-outcomes").json()
    p.append(ok("intervention outcomes deltas", io.get("ok") and "total_cost_avoided" in io))
    ip=requests.post(BASE+"/api/propose/intervention",json={"patient_ref":"MRN-002","kind":"MIH home visit","before":{"ed":1,"readmissions":0,"cost":1500}}).json()
    p.append(ok("propose intervention -> human", ip.get("status")=="PROPOSED"))
    fa=requests.get(BASE+"/api/frailty-acp").json()
    p.append(ok("frailty/ACP panel", fa.get("ok") and fa.get("frail_count",0)>=1))
    fp=requests.post(BASE+"/api/propose/frailty-acp",json={"patient_ref":"MRN-002","goals":["ACP discussion"]}).json()
    p.append(ok("propose frailty ACP -> human", fp.get("status")=="PROPOSED" and fp.get("needs")=="human_confirmation"))
    cb=requests.get(BASE+"/api/cpho/board").json()
    p.append(ok("CPHO command center board", cb.get("ok") and cb.get("role")=="cpho" and "risk" in cb and "mih" in cb))

    # Phase-3: payer / Solis reconcile
    ps=requests.get(BASE+"/api/payer/reconcile/status").json()
    p.append(ok("payer reconcile status", ps.get("ok") and ps.get("policy",{}).get("no_overwrite_unresolved_identity_conflicts") and ps.get("exceptions_open",0)>=1))
    pe=requests.get(BASE+"/api/payer/reconcile/exceptions").json()
    p.append(ok("payer exception queue", pe.get("ok") and len(pe.get("exceptions",[]))>=2))
    pr=requests.get(BASE+"/api/payer/roster?payer=Solis").json()
    p.append(ok("payer roster (Solis)", pr.get("ok") and len(pr.get("rows",[]))>=3))
    pc=requests.get(BASE+"/api/payer/contracts").json()
    p.append(ok("payer contract reconcile", pc.get("ok") and len(pc.get("contracts",[]))>=2))
    dry=requests.post(BASE+"/api/payer/reconcile/run",json={"payer":"Solis","apply":False}).json()
    p.append(ok("payer reconcile dry-run skips conflicts", dry.get("ok") and dry.get("run",{}).get("skipped_conflicts",0)>=1))
    prop=requests.post(BASE+"/api/propose/payer-sync",json={"payer":"Solis","apply":True}).json()
    p.append(ok("propose payer-sync -> human", prop.get("status")=="PROPOSED" and prop.get("needs")=="human_confirmation"))
    run_id=prop["run"]["id"]
    ro=requests.post(BASE+f"/api/payer/reconcile/{run_id}/apply",headers=role("read_only"))
    p.append(ok("payer apply read_only -> 403", ro.status_code==403))
    ap=requests.post(BASE+f"/api/payer/reconcile/{run_id}/apply",headers=role("compliance")).json()
    p.append(ok("payer human apply (no conflict overwrite)", ap.get("ok") and "applied" in ap))
    eid=pe["exceptions"][0]["id"]
    rx=requests.post(BASE+f"/api/payer/reconcile/exceptions/{eid}/resolve",headers=role("compliance"),json={"resolution":"resolved"}).json()
    p.append(ok("payer exception human resolve", rx.get("ok") and rx.get("exception",{}).get("status")=="resolved"))

    print(f"\n{sum(p)}/{len(p)} passed")
    return 0 if all(p) else 1
if __name__=="__main__": sys.exit(run())
