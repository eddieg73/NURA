# NURA — the Clinical Communications & Intelligence Platform

The monorepo for the NURA stack: the mobile app, the backend-services, the imaging-chain, and the ops-engines.

## The layout
```
NURA/
├── apps/
│   ├── nura_medical/        # the Flutter app (Android+iOS!) — the Doximity-style clinical workspace
│   └── meshtastic-monitor/  # the LoRa-mesh node monitor (the listener + Flask + Leaflet!)
├── backend/
│   └── (the API-services: the DocsGPT-core · the NURA-Bridge!)
├── automation/
│   └── (the n8n-workflow-exports!)
├── infra/
│   ├── scripts/             # the production-ops: the self-heal · the sweep · the ledger · the managers
│   └── (the fleet-configs: the WireGuard · the docker-stacks!)
└── docs/
    └── (the architecture + the guides!)
```

## The stack
- **App**: Flutter (the nura_medical — the clinical-dialer + the inbox + the AI + the scribe + the fax!)
- **Brain**: the DocsGPT-core (the 18-textbook medical-knowledge engine!)
- **Lanes**: the 53-MCP-fleet (the OpenEMR · the Mirth · the Orthanc · the Chatwoot · the Perfex + more!)
- **Ops**: the self-healing engines (the sweep-16/16 · the guardians · the managers · the ledgers!)
- **Infra**: the 3-server fleet + the WireGuard mesh!

## The workflows
- **The CI**: the Codemagic for the iOS-builds (apps/nura_medical/codemagic.yaml!)
- **The build-to-repo**: every production-build lands here (the app ✓ the monitor ✓ the ops-scripts ✓!)
- **The secrets**: NEVER in the repo — the .env-0600 + the credential-registry!

## The governance
- The clinical-truth = the OpenEMR (the sidecar-doctrine!)
- The AI-support + the clinician-decides (the human-review-gates!)
- The audit-trail on every clinical output!
