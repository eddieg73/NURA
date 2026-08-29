# ONE App — the final combined architecture (2026-08-17)

The Doximity-style provider app combining EVERYTHING built. The pieces now exist end to end.

## The stack (each layer = built or installing)
```
FLUTTER APP (the ONE face — /opt/data/nura_medical)
  Screen 1: the NURA command UI · Screen 2: the Doximity-style clinical toggle
  Login gate: NPI or paramedic license (the founder's 08-16 rule)
  + the fhir package (pub.dev fhir 0.12.1) for the data layer

FHIR BACKBONE — Medplum (installing on the Lab, Apache-2.0)
  the CDR (the FHIR server) · the SMART-on-FHIR/OAuth auth (the login!)
  the React/TS component library · the Bots (the automation lane)
  (the alternative: microsoft/fhir-server 1,377★ — the backup FHIR service)

THE RECORD — OpenEMR (the clinical truth, the FHIR R4 surface mapped)
  labs→Observation · interpretation→DiagnosticReport · faxes→DocumentReference

THE ENGINES (the scut work — all provider-approved)
  nura-dx · nura-clinical-synthesis · nura-lab-trends · the radiology classifiers
  (TorchXRayVision + TotalSegmentator) · the tools API :8095

THE HANDS — the NURA harness + dsh (the DeepSeek Harness, the plugins)
THE BRAIN — Hermes (the memory, the lanes, the orchestration)
THE RECEIPTS — OpenWALDO (the provenance on every artifact)
THE TRANSPORT — Mirth/OIE (the HL7/MLLP routing)
THE IMAGING — Orthanc (:4242/:8042) + the OHIF viewer space
THE REVENUE — Perfex (the 183-tool MCP, the sanitized billing)
```

## The combined flow (one patient, one chain)
```
Login (NPI gate) → the patient chart (Medplum FHIR + OpenEMR)
  → the labs land (fax/email → Mirth → Observation + the interpretation)
  → the images land (modalities → Orthanc → the OHIF view + the AI read)
  → the encounter: the dx + synthesis + trends (the engines)
  → the provider approves → the sanitized billing → Perfex
  → every artifact carries the WALDO receipt + the provenance
```

## The remaining gates (the founder's list)
- The Perfex token + the OpenEMR API key (the revenue wire)
- The Kaggle fine-tune (the trained clinical model)
- The Medplum deploy verification (the ping inbound)
- The Flutter build → the app store lane

## The doctrine (unchanged)
- One brain (Hermes) · the provider approves · API only, never DB writes
- PHI never crosses into the revenue systems · every output labeled DRAFT
