---
title: App-Flow-Audit-Release
date: 2026-08-19
tags:
  - nura
  - ios
  - release
  - security
  - marketing
---

# NURA App — Flow Audit, Release Checklist & Launch Plan (2026-08-19)

The QA + iOS-release + security + growth audit of the ONE app (`/opt/data/nura_medical/apps/nura_medical`).
The verdict up front: **the Codemagic pipeline is CORRECT for the TestFlight upload — the Apple key is the ONLY blocking gap.** The app's security posture is good at the data layer (nothing persists = no PHI at rest) but the license-gate is documented, not yet enforced.

Related: [[ONE-App-Final-Architecture]] · [[NURA-Credential-Registry]] · the full deployment checklist: `docs/manuals/IOS-DEPLOYMENT-CHECKLIST.md` · the build guide: `apps/nura_medical/IOS-BUILD-GUIDE.md`

---

## 1. The Codemagic pipeline — verified ✅ (with the notes)

Read: `apps/nura_medical/codemagic.yaml` — workflow `ios-build` ("NURA-iOS").

| Item | State | Note |
|---|---|---|
| `instance_type: mac_mini_m2` | ✅ CORRECT | the macOS M2 builder — required for iOS |
| `integrations: app_store_connect: NURA-AppStoreConnect` | ✅ declared | the credentials live in the Codemagic UI — **the founder's key-drop wires them** |
| `XCODE_WORKSPACE` / `XCODE_SCHEME` (Runner.xcworkspace / Runner) | ✅ CORRECT | the standard Flutter iOS targets |
| `BUNDLE_ID: com.nuratech.nuraMedical` | ✅ CORRECT | matches the enrolled bundle |
| Scripts: pub get → analyze → build `--release --no-codesign` → `xcode-project build-ipa` | ✅ CORRECT | the `--no-codesign` + `build-ipa` is the canonical Codemagic signing pattern (the ASC integration signs at the IPA step) |
| `publishing.app_store_connect`: `auth: integration`, `submit_to_testflight: true`, `beta_groups: NURA-Testers`, `submit_to_app_store: false` | ✅ CORRECT | the TestFlight-first lane, the App-Store submit explicitly off |
| Artifacts (`build/ios/ipa/*.ipa` + xcode logs) + email notify (`eg@nuratech.ai`) | ✅ CORRECT | |

**The verdict: the pipeline's correct for the TestFlight's the upload. The Apple key = the only gap.** ✓ (the task-premise CONFIRMED)

The non-blocking hardening (do them, but they don't stop the TestFlight):
- `APP_STORE_APPLE_ID: 0` — the placeholder by design; set the real app-ID after the first upload (the workflow's comment says so).
- The `beta_groups: NURA-Testers` group must EXIST in App Store Connect before the first publish, or the publishing step fails — create it during the key-setup.
- No `triggering:` section — Codemagic defaults to push-to-any-branch + manual. Add a `push → main` only trigger to match the header comment.
- `flutter: stable` unpinned — fine today; pin the Flutter version once the first green build lands (the reproducible-builds).
- `flutter analyze` fails on errors — the tree is clean, but confirm a local `flutter analyze` green before the first push.

---

## 2. The release checklist — the done vs the pending

### The DONE ✅
- [x] The Flutter app scaffolded (the 5 tabs: Scribe · Clinical · Ops · E6B · Account)
- [x] The bundle ID `com.nuratech.nuraMedical` in the Xcode project
- [x] The iOS build runs local (`flutter build ios --release`)
- [x] The `codemagic.yaml` in-repo, verified correct (the §1 above)
- [x] The build-guide in the repo (`IOS-BUILD-GUIDE.md` — the founder's 5 steps)
- [x] The secrets-doctrine honored — zero secrets in the repo (the URLs only, never the keys)

### The PENDING ⏳ — the Apple key is the gate
- [ ] **Step 1 — the Apple Developer enrollment** ($99/yr, the `Eddie_Garrido@me.com` account, the 24–48h approval)
- [ ] **Step 2 — the App Store Connect API key** (the Key-ID + the Issuer-ID + the `.p8` — the machine seals them 0600 + registers in [[NURA-Credential-Registry]])
- [ ] **Step 3 — the App-Specific Password** (the signing auth — same seal)
- [ ] **Step 4 — the Codemagic wiring** (the repo connect, the `NURA-AppStoreConnect` integration paste, the "NURA-Testers" group create, the first push → the first build)
- [ ] **Step 5 — the TestFlight install** (the workflow auto-submits; the founder's test-devices invited)
- [ ] Post-first-upload: the real `APP_STORE_APPLE_ID` replaces the `0` placeholder

The order's the founder's build-guide, verbatim. The Apple key drop → the pipeline goes live unchanged — no code changes needed.

---

## 3. The security review — the screens (the read-only pass)

| Screen | Finding | Verdict |
|---|---|---|
| `main.dart` | The 5-tab shell, no login gate at startup — any tab opens without credential check | ❌ the gate not enforced (the copy exists, the code doesn't) |
| `account_screen.dart` | The license-gate DOCUMENTED in the UI (the NPI/paramedic, the founder's law, the local-first copy) | ✅ documented · ⚠️ UI-only, no verification behind it |
| `scribe_screen.dart` | `http://YOUR_GATEWAY:8095/scribe` — plaintext HTTP + placeholder host; no auth token on the request; the note held in-memory only (nothing cached) | ❌ HTTPS required (the ATS will block cleartext anyway — the security-default working FOR us) · ✅ zero persistence |
| `clinical_screen.dart` | `http://127.0.0.1:8095` loopback placeholder (the device-localhost = the phone, not the gateway); the output labeled `[DRAFT — PROVIDER APPROVAL REQUIRED]` | ❌ endpoint placeholder · ✅ the draft-label doctrine enforced |
| `ops_screen.dart` | Static tiles; names the internal lanes (Twilio/NMI/Documo/Google/n8n/Akaunting) in the UI copy | ⚠️ the internal names in the customer-facing UI — rename to the NURA names before the public beta (the product-lineup rule) |
| `e6b_screen.dart` | The planning-aid disclaimer ("not the primary navigation") | ✅ clean, no PHI |
| `pubspec.yaml` | ZERO storage/crypto/network deps — no DB, no cache, no persistence anywhere | ✅ the local-first trivially satisfied (nothing exists to leak) · ⚠️ the AES-256/biometric/audit-log controls are therefore not-yet-built |
| `Info.plist` | No `NSMicrophoneUsageDescription`, no `PrivacyInfo.xcprivacy`, no ATS keys | ❌ the mic string REQUIRED before the scribe goes live · ⚠️ the privacy-manifest before the App-Store submit |

### The security checklist (the HIPAA doctrine — the local-first)
- [x] **No PHI persisted** — state-only, the in-memory, zero cache, zero DB (the standing rule: never add a PHI cache without the AES-256 + the audit-log)
- [x] **No secrets in the repo** — the sealed-credentials doctrine holds
- [x] **The DRAFT doctrine** — every clinical output carries the provider-review label
- [x] **The disclaimers** — the E6B planning-aid, the review-required copy
- [ ] **The HTTPS-only gateway** — replace both `http://` endpoints with the real `https://` gateway URL (the deployment-config override)
- [ ] **The license-gate enforcement** — the NPI/paramedic verification must actually block the clinical tabs (today it's a card)
- [ ] **The API auth** — a token/attestation header on every `:8095` call
- [ ] **The mic permission string** — `NSMicrophoneUsageDescription` in the Info.plist
- [ ] **The privacy manifest** — the `PrivacyInfo.xcprivacy` before the store submit
- [ ] **The biometric/strong auth + the audit log** (login/logout/note create/view/delete) — the day any persistence ships
- [ ] **The BAA posture** — local-first = no dev-controlled cloud PHI path = no BAA needed (the standing position; revisit if the gateway starts storing)

---

## 4. The launch marketing plan — the TestFlight → the App Store → the promotion

The brand: **NURA HEALTH** — the orange/navy/white; the Orange Star 🍊 = the EMS line. The external names ONLY (the NURA CRM/ERP/Claw/Tron/MCP names; never Perfex/OpenEMR/Twilio/Documo — the CMO Iris enforces). The claims gate: **no FDA language, no "AI diagnoses"** — the copy says "the drafts, the provider approves."

### Phase 0 — the unlock (the founder's key-drop)
The enrollment + the API key + the password → the seal (0600) → the [[NURA-Credential-Registry]] entry → the Codemagic wire. No marketing before the build exists.

### Phase 1 — the TestFlight beta (the internal → the external)
- **The internal wave**: the founder's devices (the iPad/iPhone) — the dogfood pass on the 5 tabs
- **The external wave**: the `NURA-Testers` group — the paramedic network + the EMS crews (the Orange Star 🍊 audience) — up to 100 external testers
- **The beta ask**: the feedback on the scribe flow, the clinical drafts, the license-gate feel
- **The exit bar**: the crash-free sessions, the founder's sign-off on the gate + the branding → then the store

### Phase 2 — the App Store submit
- **The compliance pack** (the `ios-app-store-compliance` canon): the privacy policy in-app + on the store page (5.1.1, the PHI handling explicit), the documentation-aid positioning — NOT a diagnostic tool (5.1.2), the AI disclosure (2.4.5 — "the open-source Whisper ASR + the local LLM"), the App-Review-Notes explaining the on-device processing + the PHI security
- **The ASO**: the keywords "Clinical Documentation", "Ambient AI", "SOAP Notes"; the screenshots in the orange/navy/white; the store copy = NURA names only
- **The submit gate**: the claims-review pass (no autonomous-diagnosis language anywhere) before the App-Review submission

### Phase 3 — the promotion channels
- **The owned**: the nuratech.ai site (the product page) · the email list (the practice + the provider contacts) · the Instagram/Facebook lanes (the social lane) · the X daily check-in · the YouTube brand content (the Reel/media lane, the NURA names only)
- **The practitioner**: the EMS/paramedic communities (the Orange Star line), the provider word-of-mouth, the Google review-invite lane (the Ops tab does this natively once live)
- **The in-product flywheel**: the Ops tab's the front-office — every practice on NURA is a distribution channel
- **The KPIs**: the TestFlight installs → the crash-free % → the store rating → the downloads → the provider accounts created through the license-gate

### The one-paragraph summary
The NURA ONE app is release-shaped but not release-ready: the Codemagic pipeline (the mac_mini_m2, the Runner workspace/scheme, the `build-ipa` + the TestFlight publishing with the NURA-Testers group) is verified CORRECT for the TestFlight upload, and the only blocking gap is the founder's Apple key-drop — the Developer enrollment, the App Store Connect API key, and the app-specific password, sealed and wired into the Codemagic integration, after which the first push ships the beta with zero code changes. The security pass is a split verdict: the data layer is clean (nothing persists, no PHI cache, no secrets in the repo, the DRAFT-label doctrine in the code), but the license-gate is documented-only (the NPI/paramedic verification must actually block the clinical tabs), both API endpoints are plaintext-HTTP placeholders that iOS's ATS will reject until they become the HTTPS gateway, and the mic-permission string and privacy manifest are missing before the store submit. The marketing runway is three phases — the TestFlight beta to the founder's devices then the paramedic/EMS network (the Orange Star audience), the App Store submit with the full compliance pack (the privacy policy, the documentation-aid positioning, the AI disclosure, the ASO keywords), then the promotion across the owned channels (the site, the email, the social lanes, the YouTube brand content) with the claims-gate holding: no FDA language, the provider always approves.

---

*The audit by the QA + iOS-Release + Security + Growth pass — the read-only on the code, the no PHI touched, the single deliverable written.*
