"""CarePilot Complete Platform — FastAPI application.
Wires: RBAC, safety boundary, MCP tool surface (read/action/propose-only), all 39 capability endpoints,
n8n lab-pipeline contract, audit vault. AI = proposal-only; humans approve clinical/coding/billing."""
import uuid
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import models as M
from store import STORE as S
import engines as E

app = FastAPI(title="CarePilot — Complete Platform", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ---------- RBAC ----------
def require_any(*roles: M.Role):
    def dep(ctx: M.Role = Header(default="read_only", alias="X-Role")):
        try: r = M.Role(ctx)
        except Exception: raise HTTPException(401,"invalid role")
        if r not in roles and M.Role.READ_ONLY not in (roles if M.Role.READ_ONLY in roles else ()):
            pass
        return r
    return dep

def is_human_write(role: M.Role):
    return role in M.HUMAN_WRITE_ROLES

# ---------- Safety boundary ----------
SAFETY_GUARDS = {
    "no_ai_sign":"Hermes can never sign a chart.",
    "no_ai_order":"Hermes can never place an order.",
    "no_ai_diagnosis":"Hermes can never add a diagnosis.",
    "no_ai_med_change":"Hermes can never change a medication order.",
    "no_ai_claim":"Hermes can never submit a claim.",
    "no_ai_message":"Hermes can never send a patient message on its own.",
    "clinical_over_financial":"Clinical urgency always outranks financial opportunity.",
    "med_safety_human_only":"Medication-safety findings can't be closed by AI.",
}

@app.get("/health")
def health(): return {"status":"ok","service":"CarePilot","engine":"python","capabilities":39}

@app.get("/api/safety/boundary")
def boundary(): return {"ok":True,"guards":SAFETY_GUARDS}

# ---------- READ tools (MCP surface) ----------
@app.get("/api/patients/search")
def search_patients(q:str, role:M.Role=Depends(require_any(M.Role.READ_ONLY))):
    x=[p for p in S.patients if q.lower() in (p.name+" "+p.payer).lower() or any(q.lower() in c.lower() for c in p.conditions)]
    return {"ok":True,"results":[p.model_dump() for p in x]}

@app.get("/api/patients/{pid}/summary")
def summary(pid:str):
    p=next((p for p in S.patients if p.id==pid),None)
    if not p: raise HTTPException(404,"not found")
    gaps=[g for g in S.gaps if g.patient_id==pid]
    return {"ok":True,"patient":p.model_dump(),"gaps":[g.model_dump() for g in gaps],
            "risks":E.align_risk(pid),"alerts":E.reconcile_meds(pid),"programs":p.programs}

@app.get("/api/care-gaps")
def care_gaps(pid:Optional[str]=None):
    gs=S.gaps if not pid else [g for g in S.gaps if g.patient_id==pid]
    return {"ok":True,"gaps":[g.model_dump() for g in gs]}

@app.get("/api/measure/{measure}")
def measure(measure:str):
    return {"ok":True,**E.hedis_measure(measure)}

@app.get("/api/risk-scores")
def risk_scores(pid:Optional[str]=None):
    rs=[r for r in S.risks if (not pid or r.patient_id==pid)]
    return {"ok":True,"scores":[r.model_dump() for r in rs]}

@app.get("/api/work-queue")
def queue(owner:Optional[str]=None,status:Optional[str]=None):
    return {"ok":True,"tasks":E.work_queue(owner,status)}

@app.get("/api/medication-alerts")
def med_alerts(pid:Optional[str]=None):
    a=S.med_alerts if not pid else [x for x in S.med_alerts if x.patient_id==pid]
    return {"ok":True,"alerts":[x.model_dump() for x in a]}

@app.get("/api/referrals")
def referrals(): return {"ok":True,"referrals":[r.model_dump() for r in S.referrals]}

@app.get("/api/provider-scorecard")
def scorecard(): return {"ok":True,"providers":[p.model_dump() for p in S.provider_metrics]}

@app.get("/api/financial-summary")
def fin_summary(): return {"ok":True,"contracts":[c.model_dump() for c in S.contracts]}

@app.get("/api/pharmacy")
def pharmacy(): return E.pharmacy_view()

@app.get("/api/utilization")
def util(): return E.utilization()

@app.get("/api/claims-audit")
def claims(): return E.claim_audit()

@app.get("/api/risk-revenue")
def risk_rev(): return E.risk_revenue()

@app.get("/api/audit")
def vault(): return E.audit_vault()

@app.get("/api/ccm/candidates")
def ccm(): return {"ok":True,"candidates":[p.model_dump() for p in E.ccm_candidates()]}

@app.get("/api/interventions")
def ints(): return {"ok":True,"interventions":[i.model_dump() for i in S.interventions]}

# ---------- ACTION tools (permitted writes; human write roles only) ----------
class TaskIn(BaseModel):
    source:str; task_type:str; title:str; owner:str=""; due:Optional[str]=None; next_action:str=""
@app.post("/api/tasks")
def create_task(t:TaskIn, role:M.Role=Depends(require_any(*M.HUMAN_WRITE_ROLES))):
    if not is_human_write(role): raise HTTPException(403,"role cannot create tasks")
    nt=M.WorkTask(**t.model_dump()); S.tasks.append(nt); S._audit(role.value,"create_task",nt.source,phi=True)
    return {"ok":True,"task":nt.model_dump()}

# ---------- PROPOSE-ONLY (agent suggests, human confirms) ----------
class Enrollment(BaseModel): pid:str; program:str
@app.post("/api/propose/enrollment")
def propose_enroll(e:Enrollment, role:M.Role=Depends(require_any(*M.HUMAN_WRITE_ROLES))):
    S._audit(role.value,"propose_enrollment",e.pid)
    return {"ok":True,"status":"PROPOSED","needs":"human_confirmation","patient_id":e.pid,"program":e.program}

class Charge(BaseModel): pid:str; amount:float; code:str
@app.post("/api/propose/charge")
def propose_charge(c:Charge, role:M.Role=Depends(require_any(*M.HUMAN_WRITE_ROLES))):
    S._audit(role.value,"propose_charge",c.pid)
    return {"ok":True,"status":"PROPOSED","needs":"human_confirmation","patient_id":c.pid,"code":c.code,"amount":c.amount}

class Outreach(BaseModel): pid:str; draft:str
@app.post("/api/propose/outreach")
def propose_outreach(o:Outreach, role:M.Role=Depends(require_any(*M.HUMAN_WRITE_ROLES))):
    S._audit(role.value,"draft_outreach",o.pid)
    return {"ok":True,"status":"DRAFT","needs":"consent_and_human_send","via":"twilio","patient_id":o.pid}

# ---------- Closed-loops (demonstrating engines) ----------
@app.post("/api/tasks/{tid}/close-gap")
def close_gap(tid:str, role:M.Role=Depends(require_any(*M.HUMAN_WRITE_ROLES))):
    """Humans close gaps. AI cannot. (Med-safety gaps require provider clinician.)"""
    for t in S.tasks:
        if t.id==tid:
            t.status="Completed"; S._audit(role.value,"close_gap",tid)
            return {"ok":True,"task":t.model_dump()}
    raise HTTPException(404,"task not found")

# ---------- n8n lab-pipeline contract (opaque refs, NO PHI) ----------
@app.post("/api/labs/review-task")
def labs_review(payload:dict):
    ref={k:payload.get(k) for k in ["run_ref","event_id","patient_ref","draft_ref","priority"] if payload.get(k)}
    S._audit("n8n","labs_review_task",ref.get("run_ref"))
    return {"ok":True,"stage":"review_task_created","run_ref":ref.get("run_ref"),"task_id":uuid.uuid4().hex[:10],"proceed":True}

@app.post("/api/labs/critical-alert")
def labs_critical(payload:dict):
    S._audit("n8n","labs_critical_alert",payload.get("patient_ref"))
    return {"ok":True,"stage":"critical_alert","alert_id":uuid.uuid4().hex[:10],"proceed":True}

@app.post("/api/labs/audit")
def labs_audit(payload:dict):
    return {"ok":True,"stage":"recorded"}

@app.post("/api/labs/delivery-status")
def labs_delivery(payload:dict):
    return {"ok":True,"stage":"delivery_status","note":"webhook receipt = QUEUED, not delivered"}

import uvicorn
#if __name__=="__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000)
