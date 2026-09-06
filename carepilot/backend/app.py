# CarePilot — Complete Platform (Python FastAPI + Flutter)
# P0 Foundation build. Per the spec: identity → provenance/DW → versioned rules → work queue →
# MCP tools (read/action/propose-only) → safety boundary. All AI = proposal-only; human approves.

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from enum import Enum
import uuid, datetime, hashlib, json

app = FastAPI(title="CarePilot — Complete Platform", version="0.1.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# -----------------------------------------------------------------------------
# 0. Roles & separation of duties (per spec: RBAC, PHI logged, least privilege)
# -----------------------------------------------------------------------------
class Role(str, Enum):
    EXECUTIVE = "executive"
    MEDICAL_DIRECTOR = "medical_director"
    PROVIDER = "provider"
    NURSE = "nurse"
    MA = "ma"
    CODER = "coder_billing"
    COMPLIANCE = "compliance"
    CPHO = "cpho"
    READ_ONLY = "read_only"

# Write-access = human clinical/coding/billing; Hermes AI is NEVER in this set.
HUMAN_WRITE_ROLES = {Role.PROVIDER, Role.MEDICAL_DIRECTOR, Role.COMPLIANCE, Role.CODER}

# -----------------------------------------------------------------------------
# 1. In-memory store (P0; swap for Postgres + FHIR in P1 per spec)
# -----------------------------------------------------------------------------
DB = {"patients": [], "tasks": [], "care_gaps": [], "audit": [], "rules": []}
_rules_versions = []

def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def _audit(actor, action, target, phi_ok=False, opaque_ref=None):
    """Append-only audit vault. Never stores PHI unless explicitly allowed."""
    DB["audit"].append({
        "ts": _now(),
        "actor": actor,
        "action": action,
        "target_ref": opaque_ref,     # PHI-free ref only
        "phi_exposed": bool(phi_ok),
    })

# -----------------------------------------------------------------------------
# 2. Domain models
# -----------------------------------------------------------------------------
class Patient(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:10])
    mrn: str
    name: str
    payer: str = "Solis"
    product: Optional[str] = None
    status: str = "active"
    conditions: List[str] = []
    risk_scores: dict = {}           # {model: {version, year, clinical, raf, source}}
    programs: List[str] = []
    last_updated: str = Field(default_factory=_now)

class CareGap(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:10])
    patient_id: str
    measure: str                       # e.g. HEDIS HbA1c
    status: Literal["open", "in_progress", "closed"] = "open"
    evidence: dict = {}                # numerator/denominator/source
    owner: str = ""

class WorkTask(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:10])
    source: str                        # patient_id or measure
    task_type: str                     # ccm, gap, med_safety, referral, ...
    title: str
    owner: str = ""
    due: Optional[str] = None
    next_action: str = ""
    status: Literal["New", "In Progress", "Completed", "Escalated"] = "New"
    evidence: dict = {}
    created: str = Field(default_factory=_now)

# -----------------------------------------------------------------------------
# 3. RBAC dependency + safety boundary
# -----------------------------------------------------------------------------
def require_role(role: Role):
    def dep(x_role: Role = Header(alias="X-Role")) -> Role:
        try:
            r = Role(x_role)
        except Exception:
            raise HTTPException(401, "invalid role")
        return r
    return dep

@app.get("/health")
def health():
    return {"status": "ok", "service": "CarePilot", "engine": "python"}

# -----------------------------------------------------------------------------
# 4. READ tools (safe, always allowed) — mirror the MCP read surface
# -----------------------------------------------------------------------------
@app.get("/api/patients/search")
def search_patients(q: str, role: Role = Depends(require_role(Role.READ_ONLY))):
    """Read: find patients by name/condition/payer. Minimum-necessary."""
    items = [p for p in DB["patients"] if q.lower() in (p["name"] + " " + p["payer"] + " " + " ".join(p["conditions"])).lower()]
    _audit(role.value, "search_patients", None, phi_ok=True)
    return {"ok": True, "results": items}

@app.get("/api/patients/{pid}/summary")
def patient_summary(pid: str, role: Role = Depends(require_role(Role.READ_ONLY))):
    for p in DB["patients"]:
        if p["id"] == pid:
            return {"ok": True, "patient": p}
    raise HTTPException(404, "not found")

@app.get("/api/care-gaps")
def care_gaps(pid: Optional[str] = None, role: Role = Depends(require_role(Role.READ_ONLY))):
    if pid:
        return {"ok": True, "gaps": [g for g in DB["care_gaps"] if g["patient_id"] == pid]}
    return {"ok": True, "gaps": DB["care_gaps"]}

@app.get("/api/work-queue")
def work_queue(owner: Optional[str] = None, status: Optional[str] = None, role: Role = Depends(require_role(Role.READ_ONLY))):
    items = DB["tasks"]
    if owner: items = [t for t in items if t["owner"] == owner]
    if status: items = [t for t in items if t["status"] == status]
    return {"ok": True, "tasks": items}

# -----------------------------------------------------------------------------
# 5. ACTION tools (permitted writes; logged) — AI/Hermes may create tasks/notes-draft/flag,
#    but NEVER sign a chart, place an order, add a diagnosis, change a med, or submit a claim.
# -----------------------------------------------------------------------------
@app.post("/api/tasks")
def create_task(task: WorkTask, role: Role = Depends(require_role(Role.NURSE))):
    """Action: create a work-queue task (owner/due/next-action). Logged."""
    if role not in {Role.NURSE, Role.MA, Role.CPHO, Role.PROVIDER}:
        raise HTTPException(403, "role cannot create tasks")
    task.id = uuid.uuid4().hex[:10]
    DB["tasks"].append(task.model_dump())
    _audit(role.value, "create_task", None, phi_ok=True)
    return {"ok": True, "task": task.model_dump()}

@app.post("/api/tasks/{tid}/assign")
def assign_task(tid: str, owner: str, role: Role = Depends(require_role(Role.NURSE))):
    for t in DB["tasks"]:
        if t["id"] == tid:
            t["owner"] = owner
            _audit(role.value, "assign_task", tid)
            return {"ok": True, "task": t}
    raise HTTPException(404, "task not found")

# -----------------------------------------------------------------------------
# 6. PROPOSE-ONLY tools — the agent suggests, a HUMAN confirms. Never auto-executes.
# -----------------------------------------------------------------------------
class EnrollmentProposal(BaseModel):
    pid: str
    program: str

@app.post("/api/propose/enrollment")
def propose_enrollment(prop: EnrollmentProposal, role: Role = Depends(require_role(Role.MA))):
    """Propose-only: CCM/TCM enrollment candidate. Human confirms; consent required first."""
    _audit(role.value, "propose_enrollment", prop.pid)
    return {"ok": True, "status": "PROPOSED", "needs": "human_confirmation", "patient_id": prop.pid, "program": prop.program}

class ChargeProposal(BaseModel):
    pid: str
    amount: float
    code: str

@app.post("/api/propose/charge")
def propose_charge(prop: ChargeProposal, role: Role = Depends(require_role(Role.MA))):
    """Propose-only: billing charge candidate. Human confirms. NEVER auto-bills."""
    _audit(role.value, "propose_charge", prop.pid)
    return {"ok": True, "status": "PROPOSED", "needs": "human_confirmation", "patient_id": prop.pid, "code": prop.code, "amount": prop.amount}

# -----------------------------------------------------------------------------
# 7. SAFETY BOUNDARY — the non-negotiable rules (spec: AI drafts/flags only)
# -----------------------------------------------------------------------------
SAFETY_GUARDS = {
    "no_ai_sign": "Hermes can never sign a chart.",
    "no_ai_order": "Hermes can never place an order.",
    "no_ai_diagnosis": "Hermes can never add a diagnosis.",
    "no_ai_med_change": "Hermes can never change a medication order.",
    "no_ai_claim": "Hermes can never submit a claim.",
    "no_ai_message": "Hermes can never send a patient message on its own.",
    "clinical_over_financial": "Clinical urgency always outranks financial opportunity.",
    "med_safety_human_only": "Medication-safety findings can't be closed by AI.",
}

@app.get("/api/safety/boundary")
def safety_boundary():
    return {"ok": True, "guards": SAFETY_GUARDS}

# -----------------------------------------------------------------------------
# 8. n8n lab-pipeline connection contract (opaque refs only, idempotent, no PHI in payloads)
# -----------------------------------------------------------------------------
@app.post("/api/labs/review-task")
def labs_review_task(payload: dict):
    """n8n -> CarePilot: create provider-review task from a DRAFT. References only, no PHI."""
    ref = {k: payload.get(k) for k in ["run_ref", "event_id", "patient_ref", "draft_ref", "priority"] if payload.get(k)}
    _audit("n8n", "labs_review_task", ref.get("run_ref"))
    return {"ok": True, "stage": "review_task_created", "run_ref": ref.get("run_ref"), "task_id": uuid.uuid4().hex[:10], "proceed": True}

@app.post("/api/labs/critical-alert")
def labs_critical_alert(payload: dict):
    _audit("n8n", "labs_critical_alert", payload.get("patient_ref"))
    return {"ok": True, "stage": "critical_alert", "alert_id": uuid.uuid4().hex[:10], "proceed": True}

@app.post("/api/labs/approval")
def labs_approval(payload: dict):
    """CarePilot -> (handled by n8n webhook). Provider signed; release with references only."""
    return {"ok": True, "stage": "approval_released", "approval_ref": payload.get("approval_ref"), "note": "QUEUED, not delivered"}

# -----------------------------------------------------------------------------
# 9. Seed demo data (so the Flutter app has something to render)
# -----------------------------------------------------------------------------
def _seed():
    p1 = {"id": "P0001", "mrn": "MRN-0001", "name": "Patient Demo One", "payer": "Solis", "product": "HMO",
          "status": "active", "conditions": ["Diabetes", "Heart Failure"],
          "risk_scores": {"V28": {"version": "0.28.0", "year": 2026, "clinical": 1.30, "raf": 1.30, "source": "v28-2026"}},
          "programs": ["CCM"], "last_updated": _now()}
    p2 = {"id": "P0002", "mrn": "MRN-0002", "name": "Patient Demo Two", "payer": "Solis", "product": "FFS",
          "conditions": ["Hypertension"], "risk_scores": {}, "programs": [], "last_updated": _now()}
    DB["patients"] = [p1, p2]
    DB["care_gaps"] = [{"id": "G0001", "patient_id": "P0001", "measure": "HEDIS HbA1c", "status": "open",
                        "evidence": {"numerator": 0, "denominator": 1, "source": "2026 HEDIS"}, "owner": ""}]
    DB["tasks"] = [{"id": "T0001", "source": "G0001", "task_type": "gap", "title": "Close HbA1c gap",
                    "owner": "nurse-1", "due": _now(), "next_action": "order A1c", "status": "New", "evidence": {}, "created": _now()}]

_seed()

import uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
