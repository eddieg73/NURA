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
    if owner: items=[t for t in items if t.owner==owner]
    if status: items=[t for t in items if t.status==status]
    return [t.model_dump() if hasattr(t,"model_dump") else t for t in items]

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

# ---------- 14. Evidence & Audit Vault (see Phase-2 provenance_* below) ----------
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


# ---------- Phase-2: Identity resolution ----------
def identity_queue(status=None):
    """Visible unmatched/conflict identity queue. Matched listed when status omitted or matched."""
    rows = list(S.identity)
    if status:
        rows = [r for r in rows if r.match_status == status]
    return [{"id":r.id,"source_system":r.source_system,"source_ref":r.source_ref,
             "patient_id":r.patient_id,"match_status":r.match_status,"confidence":r.confidence,
             "conflict_reason":r.conflict_reason,"updated":r.updated} for r in rows]

def identity_match(source_system, source_ref, patient_ref=None, propose=True):
    """Resolve opaque source_ref to CarePilot patient. Propose-only by default (status=proposed).
    Exact MRN / id match auto-links; unknown refs stay unmatched in the queue."""
    from models import _now
    existing = next((r for r in S.identity if r.source_system==source_system and r.source_ref==source_ref), None)
    pid = None
    if patient_ref:
        pid = _resolve_patient(patient_ref)
    if not pid:
        # try source_ref as MRN/id
        pid = _resolve_patient(source_ref)
    if existing is None:
        status = "unmatched"
        conf = 0.0
        if pid:
            status = "proposed" if propose else "matched"
            conf = 0.9 if propose else 0.99
        rec = M.IdentityRecord(source_system=source_system, source_ref=source_ref,
                               patient_id=pid, match_status=status, confidence=conf)
        S.identity.append(rec)
        S._audit("system","identity_match",rec.id, evidence={"source_system":source_system,"status":status})
        return {"ok":True,"record":rec.model_dump(),"created":True}
    # update existing (status transitions only; keep history via provenance)
    if pid and existing.match_status in ("unmatched","proposed","conflict"):
        existing.patient_id = pid
        existing.match_status = "proposed" if propose else "matched"
        existing.confidence = 0.9 if propose else 0.99
        existing.updated = _now()
        S._audit("system","identity_rematch",existing.id, evidence={"patient_id":pid})
    return {"ok":True,"record":existing.model_dump(),"created":False}

def identity_confirm(identity_id, role_actor):
    """Human confirms a proposed identity link (not AI)."""
    from models import _now
    rec = next((r for r in S.identity if r.id==identity_id), None)
    if not rec: return {"error":"not found"}
    if rec.match_status not in ("proposed","conflict") or not rec.patient_id:
        return {"error":"not confirmable","status":rec.match_status}
    rec.match_status = "matched"
    rec.confidence = 1.0
    rec.updated = _now()
    S._audit(role_actor,"identity_confirm",rec.id, evidence={"patient_id":rec.patient_id})
    return {"ok":True,"record":rec.model_dump()}

# ---------- Phase-2: Provenance / Evidence vault ----------
def provenance_list(limit=100):
    """Append-only provenance stream (newest last)."""
    rows = S.provenance[-limit:]
    return [r.model_dump() for r in rows]

def provenance_append(actor, action, subject_ref=None, rule_version=None, model_version=None, evidence=None, phi=False):
    """Explicit provenance write — append-only via store._audit."""
    S._audit(actor, action, subject_ref, phi=phi, rule_version=rule_version,
             model_version=model_version, evidence=evidence or {})
    return {"ok":True,"count":len(S.provenance),"latest":S.provenance[-1].model_dump()}

def audit_vault():
    """Append-only, unchangeable record of material actions (+ provenance count)."""
    return {"audit":S.audit,"provenance_count":len(S.provenance),"append_only":True}

# ---------- Phase-2: Versioned Rules Registry ----------
def rules_list(status=None):
    rows = list(S.rules)
    if status:
        rows = [r for r in rows if r.status==status]
    return [r.model_dump() for r in rows]

def rules_versions(rule_id=None):
    vers = list(S.rules_versions)
    if rule_id:
        vers = [v for v in vers if v.get("rule_id")==rule_id]
    return vers

def rules_create(kind, name, version, payload=None, actor="system"):
    rs = M.RuleSet(kind=kind, name=name, version=version, status="draft",
                   payload=payload or {})
    S.rules.append(rs)
    S.rules_versions.append({"rule_id":rs.id,"version":version,"status":"draft","approved_by":None})
    S._audit(actor,"rules_create",rs.id, rule_version=version, evidence={"kind":kind,"name":name})
    return rs.model_dump()

def rules_sandbox_test(rule_id, actor="system"):
    rs = next((r for r in S.rules if r.id==rule_id), None)
    if not rs: return {"error":"not found"}
    if rs.status == "retired": return {"error":"retired"}
    rs.sandbox_passed = True
    rs.status = "sandbox"
    S._audit(actor,"rules_sandbox_test",rs.id, rule_version=rs.version, evidence={"passed":True})
    return {"ok":True,"rule":rs.model_dump()}

def rules_propose_activate(rule_id, actor="system"):
    """Propose-only: mark ready for human go-live approval."""
    rs = next((r for r in S.rules if r.id==rule_id), None)
    if not rs: return {"error":"not found"}
    if not rs.sandbox_passed: return {"error":"sandbox_required"}
    S._audit(actor,"rules_propose_activate",rs.id, rule_version=rs.version)
    return {"ok":True,"status":"PROPOSED","needs":"human_approval","rule":rs.model_dump()}

def rules_activate(rule_id, actor):
    """Human activates a sandbox-passed rule set; prior active of same kind -> retired."""
    from models import _now
    rs = next((r for r in S.rules if r.id==rule_id), None)
    if not rs: return {"error":"not found"}
    if not rs.sandbox_passed: return {"error":"sandbox_required"}
    for other in S.rules:
        if other.kind==rs.kind and other.status=="active" and other.id!=rs.id:
            other.status = "retired"
            S.rules_versions.append({"rule_id":other.id,"version":other.version,"status":"retired","approved_by":actor})
    rs.status = "active"
    rs.approved_by = actor
    rs.effective_from = rs.effective_from or _now()[:10]
    S.rules_versions.append({"rule_id":rs.id,"version":rs.version,"status":"active","approved_by":actor})
    S._audit(actor,"rules_activate",rs.id, rule_version=rs.version)
    return {"ok":True,"rule":rs.model_dump()}

def rules_rollback(rule_id, to_version, actor):
    """Human rollback: re-activate a prior version row if present; retire current."""
    rs = next((r for r in S.rules if r.id==rule_id), None)
    if not rs: return {"error":"not found"}
    prior = next((v for v in reversed(S.rules_versions)
                  if v.get("rule_id")==rule_id and v.get("version")==to_version), None)
    if not prior: return {"error":"version_not_found"}
    rs.version = to_version
    rs.status = "active"
    rs.approved_by = actor
    S.rules_versions.append({"rule_id":rs.id,"version":to_version,"status":"active","approved_by":actor,"rollback":True})
    S._audit(actor,"rules_rollback",rs.id, rule_version=to_version, evidence={"from":prior})
    return {"ok":True,"rule":rs.model_dump()}

# ---------- Phase-2: Enterprise DW + Interop Hub scaffold ----------
def dw_hub():
    return {"ok":True,"feeds":S.dw_feeds,"entity_counts":_dw_counts(),"append_only_provenance":True}

def _dw_counts():
    counts={}
    for r in S.dw_records:
        counts[r.entity_type]=counts.get(r.entity_type,0)+1
    return counts

def dw_entities(entity_type=None):
    rows = S.dw_records
    if entity_type:
        rows = [r for r in rows if r.entity_type==entity_type]
    return [r.model_dump() for r in rows]

def dw_ingest(entity_type, source, payload, actor="system"):
    """Ingest a synthetic DW row; attaches provenance. No PHI required."""
    rec = M.DWRecord(entity_type=entity_type, source=source, payload=payload or {})
    S.dw_records.append(rec)
    S._audit(actor,"dw_ingest",rec.id, evidence={"entity_type":entity_type,"source":source})
    if S.provenance:
        rec.provenance_id = S.provenance[-1].id
    return {"ok":True,"record":rec.model_dump()}


# ---------- Population Health: 26. Risk Stratification (XL) ----------
def pop_risk_stratify(band=None):
    """Panel-wide risk bands (deterministic). Drill to patient + contributors. Propose-only read."""
    rows = list(S.risk_bands)
    if band:
        rows = [r for r in rows if r.band == band]
    by_band = {}
    for r in rows:
        by_band.setdefault(r.band, 0)
        by_band[r.band] += 1
    return {"ok":True,"counts":by_band,"rows":[r.model_dump() for r in rows],
            "model":"V28","version":"0.28.0","propose_only":True}

def pop_risk_patient(patient_ref):
    """Single-member stratification — uses identity-aware resolve when possible."""
    pid = _resolve_patient(patient_ref) or patient_ref
    row = next((r for r in S.risk_bands if r.patient_id==pid), None)
    if not row:
        # compute on the fly
        p = next((x for x in S.patients if x.id==pid), None)
        if not p: return {"error":"patient not found"}
        return risk_stratify(pid)
    return {"ok":True,"row":row.model_dump(),"tcm":risk_stratify(pid)}

# ---------- Population Health: 27. MIH / Community Paramedicine (XL) ----------
def mih_queue(status=None):
    """MIH dispatch queue. Proposed episodes need human accept before field dispatch."""
    rows = list(S.mih_episodes)
    if status:
        rows = [m for m in rows if m.status==status]
    return {"ok":True,"episodes":[m.model_dump() for m in rows],
            "proposed":sum(1 for m in S.mih_episodes if m.status=="proposed"),
            "propose_only":True}

def mih_propose(patient_ref, reason, priority="routine", sdoh_needs=None, actor="hermes"):
    """Propose-only MIH dispatch — never auto-dispatches to field."""
    pid = _resolve_patient(patient_ref) or patient_ref
    p = next((x for x in S.patients if x.id==pid), None)
    if not p: return {"error":"patient not found"}
    ep = M.MIHEpisode(patient_id=pid, reason=reason, priority=priority,
                      status="proposed", sdoh_needs=sdoh_needs or [])
    S.mih_episodes.append(ep)
    S._audit(actor,"mih_propose",ep.id, evidence={"patient_id":pid,"priority":priority,"status":"proposed"})
    return {"ok":True,"status":"PROPOSED","needs":"human_confirmation","episode":ep.model_dump()}

def mih_accept(episode_id, actor):
    """Human accepts proposed MIH episode (not AI)."""
    from models import _now
    ep = next((m for m in S.mih_episodes if m.id==episode_id), None)
    if not ep: return {"error":"not found"}
    if ep.status != "proposed": return {"error":"not_proposed","status":ep.status}
    ep.status = "accepted"
    ep.updated = _now()
    S._audit(actor,"mih_accept",ep.id, evidence={"patient_id":ep.patient_id})
    return {"ok":True,"episode":ep.model_dump()}

# ---------- Population Health: 28. Provider Performance Command Center (L) ----------
def provider_performance():
    """Provider scorecards with drill refs (opaque ids). Every value drills."""
    rows = [r.model_dump() for r in S.provider_scorecards] or [
        {**p.model_dump(),"panel_size":len(S.patients),"open_gaps":p.gaps,
         "mih_referrals":0,"intervention_delta_cost":0.0,"drill":{}}
        for p in S.provider_metrics]
    return {"ok":True,"providers":rows,"propose_only":True}

# ---------- Population Health: 29. Intervention Outcomes (L) ----------
def intervention_outcomes():
    """Before/after deltas for ED/readmissions/cost. AI proposes; humans close."""
    out=[]
    for i in S.interventions:
        before_c = i.before.get("cost",0) or 0
        after_c = i.after.get("cost",0) or 0
        out.append({**i.model_dump(),
                    "delta_ed":(i.before.get("ed",0) or 0)-(i.after.get("ed",0) or 0),
                    "delta_readmissions":(i.before.get("readmissions",0) or 0)-(i.after.get("readmissions",0) or 0),
                    "delta_cost":before_c-after_c})
    return {"ok":True,"interventions":out,
            "total_cost_avoided":sum(x["delta_cost"] for x in out),
            "propose_only":True}

def intervention_propose(patient_ref, kind, before=None, actor="hermes"):
    """Propose a new intervention tracking row (no clinical write)."""
    from models import _now
    pid = _resolve_patient(patient_ref) or patient_ref
    if not any(p.id==pid for p in S.patients): return {"error":"patient not found"}
    i = M.Intervention(patient_id=pid, kind=kind, started=_now(),
                       before=before or {"ed":0,"readmissions":0,"cost":0}, after={})
    S.interventions.append(i)
    S._audit(actor,"intervention_propose",i.id, evidence={"kind":kind,"patient_id":pid})
    return {"ok":True,"status":"PROPOSED","needs":"human_confirmation","intervention":i.model_dump()}

# ---------- Population Health: 30. Frailty / ACP (M) ----------
def frailty_acp(patient_ref=None):
    rows = list(S.frailty)
    if patient_ref:
        pid = _resolve_patient(patient_ref) or patient_ref
        rows = [f for f in rows if f.patient_id==pid]
    return {"ok":True,"rows":[f.model_dump() for f in rows],
            "frail_count":sum(1 for f in S.frailty if f.frailty_band=="frail"),
            "acp_proposed":sum(1 for f in S.frailty if f.acp_status=="proposed"),
            "propose_only":True}

def frailty_propose_acp(patient_ref, goals=None, actor="hermes"):
    """Propose ACP outreach — human documents; AI never documents ACP alone."""
    from models import _now
    pid = _resolve_patient(patient_ref) or patient_ref
    row = next((f for f in S.frailty if f.patient_id==pid), None)
    if not row:
        row = M.FrailtyACP(patient_id=pid, frailty_score=0.5, frailty_band="prefrail",
                           acp_status="proposed", goals=goals or [])
        S.frailty.append(row)
    else:
        row.acp_status = "proposed"
        if goals: row.goals = goals
        row.updated = _now()
    S._audit(actor,"frailty_propose_acp",row.id, evidence={"patient_id":pid,"status":"proposed"})
    return {"ok":True,"status":"PROPOSED","needs":"human_confirmation","row":row.model_dump()}

# ---------- Population Health: 31–32. CPHO Command Center (L) ----------
def cpho_command_center():
    """Exec CPHO one-glance: risk bands, MIH queue, scorecards, interventions, frailty, TCM, identity."""
    bands = {}
    for r in S.risk_bands:
        bands[r.band] = bands.get(r.band, 0) + 1
    return {
        "ok":True,
        "role":"cpho",
        "propose_only":True,
        "risk":{"counts":bands,"high_or_above":bands.get("high",0)+bands.get("very_high",0)},
        "mih":{"proposed":sum(1 for m in S.mih_episodes if m.status=="proposed"),
               "active":sum(1 for m in S.mih_episodes if m.status in ("accepted","en_route")),
               "episodes":len(S.mih_episodes)},
        "providers":provider_performance()["providers"],
        "interventions":{"count":len(S.interventions),
                         "total_cost_avoided":intervention_outcomes()["total_cost_avoided"]},
        "frailty":{"frail":sum(1 for f in S.frailty if f.frailty_band=="frail"),
                   "acp_proposed":sum(1 for f in S.frailty if f.acp_status=="proposed")},
        "tcm":tcm_board(),
        "identity_unmatched":sum(1 for i in S.identity if i.match_status in ("unmatched","conflict")),
        "dw_feeds":len(getattr(S,"dw_feeds",[])),
    }


# ---------- Phase-3: Payer / Solis reconciliation ----------
def payer_reconcile_status(payer=None):
    """Summary of roster reconcile state. Never auto-overwrites identity conflicts."""
    rows = list(S.payer_roster)
    if payer:
        rows = [r for r in rows if r.payer.lower()==payer.lower()]
    ex = [e for e in S.reconcile_exceptions if e.status=="open"]
    if payer:
        ex = [e for e in ex if e.payer.lower()==payer.lower()]
    return {
        "ok":True,
        "propose_only":True,
        "policy":{"no_overwrite_unresolved_identity_conflicts":True,
                  "exception_queue_required":True},
        "roster_count":len(rows),
        "matched":sum(1 for r in rows if r.reconcile_status=="matched"),
        "unmatched":sum(1 for r in rows if r.reconcile_status=="unmatched"),
        "exceptions_open":len(ex),
        "skipped_conflicts":sum(1 for r in rows if r.reconcile_status=="exception"),
        "applied":sum(1 for r in rows if r.reconcile_status=="applied"),
        "contracts":[c.model_dump() for c in S.contracts],
        "last_runs":[r.model_dump() for r in S.reconcile_runs[-5:]],
    }

def payer_exception_queue(status="open"):
    rows = list(S.reconcile_exceptions)
    if status:
        rows = [e for e in rows if e.status==status]
    return {"ok":True,"exceptions":[e.model_dump() for e in rows],"propose_only":True}

def payer_roster(payer=None, reconcile_status=None):
    rows = list(S.payer_roster)
    if payer:
        rows = [r for r in rows if r.payer.lower()==payer.lower()]
    if reconcile_status:
        rows = [r for r in rows if r.reconcile_status==reconcile_status]
    return {"ok":True,"rows":[r.model_dump() for r in rows]}

def _conflict_patient_ids():
    """Patients with open identity_conflict exceptions — never overwrite."""
    return {e.patient_id for e in S.reconcile_exceptions
            if e.status=="open" and e.kind=="identity_conflict" and e.patient_id}

def payer_reconcile_run(payer="Solis", apply=False, actor="system"):
    """Dry-run (default) or propose-apply Solis roster.
    Unresolved identity conflicts are skipped — never overwrite.
    apply=True only records a PROPOSED apply; human must confirm via /apply."""
    from models import _now
    conflict_pids = _conflict_patient_ids()
    matched=unmatched=exceptions=skipped=0
    for row in S.payer_roster:
        if payer and row.payer.lower()!=payer.lower():
            continue
        # link via identity if possible
        idrec = next((i for i in S.identity
                      if i.source_ref==row.source_ref or
                      (i.source_system in ("solis","ensure") and i.source_ref.endswith(row.source_ref[-3:])
                       and False)), None)
        # simpler: match by existing matched_patient_id or MRN-like identity
        if not row.matched_patient_id:
            idrec = next((i for i in S.identity if i.source_ref==row.source_ref and i.patient_id), None)
            if idrec:
                row.matched_patient_id = idrec.patient_id
        if row.matched_patient_id and row.matched_patient_id in conflict_pids:
            row.reconcile_status = "exception"
            row.exception_reason = "unresolved_identity_conflict"
            row.updated = _now()
            skipped += 1
            # ensure exception visible
            if not any(e.source_ref==row.source_ref and e.kind=="identity_conflict" and e.status=="open"
                       for e in S.reconcile_exceptions):
                S.reconcile_exceptions.append(M.ReconcileException(
                    kind="identity_conflict", source_ref=row.source_ref,
                    patient_id=row.matched_patient_id, payer=row.payer, contract=row.contract,
                    detail="skipped — unresolved identity conflict; no overwrite"))
            continue
        if row.reconcile_status == "exception" or row.exception_reason:
            exceptions += 1
            continue
        if row.matched_patient_id:
            row.reconcile_status = "matched"
            matched += 1
        else:
            row.reconcile_status = "unmatched"
            unmatched += 1
            if not any(e.source_ref==row.source_ref and e.kind=="unmatched" and e.status=="open"
                       for e in S.reconcile_exceptions):
                S.reconcile_exceptions.append(M.ReconcileException(
                    kind="unmatched", source_ref=row.source_ref, payer=row.payer,
                    contract=row.contract, detail="no CarePilot patient for roster ref"))
        row.updated = _now()

    mode = "proposed_apply" if apply else "dry_run"
    run = M.ReconcileRun(payer=payer, mode=mode, matched=matched, unmatched=unmatched,
                         exceptions=exceptions, skipped_conflicts=skipped, applied=0, actor=actor)
    S.reconcile_runs.append(run)
    S._audit(actor, "payer_reconcile_run", run.id,
             evidence={"payer":payer,"mode":mode,"matched":matched,"unmatched":unmatched,
                       "exceptions":exceptions,"skipped_conflicts":skipped})
    out = {"ok":True,"run":run.model_dump(),"propose_only":True,
           "policy":{"no_overwrite_unresolved_identity_conflicts":True}}
    if apply:
        out["status"] = "PROPOSED"
        out["needs"] = "human_confirmation"
    return out

def payer_reconcile_apply(run_id, actor):
    """Human confirms a proposed_apply run — applies only non-conflict matched rows."""
    from models import _now
    run = next((r for r in S.reconcile_runs if r.id==run_id), None)
    if not run: return {"error":"run_not_found"}
    if run.mode not in ("proposed_apply","dry_run"):
        return {"error":"not_applyable","mode":run.mode}
    conflict_pids = _conflict_patient_ids()
    applied = 0
    for row in S.payer_roster:
        if row.payer.lower()!=run.payer.lower(): continue
        if row.reconcile_status!="matched": continue
        if row.matched_patient_id in conflict_pids:
            row.reconcile_status = "exception"
            row.exception_reason = "unresolved_identity_conflict"
            continue
        # apply = mark applied + sync product onto patient (non-PHI synthetic field only)
        pt = next((p for p in S.patients if p.id==row.matched_patient_id), None)
        if pt and row.product:
            pt.product = row.product
            pt.payer = row.payer
            pt.timestamps["updated"] = _now()
        row.reconcile_status = "applied"
        row.updated = _now()
        applied += 1
    run.mode = "applied"
    run.applied = applied
    S._audit(actor, "payer_reconcile_apply", run.id, evidence={"applied":applied})
    return {"ok":True,"run":run.model_dump(),"applied":applied}

def payer_exception_resolve(exc_id, actor, resolution="resolved"):
    """Human resolves or dismisses an exception — unlocks future overwrite/apply."""
    from models import _now
    ex = next((e for e in S.reconcile_exceptions if e.id==exc_id), None)
    if not ex: return {"error":"not_found"}
    if resolution not in ("resolved","dismissed"):
        return {"error":"bad_resolution"}
    ex.status = resolution
    ex.updated = _now()
    S._audit(actor, "payer_exception_resolve", ex.id,
             evidence={"resolution":resolution,"source_ref":ex.source_ref})
    return {"ok":True,"exception":ex.model_dump()}

def payer_contract_reconcile():
    """Contract-level paid/incurred/est vs roster membership counts (synthetic)."""
    rows=[]
    for c in S.contracts:
        members = [r for r in S.payer_roster if r.contract==c.contract]
        rows.append({
            **c.model_dump(),
            "roster_members":len(members),
            "roster_matched":sum(1 for r in members if r.reconcile_status in ("matched","applied")),
            "roster_exceptions":sum(1 for r in members if r.reconcile_status=="exception"),
            "variance_paid_incurred":round(c.incurred - c.paid, 2),
        })
    return {"ok":True,"contracts":rows,"propose_only":True}
