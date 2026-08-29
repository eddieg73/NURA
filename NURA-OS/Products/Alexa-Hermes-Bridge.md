# Alexa ↔ Hermes Bridge — the wiring (2026-08-16)

"Alexa, ask NURA…" → the skill → Lambda → the NURA public door → Hermes → the answer spoken by Alexa.

## What's built (ready to deploy)
- `/opt/data/alexa/nura-skill.json` — the interaction model: invocation "nura"
  - TalkIntent (ask anything) · StatusIntent · WeatherIntent · BriefingIntent · MeshIntent · ClinicalIntent (provider-gated note)
- `/opt/data/alexa/lambda_handler.py` — the Lambda: Alexa text → POST → Hermes → SSML reply
  - env `NURA_HERMES_URL` = the public door (default https://api.nuratech.ai/hermes/alexa)

## The one founder gate (5 minutes, free)
1. **developer.amazon.com** → sign in with the Amazon account
2. Alexa Developer Console → **Create Skill** → Custom → "nura"
3. Upload `nura-skill.json` (the JSON Editor → drag-drop)
4. **AWS console** → Lambda → create function (Python 3.12) → paste `lambda_handler.py`
5. Set the `NURA_HERMES_URL` env → the skill's endpoint → the Lambda ARN
6. Save + build → the skill is live on every Echo on the account

## What works the moment it's live
- "Alexa, ask NURA for the weather" → my METAR read, spoken
- "Alexa, ask NURA for a briefing" → the daily brief, spoken
- "Alexa, ask NURA how is the fleet" → fleet status, spoken
- "Alexa, ask NURA <anything>" → a real conversation with me through the Echo
- Clinical questions → answered with the provider-gate note (decision-support only, never a diagnosis as fact)

## The mesh tie-ins (after the AWS/Sidewalk gates)
- The Echo = the patient-side mesh bridge (Sidewalk) AND the voice endpoint (this skill) — one device, both lanes
- The mesh-router inbox can speak through Alexa: "NURA mesh: node X offline" → the Echo announces it

## Standing rules
- No PHI in spoken output by default (the lockscreen rule) · clinical = provider-gated · every Alexa exchange logged to the black-box
