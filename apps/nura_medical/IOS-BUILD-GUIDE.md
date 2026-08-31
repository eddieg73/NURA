# NURA Medical — iOS and App Store Build Guide

## Prerequisites

- Active Apple Developer Program membership
- App Store Connect access for the release owner
- Registered bundle identifier, proposed: `ai.nuratech.nuramedical`
- App Store distribution certificate and provisioning profile
- Current supported Xcode and Flutter stable toolchains
- Production HTTPS API URL
- Public Privacy Policy, Terms, and Support URLs
- Final app icon and de-identified screenshots

## Configure the signed build

From `apps/nura_medical`:

```bash
flutter pub get
gem install xcodeproj --no-document
chmod +x scripts/prepare_ios_release.sh
BUNDLE_ID=ai.nuratech.nuramedical \
IOS_DEPLOYMENT_TARGET=15.0 \
scripts/prepare_ios_release.sh
```

The preparation script:

- sets the display name
- sets microphone and speech-recognition purpose strings
- records the standard-encryption export declaration
- disables document/file sharing
- sets the bundle identifier and minimum iOS version
- attaches `PrivacyInfo.xcprivacy` to the Runner target
- validates the property lists

## Validate before signing

```bash
dart format --output=none lib test
flutter analyze --no-fatal-infos --no-fatal-warnings
flutter test
flutter build ios \
  --release \
  --no-codesign \
  --dart-define=API_BASE_URL=https://api.example.invalid \
  --dart-define=APP_ENVIRONMENT=release-validation
```

## Build an IPA

```bash
flutter build ipa \
  --release \
  --build-name=1.0.0 \
  --build-number=1 \
  --dart-define=API_BASE_URL=https://api.nuratech.ai \
  --dart-define=APP_ENVIRONMENT=production \
  --dart-define=PRIVACY_POLICY_URL=https://nuratech.ai/privacy \
  --dart-define=TERMS_URL=https://nuratech.ai/terms \
  --dart-define=SUPPORT_URL=https://nuratech.ai/support \
  --export-options-plist=ios/ExportOptions.plist
```

Upload with Xcode Organizer, Transporter, or the configured Codemagic App Store Connect integration.

## Codemagic

Configure these groups and variables:

- `app_store_connect_credentials`
- `nura_medical_production`
- `API_BASE_URL`
- `PRIVACY_POLICY_URL`
- `TERMS_URL`
- `SUPPORT_URL`
- `BUNDLE_ID`

Add or import the App Store distribution certificate and provisioning profile. The workflow in `codemagic.yaml` compiles, signs, creates the IPA, and submits it to TestFlight.

## TestFlight acceptance test

- Sign in and restore a session
- Exercise microphone permission allowed and denied
- Submit a de-identified scribe draft
- Submit synthesis and differential drafts
- Confirm the provider-review banner is always visible
- Test backend unavailable and expired-session states
- Create and complete an operations task
- Export account data
- Delete the dedicated test account
- Confirm no PHI appears in logs, screenshots, crash reports, or review media

## Submission blockers

A successful IPA build is not the same as an approved production release. Do not submit until the `release/app_store/RELEASE_CHECKLIST.md` blockers are complete, including live backend, privacy URLs, Apple signing, clinical validation, BAA/vendor review, final assets, and accountable approvals.
