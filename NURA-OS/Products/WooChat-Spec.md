# WOO CHAT — the patient-engagement layer (the Weave merge · 2026-08-04)

**Product:** Woo Chat = the patient-facing communication + engagement layer of the NURA app — the "rest of Weave" merged onto the existing clinical core. **The NURA stack becomes two-sided: Doximity-style (provider network) + Weave-style (patient engagement) — one app, both sides.**

## 1. WHAT WEAVE IS (the feature map we're copying)
Weave = the clinic communication platform: patient SMS/MMS texting · phone system · online reviews · payment processing · appointment reminders · online scheduling · digital forms · recall/re-engagement campaigns · email marketing · the all-in-one inbox.

## 2. THE WOO CHAT FEATURE MAP (merged onto NURA's rails)
| Weave feature | Woo Chat module | THE EXISTING RAIL (already ours) |
|---|---|---|
| Patient texting | **Chat** — two-way SMS/MMS in the app | Twilio (727-477-3636 + 305-206-8697 lines) + Chatwoot (deployed inbox) |
| The inbox | **Unified Inbox** — conversations + assignments + labels | Chatwoot omnichannel (LIVE) |
| Appointment reminders | **Reminders** — automated no-show reduction | n8n workflows + Twilio + OpenEMR schedules |
| Online scheduling | **Schedule** — patient self-booking | OpenEMR appointments + the n8n lane |
| Digital forms | **Forms** — intake/consent/registration | the forms lane (n8n + the vault templates) |
| Payments | **Pay** — card on file + payment links | NMI ChipDna (operator-gated) / Stripe-class |
| Online reviews | **Reviews** — request + monitor + respond | the social lanes (SocialPilot + the reputation skills) |
| Recall/re-engagement | **Recall** — care-gap outreach (HCC/HEDIS) | CarePilot gaps + Twilio outreach + the population-health lanes |
| Phone system | **Voice** — the clinic phone in the app | Twilio voice (the dialer rail) |
| Email marketing | **Campaigns** — newsletters/announcements | the email lanes (himalaya + the comms skills) |
| Free fax | **Fax** — send/receive fax from the app | **Documo** (the MCP tools LIVE: send_fax · list_faxes · fax_status · get_fax — the API key PENDING the founder's drop) |
| The white-label AI | **AI Concierge** — VERONICA answers the chat | VERONICA (reception/intake agent) + the MoE lanes |

## 3. THE MERGE ARCHITECTURE (into the nura-medical app)
```
nura-medical features/  (EXISTING)
├── auth · dashboard · ea · medical · scribe · billing · ems · home
+
WOO CHAT features/  (NEW — the Weave merge)
├── chat/        — the patient conversation inbox (Chatwoot SDK + Twilio SMS)
├── reminders/   — the appointment + follow-up automation (n8n webhooks)
├── schedule/    — the self-booking flow (OpenEMR availability)
├── forms/       — the digital intake (fill + sign + file to OpenEMR)
├── pay/         — the payment links + cards (NMI, operator-gated)
├── reviews/     — the reputation engine (request/monitor/respond)
├── recall/      — the care-gap outreach (CarePilot + Twilio)
├── voice/       — the in-app phone (Twilio voice)
└── concierge/   — VERONICA's chat assistant surface
```
**The doctrine stays: PHI-safe messages → Chatwoot; clinically significant content → OpenEMR only after review; payments operator-gated; the patient chat never auto-enters the chart.**

## 4. THE BUILD ORDER (the "rest of Weave" — after the Doximity layer)
1. **Chat** (the core — Twilio SMS + Chatwoot wired to the app's inbox)
2. **Reminders** (the n8n automation — the no-show reduction, the first revenue proof)
3. **Schedule** (the self-booking — OpenEMR appointments)
4. **Forms** (the digital intake — the Medisun lighthouse first)
5. **Pay** (NMI — the patient payments)
6. **Reviews + Recall + Voice + Concierge** (the engagement completion)

## 5. THE ONE-LINER
**Doximity = the doctors' network · Weave = the patients' channel · Woo Chat = NURA's patient-engagement layer merged onto the app — every patient conversation in one inbox, every reminder automated, every gap recalled, every dollar collected — with VERONICA answering the front line, boss.**
