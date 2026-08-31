# App Privacy Label Worksheet — NURA Medical

This worksheet must be reconciled against the deployed production configuration and every third-party SDK before answering App Store Connect privacy questions.

## Tracking

- **Tracking used:** No
- **Third-party advertising:** No
- **Cross-app or cross-site tracking:** No
- **Advertising identifier:** Not requested by this codebase
- **Analytics SDK:** None included by this codebase

## Data linked to the clinician account

| Apple privacy category | NURA examples | Purpose | Linked to identity | Tracking |
|---|---|---|---|---|
| Contact Info | Professional email, full name | Account management, authentication, support | Yes | No |
| Identifiers | Internal user ID and organization ID | Authentication, tenancy, audit | Yes | No |
| Health & Fitness / Health information | Clinician-entered case text, patient reference, clinical draft | App functionality and clinician workflow | Yes, within the organization | No |
| User Content | Dictation transcript, typed notes, operations tasks | App functionality | Yes | No |
| Other Data | Review status, audit correlation identifiers | Security, compliance, app functionality | Yes | No |

## Data not collected by the current code

- Precise or coarse location
- Contacts/address book
- Photos or videos
- Browsing history
- Search history outside the app
- Advertising data
- Payment card details
- Device advertising identifier

## Microphone and speech recognition

- The microphone is activated only after the clinician taps **Start dictation**.
- The app displays a consent and authority attestation before clinical text is submitted to NURA.
- The selected iOS speech-recognition implementation may use Apple platform speech services. Confirm whether the final production configuration uses on-device processing, Apple processing, or another approved processor.
- Reflect that processor and its retention/contractual terms in the production privacy policy and vendor inventory.

## Clinical data processing

- Clinical text is sent only to the configured NURA HTTPS API.
- The backend defaults to `AI_PROVIDER=disabled`.
- Hermes or OpenAI routing is disabled until the deployment owner explicitly enables it.
- OpenAI routing additionally requires `OPENAI_BAA_CONFIRMED=true` and `OPENAI_PHI_APPROVED=true`.
- No request bodies should be written to application logs.
- The production database, backups, monitoring, and support tooling must be reviewed as PHI-capable systems.

## User controls

- Account data export is available in-app.
- Permanent account deletion is available in-app and deletes sessions, encounters, drafts, and tasks for the user.
- Sign-out revokes the stored refresh session when the service is reachable and always clears local credentials.

## Reconciliation checklist

Before completing App Store Connect:

- [ ] Confirm production API host and sub-processors
- [ ] Confirm speech-processing route
- [ ] Confirm crash-reporting or analytics SDKs, if later added
- [ ] Confirm support-system access to submitted clinical text
- [ ] Confirm retention and deletion timeframes
- [ ] Confirm backup deletion behavior
- [ ] Confirm privacy policy URLs are public and accurate
- [ ] Confirm the App Store privacy answers match the production build, not merely this repository
