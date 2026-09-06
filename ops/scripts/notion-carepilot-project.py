#!/usr/bin/env python3
"""Create the CarePilot project page (CTO Suite) + canonical task — captured from the Complete Platform PDF spec."""
import os, json, requests

def _token():
    ap = "/opt/data/profiles/nura/home/.config/notion/auth.json"
    if os.path.exists(ap):
        d = json.load(open(ap))
        if d:
            return next(iter(d.values()))
    raise SystemExit("no token")

TOKEN=_token(); VER="2022-06-28"; H={"Authorization":f"Bearer {TOKEN}","Notion-Version":VER,"Content-Type":"application/json"}
API="https://api.notion.com/v1"
CTO_SUITE="3bea9b14-e498-816e-84c5-d9cda0497f87"
def req(m,p,b=None,t=40):
    r=requests.request(m,API+p,headers=H,json=b,timeout=t); return r.status_code,r.json()
def _t(x): return [{"type":"text","text":{"content":x}}]
def para(x): return {"object":"block","type":"paragraph","paragraph":{"rich_text":_t(x)}}
def head(x,l=2): return {"object":"block","type":f"heading_{l}",f"heading_{l}":{"rich_text":_t(x)}}
def bullet(x): return {"object":"block","type":"bulleted_list_item","bulleted_list_item":{"rich_text":_t(x)}}
def num(x): return {"object":"block","type":"numbered_list_item","numbered_list_item":{"rich_text":_t(x)}}
def callout(x,e="🏥"): return {"object":"block","type":"callout","callout":{"rich_text":_t(x),"icon":{"type":"emoji","emoji":e}}}
def code(x): return {"object":"block","type":"code","code":{"rich_text":_t(x),"language":"bash"}}
def divider(): return {"object":"block","type":"divider","divider":{}}

TITLE="CarePilot — Complete Platform (Population Health)"
B=[
 callout("CarePilot Complete Platform — 39-capability population-health/risk platform. Client docs per spec. Backend=Python FastAPI (built, 8/8 tests). Frontend=Flutter (built, 0 analyze issues). MCP-tools contract + n8n lab pipeline + safety boundary. HIGH-CONSEQUENCE clinical — AI is proposal-only; humans approve every clinical/coding/billing action.","🏥"),
 head("What it is",2),
 para("A finished population-health & value-based-care platform: 39 capabilities across foundation, controls, enterprise expansion, population health, and integrations. Captures recurring CCM/TCM billing, keeps risk/RAF accurate (V28-aligned), tracks HEDIS/Stars, manages med-safety, runs med economics + claims audit, and gives leadership a CPHO command center."),
 head("Foundation capabilities (P0 built)",2),
 num("CCM Automation (XL) — enroll 2+ condition patients, monthly work, consent required, billing charge approved before it leaves."),
 num("2026 Coding Sheet (M) — load official code list, validate, version history + rollback, guides documentation (never invents diagnoses)."),
 num("Solis Reconciliation (S) — re-sync patient list after Solis fixes; no overwrite of unresolved identity conflicts; exception queue."),
 num("Risk-Model Alignment V28 (M) — every score labeled model/version/year; block cross-model comparison."),
 num("Unified Work Queue (L) — every alert becomes a task with owner/due/next-action/evidence; status flow."),
 num("HEDIS & Stars Engine (XL) — standard measure rules by payer/product/year; certification-readiness only when formally certified."),
 num("Medication Safety Center (XL) — ordered vs dispensed vs given vs billed; safety separate from cost; financial never overrides safety."),
 num("Versioned Rules Registry (L) — code/model/prompt rule sets dated+versioned, sandbox test, rollback, approval to go live."),
 num("Evidence & Audit Vault (L) — append-only, unchangeable records; covers consent, decisions, billing, model versions."),
 head("Enterprise Expansion (XL builds)",2),
 bullet("Medical Economics & Contract Performance (XL) · Claims Audit & Recovery (XL) · Risk Revenue Recapture (L) · Enterprise DW & Interop Hub (XL) · Referral/Specialist-network (L) · Pharmacy/Formulary (L) · Admissions/Utilization (L) · Enterprise Case Mgmt (L) · Stop-Loss/Reinsurance (L) · ACO/CCLF (L) · Payer Ops Knowledge Center (M)."),
 head("Population Health",2),
 bullet("Risk Stratification (XL) · MIH/Community Paramedicine (XL) · Provider Performance Command Center (L) · Intervention Outcomes (L) · Frailty/ACP (M) · CPHO Command Center (L)."),
 head("MCP Tools for Hermes (governed)",2),
 bullet("READ: search_patients, get_patient_summary, get_care_gaps, get_admissions, get_work_queue, get_risk_scores, get_medication_alerts, get_measure_result, get_referrals, get_provider_scorecard, get_financial_summary."),
 bullet("ACTION: create_task, assign_task, add_note_draft, flag_for_review (all permission-checked, logged)."),
 bullet("PROPOSE-ONLY: propose_enrollment, propose_charge, draft_outreach — the agent suggests, a HUMAN confirms."),
 bullet("NEVER: Hermes can't sign a chart, place an order, add a diagnosis, change a med order, submit a claim, or send a message alone."),
 head("n8n Lab-Pipeline contract",2),
 bullet("n8n orchestrates (opaque refs only, NO PHI); Care Pilot exposes inbound: /api/labs/review-task, critical-alert, identity-match, audit, delivery-status. On sign-off Care Pilot calls n8n approval webhook with only {approval_ref,event_id}. Labs/AI/RAG/memory belong to the NURA lab pipeline, not Care Pilot."),
 head("Integration architecture",2),
 bullet("One hub: eMedPractice → bot → Mirth; other EMRs/payers/Florida HIE → Mirth. Quality engine normalizes to FHIR + CQL. All AI runs on on-prem DGX (no patient data leaves)."),
 head("Engineering controls (everywhere)",2),
 bullet("Roles & separation of duties (executive/medical-director/provider/nurse/MA/coder/compliance/CPHO/read-only); every export/approval/override logged. Dashboard integrity (numerator/denominator/source/date + drill). Reliability (idempotent, retries, DLQ, tested backup/restore/rollback). Safety boundary (AI drafts/flags only; clinical over financial; no diagnosis/order/charge/claim by AI alone)."),
 head("Recommended build order",2),
 num("1 Protect+baseline (no regression) · 2 Identity/provenance/DW/versioned rules · 3 Payer+contract reconciliation · 4 CCM + TCM · 5 Med safety + AI note audit · 6 Med economics/claims/pharmacy/utilization/referrals/case mgmt · 7 Stop-loss + ACO · 8 Validate w/ reference cases · 9 Pilot pre-sign review · 10 Expand only after gates pass."),
 head("Definition of Done",2),
 bullet("All existing Care Pilot features pass non-regression; every dashboard value drills to patients/calc/source; payer/product populations separated; every finding has owner/due/next-action/evidence/disposition; unmatched patients enter a visible queue; coding/risk/quality/AI rules versioned+tested+approved+reversible; med-safety can't be closed by AI; financials reconcile to member/claim; backups/restore/rollback tested; pilot sign-off before broad deploy."),
 head("Status (P0 built)",2),
 bullet("Backend FastAPI: safety boundary (8 guards) + RBAC (9 roles) + read/action/propose tools + n8n contract — **8/8 tests PASSED**. Frontend Flutter: work-queue home screen — **0 analyze issues**. Pushed to GitHub `b9c3246` under `carepilot/`. Owner: Hermes (CTO). Priority: P1. HIGH-CONSEQUENCE clinical; providers approve."),
 divider(),
 para("Build files: carepilot/backend/app.py (FastAPI), carepilot/backend/test_safety.py, carepilot/frontend/lib/{main,home}.dart. See nura_medical/carepilot/ in the repo."),
]

st,d=req("POST","/pages",{"parent":{"page_id":CTO_SUITE},"properties":{"title":{"title":_t(TITLE)}},"children":B[:100]})
if st>=400:
    print("ERR page:",st,d.get("message",d)[:200]); raise SystemExit(1)
PID=d.get("id"); print("Project page:",PID,"url:",d.get("url"))
st3,d3=req("GET",f"/blocks/{PID}/children?page_size=100")
print("verified blocks:",len(d3.get("results",[])) if st3<400 else "?")

# task on canonical board
DB="d3ff0c00-c629-43dc-b82c-06a28866fcb1"
TASK_TEXT="Build the CarePilot Complete Platform (39-capability population-health/risk platform) — Python FastAPI backend + Flutter frontend. P0 foundation DONE (safety boundary, RBAC, MCP read/action/propose tools, n8n contract, 8/8 tests; Flutter 0 issues; GitHub b9c3246). Next per build order: identity/provenance/DW + versioned rules. HIGH-CONSEQUENCE clinical — AI proposal-only, humans approve. Client in-spec (CarePilot-Complete-Platform)."
body={"parent":{"database_id":DB},"properties":{"Task":{"title":_t(TASK_TEXT)},"Status":{"select":{"name":"Next"}},"Priority":{"select":{"name":"P1 — High"}},"Owner":{"rich_text":_t("Hermes")},"Source System":{"select":{"name":"Hermes"}},"Task Type":{"select":{"name":"Build"}}}}
st4,d4=req("POST","/pages",body)
print("task:",st4, (d4.get("id") if st4<400 else d4.get("message",d4)[:150]))
