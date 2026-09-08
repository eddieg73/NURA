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
        self.cohorts=[]; self.tcm_cases=[]; self.tcm_steps=[]; self.care_team=[]
        self.tcm_events=[]; self.placements=[]; self.readm_risks=[]; self.sdoh=[]; self.sla=[]; self.tcm_billing=[]
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
        p2=p("MRN-002","Damien Abel",["Hypertension","Heart Failure"],[])  # 2 conditions -> legitimately high-risk
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

        # ---- TCM orchestration seed ----
        # cohorts / buckets
        self.cohorts=[
            M.Cohort(name="TCM — Post-Discharge",kind="post_discharge",criteria={"programs":["TCM"]}),
            M.Cohort(name="High-Risk Readmission",kind="high_risk",criteria={"min_conditions":2,"raf_gt":1.2}),
            M.Cohort(name="CCM Chronic",kind="ccm",criteria={"programs":["CCM"]}),
            M.Cohort(name="Behavioral Health",kind="behavioral",criteria={"conditions":["depression","anxiety","bipolar"]}),
            M.Cohort(name="Complex / Dual-Eligible",kind="complex",criteria={"flags":["dual_eligible"]}),
        ]
        # admission document checklist (the "certain set of documents to obtain on admission")
        self.tcm_checklist_template=[
            {"doc":"Admission H&P (history & physical)","status":"pending"},
            {"doc":"Discharge summary (preliminary)","status":"pending"},
            {"doc":"Medication reconciliation (admission)","status":"pending"},
            {"doc":"Problem list / active diagnoses","status":"pending"},
            {"doc":"Advance directive / DNR status","status":"pending"},
            {"doc":"Post-discharge appointment confirm","status":"pending"},
            {"doc":"Insurance / payer eligibility verify","status":"pending"},
            {"doc":"Functional + social support screen","status":"pending"},
        ]
        # per-step TCM alert ladder (each step has its own alert for the patient)
        self.tcm_alert_ladder=[
            {"seq":1,"name":"Patient admitted — alert care team","alert_level":"critical","due_in_hours":1,"assignee":"hospital_nurse"},
            {"seq":2,"name":"TCM case opened + cohort assigned","alert_level":"warning","due_in_hours":4,"assignee":"case_manager"},
            {"seq":3,"name":"Admission document checklist (all docs)","alert_level":"warning","due_in_hours":24,"assignee":"case_manager"},
            {"seq":4,"name":"Medication reconciliation complete","alert_level":"warning","due_in_hours":48,"assignee":"clinical"},
            {"seq":5,"name":"Patient discharged — arrange home healthcare","alert_level":"critical","due_in_hours":24,"assignee":"community_paramedic_np"},
            {"seq":6,"name":"Post-discharge follow-up visit (24h)","alert_level":"warning","due_in_hours":24,"assignee":"community_paramedic_np"},
            {"seq":7,"name":"72h follow-up (readmission risk screen)","alert_level":"warning","due_in_hours":72,"assignee":"community_paramedic_np"},
            {"seq":8,"name":"Care-gap closure + PCP handoff","alert_level":"info","due_in_hours":720,"assignee":"case_manager"},
        ]
        # an active TCM case (Cleo already discharged -> home-health arranged + care team assigned)
        tcm1=M.TCMCase(patient_id=p1.id,trigger="discharge",cohort_id=self.cohorts[0].id,
                       checklist=[dict(x) for x in self.tcm_checklist_template],
                       alerts=["Patient discharged — arrange home healthcare","72h follow-up pending"],
                       home_health={"agency":"Bay Area Home Health","arranged":_now(),"start":_now(),"level":"skilled nursing + PT"},
                       care_team=["case_manager","community_paramedic_np","hospital_nurse"])
        self.tcm_cases.append(tcm1)
        self.tcm_steps=[M.TCMStep(case_id=tcm1.id,seq=s["seq"],name=s["name"],alert_level=s["alert_level"],
                                  due_in_hours=s["due_in_hours"],assignee=s["assignee"],status="done" if s["seq"]<=5 else "pending")
                         for s in self.tcm_alert_ladder]
        # care team for Cleo
        self.care_team=[
            M.CareTeam(patient_id=p1.id,role="case_manager",name="CM-01 (registered case manager)"),
            M.CareTeam(patient_id=p1.id,role="community_paramedic_np",name="Community Paramedic NP — Medisun MIH"),
            M.CareTeam(patient_id=p1.id,role="hospital_nurse",name="Hospital Discharge Nurse"),
        ]
        # a fresh ADMISSION to demonstrate the admit-trigger (Damien just admitted)
        tcm2=M.TCMCase(patient_id=p2.id,trigger="admit",cohort_id=self.cohorts[1].id,
                       checklist=[dict(x) for x in self.tcm_checklist_template],
                       alerts=["Patient admitted — alert care team"],care_team=[])
        self.tcm_cases.append(tcm2)

        # ---- integration topology (data plane that feeds TCM events) ----
        self.integrations=[
            {"name":"eMedical","vendor":"eMedPractice","kind":"EMR","lane":"admit/discharge + chart","status":"connected"},
            {"name":"Ensure Data Solutions","vendor":"Solis Health Plans","kind":"portal/MA data","lane":"payer cohorts + eligibility","status":"connected"},
            {"name":"Mirth NextGen Connect","vendor":"Mirth/OIE","kind":"HL7 engine","lane":"HL7 ADT (admit/discharge) + orders/results","status":"connected"},
        ]

        # ---- live event feed (the 3 lanes pushing admit/discharge) ----
        self.tcm_events=[
            M.TCMEvent(patient_id=p1.id,event="discharge",source="mirth_adt",facility="Broward General",
                       admit_dt=_now(),discharge_dt=_now()),
            M.TCMEvent(patient_id=p2.id,event="admit",source="emeditical",facility="Baptist MDC"),
            M.TCMEvent(patient_id=p2.id,event="er_visit",source="ensure",facility="Broward General"),
        ]
        # post-acute placement (Cleo -> home health arranged on discharge)
        self.placements=[M.PostAcutePlacement(patient_id=p1.id,kind="home_health",
                           facility="Bay Area Home Health",rn_visit_before=True)]
        # readmission risk (Cleo high, Damien medium)
        self.readm_risks=[M.ReadmissionRisk(patient_id=p1.id,score=0.82,band="high",
                            contributors=["HF","recent admission","polypharmacy","missed TCM visit"]),
                          M.ReadmissionRisk(patient_id=p2.id,score=0.48,band="medium",
                            contributors=["2 conditions","Solis dual-eligible"])]
        # SDOH screen (Cleo has a transport barrier)
        self.sdoh=[M.SDOHScreen(patient_id=p1.id,food="ok",transport="gap",housing="ok",isolation="ok",
                    needs=["transport"],referral="Medisun MIH paramedic pickup / paratransit")]
        # SLA breach (step 6 24h follow-up overdue on Cleo)
        self.sla=[M.SLABreach(case_id=tcm1.id,step="Post-discharge follow-up visit (24h)",overdue_hours=6.5,severity="warning")]
        # TCM billing (CPT codes — proposed, human approves submit)
        self.tcm_billing=[M.TCMBilling(patient_id=p1.id,code="99495",desc="Transitional Care Mgmt (moderate)",
                            status="proposed",value=240.0,evidence={"interactive_contact":"2-biz-days","mdm":"moderate"}),
                          M.TCMBilling(patient_id=p1.id,code="99496",desc="Transitional Care Mgmt (high)",
                            status="proposed",value=320.0,evidence={"interactive_contact":"2-biz-days","mdm":"high","readmission_risk":"high"})]

STORE = Store()
