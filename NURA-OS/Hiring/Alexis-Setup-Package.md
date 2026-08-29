# ALEXIS — THE SETUP PACKAGE (new-hire enablement · 2026-08-04)

**Owner:** Alexis Schloeter (the onboarding coordinator — FDA de novo + eMedical/RCM workstreams) · **Signer:** the founder · **Funnel:** the AI hiring manager runs it
**The rule: every hire gets set up CORRECTLY = the spec contract + the access matrix + the environments + the compliance training + the 90-day check-ins — no exceptions, no "we'll figure it out later."**

## 1. THE SETUP SEQUENCE (per new hire)
1. **The funnel closes** → the founder signs → the offer
2. **The spec contract**: the role spec (the vault Hiring/ folder) = the job description + the 90-day plan = the onboarding contract — handed to the hire on day 0
3. **The access matrix** (below) — provisioned by role, revoked on exit (automated where possible)
4. **The environments** — the dev/staging accounts created (never production access by default)
5. **The compliance onboarding** — HIPAA training + the security policies + the BAA awareness (before ANY data access)
6. **The team wiring** — Mattermost account + the role's channels + the calendar + the email (the @nuratech.ai address)
7. **The 30/60/90 check-ins** — the milestones from the spec's 90-day plan, tracked by the Technical PM, reported to the founder
8. **The exit run** — access revocation + the credential sweep + the knowledge handoff (docs owned by the org, never the individual)

## 2. THE ACCESS MATRIX (minimum necessary, role-scoped)
| System | Engineering roles | Clinical roles | Ops/PM | Contractors |
|---|---|---|---|---|
| GitHub (@Nuratech-ai org) | repo-scoped write | read | read | issue-only |
| Mattermost (chat.nuratech.ai) | team + dev channels | clinical channels | ops channels | project channels |
| Email (@nuratech.ai) | yes | yes | yes | yes |
| VPS fleet (root) | **NEVER** (bastion/limited) | never | never | never |
| Docker/gateways (admin) | staging-only | never | read-only dashboards | never |
| Databases | staging-only creds | read-only (approved views) | read-only dashboards | never |
| OpenEMR | staging instance | production (clinician-scoped) | read-only | never |
| Perfex/Paperclip | project-scoped | ops-scoped | full ops | project-scoped |
| Secrets (the sealed env) | Hermes + the founder ONLY | never | never | never |
| AI model keys | staged keys | never | never | never |

## 3. THE ENVIRONMENT PROVISIONING (per new engineer)
- GitHub account → the org + the repo access (the repos: nura-medical, the kernel, the docs) · CI permissions staged
- The dev/staging environment (the 3-node map: Clinic=1441409 · Lab=1030183 · Edge=817449) — the staging containers, the test credentials, the synthetic data (the QA spec's governed data program)
- The docs access (the vault + the docs system) · the SOP library
- The tooling: the IDE/CLI config, the API keys for the staged lanes, the Mattermost/email/calendar
- **The security defaults:** MFA on day 0 · the device posture check · no shared accounts (the Cybersecurity spec's prohibitions)

## 4. THE COMPLIANCE ONBOARDING (before any data access)
- HIPAA Security + Privacy training (role-specific: engineers vs clinicians) · the PHI-handling doctrine (the Lattice, the redaction rules) · the security policies (the policy library) · the AI-boundary training (what Hermes may/may not do — the clinical skills doctrine) · the acceptable-use + the incident-reporting · the signed BAA/HIPAA acknowledgment
- **No access to PHI-touching systems until the training is COMPLETE — tracked, not assumed.**

## 5. THE FOUNDER'S OVERSIGHT
- The 30/60/90 milestones per hire (from the specs) → the Technical PM tracks → the founder reviews monthly (the Executive Review)
- The role specs live in the vault (Hiring/) — the single source of truth for the seats
- Every new hire's setup = the checklist above + the spec contract + the compliance gate — **the "set up correctly" = the checklist, not a vibe.**

## 6. THE TOOLING (Alexis' command center)
- The funnel tracker (the AI hiring manager's board — Paperclip) · the onboarding checklist template (this package, per-role) · the access-request workflow (the founder approves privileged, Alexis provisions standard) · the exit checklist (automated revocation where the platforms allow)
- The SOPs: "Provision a new hire" · "Revoke access" · "The 30/60/90 review" — written by the Technical Writer, owned by Alexis.

**The doctrine: correct setup = the contract + the access + the environments + the compliance gate + the check-ins. The checklist IS the process — every box checked, every gate logged, boss.**
