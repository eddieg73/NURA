# NURA Medical — Clinical Safety Case

## Intended use

NURA Medical assists authenticated clinicians with source-text capture, documentation drafts, clinical synthesis drafts, differential-support drafts, and operational task tracking. It is clinician decision support and workflow software.

## Explicit exclusions

NURA Medical is not intended to:

- replace an accountable clinician
- establish a final diagnosis
- issue or execute medication, procedure, disposition, or treatment orders
- autonomously contact patients or third parties
- function as an emergency communication system
- monitor a patient continuously
- control a medical device
- overwrite verified facts in an EHR
- serve as the sole basis for a time-critical decision

## Accountable users

- **Clinician:** enters source facts and receives drafts
- **Reviewer:** approves or rejects a draft after independent review
- **Administrator:** manages organizational access and can review audit records
- **Clinical owner:** approves intended use, validation, and release criteria
- **Security/privacy owner:** approves data flow, vendors, retention, and incident controls

## Safety architecture

1. User-entered source text is stored separately from model interpretation.
2. Submission requires consent and authority attestation.
3. The backend is organization-scoped.
4. Every output follows the NURA clinical contract.
5. Every output is created with status `draft`.
6. Only reviewer or administrator roles can approve or reject a draft.
7. No downstream clinical action is implemented in this release.
8. Inference defaults to disabled safe mode.
9. External AI routing is blocked without explicit contractual and PHI approval flags.
10. Audit events record authentication, draft creation, review, task changes, export, and deletion without storing request bodies in logs.

## Clinical output contract

Each draft must represent:

- source facts
- interpretation
- ordered possibilities and support
- dangerous alternatives
- red flags
- missing data
- recommended next step
- urgency
- confidence
- evidence date
- provenance
- limitations
- provider/reviewer status

If the output cannot satisfy the contract, the request must fail rather than silently return unstructured text.

## Failure behavior

| Failure | Required behavior |
|---|---|
| No approved AI provider | Return disabled safe-mode draft; do not infer |
| Provider timeout or malformed output | Return controlled error; store no misleading draft |
| Expired access token | Attempt one refresh; require sign-in if refresh fails |
| Backend unavailable | Preserve local session, show service-unavailable state, do not fabricate output |
| Consent not attested | Reject submission |
| Unauthorized reviewer action | Reject with role error |
| Cross-organization identifier | Return not found; never reveal existence |
| Emergency language | Application warning remains visible; model must not replace emergency activation |
| Account deletion | Delete user sessions and user-owned clinical/operations records |

## Validation plan

Before clinical production use, validate on a locked, representative dataset that includes:

- common outpatient presentations
- emergency and time-critical red flags
- ambiguous, incomplete, and contradictory cases
- medication and allergy complexity
- pediatric, geriatric, pregnancy, and disability-related subgroups as applicable
- multilingual or low-literacy source text as applicable
- adversarial and prompt-injection text
- data with missing vital signs or test results
- cases where the correct behavior is to abstain

Measure at minimum:

- source-fact fidelity
- hallucinated-fact rate
- dangerous-alternative recall
- red-flag recall
- calibration and abstention
- reviewer agreement and correction burden
- subgroup performance
- latency, timeout, and recovery behavior
- cross-tenant access tests

## Monitoring and rollback

Monitor:

- provider failures and malformed outputs
- latency and timeout rate
- authentication and refresh failures
- unexpected volume or abuse
- reviewer rejection and material-correction rates
- dangerous-alternative misses discovered in review
- cross-tenant authorization failures

Rollback triggers include:

- any confirmed cross-tenant disclosure
- unexplained source-fact alteration
- material dangerous-alternative failures above the approved threshold
- unapproved PHI routing
- loss of auditability
- inability to revoke access or delete an account

Rollback must set `AI_PROVIDER=disabled`, preserve source data and audit evidence, stop external inference, and retain the clinician’s manual workflow.

## Unresolved release approvals

- Production inference provider and model
- PHI/BAA status and retention configuration
- Validation dataset and acceptance thresholds
- Regulatory classification and claims approval
- Published privacy and terms documents
- Final accountable clinical, security, privacy, legal, and executive approvers
