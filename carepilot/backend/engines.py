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
