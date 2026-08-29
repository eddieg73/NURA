# Advisory Board Decision [D3] — Tactical Sensor Stack: Axon Body Cam + ATAK/CIVTAK (2026-08-02)

Founder: embed NURA in Axon body cams (EMS/first-response/tactical medicine); set up ATAK/CIVTAK; research, seat analysis, execute; board improves.

## VERIFIED AXON SURFACE (2026-08-02)
- **Fusus** = Axon's common operating picture (single pane: body cams, drones (Axon Air), fleet, third-party feeds, AI models, CAD) — their LATTICE analog, open platform
- **Evidence Partner API** (developers.axon.com) — official integration lane
- **Draft One** = AI report drafting from BWC audio (GPT-4 Turbo transcribe, officer-in-the-loop, ~5 min) — the DOCUMENTATION play we replicate internally (whisper + Hermes scribe = our Draft One, no per-seat Axon AI fees)

## SEAT ANALYSIS — ATAK/CIVTAK
**Strengths**: open SDK (plugin dev real) · CIVTAK available to first responders · our stack fits (BLE/audio/vision) · Fusus/Axon open-platform fits partner model
**Weaknesses**: our dev capacity busy (app priority) · plugin SDK learning curve · certification/testing burden for field use
**Opportunities**: PJ lane (earpiece + TAK = the founder's special-forces story) · EMS/fire adoption (CIVTAK) · Fusus + TAK + NURA = full COP
**Threats**: ATAK ecosystem crowding · Axon's own AI (Draft One) · mil requirements lock-in
**VERDICT**: BUILD — plugin SDK lane (execution below); DON'T replicate Fusus (integrate as partner); DO replicate Draft One internally (we own the lane, zero licensing)

## BOARD TAKES (10-CEO, paraphrased)
- **Musk**: build the minimum that ships — the Draft-One-equivalent (whisper→scribe) is the fastest proof; don't boil the ocean
- **Bezos**: the customer is the agency — documentation time is their pain; demo = "report drafted in 5 min, you review, done"
- **Zuck**: platform play — Fusus integration as a partner = distribution; our feeds become their ecosystem
- **Huang**: the sensor graph — body cam + drone + vehicle + TAK = one data fabric feeding the COP
- **Jobs**: ONE product: the COP with NURA intelligence; the body cam is a sensor, not the product

## SYNTHESIS + IMPROVEMENTS (board-approved direction)
1. **BUILD Draft-One-equivalent** (whisper transcription + Hermes clinical scribe, provider/officer-in-the-loop) — fastest proof, own the lane
2. **PARTNER with Fusus** (Evidence Partner API — read feeds, export evidence) — never rebuild their COP
3. **BUILD ATAK/CIVTAK plugin** (casualty pins, telemetry overlays, NURA guidance) — the tactical app layer
4. **Body cam = NURA sensor node** (audio→scribe; video→vision cascade; livestream→COP) — EMS/tactical lane
5. Milestones: Draft-One-equivalent PoC by 08-15 · TAK plugin scaffold by 08-22 · Fusus partner application by 08-31

## EXECUTION OWNER
Atlas (directive filed); Hermes executes the PoC lanes; founder approves before any Axon spend.

## [D4] 2026-08-02 — Dual-use wearables + defense contracting (founder directive, board reviewed)
- **Zuckerberg**: wearables = the platform endgame; Meta SDK streaming proves the category; our edge = on-device/sovereign vs cloud-locked Meta — build the glasses SDK-compatible layer but own the inference.
- **Musk**: minimum that ships = camera earbuds first (VueBuds-class, 150-200x adoption) with glasses second; cost target < $300 BOM; dual-use = one product, two markets.
- **Bezos**: last-mile moat = the blind/low-vision civilian distribution (accessibility networks, VA, non-profits) feeding military/LE credibility.
- **Jobs**: say no to a wearables portfolio — ONE wearable product family (glasses + earbuds sharing the same VLM core).
- **Huang**: on-device small VLM (Qwen2.5-VL/Phi-4-vision) + sovereign edge = the differentiator vs cloud-only competitors.
- **Synthesis**: build the dual-use wearable family (earbuds first, glasses second) on one VLM core; PJ connectivity + CIVTAK/ATAK lanes; defense via CMMC 2.0 + SBIR + prime/sub; civilian via EMS/LE/accessibility. Filed: 3137a5ab. Gates: 08-14 spec · 08-20 PJ dossier · 08-25 CMMC/ITAR · 09-01 defense roadmap.
