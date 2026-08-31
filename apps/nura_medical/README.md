# NURA Medical

Clinician-facing Flutter application for secure source-text capture, ambient dictation, clinical decision-support drafts, operations tasks, account/privacy controls, and an offline advisory E6B utility.

## Safety boundary

- Clinical output is a draft.
- Accountable clinician review is required.
- NURA does not establish a final diagnosis, authorize treatment, or replace professional judgment.
- NURA is not an emergency communication service.
- The application will not use HTTP or a loopback API host in release mode.

## Application lanes

1. **Scribe** — clinician-initiated dictation or typed source text and a controlled documentation draft
2. **Clinical** — structured synthesis or differential-support draft
3. **Ops** — persistent organization-scoped task queue
4. **E6B** — offline advisory aviation calculations
5. **Account** — identity, legal disclosure, data export, logout, and permanent deletion

## Backend

The paired API is located at:

```text
services/nura_medical_api/
```

Start it locally as described in that directory’s README.

## Local Flutter run

```bash
cd apps/nura_medical
flutter pub get
flutter run \
  --dart-define=API_BASE_URL=https://your-development-api.example \
  --dart-define=APP_ENVIRONMENT=development
```

Use an HTTPS development endpoint. The iOS release configuration intentionally includes no App Transport Security exception for arbitrary HTTP.

## Tests

```bash
dart format --output=none lib test
flutter analyze --no-fatal-infos --no-fatal-warnings
flutter test
```

The repository workflow `.github/workflows/nura-medical-ci.yml` also validates the API, Flutter client, and an unsigned iOS release compilation.

## iOS release preparation

```bash
cd apps/nura_medical
gem install xcodeproj --no-document
chmod +x scripts/prepare_ios_release.sh
BUNDLE_ID=ai.nuratech.nuramedical \
IOS_DEPLOYMENT_TARGET=15.0 \
scripts/prepare_ios_release.sh
```

Then build:

```bash
flutter build ipa \
  --release \
  --dart-define=API_BASE_URL=https://api.nuratech.ai \
  --dart-define=APP_ENVIRONMENT=production \
  --export-options-plist=ios/ExportOptions.plist
```

The Codemagic workflow can sign and submit the IPA to TestFlight after App Store Connect credentials, a distribution certificate, a provisioning profile, and production environment variables are connected.

## App Store package

See:

```text
release/app_store/APP_STORE_SUBMISSION.md
release/app_store/APP_REVIEW_NOTES.md
release/app_store/PRIVACY_LABEL_WORKSHEET.md
release/app_store/RELEASE_CHECKLIST.md
release/CLINICAL_SAFETY_CASE.md
```

Actual App Store submission remains blocked until Apple credentials, production backend deployment, public legal URLs, final app assets, clinical validation, vendor/BAA review, and accountable release approvals are complete.
