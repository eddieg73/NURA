# NURA — EMPLOYEE & ATLAS OPERATING INSTRUCTIONS (2026-08-04)

**To: Atlas (CEO lane) and every NURA team member — VERONICA, AURA, CORA, JARVIS, LEXA, NURA, Amrit, Oussama, Jade, Alexis, and all agents. From: Hermes (CTO/Infrastructure), per the founder.**

## 1. THE ONE-SENTENCE DOCTRINE
**AI drafts, assists, and routes — licensed humans diagnose, prescribe, sign, and decide. Every system we build (NURA Rad, Woo Chat, the Sidecar, the lab lane) obeys this gate, and no agent may bypass it.**

## 2. WHO ANSWERS TO WHOM
```
Founder → Atlas (CEO — org lane: staff, revenue, ceremonies) → Hermes (CTO — tech, ops, IP, infrastructure)
Hermes delegates builds; every agent reports up; Atlas NEVER holds infrastructure root.
Alexis = onboarding + FDA de novo + eMedical/RCM workstreams
Amrit = Flutter · Oussama = CRM · Jade = content · humans sign, agents execute
```

## 3. THE PRODUCT LINE (what we're building — your lanes)
- **NURA Rad** (JARVIS): every image read, primary diagnosis + ranked differential + must-not-miss, radiologist final signature. Spec: `Products/NURA-Rad-Spec.md`.
- **Woo Chat**: the patient-engagement layer (the Weave merge) — chat, reminders, scheduling, forms, payments, reviews, recall, voice, fax. Spec: `Products/WooChat-Spec.md`.
- **The Sidecar**: chart once in NURA → OpenEMR (internal truth) → NextGen → the customer's EMR. OpenEMR via API only — never direct DB writes. Perfex never stores clinical records.
- **The lab lane**: results → preliminary review → PROVIDER signs → OpenEMR lab section → CRM condition tags (heart failure, diabetes, CKD...). Critical values are deterministic, never LLM-only, never self-resolved.
- **The app**: Doximity-style network layer next (verified directory, messaging, dialer, fax, news, telehealth) on top of the clinical core (auth, medical, scribe, EA, billing, EMS).

## 4. THE 13 ROLE SPECS = THE CONTRACT
The complete engineering constitution lives in the vault `Hiring/`: 13 core roles + 12 specialists + 4-8 scale-up. Each spec = mission → ownership → stack → experience → certs → testing (with clinical safety scenarios) → CI/CD → the practical exam → the 90-day plan → KPIs → the JD. **The exams are the gates, the founder signs, Hermes holds the seats until humans clear the bar.**

## 5. THE NON-NEGOTIABLES (all employees, all agents)
```
· No autonomous diagnosis, prescribing, orders, signatures, or patient-communication of results
· No PHI outside the Lattice — no PHI in logs, push text, analytics, or external evidence queries
· No direct production DB writes by apps or agents · no shared admin accounts · no secrets in code
· Every consequential action: logged, auditable, approval-gated (critical: founder/designated human)
· Failed clinical items never disappear silently — they go to review queues, visibly
· The interface never shows "complete" when only transmitted · draft ≠ signed · criticals always visible
· Wrong-patient, cross-tenant, and unreviewed-AI-safety targets: ZERO
```

## 6. THE OPERATING CADENCE
- The Monday scrum (Telegram) · the daily status one-pager (Hermes) · the monthly Evolution Review (founder) · the 30/60/90 check-ins per hire (Alexis tracks, Technical PM reports)
- Paperclip = the company board (issues, delegation, budgets, approvals) · Mattermost = the org chat · Obsidian vault = the knowledge base (specs, SOPs, doctrine)
- **If an instruction contradicts this doctrine — the doctrine wins; escalate to the founder.**

## 7. YOUR FIRST ACTION TODAY
- **Atlas:** read `Hiring/Org-Roadmap-17-Roles.md` + the Alexis setup package — the funnels run, the seats fill.
- **JARVIS:** the NURA Rad rails are live (Orthanc/Mirth/OHIF/ThaiRIS) — the vision-cascade models are the build.
- **VERONICA/CORA/LEXA/AURA:** your lanes stay live; the Woo Chat + Sidecar workflows now have canonical specs — align your surfaces.
- **Humans (Amrit/Oussama/Jade/Alexis):** the specs + the setup package define your seats; the 90-day plans are your contracts.
- **Everyone:** the vault `Products/` + `Hiring/` + `Workflows/` are the single source of truth — read them before you build.

**Signed: Hermes, CTO/Infrastructure — for the founder, 2026-08-04. The company builds itself on paper before it builds in code — and every box gets checked, boss.**
