# NURA Repository Governance

## Purpose

This repository is the canonical source for the shared NURA clinical communications and intelligence platform. It is **not** a catch-all repository for unrelated ventures, prototypes, or one-off research projects.

## Canonical branch model

- `master` — protected release/canonical branch for the shared NURA platform.
- `develop` — optional integration branch when needed for multi-PR release trains.
- `feature/*` — isolated feature work.
- `fix/*` — defect corrections.
- `release/*` — release candidates.
- `chore/*` — maintenance, governance, CI, documentation.
- Experimental work must live under `experiment/*` or, preferably, in a dedicated repository.

The repository default branch should point to the canonical release branch, not a product-specific feature branch.

## Product boundaries

### Belongs here

- NURA shared platform services
- NURA clinician/mobile application
- shared authentication and identity
- governed agent interfaces
- interoperability adapters and shared integration contracts
- platform-wide observability, audit, and security controls
- shared SDKs and reusable infrastructure

### Does not belong here

- Brawlerz Box fitness product
- Artificial Medic robotics/humanoid R&D
- Medisun-specific operating policy and clinical standing orders
- Care Pilot product-specific implementation when it can be isolated in its own repository
- one-off prototypes that do not ship as part of the NURA shared platform

## Source-of-truth boundaries

- **GitHub:** code, versioned technical architecture, CI/CD, infrastructure-as-code, ADRs.
- **Notion / JARVIS:** executive portfolio, ownership, decisions, operating policies, clinical governance.
- **Clinical EMR:** patient record/source record for deployed clinical environments.
- **Google Drive / legal document repository:** signed contracts, legal originals, corporate records.

## Clinical safety boundary

AI can assist with retrieval, drafting, prioritization, and decision support. Production systems must preserve human review for consequential clinical, coding, billing, legal, and credentialing actions unless a specifically approved workflow authorizes otherwise.

## Change control

Every production change should answer:

1. What product/domain owns this change?
2. What repository and service own it?
3. What data source is affected?
4. Does it touch PHI, clinical decision support, billing, identity, or credentials?
5. What tests/acceptance criteria prove it works?
6. What rollback path exists?
7. What documentation/ADR must be updated?

## Migration rule for legacy branches

Legacy branches are not deleted until their unique commits have been classified as one of:

- merged/current
- product extraction candidate
- historical/archive
- superseded
- unsafe/abandoned

After extraction/merger, stale branches may be deleted only after confirmation that no unique production or legal record depends on them.
