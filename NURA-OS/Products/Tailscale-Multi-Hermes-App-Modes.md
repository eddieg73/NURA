# Tailscale Every-Device + Multi-Hermes + App UI Modes (2026-08-16)

## 1. Tailscale on every device (free, 5-minute each)
| Device | Install | Then |
|---|---|---|
| **Windows laptop** | tailscale.com/download → Windows .exe → install → log in with the founder account | appears on the tailnet → browser → http://hermes-webui.tail90d8a0.ts.net |
| **iMac** | App Store "Tailscale" (or .pkg) → log in | same tailnet |
| **iPad** | App Store "Tailscale" → log in | WebUI + all :80xx APIs reachable from anywhere |
| **iPhone** | Already ON the tailnet ✓ (12MB of traffic — it's working) | same |
| **Another computer** | same installer → same account login | joins automatically |
- Every device gets a 100.x.x.x address; `hermes-webui` resolves on ALL of them.
- The served APIs (:8080 mesh map, :8092 radiology, :8095 tools, :8440-8446 fleet) all reachable from every device.
- MagicDNS on = plain names, no IPs.

## 2. Multi-Hermes: ONE brain, many faces (the architecture)
- **The brain stays HERE** (the gateway box) — one source of truth for memory, crons, skills, credentials.
- **Every device = a face**: Tailscale + WebUI (the dashboard) + Telegram (the chat) — no local Hermes needed on iPad/iPhone (they CAN'T run it natively — and don't need to).
- **Optional local brains** (Mac/Windows/another computer): install Hermes Agent (pip) — useful for LOCAL compute only:
  - the **iMac/Mac** → the Flutter/iOS build lane (Xcode + CI — the iOS build gate!)
  - the **Windows laptop** → the Windows-side testing lane
  - Local instances stay CLI shells + connect to the shared tailnet services; they do NOT fork the memory — the central brain stays the authority (hermes-profile-operations doctrine: merge, never fork).
- **The rule**: one memory, one cron fleet, one gateway; local installs = workers, not peers.

## 3. The Flutter app = the PRIMARY interface (nura_medical)
- **Screen 1 — the NURA command UI** (the primary, default): chat with Hermes · live status board (fleet, lanes, mesh) · quick tools (derm photo, voice notes, METAR, radiology drafts) · alerts
- **Screen 2 — the Doximity-style clinical UI** (the toggle, for providers who want that route): patient feed · secure provider messaging · clinical documents · referral/collab directory · CME-style feed · the NURA-Frontend-Doximity-Style.md feature set — backed by the SAME backend (OpenEMR + Perfex + Twilio + DocsGPT + radiology + tools)
- **The toggle**: one app, two modes — the provider picks; both hit the same lanes (the ONE-app doctrine: every provider, one surface, full backend)
- Backend contract: WebUI APIs + the tools API :8095 + OpenEMR MCP + the gateway — all tailnet-reachable from the app.

## 4. The roadmap
1. App skeleton: both screens + the Tailscale URLs baked in
2. Auth: the login gate (NPI or paramedic license — the founder's rule)
3. Chat + voice + derm (the tools API) in screen 1
4. The Doximity screen-2 feeds (patients, messages, docs) from OpenEMR/Perfex
5. App Store submit (iOS gate = the iMac/Xcode lane)
