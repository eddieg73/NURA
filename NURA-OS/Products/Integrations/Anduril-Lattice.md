# Integration One-Pager — Anduril Lattice

**Date:** 2026-08-19 · **Public sources only** · Feasibility verdict at bottom.

## What it is
Anduril's **Lattice** is an AI-powered command-and-control / sensor-fusion platform — the "single pane of glass" common operating picture (COP). Sensor-, network-, and system-agnostic: it ingests feeds from thousands of sensors and assets, applies AI/ML to filter signal, and lets operators task assets from the same pane. Publicly positioned as **dual-use**: CBP border security, UK Home Office maritime tracking, USSOCOM ISR/force protection, offshore wind AUV inspection, search-and-rescue, JADC2 ("an open operating system for defense"). One operator supervises hundreds of autonomous systems.

## Developer / integration surface
- **developer.anduril.com** — public documentation for the **Lattice SDK**: **Entities** (the COP data structure — assets you control, tracks (radar/sensor/camera detections, SPI, SOI), geo-entities/regions), **Tasks** (route/execute tasking to assets), **Objects** (binary distribution).
- Protocols: **REST** (HTTP/JSON) and **gRPC/Protobuf** (30–50% bandwidth savings for high-frequency telemetry — drones, robots).
- **Lattice Developer Program:** qualified developers get dev environments with representative **notional data** + Anduril solutions-architecture guidance. Qualification-gated, not open.
- Integration patterns: push data into Lattice (new sensor, new robot), pull data out (task against tracks), build Lattice **apps** (C2, SA, tasking) or **data services** (track correlation, gen-AI track-picture synthesis).

## NURA fit
- **Strategic vision:** NURA already names its internal nervous system "Lattice" (Lattice-Wiring.md — Hermes brain + MCP spine). Anduril Lattice is the *defense-grade* version of that pattern: the EMS agency + Aero drones + field sensors fused into one disaster COP is exactly Lattice's public-safety story (SAR, MCI coordination, drone tasking).
- **Practical fit today:** NURA's EMS/disaster lane needs a COP; **ATAK + TAK Server (free, see companion page) solves that now**. Anduril Lattice becomes relevant only at government-contract scale (defense funding lane, dual-use IP story) — or if NURA ever bids DoD/public-safety programs where Lattice is the incumbent platform.

## Risks / constraints
- Developer Program is **qualified access** — not free, not open; no production deployment without a commercial relationship.
- Defense-adjacent: export controls, ITAR-adjacent sensitivities, no PHI in any shared feed, and NURA's public-source-only doctrine limits how deep we can integrate pre-contract.
- Overkill: Lattice assumes sensor networks at port/border/national scale. NURA's fleet (drones + trucks + wearables) is well within ATAK/TAK Server's capability at zero cost.

## Feasibility verdict
**LOW today, MONITOR for the defense lane.** No public path to production use without a qualified partnership. Practical move: build the EMS COP on ATAK/TAK Server (free, proven — companion page), design the sensor-fusion schema to be Lattice-shaped (entity/track/task concepts), and revisit Lattice only when a public-safety or defense contract makes it the customer's platform. The Lattice *doctrine* is already NURA's internal wiring; the Anduril *product* can wait.
