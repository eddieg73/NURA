# NURA APP — ROLE MATRIX v1.0 (2026-08-02)

**Founder: "How do I connect you to a mobile app so you can serve different individuals in different specialties — clinicians, paramedics, nurses, doctors, PAs, NPs, lab professionals?"**
**Answer: ONE gateway (:8642 /v1, live) · ONE brain · MANY role-scoped users · per-org profiles at SaaS scale (NUR-106). No new server.**

## Architecture
```
Mobile app (Flutter, Canvas) → AUTH (OpenEMR PKCE primary, NUR-58; per-user accounts)
→ Hermes API gateway :8642/v1 (LIVE, HTTP 200) → role-scoped PERSONA + TOOLSET
→ MCP lanes: OpenEMR (clinical) · Perfex (org) · Chatwoot (inbox) · labs · devices · n8n
```
- Identity = WHO is calling (authenticated user)
- Role = WHAT they may do (persona + toolset + gate level)
- Org = WHERE their data lives (per-tenant profile — one profile per customer org at SaaS scale; users inside an org share it via role scoping — NOT a separate instance per person)

## Role matrix (v1)
| Role | Persona | Allowed lanes | Gate level |
|---|---|---|---|
| **Physician (MD/DO)** | Clinical authority | Full clinical + chart + orders draft + sign-off | Final sign-off |
| **PA / NP** | Clinical provider | Chart review · labs · meds · coding support · orders draft · visit prep | Provider review |
| **Registered Nurse** | Care coordinator | Vitals · med admin assist · patient comms · tasks · follow-up | Nurse review + provider escalate |
| **Paramedic / EMT** | Field clinician | EMS lanes · EMD scripts · device feeds (Lifepak/T1) · drone/overwatch view · scene triage | Field protocols + provider escalate |
| **Lab professional** | Lab operator | Lab lanes · results · QA flags · reference ranges | Lab director review |
| **Radiology tech** | Imaging operator | PACS/Orthanc · study status · protocol checklists · AI-cascade assist (JARVIS) | Tech + radiologist review |
| **Front desk / Admin** | Office | Scheduling · intake · billing support · Perfex tasks | Org admin |
| **Patient / consumer** | Self-service (SANDBOXED) | Appointments · comms · results-view · wellness | Never clinical decision output |

## Rules
1. **One brain, zero lane collisions** — role scoping is config on the SAME gateway (per-tenant Hermes Profiles, NUR-106)
2. **Provider gate is absolute** — lower roles escalate; higher roles sign; nobody below MD/DO gets final clinical authority (founder's doctrine)
3. **PHI stays in OpenEMR** — the app never stores PHI; it renders what the role may see
4. **Per-org isolation at scale** — when a new provider org signs (SaaS), they get a profile + their own data scope — NOT a new server per user
5. **New server only when** — a customer needs full isolation (enterprise) or a new geographic/fleet domain (edge truck node); that's the NUR-106 enterprise tier

## Next steps (in the app build directive a0054c6c)
- Auth scoping: role claims in PKCE token (Canvas) · role matrix into the interface spec · provider-gate enforcement (Hermes) · demo: PA role end-to-end by 08-13
