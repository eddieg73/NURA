# RPM + Amazon Sidewalk Strategy (2026-08-16)

## The revenue model — run against the actual panel
- Panel: 97 lives (CarePilot) · 79 active (Solis truth)
- Enrollment assumption: 50–60% of the 79 active = **40–47 patients** (conservative)
- Billing: 99454 ~$21 one-time setup · 99457 ~$52/mo (20 min review) · 99458 ~$42/mo (each +20 min) · stackable CCM 99490 ~$62/mo
- **40 patients:** 99457 ×12 = $25K + 99458 (half) $10K + CCM $30K ≈ **$65K/yr gross**
- **At full 97 lives:** ≈ **$150K/yr gross** before device costs (~$80/patient one-time ≈ $3–8K) → net ~**$140K/yr**
- This is on TOP of the RAF/HCC work — same patients, second revenue stream.

## The stack (reuses what we already own)
```
Device (BP cuff, glucose, scale, SpO2 — Bluetooth/11073-20601)
  → phone hub (the nura app BLE lane, offline-first)
    → Hermes device-lane: NEWS2/trend scoring (device-scores.py ✓ built)
      → provider dashboard (WebUI) + threshold alerts (Telegram/SMS)
        → billing feed (99457/99458/99490) → Perfex/RCM export
```
- Transport: Bluetooth/app for medical data (regulatory-safe); **Amazon Sidewalk = the free adjunct** (fall detection, room presence, device battery, geo-fence — metadata only)
- OIE intake: vendor gateways → HL7 → DEVICE_TELEMETRY :6668 (the channel exists)

## RPM intake workflow (build phases)
1. **Enrollment** — eligibility check (Medicare Part B, chronic condition) → consent (CMS-compliant) → device assignment → GHL/CRM record
2. **Device ship** — fulfillment + activation (app pairing)
3. **16-day data run** — daily transmissions logged (CMS requires 16 days for 99454)
4. **Monthly review** — 20-min clinical review (99457) → provider sign-off → billing export
5. **Alerts** — NEWS2 ≥5 → provider ping; ≥7 → urgent (the scoring engine is live)

## Honest gaps (flagged)
- Sidewalk's healthcare device ecosystem is thin — pilot it for non-clinical telemetry only
- Vendor BAA needed for any cloud-connected device (vendor-baa-register discipline)
- CMS RPM rules: patient consent, 16-day minimum, provider time documentation — the intake workflow enforces each

## Decision
Build the RPM intake workflow on n8n + the existing lanes; run Sidewalk as a pilot for fall/activity telemetry only; target the 79 active lives with a 50% enrollment goal by Q4.

## Amazon Sidewalk — the PATIENT-home mesh (founder directive 08-16)
The patient-side fabric: Sidewalk = the free home mesh (LoRa 900 + BLE via Echo/Ring bridges, ~90% US coverage).
- **The killer advantage**: zero patient WiFi setup — the #1 RPM dropout cause is pairing/credential failure in elderly homes; Sidewalk devices just work.
- **The device path**: Sidewalk-certified sensors (or BLE devices) → Echo/Ring bridge → Amazon Sidewalk cloud → **AWS IoT Core** → Hermes (MQTT/Tailscale) → the device-lane (NEWS2) → provider alerts → billing.
- **The honest constraint**: Sidewalk's HEALTHCARE device catalog is thin today — the pragmatic split:
  - BLE RPM devices (BP/glucose/scale/SpO2) → the nura app / Echo BLE bridge (the established lane)
  - Sidewalk = the low-bandwidth adjunct: fall detection, room presence, panic buttons, device battery states
- **The compliance note**: PHI transiting Amazon's network = the AWS HIPAA-eligible services + BAA discipline (vendor-baa-register) — the mesh is a carrier, not a substitute for the BAA.
- **The patient stack**: Echo (voice reminders + the bridge) + BLE RPM kit + Sidewalk fall/presence → Hermes: NEWS2 scoring, threshold alerts to the provider, the 99457 review queue.
