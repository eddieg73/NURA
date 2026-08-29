# Medisun Safety-Cam Policy (DRAFT — medical director sign-off required)

## Purpose
A safety-cam (glasses-mounted or body-worn, per the founder's directive) on a community medic
serves **medic protection**, **scene documentation**, and **incident reconstruction**. This
policy governs its capture + retention to keep it defensible.

## The line (non-negotiable)
- **Capture for safety is legitimate** — recording a clinical scene for medic protection is
  standard EMS practice and implied-consent in an emergency.
- **Detection, not identification** — the cam runs local face *detection* (is someone there, age/
  gender/safety context). The `/detect` lane returns **`identity: null`** — it never identifies
  unknown people.
- **NO stranger-surveillance** — no crowd watchlists, no "who are these people" reverse-ID of
  non-participants. That is tracking, not triage, and is prohibited.
- **Consent-gated identity** — if a medic needs to *identify* someone, it's against a **consented
  roster** (enrolled patient/staff) OR an **official missing-person/SAR/alert list**. Never
  ad-hoc reverse-search.

## Capture
- Notification where practical (a small indicator on the device; verbal notice at scene entry).
- Recording starts only on medic action (not always-on background).

## Retention
- 30 days default, then purge (industry practice). Medical-legal holds override.
- Audited: every session logged (who, when, trigger, retention).

## Who can access
- Medic + the clinical/QA review lane. PHI stays on the clinical side. No external/non-BAA host.

## Review
- Periodic QA review of flagged events only; no routine mass review.

## Sign-off
- This is a DRAFT. The founder (medical director) must sign before go-live, and it must live in
  the Medisun clinic SOP. Hermes holds the engineering boundary; the medical director holds the
  clinical one.
