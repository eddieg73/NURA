# NURA CLIENT HELP — the guide to your system (v1, 2026-08-11)

## What you have
The NURA stack is a clinical communications and intelligence platform: one app connecting secure calls, messaging, fax, AI assistance, and your medical records.

## The five things you can do today
1. **The AI brain (DocsGPT)** — ask the medical-knowledge engine anything (the 18-textbook library!): answers come grounded with sources. Reach it through LibreChat (the chat-UI) or the app's AI tab.
2. **The clinical record (OpenEMR)** — your patient charts, labs, and encounters live here; the AI reads trends (A1c, LDL, eGFR) and flags anomalies for review.
3. **Secure communications** — the dialer (Twilio-powered), messaging, and fax lanes (Documo) — all HIPAA-oriented and audit-logged.
4. **The dashboard (Mission Control)** — your standing health: the fleet, the lanes, the crons, the status board — updated daily.
5. **The mobile app (nura_medical)** — the Android APK is built; iOS is staged for the App Store (your Apple ID is enrolled).

## The support rails
- **The status board**: every morning you see the system health (16-point sweep, all green).
- **The digests**: morning and evening summaries of what happened.
- **The escalation**: any outage pages you immediately; founder-only items (key drops, vendor switches) are flagged once.
- **The recovery**: the machine self-heals tunnels, containers, and the mesh — most issues never reach you.

## The rules of the road (important!)
- The AI **supports** decisions; licensed clinicians **make** them. No AI output signs charts, orders, or prescriptions.
- Every AI answer carries a source, a confidence, and a review flag when clinical.
- Your data stays in your infrastructure: sealed keys, local storage, encrypted lanes.

## The common questions
- *How do I reach the AI?* → LibreChat (the browser) or the app's AI tab.
- *Where are my records?* → OpenEMR (the clinical record of truth).
- *What if something breaks?* → You'll get an alert; the machine usually fixes it first. If you see a "founder action needed" flag, that's the one thing needing your click (usually a key or a vendor switch).

## The escalation matrix
| Issue | Who | Response |
|---|---|---|
| App down / brain down | Machine self-heals + alerts | ≤15 min |
| Key invalid | Founder re-drops | flagged once |
| Vendor switch (eMedical, Apple) | Founder click | flagged once |
| Clinical question | AI + licensed provider | provider decides |
