# NURATECH.ai — UNIFIED MASTER DEPLOYMENT & OPERATIONS MANIFEST (index, 2026-08-02)
Source: founder paste (canonical, consolidated). This file = adopted copy + build-state mapping.

## Manifest structure (Sections I–XI, all adopted)
I. Executive summary & YC thesis — "The New UI is no UI™", Anthropic-for-Healthcare.
II. Unified Platform Architecture — Flutter app → NURA AI Core Router → OpenEMR / Mirth / Perfex → Twilio telecom.
III. Feature matrix — M1 Doximity Super-Suite (HIPAA dialer/WebRTC/voicemail drop · ambient scribe · eFax OCR · AI copilot) · M2 Weave Practice OS (AI voice receptionist · patient comms hub · recall campaigns · scheduling/text-to-pay) · M3 Surgical & Aesthetic Suite (photo grids · treatment plans · tox/filler inventory) · **M4 AI Media Suite (v2: HeyGen avatars · Higgsfield B-roll · CapCut assembly · Socialmonials syndication; SOP-5 blog-to-reel · SOP-6 testimonial syndication · SOP-7 post-op care video → SMS)**.
   Media stack truth (verified): syndication = **bundle.social lane (68 tools, WIRED)** · video gen = **FLUX3 tools (in-toolset)** + HeyGen/CapCut via REST wrappers (all 4 npm packages E404) · voice = **ElevenLabs (VALID)**.
IV. Mirth channels — ADT^A04/A08 (demographics → OpenEMR + Perfex customer) · MDM^T02 (scribe SOAP → external EHR) · DFT^P03 (fee sheets → Perfex invoices). [Deploy with mirth stack :8081]
V. Flutter app spec — lib/ structure (dialer/scribe/fax/communication/scheduling/rcm_analytics) + pubspec deps (flutter_bloc, record, flutter_webrtc, web_socket_channel, pdfview, camera, secure/biometric storage). [All-Flutter ADR ✓; naming decision pending]
VI. Paperclip org chart — Hermes DevOps ($50/mo, 15min heartbeat) · NURA RCM ($30/mo, 6h) · NURA Triage ($120/mo, event-driven) → map to corps roles.
VII. Topology — manifest proposes EDGE node (Traefik/WireGuard/Uptime Kuma) + Core (Hermes/EMR/CRM/Mirth) + Imaging (PACS/RIS). ⚠️ Conflicts with verified fleet: no KVM 2 exists; Perfex = KVM1; PACS = KVM4; NPM not Traefik. → DECISION NEEDED (buy KVM 2 as dedicated edge?).
VIII–XI. Charter/guardrails/SOPs/audit — duplicates of operator-charter + skills (already encoded).

## Pillar → Current build state (verified 2026-08-02)
| Pillar | Component | State |
|---|---|---|
| Clinical dialing/eFax | Doximity | ⏳ app leads on board (Flutter + Backend) — now adapter-fixed, can execute |
| Patient VoIP/SMS/recall | Weave / Solutionreach | ⏳ Twilio lane (0/9 live creds) · ElevenLabs IVR · Chatwoot live |
| EHR/charting/CPT-ICD10 | OpenEMR | ✅ Docker :8080 live · lane mock→api (creds gate) · 20 tools |
| RCM/leads/invoicing | Perfex | ✅ live (183 tools) · bridge spec NUR-41 (manifest SOP-3/4) |
| Ambient scribe | Hermes clinical scribe skills | ✅ hermes-clinical-documentation-scribe · nlp-clinical-notes · encounter orchestrator |
| Payments | NMI (+ pay.nuratech.ai) | ✅ NMI docs complete · ChipDna/Direct Connect · NURAPAY pending |
| Integration engine | NextGen Connect = Mirth | ✅ mirth-docker-stack (validated, deploy pending :8081) |
| Control plane | Paperclip | ✅ **CEO + 46/48 agents LIVE on Hermes gateway** (fixed 2026-08-02) · NUR-42 launch directive active |
| Mobile/desktop UI | Flutter (all-Flutter ADR) | ⏳ nura-mobile vs nura_health_communications decision pending |

## Standing commitments (carried)
All-Flutter · local-first/offline-capable · PHI stays on KVM4 · approval-gated · audit-friendly · 99.9% SLA · free-lane-first inference · no duplication (dedupe registry) · skill+memory per fix.
