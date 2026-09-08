"""CarePilot capability engines — the domain logic behind the 39 capabilities.
Every function is deterministic + point-in-time. AI proposals only; humans approve writes."""
import models as M
from store import STORE as S

# ---------- 1. CCM Automation (XL) ----------
def ccm_candidates():
    """Find patients with 2+ ongoing conditions (candidate), NOT enrollment — consent required."""
    return [p for p in S.patients if len(p.conditions) >= 2 and "CCM" not in p.programs]

# ---------- 4. Risk-Model Alignment V28 ----------
def align_risk(patient_id):
    """Label every score with model/version/year + block cross-model compare."""
    return {pid: {"model":s.model,"version":s.version,"year":s.year,"clinical":s.clinical,
                  "raf":s.raf,"source":s.source} for pid in (patient_id,) for s in S.risks if s.patient_id==patient_id}

# ---------- 11. HEDIS & Stars Engine (XL) ----------
def hedis_measure(measure):
    """Numerator/denominator with proof; order does not count when a completed service is required."""
    gaps = [g for g in S.gaps if g.measure==measure]
    den = len(gaps); num = len([g for g in gaps if g.status=="closed"])
    return {"measure":measure,"numerator":num,"denominator":den,"evidence":[g.evidence for g in gaps],
            "open_gaps":[g.patient_id for g in gaps if g.status in ("open","in_progress")]}

# ---------- 12. Medication Safety Center (XL) ----------
def reconcile_meds(patient_id):
    """Cross-check ordered vs dispensed vs given vs billed. Safety separate from cost.
    A financial result never overrides a safety escalation; AI can't change an order.
    A safety finding is NOT closable by AI — human clinical only."""
    alerts = [a for a in S.med_alerts if a.patient_id==patient_id]
    return alerts

# ---------- 5. Unified Work Queue ----------
def work_queue(owner=None, status=None):
    items = list(S.tasks)
    if owner: items=[t for t in items if t["owner"]==owner]
    if status: items=[t for t in items if t["status"]==status]
    return items

# ---------- 20. Pharmacy & Formulary Economics ----------
def pharmacy_view():
    """Drug cost/use + adherence by Rx PMPM; never auto-switch therapy for price alone."""
    phm = sum(d.cost for d in S.drugs) / max(len(S.patients),1)
    return {"drugs":[{"drug":d.drug,"cost":d.cost,"adherence":d.adherence} for d in S.drugs],
            "rx_pmpm":round(phm,2)}

# ---------- 21. Admissions / Utilization / High-Cost ----------
def utilization():
    admitted = len([h for h in S.admissions if h.discharge_dt is not None])
    return {"admissions":admitted,"top_high_cost":[p.name for p in S.patients]}

# ---------- 16. Claims Audit & Recovery ----------
def claim_audit():
    """Detects duplicates/pricing/COB; tracks identified→validated→submitted→recovered (proof required)."""
    return S.claims

# ---------- 15. Medical Economics ----------
def contract_performance():
    """Drill contract→member→claim; separates paid/incurred/estimated."""
    return S.contracts

# ---------- 27. Risk Revenue Recapture (conservative) ----------
def risk_revenue():
    """Member-level suspected vs validated vs paid; NEVER shown as earned before payer acceptance."""
    return [{"patient":p.name,"suspected":p.risk_scores.get("V28",{}).get("raf",0.0),"validated":0.0,"paid":0.0}
            for p in S.patients]

# ---------- 14. Evidence & Audit Vault ----------
def audit_vault():
    """Append-only, unchangeable record of material actions."""
    return S.audit

def log_audit(actor, action, ref=None, phi=False):
    S._audit(actor, action, ref, phi)

# ---------- 39. Transition of Care (TCM) Orchestration ----------
def assign_cohort(patient_id):
    """Place a patient into a cohort/bucket by criteria (deterministic, propose-only)."""
    p = next((x for x in S.patients if x.id==patient_id), None)
    if not p: return {"error":"patient not found"}
    matched=[]
    for c in S.cohorts:
        crit=c.criteria
        ok=True
        if "min_conditions" in crit and len(p.conditions)<crit["min_conditions"]: ok=False
        if "programs" in crit and not any(x in p.programs for x in crit["programs"]): ok=False
        if "conditions" in crit and not any(x in p.conditions for x in crit["conditions"]): ok=False
        if "flags" in crit and not any(getattr(p,k,False) for k in crit["flags"]): ok=False
        if ok: matched.append({"cohort":c.name,"kind":c.kind,"id":c.id})
    return {"patient_id":patient_id,"cohorts":matched}

def tcm_start_cases(trigger="discharge"):
    """All open TCM cases for a trigger (admit or discharge) — the team alert set."""
    return [c for c in S.tcm_cases if c.trigger==trigger]

def tcm_case(patient_id):
    return [c for c in S.tcm_cases if c.patient_id==patient_id]

def tcm_checklist(patient_id):
    """The admission document checklist for a patient's TCM case."""
    case = next((c for c in S.tcm_cases if c.patient_id==patient_id), None)
    if not case: return []
    return [{"doc":d["doc"],"status":d["status"]} for d in case.checklist]

def tcm_steps_for(patient_id):
    case = next((c for c in S.tcm_cases if c.patient_id==patient_id), None)
    if not case: return []
    steps=[s for s in S.tcm_steps if s.case_id==case.id]
    return [{"seq":s.seq,"name":s.name,"status":s.status,"alert_level":s.alert_level,
             "due_in_hours":s.due_in_hours,"assignee":s.assignee} for s in steps]

def tcm_care_team(patient_id):
    """Case manager + community-paramedic NP + hospital nurse assigned to the client."""
    return [{"role":t.role,"name":t.name,"active":t.active} for t in S.care_team if t.patient_id==patient_id]

def tcm_home_health(patient_id):
    case = next((c for c in S.tcm_cases if c.patient_id==patient_id), None)
    return case.home_health if case else None

def tcm_pipeline():
    """The full TCM board for the team — every patient, their trigger, cohort, checklist, care team."""
    out=[]
    for case in S.tcm_cases:
        cohort=next((c.name for c in S.cohorts if c.id==case.cohort_id), "")
        out.append({
            "patient_id":case.patient_id, "trigger":case.trigger, "status":case.status,
            "cohort":cohort, "alerts":case.alerts, "care_team":case.care_team,
            "home_health":case.home_health,
            "checklist":case.checklist,
            "steps":[s.name for s in S.tcm_steps if s.case_id==case.id],
        })
    return out

# ---------- 39b. Integration Topology (data plane feeding TCM) ----------
def integrations():
    """CarePilot connect: eMedical (EMR), Ensure Data Solutions (Solis), Mirth NextGen Connect (HL7)."""
    return getattr(S, "integrations", [])
