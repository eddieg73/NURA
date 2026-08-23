# 09 — MODULE INDEX (peripheral domains — document, don't rebuild)

These domains are already substantial, tested systems documented as **skills** in the Hermes
harness + existing fleet services. This is the index; the skill is the detailed reference. They are
consumer/clients of the platform (emit/consume Hermes events or are control surfaces), not core
platform services.

| Module | Category | Home (skill / service) | Boundary |
|---|---|---|---|
| **Aviation** | J | [S]aviation-pilot-ops · foreflight-integration · weather-lightning-monitor | Garmin/ForeFlight integration; Avionics → Atlas |
| **Vehicles / AV** | K | [S]openpilot-* · obd2-vehicle-telemetry · comma-av-control | Hermes=brain, openpilot=driver (sim-first, read-only default, human override) |
| **Drones / EMS** | L | [S]drone-swarm-division · ems-agency-ops · meshtastic-node-monitor | EMS mesh (:8080) · T-Beam client/towers · LoRa custom-PSK · 'EMS DRONE' |
| **Voice / AI persona** | M | [S]voice-message-ops · elevenlabs-tts · emh-clinical-persona | Hermes (JARVIS cadence) · EMH variant (clinical) · Echo local TTS · Chatterbox cloned VP |
| **Business / Corporate** | N | [S]perfex-mcp · self-hosted-accounting-ops · payment-gateway-integrations | Perfex pnl/RCM · pay.nuratech.ai · NMI · Paperclip org · Solis/Oscar MA |
| **Data / Datasets** | O | [S]kaggle-ops · huggingface-hub · clinical-evidence-lanes | B2 dataset lake · Dataset/Knowledge Gateway (license/DUA) |
| **Agents** | R | [S]agent-harness-routing · human-team-management · paperclip-* | VERONICA/AURA/CORA/JARVIS/LEXA/NURA agents + Hermes |

## Cross-cutting note
These peripheral domains share the platform's **boundaries** (PHI rules, storage, event backbone,
approval gates) but add nothing to the core. Treat them as **consumers/clients** of Hermes events and
the Model Gateway — not as sources of authoritative platform state. Reuse existing skills before
adding new code (don't duplicate systems).
