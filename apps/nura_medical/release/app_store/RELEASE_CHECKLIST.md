# NURA Medical — Release Checklist

A release is submission-ready only when every blocking item below is complete and evidenced.

## Code and automated verification

- [x] Mobile API base URL is compile-time configurable
- [x] Release builds reject HTTP and loopback API hosts
- [x] Secure token storage and refresh-token rotation are implemented
- [x] Clinical source capture requires consent/authority attestation
- [x] Clinical results display facts, interpretation, differential, danger, missing data, urgency, confidence, provenance, limitations, and review status
- [x] Account export is implemented
- [x] In-app permanent account deletion is implemented
- [x] API tests are included
- [x] Flutter tests are included
- [x] Linux Flutter and backend CI are defined
- [x] macOS unsigned iOS release compilation is defined
- [x] Codemagic signed IPA/TestFlight workflow is defined
- [x] Privacy manifest and permission descriptions are included

## Apple Developer and App Store Connect — blocking external items

- [ ] Confirm the Apple Developer legal entity and active paid membership
- [ ] Register or confirm ownership of `ai.nuratech.nuramedical`
- [ ] Create the App Store Connect app record
- [ ] Connect App Store Connect API credentials to Codemagic
- [ ] Create or import the App Store distribution certificate and provisioning profile
- [ ] Confirm the iOS deployment target and supported devices
- [ ] Upload a final NURA-owned app icon with no transparency
- [ ] Upload screenshots using de-identified demonstration data
- [ ] Complete age rating and content-rights questions
- [ ] Complete export-compliance questions
- [ ] Complete the App Privacy questionnaire using the production vendor inventory
- [ ] Supply the review account and keep it active through review

## Production backend — blocking external items

- [ ] Inventory Hostinger/VPS containers, ports, reverse proxy, volumes, databases, backups, certificates, and secrets
- [ ] Deploy `services/nura_medical_api` behind an approved HTTPS route
- [ ] Replace JWT, database, administrator, review-account, and upstream-engine secrets
- [ ] Disable demo-data seeding
- [ ] Restrict CORS to approved origins
- [ ] Configure encrypted backups and complete a restoration test
- [ ] Configure centralized audit retention, monitoring, alerting, and incident response
- [ ] Confirm account deletion behavior in primary storage and backup-retention policy
- [ ] Run load, restart, network-failure, and rollback tests

## Clinical, privacy, legal, and security — blocking external items

- [ ] Approve intended use, exclusions, accountable owner, and reviewer roles
- [ ] Complete clinical validation on representative cases and subgroups
- [ ] Establish dangerous-alternative and red-flag acceptance criteria
- [ ] Approve known failure modes and downtime workflow
- [ ] Complete HIPAA/PHI data-flow review
- [ ] Execute required BAAs and vendor agreements
- [ ] Approve the speech-recognition processing route
- [ ] Publish accurate Privacy Policy, Terms, and Support pages
- [ ] Confirm medical-device/regulatory posture for the final claims and functionality
- [ ] Obtain final clinical, privacy, security, legal, and executive release approvals

## TestFlight release gate

- [ ] CI is green at the release commit
- [ ] Signed IPA builds successfully
- [ ] TestFlight smoke test passes on at least one current iPhone and one minimum-supported iPhone
- [ ] Microphone denied/allowed flows pass
- [ ] Expired access token and refresh token flows pass
- [ ] Offline and backend-unavailable flows pass without data loss or unsafe output
- [ ] Consent enforcement passes
- [ ] Draft/review banner remains visible on every clinical output
- [ ] Export and deletion pass against the production candidate environment
- [ ] No real PHI appears in screenshots, logs, crash reports, analytics, or review data

## Final submission record

Record before submission:

- Release commit:
- CI run:
- Codemagic build:
- TestFlight build:
- API deployment version:
- Clinical approver:
- Security approver:
- Privacy/legal approver:
- Executive approver:
- Submission date:
- Rollback owner and procedure:
