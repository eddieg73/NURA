# NURA Product Boundaries

## Shared NURA Platform

Owns reusable capabilities shared by multiple NuraTech products:

- identity, authentication, authorization
- clinician/mobile shell
- agent/MCP interface contracts
- audit and observability
- shared interoperability adapters
- common UI/design system
- shared event contracts

## Care Pilot

Population-health command system. Product responsibilities include:

- clinical and utilization risk stratification
- high-utilizer/readmission workflows
- HEDIS/Stars and preventive care workflows
- TCM/CCM/APCM operations
- medication safety/adherence workflows
- MIH/community-paramedicine candidate identification and closed-loop routing
- provider/payer/outcome dashboards

Care Pilot is **not** the clinical EMR and must not become an uncontrolled PHI dumping ground.

## NURA ERP

Operational CRM/ERP. Owns permitted enterprise operations, assignments, workflow status, project/account operations, and minimum-necessary operational metadata. It is not the clinical source record.

## Provider Labs

Clinical intelligence layer for governed provider assistance, including labs, documentation, imaging/radiology support, specialty reasoning modules, and clinical knowledge retrieval. Consequential outputs require the appropriate human approval gate.

## NURA Radiology

PACS/RIS/imaging domain: Orthanc, OHIF, DICOM/DICOMweb, imaging worklists, storage, report workflow, and governed AI imaging support.

## Hermes / NURA Agents

Agent orchestration and tool-use layer. Agents may query governed state and create permitted tasks/actions through controlled APIs. RBAC, tenant isolation, audit, approval gates, and deterministic safety controls are mandatory.

## Medisun MIH

Medisun's clinical operating program, not a NuraTech software product. NURA/Care Pilot provides technology to support it. Standing orders, credentialing, medical direction, scope, training, legal authority, and clinical policy belong in the Medisun governance system; technical interface contracts may be versioned in GitHub.

## Artificial Medic Lab

Robotics/humanoid medical research. Keep separate from production clinical platform repositories until an approved interface is defined.

## Brawlerz Box

Independent fitness/wellness product. It must not share the canonical NURA repository root or default branch.
