# NURA Medical — App Store Submission Package

## Product identity

- **App name:** NURA Medical
- **Subtitle:** Clinician Workflow & Drafts
- **Bundle identifier:** `ai.nuratech.nuramedical` (confirm ownership in the Apple Developer account before signing)
- **Primary category:** Medical
- **Suggested secondary category:** Productivity
- **Version:** `1.0.0`
- **Minimum iOS:** 15.0
- **Support URL:** `https://nuratech.ai/support`
- **Privacy policy URL:** `https://nuratech.ai/privacy`
- **Terms URL:** `https://nuratech.ai/terms`

## Promotional text

Capture clinician-entered source facts, create controlled documentation and clinical synthesis drafts, manage operational tasks, and retain a visible provider-review boundary.

## Description

NURA Medical is a clinician-facing workflow application for secure source-text capture, ambient dictation, documentation drafts, clinical synthesis drafts, operations tasks, and an offline E6B calculation aid.

Clinical outputs are separated into source facts, interpretation, ordered possibilities, dangerous alternatives, red flags, missing data, recommended next steps, urgency, confidence, evidence date, provenance, and limitations. Every generated clinical output is visibly labeled as a draft and requires accountable clinician review before use.

Key capabilities:

- Clinician-initiated dictation and editable source-text capture
- Structured scribe, synthesis, and differential-support drafts
- Persistent draft history and review status
- Organization-scoped operations task queue
- Secure sign-in with encrypted platform credential storage
- Account data export and permanent in-app account deletion
- Privacy, support, and clinical-safety disclosures in the app
- Offline advisory E6B calculations

NURA Medical is not an emergency communication service and does not replace professional judgment, establish a diagnosis, or authorize treatment.

## Keywords

`clinical workflow, medical scribe, clinician, documentation, decision support, healthcare, tasks, E6B`

## Review notes

Use the separate `APP_REVIEW_NOTES.md` file. The review backend must remain available over HTTPS for the entire review period. Do not place permanent production credentials in this repository or the listing.

## Required creative assets

Before submission, upload final NURA-owned assets through App Store Connect:

- App icon without transparency
- iPhone screenshots for the device classes requested by App Store Connect
- iPad screenshots if iPad distribution remains enabled
- Optional app preview video

Recommended screenshot sequence:

1. Secure clinician sign-in
2. Ambient Scribe consent and source capture
3. Structured draft with provider-review banner
4. Clinical synthesis with uncertainty and missing-data fields
5. Operations task queue
6. Account privacy, export, and deletion controls

Do not show real patient information in screenshots or preview media.

## Claims discipline

Do not use the following phrases in metadata, screenshots, or marketing without a completed regulatory and evidentiary review:

- autonomous diagnosis
- replaces a physician or clinician
- guaranteed accuracy
- FDA approved or cleared
- prevents adverse events
- treats, cures, or manages a disease autonomously

Use: **clinician workflow**, **decision-support draft**, **provider review required**, and **not for emergency communication**.

## Export compliance

The build sets `ITSAppUsesNonExemptEncryption=false` because the application relies on standard platform and HTTPS encryption rather than proprietary non-exempt cryptography. Confirm the final export-compliance answer in App Store Connect with counsel or the release owner.
