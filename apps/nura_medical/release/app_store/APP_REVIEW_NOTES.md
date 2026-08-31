# App Review Notes — NURA Medical

## Review account

Create a dedicated, non-production review account in the deployed backend immediately before submission.

- **Email:** `[APP_REVIEW_EMAIL]`
- **Password:** `[APP_REVIEW_PASSWORD]`
- **Role:** Clinician
- **Organization:** NURA App Review

Do not reuse an employee password or include the final password in source control.

## Steps for the reviewer

1. Sign in using the review account.
2. Open **Scribe**.
3. Enter a de-identified sample such as: `Adult with cough for three days. No vital signs supplied.`
4. Enable the consent and authority attestation.
5. Tap **Generate scribe draft**.
6. Observe the persistent `DRAFT — accountable clinician approval is required` banner.
7. Open **Clinical**, select **Synthesis** or **Differential**, submit the same de-identified sample, and review the structured sections.
8. Open **Ops** to create and complete a task.
9. Open **Account & Safety** to view privacy/support information, export account data, sign out, or permanently delete the account.
10. Open **E6B Utility** to test the offline advisory calculations.

## Clinical function explanation

NURA Medical is a clinician workflow and decision-support drafting application. It does not establish a diagnosis, issue treatment orders, or replace the accountable clinician. The backend separates source facts, interpretation, differential possibilities, dangerous alternatives, red flags, missing data, recommended next steps, urgency, confidence, evidence date, provenance, and limitations. Clinical output remains a draft unless reviewed through an authorized reviewer workflow.

The App Store review environment may operate in `AI_PROVIDER=disabled` safe mode. In that mode, the backend demonstrates the complete data, security, consent, and draft workflow without generating diagnostic conclusions.

## Emergency use

The app is not an emergency communication service. The Clinical screen presents an emergency-use warning. Reviewers should not use the app to request or coordinate emergency assistance.

## Microphone

Microphone and speech-recognition permission are requested only when the reviewer taps **Start dictation**. The app remains functional with typed text if permission is denied.

## Account deletion

Account deletion is available inside the Account tab. It requires re-entering the password and deletes the user’s refresh sessions, encounters, clinical drafts, and tasks.

## Backend availability

Keep the review API host, database, TLS certificate, and review account active throughout review. Monitor `/healthz` and `/readyz`, but do not expose those endpoints as a substitute for application authentication.

## Contact

- **Support:** `https://nuratech.ai/support`
- **Privacy:** `https://nuratech.ai/privacy`
- **Technical contact:** `[APP_REVIEW_TECHNICAL_CONTACT]`
