# NURA OSINT Edge Display

## Purpose

Create one compact live intelligence display that can be rendered in two places:

1. the physical ESP32/Raspberry Pi edge screen; and
2. the Notion OSINT command page.

Both surfaces must consume the same normalized state payload so they do not drift.

## Architecture

```text
OSINT sources
    |
    v
Hermes / collector services
    |
    v
Verification + confidence layer
    |
    v
Normalized DisplayState JSON
    |
    +--> ESP32 / Raspberry Pi display
    |
    +--> Notion command display
```

## DisplayState contract

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-08-31T00:00:00-05:00",
  "system_status": "ONLINE",
  "threat_level": "NORMAL",
  "p0_alerts": 0,
  "source_health": "HEALTHY",
  "brief_status": "READY",
  "top_signal": {
    "title": "Waiting for next verified high-priority item",
    "priority": "P2",
    "confidence": "H",
    "domain": "Ops/Vendor"
  },
  "watch_domains": [
    "Geo/Regional",
    "Cyber/Tech",
    "Ops/Vendor",
    "Markets",
    "Space/Aviation",
    "Weather"
  ]
}
```

## Screen sections

### System header
- NURA OSINT // EDGE DISPLAY
- online/offline state
- last sync timestamp

### Threat
- NORMAL / ELEVATED / HIGH / CRITICAL
- count of P0 alerts

### Source health
- HEALTHY / DEGRADED / DOWN
- source staleness and API failure indicator

### Brief status
- READY / BUILDING / STALE
- confidence state H / M / L

### Top signal
One verified high-priority item with domain, priority, confidence and source provenance.

### Watch domains
Geo/Regional, Cyber/Tech, Ops/Vendor, Markets, Space/Aviation and Weather.

### Pipeline
Intake -> Triage -> Verify -> Synthesize -> Publish -> Archive.

## Governance

- OSINT only: public or commercially available sources.
- Preserve source provenance for every displayed claim.
- Prefer primary sources.
- Require two-source corroboration for high-impact claims when feasible.
- Explicitly label low-confidence or speculative information.
- Minimize PII and do not target private individuals.
- Keep the display unclassified/shareable unless a separate approved workflow requires otherwise.

## Engineering rules

- The ESP32 and Notion surfaces are presentation clients, not independent sources of truth.
- Display payload must be versioned and backward compatible.
- Never hard-code credentials in firmware, Notion content or this repository.
- Use authenticated read-only endpoints for the edge device.
- Cache the last known good state locally for temporary network outages.
- Show a visible stale-data indicator when the payload exceeds its freshness threshold.
- Log collection/verification errors without storing secrets or sensitive data.

## Acceptance criteria

- ESP32 and Notion show the same top signal and threat state from one payload.
- Last-sync timestamp is visible.
- Stale data is clearly flagged.
- P0 events can override the normal display state.
- Each displayed signal can be traced to source provenance in the OSINT board.

## Next implementation

1. Define `/api/v1/display-state` on the NURA/Hermes backend.
2. Add schema validation and signed/authenticated read access.
3. Build the ESP32 renderer.
4. Build the Notion HTML/embed renderer or synced dashboard surface.
5. Add source-health and staleness checks.
6. Add a P0 alert mode and test offline behavior.
