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
