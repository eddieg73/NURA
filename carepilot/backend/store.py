"""CarePilot store + capability engines (the 39-capability logic)."""
import json, datetime
import models as M

def _now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()

class Store:
    def __init__(self):
        self.patients=[]; self.gaps=[]; self.tasks=[]; self.risks=[]; self.referrals=[]
        self.claims=[]; self.med_alerts=[]; self.admissions=[]; self.interventions=[]
        self.drugs=[]; self.case_plans=[]; self.provider_metrics=[]; self.contracts=[]
        self.audit=[]; self.rules=[]; self.rules_versions=[]; self.identity=[]
        self._seed()

    def _audit(self, actor, action, ref=None, phi=False):
        self.audit.append({"ts":_now(),"actor":actor,"action":action,"target_ref":ref,"phi":bool(phi)})

    def _seed(self):
        import uuid
        def p(mrn,name,conds,progs,sc=None):
            pt=M.Patient(mrn=mrn,name=name,conditions=conds,programs=progs,
                         risk_scores=sc or {})
            self.patients.append(pt); return pt
        p1=p("MRN-001","Cleo Torres",["Diabetes","Heart Failure"],["CCM"],{"V28":{"version":"0.28.0","year":2026,"clinical":1.30,"raf":1.30,"source":"v28-2026"}})
        p2=p("MRN-002","Damien Abel",["Hypertension"],[])
        p3=p("MRN-003","Rene Okonkwo",["COPD"],["TCM"],{"V28":{"version":"0.28.0","year":2026,"clinical":1.18,"raf":1.18,"source":"v28-2026"}})
        p4=p("MRN-004","Sofia Marchetti",["Diabetes","Hypertension","CKD"],[])  # CCM candidate (2+ conditions, NOT enrolled)
        for pt in (p1,p2,p3):
            self.risks.append(M.RiskScore(patient_id=pt.id,model="V28",version="0.28.0",year=2026,
                clinical=pt.risk_scores.get("V28",{}).get("clinical",1.0),
                raf=pt.risk_scores.get("V28",{}).get("raf",1.0),
                components={"demographics":0.9,"diagnoses":pt.risk_scores.get("V28",{}).get("clinical",1.0),"total":pt.risk_scores.get("V28",{}).get("raf",1.0)}))
        self.gaps=[M.CareGap(patient_id=p1.id,measure="HEDIS HbA1c",evidence={"num":0,"den":1,"source":"2026 HEDIS"}),
                   M.CareGap(patient_id=p1.id,measure="HEDIS Eye Exam",evidence={"num":0,"den":1,"source":"2026 HEDIS"}),
                   M.CareGap(patient_id=p3.id,measure="CCM Follow-up",evidence={"num":0,"den":1,"source":"2026"})]
        self.tasks=[M.WorkTask(source=p1.id,task_type="gap",title="Close HbA1c gap",owner="nurse-1",
                    next_action="order A1c",status="New"),
                    M.WorkTask(source=p1.id,task_type="ccm",title="CCM monthly call",owner="provider-1",
                    next_action="call + log care time",status="In Progress")]
        self.med_alerts=[M.MedicationAlert(patient_id=p1.id,finding="Drug billed but never ordered",severity="critical",type="billed"),
                         M.MedicationAlert(patient_id=p2.id,finding="Ordered vs dispensed mismatch",severity="warning",type="dispensed")]
        self.referrals=[M.Referral(patient_id=p1.id,specialist="Cardiology",status="ordered",cost=1200,access_days=14)]
        self.claims=[M.Claim(patient_id=p1.id,payer="Solis",contract="Solis-HMO-2026",amount=1200,status="identified",kind="duplicate"),
                     M.Claim(patient_id=p3.id,payer="Oscar",contract="Oscar-FFS",amount=300,status="identified",kind="pricing_variance")]
        self.admissions=[M.Hospitalization(patient_id=p1.id,kind="inpatient",admit_dt=_now(),discharge_dt=_now())]
        self.interventions=[M.Intervention(patient_id=p1.id,kind="post-discharge call",started=_now(),
                            before={"ed":2,"readmissions":1,"cost":5000},after={"ed":0,"readmissions":0,"cost":2000})]
        self.drugs=[M.DrugUse(patient_id=p1.id,drug="Empagliflozin",cost=400,adherence=0.92)]
        self.case_plans=[M.CasePlan(patient_id=p1.id,goals=["ACH below 8%"],interventions=["weekly call"],owner="case-mgmt-1")]
        self.provider_metrics=[M.ProviderMetric(provider="Dr. Ingrid Mixter-Leon",quality=0.82,raf=1.22,gaps=12,utilization=0.61)]
        self.contracts=[M.ContractPerf(contract="Solis-HMO-2026",paid=100000,incurred=110000,est=115000,pmpm=360),
                        M.ContractPerf(contract="Oscar-FFS",paid=50000,incurred=47000,est=50000,pmpm=180)]
        self.rules=[{"id":"RULES-2026","kind":"coding","version":"2026.1","status":"active","approved_by":"coding-lead"}]

STORE = Store()
