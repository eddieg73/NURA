# NURA Radiology Intelligence — Hermes Event Catalog (spec §3)

Hermes is the exclusive event backbone (A1/A5). Radiology modules publish/subscribe to the
topics below; **no module writes into another module's database**. Every event uses the
canonical envelope (correlation_id, causation_id, idempotency_key, provenance) and carries a
**payload_ref + payload_sha256** instead of large PHI payloads (DICOM SR/SEG, audio, reports
go to encrypted object storage).

## Canonical envelope
```json
{
  "spec_version": "1.0",
  "event_id": "uuid",
  "event_type": "nura.imaging.inference.completed.v1",
  "schema_version": "1.0.0",
  "source_service": "radiology-orchestrator",
  "tenant_id": "tenant-001",
  "patient_ref": "opaque-patient-uuid",
  "encounter_ref": "opaque-encounter-uuid",
  "case_id": "case-uuid",
  "correlation_id": "workflow-uuid",
  "causation_id": "prior-event-uuid",
  "idempotency_key": "sha256(source+version)",
  "occurred_at": "2026-07-18T18:45:00Z",
  "data_classification": "PHI",
  "payload_ref": "s3://nura-clinical-data/<tenant>/<case>/object.json",
  "payload_sha256": "hex",
  "provenance": {"source_system": "pacs", "model_version": null, "rule_version": null}
}
```

## Topics
| Topic | Producer | Consumer |
|---|---|---|
| nura.imaging.study.received.v1 | Mirth/Orthanc/PACS | ingestion |
| nura.imaging.study.normalized.v1 | ingestion | orchestrator |
| nura.imaging.study.routed.v1 | router | modality pipeline |
| nura.imaging.quality.completed.v1 / .failed.v1 | quality agent | orchestrator |
| nura.imaging.{xray,mammo,ultrasound,dxa,ct,mri}.requested.v1 | router | modality pipeline |
| nura.imaging.inference.completed.v1 / .failed.v1 | modality pipeline | fusion |
| nura.imaging.findings.generated.v1 | findings | differential |
| nura.imaging.differential.generated.v1 | differential | evidence |
| nura.imaging.evidence.retrieved.v1 | evidence engine | report drafter |
| nura.imaging.report.draft-created.v1 | drafter | safety / provider review |
| nura.imaging.urgent-finding.detected.v1 | safety/classifier | escalation |
| nura.imaging.critical-finding.detected.v1 | safety/classifier | escalation |
| nura.imaging.provider-review.requested.v1 | orchestrator | provider review UI |
| nura.imaging.provider-decision.recorded.v1 | provider UI | action executor |
| nura.imaging.report.approved.v1 | provider | action executor |
| nura.imaging.report.finalized.v1 | action executor | Mirth/EHR |
| nura.<domain>.<event>.dlq.v1 | every service | dead-letter |

## Modality routing (deterministic — spec §48)
Model choice = f(Modality, BodyPartExamined, StudyDescription, SeriesDescription) -> model_registry
(routing_policy table). If no validated model exists for the tuple -> **ABSTAIN** and send the
study straight to radiologist review. Never let an arbitrary model decide its own competence.

## Research vs production data (spec §6)
- **Production imaging** = PACS / RIS / DICOM / DICOMweb / FHIR ImagingStudy+DiagnosticReport.
- **Research/eval** = NCI-IDC, TCIA, MIMIC-CXR, VinDr-*, CheXpert, PadChest, CBIS-DDSM, INbreast,
  BUSI, LIDC-IDRI, BraTS, fastMRI, NHANES-DXA, Synthea — all behind the Dataset Gateway,
  gated by dataset_registry.dua/license.
