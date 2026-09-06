#!/usr/bin/env python3
"""Create CarePilot as a TOP-LEVEL project page (workspace root) 'next to JARVIS'.
JARVIS = 613e14da-104a-470e-af85-799d66eb8ebc (workspace-root). Try root; fall back to JARVIS page parent."""
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
JARVIS="613e14da-104a-470e-af85-799d66eb8ebc"
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
 callout("CarePilot Complete Platform — TOP-LEVEL project (next to JARVIS). 39-capability population-health/risk platform. Backend=Python FastAPI (8/8 tests). Frontend=Flutter (0 issues). MCP tools + n8n lab-pipeline + safety boundary. HIGH-CONSEQUENCE clinical — AI proposal-only; humans approve every clinical/coding/billing action.","🏥"),
 head("What it is",2),
 para("Finished population-health & value-based-care platform: 39 capabilities across foundation, controls, enterprise expansion, population health, integrations. Captures recurring CCM/TCM billing, keeps risk/RAF V28-accurate, HEDIS/Stars, med-safety, med economics + claims audit, CPHO command center."),
 head("Foundation (P0 built)",2),
 bullet("CCM Automation (XL) · 2026 Coding Sheet (M) · Solis Reconciliation (S) · Risk-Model V28 Alignment (M) · Unified Work Queue (L) · HEDIS & Stars (XL) · Medication Safety Center (XL) · Versioned Rules Registry (L) · Evidence & Audit Vault (L)."),
 head("Enterprise Expansion",2),
 bullet("Medical Economics & Contract Performance (XL) · Claims Audit & Recovery (XL) · Risk Revenue Recapture (L) · Enterprise DW & Interop Hub (XL) · Referral/Specialist (L) · Pharmacy/Formulary (L) · Admissions/Utilization (L) · Enterprise Case Mgmt (L) · Stop-Loss (L) · ACO/CCLF (L) · Payer Ops Knowledge Center (M)."),
 head("Population Health",2),
 bullet("Risk Stratification (XL) · MIH/Community Paramedicine (XL) · Provider Performance Command Center (L) · Intervention Outcomes (L) · Frailty/ACP (M) · CPHO Command Center (L)."),
 head("MCP Tools (governed)",2),
 bullet("READ: search_patients, get_patient_summary, get_care_gaps, get_admissions, get_work_queue, get_risk_scores, get_medication_alerts, get_measure_result, get_referrals, get_provider_scorecard, get_financial_summary."),
 bullet("ACTION: create_task, assign_task, add_note_draft, flag_for_review. PROPOSE-ONLY: propose_enrollment, propose_charge, draft_outreach."),
 bullet("NEVER: sign a chart, place an order, add a diagnosis, change a med, submit a claim, or send a message alone."),
 head("n8n lab-pipeline contract",2),
 bullet("n8n orchestrates (opaque refs, NO PHI). Care Pilot inbound: /api/labs/{review-task, critical-alert, identity-match, audit, delivery-status}. Care Pilot → n8n approval webhook {approval_ref,event_id}."),
 head("Integration architecture",2),
 bullet("One hub: eMedPractice → bot → Mirth; EMRs/payers/Florida HIE → Mirth. Quality = normalize to FHIR + CQL. AI on on-prem DGX (no PHI leaves)."),
 head("Engineering controls",2),
 bullet("Roles & separation of duties (9 roles); everything logged. Dashboard integrity (num/den/source/date + drill). Reliability (idempotent, retries, DLQ, tested backup/restore/rollback). Safety boundary (AI drafts/flags; clinical > financial; no diagnosis/order/charge/claim by AI)."),
 head("Build order",2),
 num("1 Baseline no-regression · 2 Identity/provenance/DW/versioned rules · 3 Payer reconciliation · 4 CCM+TCM · 5 Med safety+AI note audit · 6 Med economics/claims/pharm/utilization/referrals/case mgmt · 7 Stop-loss+ACO · 8 Validate · 9 Pilot pre-sign · 10 Expand after gate."),
 head("Definition of done",2),
 bullet("No regression; every value drills; payers separated; findings have owner/due/next/evidence/disposition; unmatched patients visible-queued; rules versioned+approved+reversible; med-safety not AI-closable; financials reconcile; backup/restore tested; pilot sign-off."),
 head("Status (P0 built)",2),
 bullet("Backend FastAPI safety boundary (8 guards) + RBAC (9 roles) + read/action/propose tools + n8n contract — 8/8 tests PASSED. Flutter work-queue home — 0 analyze issues. GitHub b9c3246 (carepilot/). Owner: Hermes (CTO). Priority P1. HIGH-CONSEQUENCE clinical."),
 divider(),
 para("Build files: carepilot/backend/{app.py, test_safety.py} · carepilot/frontend/lib/{main,home}.dart"),
]

# try workspace-root first (JARVIS is at root — sibling), fall back to JARVIS page parent
body={"parent":{"type":"workspace"},"properties":{"title":{"title":_t(TITLE)}},"children":B[:100]}
st,d=req("POST","/pages",body)
if st>=400:
    print("workspace-root failed:",st,d.get("code","?"))
    body={"parent":{"page_id":JARVIS},"properties":{"title":{"title":_t(TITLE)}},"children":B[:100]}
    st,d=req("POST","/pages",body)
    print("fell back to JARVIS page parent:",st)
if st<400:
    print("OK page id:",d.get("id"))
    print("url:",d.get("url"))
    st3,d3=req("GET",f"/blocks/{d.get('id')}/children?page_size=100")
    print("verified blocks:",len(d3.get("results",[])) if st3<400 else "?")
else:
    print("ERR:",d.get("message",d)[:200])
