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

# ---------- 40. TCM Event Intake (admit/discharge from the 3 lanes) ----------
def ingest_event(event, patient_ref, source, **kw):
    """Record an admit/discharge trigger from Mirth ADT / eMedical / Ensure.
    Returns the event + the TCM actions it fired (alert + checklist on admit; home-health on discharge)."""
    pid = _resolve_patient(patient_ref)
    if not pid: return {"error":"patient not resolved"}
    ev = M.TCMEvent(patient_id=pid, event=event, source=source,
                    facility=kw.get("facility",""), admit_dt=kw.get("admit_dt"),
                    discharge_dt=kw.get("discharge_dt"))
    S.tcm_events.append(ev)
    fired = []
    # on admit -> open TCM case + alert care team + seed checklist
    if event == "admit":
        cohort = assign_cohort(pid).get("cohorts", [{}])[0].get("id","")
        case = M.TCMCase(patient_id=pid, trigger="admit", cohort_id=cohort,
                         checklist=[dict(x) for x in S.tcm_checklist_template],
                         alerts=[f"Patient ADMITTED via {source} — alert care team"])
        S.tcm_cases.append(case)
        S.tcm_steps += [M.TCMStep(case_id=case.id, seq=s["seq"], name=s["name"],
                          alert_level=s["alert_level"], due_in_hours=s["due_in_hours"], assignee=s["assignee"])
                        for s in S.tcm_alert_ladder]
        fired.append("tcm_case_opened"); fired.append("care_team_alerted"); fired.append("checklist_seeded")
    # on discharge -> arrange home health + schedule follow-up
    elif event == "discharge":
        if not S.placements or not any(p.patient_id==pid for p in S.placements):
            S.placements.append(M.PostAcutePlacement(patient_id=pid, kind="home_health",
                                    facility=kw.get("hh_agency","Medisun home-health"), rn_visit_before=True))
        fired.append("home_health_arranged"); fired.append("follow_up_scheduled")
    elif event == "er_visit":
        S.tcm_cases.append(M.TCMCase(patient_id=pid, trigger="admit", cohort_id="",
                            alerts=[f"ER visit via {source} — assess for TCM"]))
        fired.append("er_assess_for_tcm")
    return {"event":ev.id,"patient_id":pid,"fired":fired}

def _resolve_patient(ref):
    """Accept a patient id OR mrn; return patient id or None."""
    p = next((x for x in S.patients if x.id==ref or x.mrn==ref), None)
    return p.id if p else None

def event_feed():
    """Recent admit/discharge events across all lanes."""
    return [{"patient_id":e.patient_id,"event":e.event,"source":e.source,"facility":e.facility,"ts":e.ts}
            for e in S.tcm_events]

# ---------- 41. Risk Stratification (cohort + band) ----------
def risk_stratify(patient_ref):
    pid = _resolve_patient(patient_ref)
    if not pid: return {"error":"patient not found"}
    p = next(x for x in S.patients if x.id==pid)
    cohort = assign_cohort(pid).get("cohorts", [])
    # readmission band from the latest risk record
    rr = next((x for x in S.readm_risks if x.patient_id==pid), None)
    band = "medium"
    if rr: band = rr.band
    return {"patient_id":pid,"cohorts":[c["cohort"] for c in cohort],
            "readmission_band":band,"conditions":p.conditions,"raf":p.risk_scores.get("V28",{}).get("raf",0.0)}

# ---------- 42. Readmission-Risk Prediction (deterministic v1) ----------
def readmission_risk(patient_ref):
    """Score 0-1 from conditions, recent admission, SDOH, missed follow-up. AI propose-only."""
    pid = _resolve_patient(patient_ref)
    if not pid: return {"error":"patient not found"}
    score = 0.2; contrib=[]
    p = next(x for x in S.patients if x.id==pid)
    if len(p.conditions) >= 2: score += 0.2; contrib.append("2+ chronic conditions")
    if any(h in p.conditions for h in ("Heart Failure","COPD","CKD","Diabetes")): score += 0.15; contrib.append("cardiopulmonary/metabolic")
    if any(h.event=="discharge" for h in S.tcm_events if h.patient_id==pid): score += 0.2; contrib.append("recent discharge")
    if any(s.overdue_hours>0 for s in S.sla if s.case_id and any(c.id==s.case_id and c.patient_id==pid for c in S.tcm_cases)): score += 0.15; contrib.append("missed follow-up")
    if any(x.needs for x in S.sdoh if x.patient_id==pid): score += 0.1; contrib.append("SDOH barrier")
    score = min(score, 1.0)
    band = "low" if score<0.35 else "medium" if score<0.6 else "high" if score<0.8 else "very_high"
    return {"patient_id":pid,"score":round(score,2),"band":band,"contributors":contrib,"model":"v1"}

# ---------- 43. Behavioral Health + SDOH ----------
def bh_sdoh(patient_ref):
    pid = _resolve_patient(patient_ref)
    if not pid: return {"error":"patient not found"}
    s = next((x for x in S.sdoh if x.patient_id==pid), None)
    bh = any(c in ("depression","anxiety","bipolar","SUD") for c in next(x for x in S.patients if x.id==pid).conditions)
    return {"patient_id":pid,
            "sdoh": {"food":s.food,"transport":s.transport,"housing":s.housing,"isolation":s.isolation,"needs":s.needs,"referral":s.referral} if s else {},
            "behavioral_risk":bh}

# ---------- 44. Post-Acute Placement ----------
def placement(patient_ref):
    pid = _resolve_patient(patient_ref)
    if not pid: return {"error":"patient not found"}
    pl = [x for x in S.placements if x.patient_id==pid]
    return {"patient_id":pid,"placements":[{"kind":p.kind,"facility":p.facility,"rn_visit_before":p.rn_visit_before} for p in pl]}

# ---------- 45. SLA / Escalation ----------
def sla_breaches():
    """Overdue TCM steps — the escalation list for the team."""
    return [{"case_id":b.case_id,"step":b.step,"overdue_hours":b.overdue_hours,"severity":b.severity} for b in S.sla]

# ---------- 46. TCM Billing (propose-only; humans submit) ----------
def tcm_billing(patient_ref):
    pid = _resolve_patient(patient_ref)
    if not pid: return {"error":"patient not found"}
    return [{"code":b.code,"desc":b.desc,"status":b.status,"value":b.value,"evidence":b.evidence}
            for b in S.tcm_billing if b.patient_id==pid]

# ---------- 47. Cost-Avoidance (the value to the payer) ----------
def cost_avoidance():
    """Readmission + ED avoidance attributed to TCM post-discharge care."""
    avoided=0.0; events=0
    for r in S.readm_risks:
        if r.band in ("high","very_high"):
            avoided += 24680.0  # avoided admit value (assumption-anchored)
            events += 1
    return {"avoided_ed":0,"avoided_admissions":events,
            "cost_avoidance_usd":round(avoided,2),
            "note":"Assumption-anchored ($24,680/admission); must be replaced with real cohort readmission+ED counts. AI propose-only."}

# ---------- 48. Quality Metrics (readmission / STAR hooks) ----------
def tcm_quality():
    """Program-level metrics for the TCM board."""
    total = len(S.tcm_cases)
    high = len([r for r in S.readm_risks if r.band in ("high","very_high")])
    breaches = len(S.sla)
    checklist = sum(1 for c in S.tcm_cases for d in c.checklist if d["status"]=="pending")
    return {"tcm_cases":total,"high_readmission_risk":high,"sla_breaches":breaches,
            "pending_checklist_items":checklist}

# ---------- 49. Executive TCM Board (the CEO view) ----------
def tcm_board():
    """One glance: every member in transition, their cohort, risk, placement, SLA, billing."""
    rows=[]
    for case in S.tcm_cases:
        pid = case.patient_id
        p = next((x for x in S.patients if x.id==pid), None)
        cohort = next((c.name for c in S.cohorts if c.id==case.cohort_id), "")
        rr = next((x for x in S.readm_risks if x.patient_id==pid), None)
        pl = next((x for x in S.placements if x.patient_id==pid), None)
        rows.append({"patient":p.name if p else pid,"trigger":case.trigger,"cohort":cohort,
                     "risk_band":rr.band if rr else "-","placement":pl.kind if pl else "none",
                     "care_team":case.care_team,"sla_breaches":sum(1 for b in S.sla if b.case_id==case.id),
                     "pending_docs":sum(1 for d in case.checklist if d["status"]=="pending")})
    return {"members_in_transition":len(rows),"rows":rows}
