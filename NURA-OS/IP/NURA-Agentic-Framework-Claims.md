# NURA Agentic Medical Intelligence Framework — Provisional Claims (FILED anchor)

Source: founder-provided provisional (2026-08-02 paste). 22 claims + FIG 1-9 + index of terms.
This is the REAL IP asset (vs the AHMAS draft = DISREGARD).
⚠️ FACTUAL NOTE: this file is a CONDENSED DIGEST of the claims for tracking purposes — NOT a substitute for the filed attorney copy. Any filing/prosecution must use the original document text.

## Claims summary (condensed from the source provisional — structure preserved, wording compressed)
1. **Independent — system**: Unity 3D avatar front-end (speech recognition + NLU dialogue) · speech/lip-sync module · clinical decision engine (conversational context/intent) · backend EHR+CRM (MEDBASE MRS/CRM) · integration middleware (PACS/LIS/eRx) · avatar↔backend secure network (retrieve data, record encounters, execute orders) · communication subsystem API (voice/SMS/fax/email) → unified clinical decision support, documentation, care coordination.
2. Avatar = lifelike, facial expression + gesture animations.
3. UI shows clinical info + controls/indicators alongside avatar.
4. MEDBASE MRS (on CRM platform): demographics/history/encounters/problems/meds/orders; MEDBASE CRM: scheduling/follow-ups/comm logs — tandem supply/accept from avatar.
5. Middleware connectors: (a) Orthanc PACS — imaging orders + DICOM retrieval; (b) OpenELIS LIS — lab orders + results; (c) DrFirst eRx — validation (interactions/allergies/formulary) + pharmacy transmission.
6. Clinical coding subsystem: ICD-10/CPT/SNOMED mappings + **RAF/HCC risk scoring** from diagnoses.
7. Coding confirmation flow: suggested codes → clinician confirm → EHR billing/problem list (real-time CDI).
8. Emergency protocol logic: critical-event detection → predefined workflows (alert code teams via comms, verbal guidance, life-safety priority).
9. Emergency triggers: user command (spoken keyword) OR automated device input (e.g., **BLE monitor cardiac-arrest rhythm**) → override normal dialogue.
10. Dynamic context switching: pause/store current context, shift focus, resume without loss; swap patients/topics on the fly.
11. Context tracks: multiple dialogue state tracks + identifiers per active context.
12. **Offline caching module**: local encrypted cache; offline retrieval/encounter recording/order+message queue → sync on reconnect.
13. Offline conflict resolution: secure local storage + reconciliation rules preserving integrity.
14. **BLE interface**: detect/connect BLE medical devices; automatic patient context + physiologic data import (wearables, smart ID badges).
15. BLE features: (a) proximity-triggered chart loading (beacon on patient/bed); (b) continuous/periodic vitals streaming + real-time abnormal alerts; (c) device data logged to EHR without manual transcription.
16. Communication subsystem (Twilio-class): (a) programmable voice calls; (b) SMS (reminders/updates/consult); (c) fax via API; (d) email w/ attachments — omnichannel outreach driven by clinical events (auto lab-result notification).
17. **Independent — method (8 steps)**: engage via 3D avatar (capture speech, animated response) → query EHR by context → AI decision support (diagnoses/tests/treatment) → execute actions (LIS orders, PACS orders, eRx) → documentation + coding (ICD-10/CPT) → communications coordination (voice/SMS/email) → context/safety monitoring (interruptions + emergency triggers) → sync/caching (offline resilience) → continuous intelligent assistant.
18. Fluid multi-topic conversational navigation.
19. Real-time CDS in conversation: drug-interaction warnings, evidence-based test suggestions without separate query.
20. **Real-time image annotation**: receive PACS image, annotate via avatar interface, save back (EHR/PACS) — image findings recorded instantly.
21. Post-encounter automation: summary/education email + SMS scheduling link (prior authorization).
22. **Computer-readable medium** → NURA Agentic Medical Intelligence Framework.

## Key inventive pillars (for continuation strategy)
Avatar-as-orchestrator · BLE proximity context + vital sync · emergency override from device input · dynamic context tracks · offline-first with conflict resolution · real-time coding + RAF · omnichannel clinical comms · image annotation in-conversation.

## Implementation matrix (founder table) — honest status vs current build
| Claim | Founder status | Current-build truth (2026-08-02) |
|---|---|---|
| 1-8, 11-13, 17-22 | ✅ Fully Implemented (original Azure/GPT-4/LangGraph build) | PARTIAL — core Hermes/MCP + OpenEMR/Perfex + Mirth live; avatar front-end = app spec v2 (SCOPE FREEZE), Unity avatar NOT built; MEDBASE→OpenEMR; DrFirst→**WENO EPCS**; OpenELIS→Mirth labs; Celero→**NMI**; Twilio **401-dead** (Documo fax instead) |
| 9 (BLE emergency trigger) | 🚧 Scheduled Phase 2 | Unbuilt — device lane just started (medical-device-connectivity skill) |
| 10 (cross-device session) | 🚧 In Progress | Shared session memory partial (Hermes profiles) |
| 14-16 (BLE + comms) | ✅ per table | BLE unbuilt; comms = Twilio dead, Documo/fax + Telegram/email live |

**Prosecution note**: claims stay broad (good); continuation should add the 2026 self-hosted/offline-first implementation + device telemetry CDS (NEWS2 engine) + provider-gate — materially strengthens claims 12/13/17.
