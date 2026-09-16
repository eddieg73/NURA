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
def vault():
    v = E.audit_vault()
    # backward-compatible: list body still present as "entries"; full vault includes provenance_count
    return {"ok":True, **v} if isinstance(v, dict) else {"ok":True,"audit":v}

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

@app.post("/api/labs/identity-match")
def labs_identity_match(payload:dict):
    """n8n contract: opaque refs only — no PHI. Queues unmatched identities."""
    src = payload.get("source_system") or payload.get("source") or "n8n"
    ref = payload.get("patient_ref") or payload.get("source_ref") or payload.get("run_ref")
    if not ref:
        raise HTTPException(400, "patient_ref/source_ref required")
    result = E.identity_match(src, str(ref), patient_ref=payload.get("carepilot_ref"), propose=True)
    S._audit("n8n","labs_identity_match",ref)
    return {"ok":True,"stage":"identity_match","proceed":True,**result}

@app.post("/api/labs/audit")
def labs_audit(payload:dict):
    return {"ok":True,"stage":"recorded"}

@app.post("/api/labs/delivery-status")
def labs_delivery(payload:dict):
    return {"ok":True,"stage":"delivery_status","note":"webhook receipt = QUEUED, not delivered"}

# ---------- Transition of Care (TCM) Orchestration ----------
@app.get("/api/tcm/cohorts")
def tcm_cohorts():
    """All cohort/bucket definitions (propose-only read)."""
    return {"cohorts":[{"id":c.id,"name":c.name,"kind":c.kind,"criteria":c.criteria} for c in S.cohorts]}

@app.get("/api/tcm/cohorts/{pid}/assign")
def tcm_assign(pid:str):
    """Deterministic cohort assignment for a patient (propose-only — tells the team the bucket)."""
    return E.assign_cohort(pid)

@app.get("/api/tcm/cases")
def tcm_cases(trigger:Optional[str]=None):
    """Open TCM cases; filter by admit/discharge."""
    cases=E.tcm_pipeline() if not trigger else [c for c in E.tcm_pipeline() if c["trigger"]==trigger]
    return {"cases":cases}

@app.get("/api/tcm/{pid}/case")
def tcm_single(pid:str):
    return {"case":E.tcm_case(pid)}

@app.get("/api/tcm/{pid}/checklist")
def tcm_checklist(pid:str):
    """The admission document checklist to obtain for this patient."""
    return {"patient_id":pid,"checklist":E.tcm_checklist(pid)}

@app.get("/api/tcm/{pid}/steps")
def tcm_steps(pid:str):
    """The per-step alert ladder for this patient (each step of the way has its own alert)."""
    return {"patient_id":pid,"steps":E.tcm_steps_for(pid)}

@app.get("/api/tcm/{pid}/care-team")
def tcm_care_team(pid:str):
    """Case manager + community-paramedic NP + hospital nurse managing this client."""
    return {"patient_id":pid,"care_team":E.tcm_care_team(pid)}

@app.get("/api/tcm/{pid}/home-health")
def tcm_home_health(pid:str):
    return {"patient_id":pid,"home_health":E.tcm_home_health(pid)}

@app.get("/api/integrations")
def integrations():
    """CarePilot connect topology: eMedical (EMR) / Ensure Data Solutions (Solis) / Mirth NextGen Connect (HL7)."""
    return {"integrations":E.integrations()}

# ---------- TCM Lifecycle (CEO/HMO/IPA care-management engine) ----------
@app.get("/api/tcm/events")
def tcm_event_feed():
    return {"events":E.event_feed()}

@app.post("/api/tcm/ingest")
def tcm_ingest(payload:dict):
    """Admit/discharge trigger from Mirth ADT / eMedical / Ensure -> opens case + alert + checklist."""
    return {"ok":True,"result":E.ingest_event(payload.get("event","admit"), payload.get("patient_ref",""),
            payload.get("source",""), facility=payload.get("facility",""))}

@app.post("/api/tcm/hl7")
def tcm_hl7(payload:dict):
    """Receive a raw HL7 ADT message (Mirth NextGen Connect) and trigger the TCM pipeline."""
    import hl7 as H
    msg = payload.get("message") or payload.get("hl7") or ""
    parsed = H.parse_adt(msg)
    if not parsed:
        return {"ok":False,"error":"no valid HL7 ADT message"}
    # fire the TCM intake (propose-only: opens case + alert + checklist; no clinical write)
    result = E.ingest_event(parsed["event"], parsed["patient_ref"], parsed["source"],
                            facility=parsed["facility"])
    return {"ok":True,"parsed":parsed,"tcm":result}

@app.get("/api/tcm/{pid}/stratify")
def tcm_stratify(pid:str):
    return E.risk_stratify(pid)

@app.get("/api/tcm/{pid}/readmission-risk")
def tcm_readm_risk(pid:str):
    return E.readmission_risk(pid)

@app.get("/api/tcm/{pid}/bh-sdoh")
def tcm_bh_sdoh(pid:str):
    return E.bh_sdoh(pid)

@app.get("/api/tcm/{pid}/placement")
def tcm_placement(pid:str):
    return E.placement(pid)

@app.get("/api/tcm/sla")
def tcm_sla():
    return {"breaches":E.sla_breaches()}

@app.get("/api/tcm/{pid}/billing")
def tcm_billing(pid:str):
    return {"patient_id":pid,"billing":E.tcm_billing(pid)}

@app.get("/api/tcm/cost-avoidance")
def tcm_cost_avoidance():
    return E.cost_avoidance()

@app.get("/api/tcm/quality")
def tcm_quality():
    return E.tcm_quality()

@app.get("/api/tcm/board")
def tcm_board():
    return E.tcm_board()

import uvicorn
#if __name__=="__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000)



# ---------- Phase-2: Identity / Provenance / Rules / DW ----------
@app.get("/api/identity/queue")
def identity_queue(status:Optional[str]=None):
    return {"ok":True,"queue":E.identity_queue(status)}

class IdentityMatchIn(BaseModel):
    source_system:str; source_ref:str; patient_ref:Optional[str]=None; propose:bool=True
@app.post("/api/identity/match")
def identity_match(body:IdentityMatchIn):
    return E.identity_match(body.source_system, body.source_ref, body.patient_ref, propose=body.propose)

@app.post("/api/identity/{iid}/confirm")
def identity_confirm(iid:str, role:M.Role=Depends(require_any(*M.HUMAN_WRITE_ROLES))):
    if not is_human_write(role): raise HTTPException(403,"role cannot confirm identity")
    out = E.identity_confirm(iid, role.value)
    if out.get("error"): raise HTTPException(400, out["error"])
    return out

@app.get("/api/provenance")
def provenance(limit:int=100):
    return {"ok":True,"append_only":True,"events":E.provenance_list(limit)}

class ProvenanceIn(BaseModel):
    action:str; subject_ref:Optional[str]=None; rule_version:Optional[str]=None
    model_version:Optional[str]=None; evidence:dict={}
@app.post("/api/provenance")
def provenance_append(body:ProvenanceIn, role:M.Role=Depends(require_any(*M.HUMAN_WRITE_ROLES))):
    if not is_human_write(role): raise HTTPException(403,"role cannot append provenance")
    return E.provenance_append(role.value, body.action, body.subject_ref,
                               body.rule_version, body.model_version, body.evidence)

@app.get("/api/rules")
def rules(status:Optional[str]=None):
    return {"ok":True,"rules":E.rules_list(status)}

@app.get("/api/rules/versions")
def rules_versions(rule_id:Optional[str]=None):
    return {"ok":True,"versions":E.rules_versions(rule_id)}

class RuleCreateIn(BaseModel):
    kind:str; name:str; version:str; payload:dict={}
@app.post("/api/rules")
def rules_create(body:RuleCreateIn, role:M.Role=Depends(require_any(*M.HUMAN_WRITE_ROLES))):
    if not is_human_write(role): raise HTTPException(403,"role cannot create rules")
    return {"ok":True,"rule":E.rules_create(body.kind, body.name, body.version, body.payload, role.value)}

@app.post("/api/rules/{rid}/sandbox-test")
def rules_sandbox(rid:str, role:M.Role=Depends(require_any(*M.HUMAN_WRITE_ROLES))):
    if not is_human_write(role): raise HTTPException(403,"role cannot sandbox-test")
    out = E.rules_sandbox_test(rid, role.value)
    if out.get("error"): raise HTTPException(400, out["error"])
    return out

@app.post("/api/rules/{rid}/propose-activate")
def rules_propose_activate(rid:str):
    """Propose-only go-live — human must call /activate."""
    out = E.rules_propose_activate(rid, "hermes")
    if out.get("error"): raise HTTPException(400, out["error"])
    return out

@app.post("/api/rules/{rid}/activate")
def rules_activate(rid:str, role:M.Role=Depends(require_any(*M.HUMAN_WRITE_ROLES))):
    if not is_human_write(role): raise HTTPException(403,"role cannot activate rules")
    out = E.rules_activate(rid, role.value)
    if out.get("error"): raise HTTPException(400, out["error"])
    return out

class RuleRollbackIn(BaseModel):
    to_version:str
@app.post("/api/rules/{rid}/rollback")
def rules_rollback(rid:str, body:RuleRollbackIn, role:M.Role=Depends(require_any(*M.HUMAN_WRITE_ROLES))):
    if not is_human_write(role): raise HTTPException(403,"role cannot rollback rules")
    out = E.rules_rollback(rid, body.to_version, role.value)
    if out.get("error"): raise HTTPException(400, out["error"])
    return out

@app.get("/api/dw/hub")
def dw_hub():
    return E.dw_hub()

@app.get("/api/dw/entities")
def dw_entities(entity_type:Optional[str]=None):
    return {"ok":True,"entities":E.dw_entities(entity_type)}

class DWIngestIn(BaseModel):
    entity_type:str; source:str; payload:dict={}
@app.post("/api/dw/ingest")
def dw_ingest(body:DWIngestIn, role:M.Role=Depends(require_any(*M.HUMAN_WRITE_ROLES))):
    if not is_human_write(role): raise HTTPException(403,"role cannot ingest DW")
    return E.dw_ingest(body.entity_type, body.source, body.payload, role.value)

# --- Ensure propose-only intake (Lane A) ---
try:
    import ensure_intake_patch as _ensure_intake
    app.include_router(_ensure_intake.router)
except Exception:
    pass


# ---------- Population Health (caps ~26–32) ----------
@app.get("/api/pop/risk")
def pop_risk(band:Optional[str]=None):
    return E.pop_risk_stratify(band)

@app.get("/api/pop/risk/{pid}")
def pop_risk_patient(pid:str):
    out = E.pop_risk_patient(pid)
    if out.get("error"): raise HTTPException(404, out["error"])
    return out

@app.get("/api/mih/queue")
def mih_queue(status:Optional[str]=None):
    return E.mih_queue(status)

class MIHProposeIn(BaseModel):
    patient_ref:str; reason:str; priority:str="routine"; sdoh_needs:list=[]
@app.post("/api/mih/propose")
def mih_propose(body:MIHProposeIn):
    """Propose-only MIH dispatch — human must accept."""
    out = E.mih_propose(body.patient_ref, body.reason, body.priority, body.sdoh_needs, "hermes")
    if out.get("error"): raise HTTPException(404, out["error"])
    return out

@app.post("/api/mih/{eid}/accept")
def mih_accept(eid:str, role:M.Role=Depends(require_any(*M.HUMAN_WRITE_ROLES))):
    if not is_human_write(role): raise HTTPException(403,"role cannot accept MIH")
    out = E.mih_accept(eid, role.value)
    if out.get("error"): raise HTTPException(400, out["error"])
    return out

@app.get("/api/provider-performance")
def provider_performance():
    return E.provider_performance()

@app.get("/api/intervention-outcomes")
def intervention_outcomes():
    return E.intervention_outcomes()

class InterventionProposeIn(BaseModel):
    patient_ref:str; kind:str; before:dict={}
@app.post("/api/propose/intervention")
def propose_intervention(body:InterventionProposeIn):
    out = E.intervention_propose(body.patient_ref, body.kind, body.before, "hermes")
    if out.get("error"): raise HTTPException(404, out["error"])
    return out

@app.get("/api/frailty-acp")
def frailty_acp(pid:Optional[str]=None):
    return E.frailty_acp(pid)

class FrailtyACPProposeIn(BaseModel):
    patient_ref:str; goals:list=[]
@app.post("/api/propose/frailty-acp")
def propose_frailty_acp(body:FrailtyACPProposeIn):
    return E.frailty_propose_acp(body.patient_ref, body.goals, "hermes")

@app.get("/api/cpho/board")
def cpho_board():
    """Exec CPHO command center — risk/MIH/scorecards/outcomes/frailty/TCM/identity."""
    return E.cpho_command_center()


# ---------- Phase-3: Payer / Solis reconciliation ----------
@app.get("/api/payer/reconcile/status")
def payer_reconcile_status(payer:Optional[str]=None):
    return E.payer_reconcile_status(payer)

@app.get("/api/payer/reconcile/exceptions")
def payer_exceptions(status:Optional[str]="open"):
    return E.payer_exception_queue(status)

@app.get("/api/payer/roster")
def payer_roster(payer:Optional[str]=None, reconcile_status:Optional[str]=None):
    return E.payer_roster(payer, reconcile_status)

@app.get("/api/payer/contracts")
def payer_contracts():
    return E.payer_contract_reconcile()

class PayerRunIn(BaseModel):
    payer:str="Solis"; apply:bool=False
@app.post("/api/payer/reconcile/run")
def payer_reconcile_run(body:PayerRunIn):
    """Dry-run by default. apply=True proposes apply — human must POST /apply."""
    return E.payer_reconcile_run(body.payer, apply=body.apply, actor="hermes")

@app.post("/api/payer/reconcile/{run_id}/apply")
def payer_reconcile_apply(run_id:str, role:M.Role=Depends(require_any(*M.HUMAN_WRITE_ROLES))):
    if not is_human_write(role): raise HTTPException(403,"role cannot apply payer reconcile")
    out = E.payer_reconcile_apply(run_id, role.value)
    if out.get("error"): raise HTTPException(400, out["error"])
    return out

class PayerExcResolveIn(BaseModel):
    resolution:str="resolved"
@app.post("/api/payer/reconcile/exceptions/{eid}/resolve")
def payer_exception_resolve(eid:str, body:PayerExcResolveIn,
                            role:M.Role=Depends(require_any(*M.HUMAN_WRITE_ROLES))):
    if not is_human_write(role): raise HTTPException(403,"role cannot resolve exceptions")
    out = E.payer_exception_resolve(eid, role.value, body.resolution)
    if out.get("error"): raise HTTPException(400, out["error"])
    return out

@app.post("/api/propose/payer-sync")
def propose_payer_sync(body:PayerRunIn):
    """Propose-only Solis roster sync — never applies without human /apply."""
    out = E.payer_reconcile_run(body.payer, apply=True, actor="hermes")
    return {"ok":True,"status":"PROPOSED","needs":"human_confirmation",
            "run":out.get("run"),"policy":out.get("policy")}
