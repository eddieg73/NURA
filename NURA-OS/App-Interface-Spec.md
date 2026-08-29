# NURA App Interface Spec — EA/Medical Dual-Mode + Slash Commands (2026-08-02)

Founder: the interface (per reference image) for the Flutter app, installable on iPhone. Telegram-style /commands. Conversation flows BETWEEN two screens: **EA (Executive Assistant)** and **MEDICAL**.

## Core UX
- **Mode switcher** (top toggle or bottom nav): `[EA] | [MEDICAL]` — switch ANY time mid-conversation
- **Shared conversation thread** — context carries across modes: start in EA, switch to MEDICAL, the thread continues with mode tags (that's the "talk in between two screens" behavior)
- **Input bar**: text + voice (STT whisper-1; hands-free for medical/EMS)
- **Slash command list**: type `/` → command palette with the lists below
- iPhone install: Flutter build → TestFlight/dev signing (Beacon = Apple dev lane)

## EA MODE commands (Hermes executive)
| Command | Action |
|---|---|
| /brief | Morning briefing: fleet · board · revenue · blockers |
| /tasks | Today's priorities (Paperclip scrum digest) |
| /board | Board status (NUR issues, blocked, owners) |
| /fleet | 3-server health — one silent-OK line |
| /crons | Scheduled routines list |
| /cost | Weekly agent cost digest |
| /money | P&L snapshot (Assurance lane) |
| /sync | Vault/LiveSync status |
| /emails | Mail triage (4-class digest) |
| /me | Schedule/calendar + priorities |
| /notes | Capture → vault (voice or text) |
| /do | Delegate to Atlas/agents (scope-tight) |
| /watch | Set a bounded watchdog |
| /status | Gateway + MCP lanes health |
| /help | EA command list |

## MEDICAL MODE commands (provider-gated)
| Command | Action |
|---|---|
| /pt | Patient lookup (OpenEMR) |
| /chart | Visit prep brief / chart summary |
| /labs | Lab trends (A1c, renal, lipids) |
| /meds | Medication list + interaction check |
| /vitals | Vital trajectories |
| /gap | Care gaps (CarePilot/HEDIS/RAF) |
| /code | Coding support (ICD-10/CPT) |
| /dx | Ranked differential (suggestive — provider review) |
| /news | NEWS2 deterioration score (telemetry) |
| /device | Device/telemetry feed status |
| /drug | FDA label / adverse events |
| /ref | Referral draft (clinician-reviewable) |
| /note | Ambient dictation → SOAP draft |
| /consent | Telehealth consent flow |
| /help-med | Medical command list |

## Rules
- Medical mode = decision support; every clinical output carries the provider-review gate
- EA mode = executive ops; consequential actions still approval-gated
- Mode switch preserves context but tags it (EA vs MEDICAL) — no PHI leaks into EA summaries
- Offline-first: both modes work in dead zones (on-device model + deterministic CDS)
- Commands are hints, not walls — free-form chat works in both modes
