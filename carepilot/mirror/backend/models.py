"""CarePilot domain models — all entities across the 39-capability platform."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Literal
from enum import Enum
import uuid, datetime

def _now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def _uid(prefix): return f"{prefix}-{uuid.uuid4().hex[:8]}"

# ---------- Identity & Provenance ----------
class Role(str, Enum):
    EXECUTIVE="executive"; MEDICAL_DIRECTOR="medical_director"; PROVIDER="provider"
    NURSE="nurse"; MA="ma"; CODER="coder_billing"; COMPLIANCE="compliance"; CPHO="cpho"; READ_ONLY="read_only"

HUMAN_WRITE_ROLES = {Role.PROVIDER, Role.MEDICAL_DIRECTOR, Role.COMPLIANCE, Role.CODER, Role.NURSE, Role.MA, Role.CPHO}

class Patient(BaseModel):
    id: str = Field(default_factory=lambda: _uid("P"))
    mrn: str
    name: str
    dob: Optional[str] = None
    payer: str = "Solis"; product: Optional[str] = None
    status: str = "active"
    conditions: List[str] = []
    risk_scores: Dict[str, dict] = Field(default_factory=dict)  # {model: {version,year,clinical,raf,source}}
    programs: List[str] = []
    mih_flag: bool = False
    timestamps: Dict[str, str] = Field(default_factory=lambda: {"created": _now(), "updated": _now()})

class CareGap(BaseModel):
    id: str = Field(default_factory=lambda: _uid("G"))
    patient_id: str; measure: str; status: Literal["open","in_progress","closed"]="open"
    evidence: dict = Field(default_factory=dict); owner: str=""; nav: str=""

class WorkTask(BaseModel):
    id: str = Field(default_factory=lambda: _uid("T"))
    source: str; task_type: str; title: str
    owner: str=""; due: Optional[str]=None; next_action: str=""
    status: Literal["New","In Progress","Completed","Escalated"]="New"
    evidence: dict = Field(default_factory=dict); created: str = Field(default_factory=_now)

class RiskScore(BaseModel):
    id: str = Field(default_factory=lambda: _uid("R"))
    patient_id: str; model: str; version: str; year: int; clinical: float; raf: float
    source: str = "v28"; components: dict = Field(default_factory=dict)  # demographics, diagnoses, total

class Referral(BaseModel):
    id: str = Field(default_factory=lambda: _uid("REF"))
    patient_id: str; specialist: str; status: Literal["ordered","attended","reviewed","closed"]="ordered"
    cost: float = 0.0; access_days: Optional[int] = None

class Claim(BaseModel):
    id: str = Field(default_factory=lambda: _uid("C"))
    patient_id: str; payer: str; contract: str; amount: float = 0.0
    status: Literal["identified","validated","submitted","recovered"]="identified"
    kind: Literal["duplicate","pricing_variance","cob","normal"]="normal"
    recovery_proof: Optional[str] = None

class MedicationAlert(BaseModel):
    id: str = Field(default_factory=lambda: _uid("M"))
    patient_id: str; finding: str; severity: Literal["info","warning","critical"]="warning"
    status: Literal["open","reviewed","closed"]="open"
    type: Literal["ordered","dispensed","given","billed"]="ordered"

class Hospitalization(BaseModel):
    id: str = Field(default_factory=lambda: _uid("ADM"))
    patient_id: str; kind: Literal["inpatient","er"]="inpatient"; admit_dt: str; discharge_dt: Optional[str]=None

class Intervention(BaseModel):
    id: str = Field(default_factory=lambda: _uid("INT"))
    patient_id: str; kind: str; started: str
    before: dict = Field(default_factory=dict)  # {ed, readmissions, cost}
    after: dict = Field(default_factory=dict)

class DrugUse(BaseModel):
    id: str = Field(default_factory=lambda: _uid("DRUG"))
    patient_id: str; drug: str; cost: float = 0.0; adherence: Optional[float] = None

class CasePlan(BaseModel):
    id: str = Field(default_factory=lambda: _uid("CP"))
    patient_id: str; goals: List[str] = []; interventions: List[str] = []
    barriers: List[str] = []; owner: str = ""; status: str = "active"

class ProviderMetric(BaseModel):
    id: str = Field(default_factory=lambda: _uid("PV"))
    provider: str; quality: float = 0.0; raf: float = 0.0
    gaps: int = 0; utilization: float = 0.0

class ContractPerf(BaseModel):
    id: str = Field(default_factory=lambda: _uid("CON"))
    contract: str; paid: float = 0.0; incurred: float = 0.0; est: float = 0.0
    pmpm: float = 0.0

# ---------- Transition of Care (TCM) Orchestration ----------
class Cohort(BaseModel):
    id: str = Field(default_factory=lambda: _uid("CO"))
    name: str; kind: Literal["ccm","tcm","high_risk","behavioral","post_discharge","complex"]="tcm"
    criteria: dict = Field(default_factory=dict)  # {min_conditions, programs, flags}
    patients: List[str] = []

class TCMCase(BaseModel):
    id: str = Field(default_factory=lambda: _uid("TCM"))
    patient_id: str; status: Literal["open","active","closed"]="open"
    trigger: Literal["admit","discharge"] = "admit"
    cohort_id: str = ""
    checklist: List[dict] = Field(default_factory=list)  # {doc, status}
    alerts: List[str] = Field(default_factory=list)
    care_team: List[str] = []  # case-manager / community-paramedic-NP / hospital-nurse
    home_health: Optional[dict] = None
    timestamps: Dict[str, str] = Field(default_factory=lambda: {"created":_now(),"updated":_now()})

class TCMStep(BaseModel):
    id: str = Field(default_factory=lambda: _uid("STEP"))
    case_id: str; seq: int; name: str; status: Literal["pending","done","alerted"]="pending"
    alert_level: Literal["info","warning","critical"]="warning"
    due_in_hours: int = 24; assignee: str = ""

class CareTeam(BaseModel):
    id: str = Field(default_factory=lambda: _uid("TEAM"))
    patient_id: str; role: str  # case_manager / community_paramedic_np / hospital_nurse
    name: str; active: bool = True

class TCMEvent(BaseModel):
    id: str = Field(default_factory=lambda: _uid("EVT"))
    patient_id: str; event: Literal["admit","discharge","er_visit"]="admit"
    source: str = ""  # mirth_adt / emedical / ensure
    ts: str = Field(default_factory=_now)
    facility: str = ""; admit_dt: Optional[str] = None; discharge_dt: Optional[str] = None

class PostAcutePlacement(BaseModel):
    id: str = Field(default_factory=lambda: _uid("PLACE"))
    patient_id: str; kind: Literal["snf","alf","home_health","ihh","iop","dme","none"]="none"
    facility: str = ""; arranged: str = Field(default_factory=_now); rn_visit_before: bool = False

class ReadmissionRisk(BaseModel):
    id: str = Field(default_factory=lambda: _uid("RR"))
    patient_id: str; score: float; band: Literal["low","medium","high","very_high"]="medium"
    contributors: List[str] = []; model: str = "v1"; ts: str = Field(default_factory=_now)

class SDOHScreen(BaseModel):
    id: str = Field(default_factory=lambda: _uid("SDOH"))
    patient_id: str; food: str = "ok"; transport: str = "ok"; housing: str = "ok"; isolation: str = "ok"
    needs: List[str] = []; referral: str = ""

class SLABreach(BaseModel):
    id: str = Field(default_factory=lambda: _uid("SLA"))
    case_id: str; step: str; overdue_hours: float; severity: Literal["warning","critical"]="warning"
    ts: str = Field(default_factory=_now)

class TCMBilling(BaseModel):
    id: str = Field(default_factory=lambda: _uid("BILL"))
    patient_id: str; code: str; desc: str; status: Literal["proposed","validated","submitted","paid"]="proposed"
    value: float = 0.0; evidence: dict = Field(default_factory=dict)


# ---------- Phase-2: Identity / Provenance / Rules / DW ----------
class IdentityRecord(BaseModel):
    """Cross-source identity link (synthetic refs only). Unmatched stay in queue."""
    id: str = Field(default_factory=lambda: _uid("ID"))
    source_system: str  # emedpractice / openemr / mirth / ensure / solis
    source_ref: str     # opaque external ref (MRN-style synthetic ok)
    patient_id: Optional[str] = None  # CarePilot patient id when matched
    match_status: Literal["matched","unmatched","conflict","proposed"]="unmatched"
    confidence: float = 0.0
    conflict_reason: Optional[str] = None
    created: str = Field(default_factory=_now)
    updated: str = Field(default_factory=_now)

class ProvenanceEvent(BaseModel):
    """Append-only provenance/evidence record. Never mutate after create."""
    id: str = Field(default_factory=lambda: _uid("PROV"))
    ts: str = Field(default_factory=_now)
    actor: str
    action: str
    subject_ref: Optional[str] = None
    rule_version: Optional[str] = None
    model_version: Optional[str] = None
    evidence: dict = Field(default_factory=dict)
    phi: bool = False

class RuleSet(BaseModel):
    """Versioned rules registry entry (coding/model/prompt/quality)."""
    id: str = Field(default_factory=lambda: _uid("RULE"))
    kind: Literal["coding","model","prompt","quality","risk"]="coding"
    name: str
    version: str
    status: Literal["draft","sandbox","active","retired"]="draft"
    effective_from: Optional[str] = None
    approved_by: Optional[str] = None
    sandbox_passed: bool = False
    payload: dict = Field(default_factory=dict)
    created: str = Field(default_factory=_now)

class DWRecord(BaseModel):
    """Minimal enterprise DW / interop hub row (synthetic feeds)."""
    id: str = Field(default_factory=lambda: _uid("DW"))
    entity_type: str  # member / claim / encounter / feed
    source: str
    payload: dict = Field(default_factory=dict)
    ingested_at: str = Field(default_factory=_now)
    provenance_id: Optional[str] = None


# ---------- Population Health (caps ~26–32) ----------
class RiskBand(BaseModel):
    """Panel risk stratification row (deterministic bands)."""
    id: str = Field(default_factory=lambda: _uid("RB"))
    patient_id: str
    band: Literal["low","medium","high","very_high"]="medium"
    raf: float = 0.0
    contributors: List[str] = []
    model: str = "V28"
    version: str = "0.28.0"
    mih_candidate: bool = False
    updated: str = Field(default_factory=_now)

class MIHEpisode(BaseModel):
    """MIH / Community Paramedicine episode — propose-only dispatch; humans confirm."""
    id: str = Field(default_factory=lambda: _uid("MIH"))
    patient_id: str
    reason: str
    priority: Literal["routine","urgent","critical"]="routine"
    status: Literal["proposed","accepted","en_route","complete","cancelled"]="proposed"
    assignee: str = "community_paramedic_np"
    sdoh_needs: List[str] = []
    provenance_id: Optional[str] = None
    created: str = Field(default_factory=_now)
    updated: str = Field(default_factory=_now)

class FrailtyACP(BaseModel):
    """Frailty screen + Advance Care Planning status (propose-only for ACP outreach)."""
    id: str = Field(default_factory=lambda: _uid("FRA"))
    patient_id: str
    frailty_score: float = 0.0  # 0-1
    frailty_band: Literal["fit","prefrail","frail"]="fit"
    acp_status: Literal["none","discussed","documented","proposed"]="none"
    goals: List[str] = []
    barriers: List[str] = []
    updated: str = Field(default_factory=_now)

class ProviderScorecardRow(BaseModel):
    """Provider Performance Command Center row with drill refs (opaque)."""
    id: str = Field(default_factory=lambda: _uid("PSC"))
    provider: str
    panel_size: int = 0
    quality: float = 0.0
    raf: float = 0.0
    open_gaps: int = 0
    utilization: float = 0.0
    mih_referrals: int = 0
    intervention_delta_cost: float = 0.0
    drill: dict = Field(default_factory=dict)  # {gap_refs, util_refs} synthetic


# ---------- Phase-3: Payer / Solis reconciliation ----------
class PayerRosterRow(BaseModel):
    """Synthetic payer/Solis roster row awaiting reconcile."""
    id: str = Field(default_factory=lambda: _uid("PAY"))
    payer: str = "Solis"
    contract: str = "Solis-HMO-2026"
    source_ref: str  # opaque Solis member ref
    product: Optional[str] = None
    status: Literal["active","termed","pending"]="active"
    matched_patient_id: Optional[str] = None
    reconcile_status: Literal["matched","unmatched","exception","applied","skipped"]="unmatched"
    exception_reason: Optional[str] = None
    updated: str = Field(default_factory=_now)

class ReconcileException(BaseModel):
    """Visible exception queue — unresolved identity conflicts never auto-overwrite."""
    id: str = Field(default_factory=lambda: _uid("REX"))
    kind: Literal["identity_conflict","unmatched","contract_mismatch","duplicate"]="unmatched"
    source_ref: str
    patient_id: Optional[str] = None
    payer: str = "Solis"
    contract: Optional[str] = None
    detail: str = ""
    status: Literal["open","proposed","resolved","dismissed"]="open"
    created: str = Field(default_factory=_now)
    updated: str = Field(default_factory=_now)

class ReconcileRun(BaseModel):
    """Point-in-time reconcile run summary (propose-only apply)."""
    id: str = Field(default_factory=lambda: _uid("RRUN"))
    payer: str = "Solis"
    mode: Literal["dry_run","proposed_apply","applied"]="dry_run"
    matched: int = 0
    unmatched: int = 0
    exceptions: int = 0
    skipped_conflicts: int = 0
    applied: int = 0
    ts: str = Field(default_factory=_now)
    actor: str = "system"
