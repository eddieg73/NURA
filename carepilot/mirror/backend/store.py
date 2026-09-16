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
        self.provenance=[]; self.dw_records=[]; self.dw_feeds=[]
        self.cohorts=[]; self.tcm_cases=[]; self.tcm_steps=[]; self.care_team=[]
        self.tcm_events=[]; self.placements=[]; self.readm_risks=[]; self.sdoh=[]; self.sla=[]; self.tcm_billing=[]
        self.risk_bands=[]; self.mih_episodes=[]; self.frailty=[]; self.provider_scorecards=[]
        self.payer_roster=[]; self.reconcile_exceptions=[]; self.reconcile_runs=[]
        self._seed()

    def _audit(self, actor, action, ref=None, phi=False, rule_version=None, model_version=None, evidence=None):
        """Append-only audit + provenance. Never mutate prior rows."""
        row={"ts":_now(),"actor":actor,"action":action,"target_ref":ref,"phi":bool(phi),
             "rule_version":rule_version,"model_version":model_version}
        self.audit.append(row)
        self.provenance.append(M.ProvenanceEvent(
            actor=actor, action=action, subject_ref=ref, phi=bool(phi),
            rule_version=rule_version, model_version=model_version,
            evidence=evidence or {}))

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
        # ---- Phase-2: versioned rules registry ----
        r_active=M.RuleSet(id="RULES-2026",kind="coding",name="2026 Coding Sheet",version="2026.1",
                           status="active",approved_by="coding-lead",sandbox_passed=True,
                           effective_from="2026-01-01",payload={"codes_ref":"coding-sheet-2026.1"})
        r_draft=M.RuleSet(kind="risk",name="V28 Risk Alignment",version="0.28.1-draft",
                          status="draft",sandbox_passed=False,
                          payload={"model":"V28","year":2026})
        self.rules=[r_active, r_draft]
        self.rules_versions=[
            {"rule_id":r_active.id,"version":"2026.0","status":"retired","approved_by":"coding-lead"},
            {"rule_id":r_active.id,"version":"2026.1","status":"active","approved_by":"coding-lead"},
            {"rule_id":r_draft.id,"version":"0.28.1-draft","status":"draft","approved_by":None},
        ]

        # ---- Phase-2: identity queue (matched + unmatched synthetic) ----
        self.identity=[
            M.IdentityRecord(source_system="emedpractice",source_ref="EMED-MRN-001",
                             patient_id=p1.id,match_status="matched",confidence=0.98),
            M.IdentityRecord(source_system="ensure",source_ref="ENS-MRN-002",
                             patient_id=p2.id,match_status="matched",confidence=0.95),
            M.IdentityRecord(source_system="openemr",source_ref="OEMR-UNKNOWN-77",
                             patient_id=None,match_status="unmatched",confidence=0.0),
            M.IdentityRecord(source_system="mirth",source_ref="HL7-PID-UNKNOWN-9",
                             patient_id=None,match_status="unmatched",confidence=0.12,
                             conflict_reason="no_mrn_match"),
            M.IdentityRecord(source_system="solis",source_ref="SOLIS-MRN-001",
                             patient_id=p1.id,match_status="conflict",confidence=0.55,
                             conflict_reason="pcp_mismatch"),
        ]

        # ---- Phase-2: DW / interop hub scaffold ----
        self.dw_feeds=[
            {"id":"FEED-EMED","source":"emedpractice","kind":"fhir_rest","status":"scaffold","direction":"inbound"},
            {"id":"FEED-MIRTH","source":"mirth","kind":"hl7_adt","status":"connected","direction":"inbound"},
            {"id":"FEED-ENSURE","source":"ensure","kind":"roster","status":"scaffold","direction":"inbound"},
            {"id":"FEED-OPENEMR","source":"openemr","kind":"fhir_lab","status":"scaffold","direction":"inbound"},
        ]
        self.dw_records=[
            M.DWRecord(entity_type="member",source="seed",payload={"patient_id":p1.id,"mrn":p1.mrn}),
            M.DWRecord(entity_type="member",source="seed",payload={"patient_id":p2.id,"mrn":p2.mrn}),
            M.DWRecord(entity_type="feed",source="mirth",payload={"feed_id":"FEED-MIRTH","last_event":"ADT"}),
        ]
        self._audit("system","phase2_seed","identity+rules+dw",phi=False,
                    rule_version="2026.1",model_version="V28-0.28.0",
                    evidence={"identity_rows":len(self.identity),"rules":len(self.rules)})

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

        # ---- Population Health (caps ~26–32) ----
        # Risk stratification bands (panel-wide; uses V28 + conditions + readmission)
        def _band_for(pt, rr=None):
            raf = pt.risk_scores.get("V28",{}).get("raf",0.0)
            ncond = len(pt.conditions)
            score = raf + 0.15*max(ncond-1,0) + (0.25 if rr and rr.band in ("high","very_high") else 0)
            if score >= 1.6 or ncond >= 3: band="very_high"
            elif score >= 1.25 or ncond >= 2: band="high"
            elif score >= 1.05: band="medium"
            else: band="low"
            contrib=[]
            if raf: contrib.append(f"V28_raf={raf}")
            if ncond: contrib.append(f"conditions={ncond}")
            if rr: contrib.append(f"readmission={rr.band}")
            if pt.mih_flag: contrib.append("mih_flag")
            return band, raf, contrib
        # flag MIH candidate on high-util / SDOH
        p1.mih_flag = True
        rr_map = {r.patient_id:r for r in self.readm_risks}
        for pt in self.patients:
            rr = rr_map.get(pt.id)
            band, raf, contrib = _band_for(pt, rr)
            self.risk_bands.append(M.RiskBand(patient_id=pt.id, band=band, raf=raf,
                contributors=contrib, mih_candidate=(band in ("high","very_high") or pt.mih_flag)))
        # MIH episodes (propose-only)
        self.mih_episodes=[
            M.MIHEpisode(patient_id=p1.id, reason="post-discharge home visit + transport barrier",
                         priority="urgent", status="proposed", sdoh_needs=["transport"]),
            M.MIHEpisode(patient_id=p2.id, reason="high-risk admit — community paramedic check-in",
                         priority="routine", status="proposed", sdoh_needs=[]),
        ]
        # Frailty / ACP
        self.frailty=[
            M.FrailtyACP(patient_id=p1.id, frailty_score=0.55, frailty_band="prefrail",
                         acp_status="discussed", goals=["remain home","avoid ED"], barriers=["transport"]),
            M.FrailtyACP(patient_id=p3.id, frailty_score=0.35, frailty_band="fit",
                         acp_status="none", goals=[], barriers=[]),
            M.FrailtyACP(patient_id=p4.id, frailty_score=0.72, frailty_band="frail",
                         acp_status="proposed", goals=["ACP discussion"], barriers=["complex multimorbidity"]),
        ]
        # Provider Performance Command Center rows
        gap_n = len(self.gaps)
        int_delta = sum((i.before.get("cost",0)-i.after.get("cost",0)) for i in self.interventions)
        self.provider_scorecards=[
            M.ProviderScorecardRow(provider="Dr. Ingrid Mixter-Leon", panel_size=len(self.patients),
                quality=0.82, raf=1.22, open_gaps=gap_n, utilization=0.61,
                mih_referrals=len(self.mih_episodes), intervention_delta_cost=float(int_delta),
                drill={"gap_count":gap_n,"intervention_ids":[i.id for i in self.interventions],
                       "mih_ids":[m.id for m in self.mih_episodes]}),
        ]
        # keep legacy provider_metrics in sync
        self.provider_metrics=[M.ProviderMetric(provider="Dr. Ingrid Mixter-Leon",quality=0.82,raf=1.22,
                                                 gaps=gap_n,utilization=0.61)]
        self._audit("system","pophealth_seed","risk+mih+frailty+scorecards",phi=False,
                    rule_version="2026.1",model_version="V28-0.28.0",
                    evidence={"risk_bands":len(self.risk_bands),"mih":len(self.mih_episodes),
                              "frailty":len(self.frailty),"scorecards":len(self.provider_scorecards)})

        # ---- Phase-3: Solis / payer roster reconcile seed (synthetic) ----
        self.payer_roster=[
            M.PayerRosterRow(payer="Solis",contract="Solis-HMO-2026",source_ref="SOLIS-MRN-001",
                             product="HMO",status="active",matched_patient_id=p1.id,
                             reconcile_status="matched"),
            M.PayerRosterRow(payer="Solis",contract="Solis-HMO-2026",source_ref="SOLIS-MRN-002",
                             product="HMO",status="active",matched_patient_id=p2.id,
                             reconcile_status="matched"),
            M.PayerRosterRow(payer="Solis",contract="Solis-HMO-2026",source_ref="SOLIS-NEW-55",
                             product="HMO",status="active",reconcile_status="unmatched"),
            M.PayerRosterRow(payer="Solis",contract="Solis-HMO-2026",source_ref="SOLIS-MRN-001",
                             product="PPO",status="active",matched_patient_id=p1.id,
                             reconcile_status="exception",exception_reason="contract_product_conflict"),
            M.PayerRosterRow(payer="Oscar",contract="Oscar-FFS",source_ref="OSC-MRN-003",
                             product="FFS",status="active",matched_patient_id=p3.id,
                             reconcile_status="matched"),
        ]
        self.reconcile_exceptions=[
            M.ReconcileException(kind="identity_conflict",source_ref="SOLIS-MRN-001",patient_id=p1.id,
                                 payer="Solis",contract="Solis-HMO-2026",
                                 detail="pcp_mismatch — do not overwrite until human resolves"),
            M.ReconcileException(kind="unmatched",source_ref="SOLIS-NEW-55",payer="Solis",
                                 contract="Solis-HMO-2026",detail="no CarePilot patient for roster ref"),
            M.ReconcileException(kind="contract_mismatch",source_ref="SOLIS-MRN-001",patient_id=p1.id,
                                 payer="Solis",contract="Solis-HMO-2026",
                                 detail="roster product PPO vs patient contract HMO"),
        ]
        self._audit("system","payer_reconcile_seed","solis+exceptions",phi=False,
                    evidence={"roster":len(self.payer_roster),"exceptions":len(self.reconcile_exceptions)})


STORE = Store()
