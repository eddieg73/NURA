# NURA Capsule / NURA Tag — BLE Wearable Hardware (banked 2026-08-02)

Source: founder engineering package (BOM + 6-sheet drawing spec, LaunchPad AI / 818 Chestnut St.).
This is REAL hardware supporting provisional claims 14-15 (BLE interface, proximity context, vital sync).

## Device concept
- **NURA Capsule** (PN NURA-C-001): PLAUD-style recording capsule — BLE 5.0, PDM beamforming mics, micro-SD, pogo charging, IP67
- **NURA Tag** (PN NURA-T-001): proximity/ID tag variant (UWB)
- Role: clinician-worn recorder + patient-room beacon → claim 15(a) proximity chart loading, 15(b) vital streaming, ambient scribe input

## BOM core (verified part numbers)
nRF52840-QIAA-R (Nordic, BLE 5.0 + Cortex-M4) · MP34DT01-A PDM MEMS ×2 (ST) · EEMB 502030 LiPo 270mAh + S-8205A/DW01A protection · MCP73831T charger · Mill-Max 851-10 pogo pins ×4 · Molex 502181-0890 micro-SD · C&K KMR211GLFS button · Kingbright WP7113ID RGB LED · PAM8302A amp + 8Ω 95dB speaker · Abracon 32MHz + Epson TG2016SB RTC · Tag-Connect TC2050 SWD · (opt) Precision Microdrives 310-101 haptic

## Enclosure/QA spec
PC-ABS UL94 V-0 white · IP67 (1m/30min) · ±0.1mm tolerances · matte Ra 0.8μm · M1.4×4 screws 0.15 N·m · torque/function tests before screw-down

## IP note
Hardware implements claims 14-15. Continuation-worthy: BLE-proximity chart loading + encrypted local cache (micro-SD) ties claims 12-13 + 14-15 together. Keep BOM + drawing spec with the provisional file set.
