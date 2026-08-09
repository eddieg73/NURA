# NURA-iOS — the founder's 5-step build-guide (the CI-cloud lane!)

The machine's done: the bundle (com.nuratech.nuraMedical ✓), the scaffold (the full iOS-structure ✓), the Codemagic workflow (codemagic.yaml ✓) — the founder's 5 steps:

## Step 1 — The Apple-Developer enrollment ($99, once!)
- developer.apple.com → the account (Eddie_Garrido@me.com) → the enroll → the payment!
- ⏳ the enrollment-approval: usually 24-48h!

## Step 2 — The App-Store-Connect API-key (for the uploads!)
- appstoreconnect.apple.com → the Users & Access → the API-Keys → the Generate!
- Save: the Key-ID + the Issuer-ID + the .p8-file (the machine uses these!)

## Step 3 — The App-Specific-Password (the signing!)
- appleid.apple.com → the Sign-In & Security → the App-Specific-Passwords → the Generate!
- (the machine uses it for the App-Store-Connect-authentication!)

## Step 4 — The Codemagic wiring (the CI-cloud!)
- codemagic.io → the sign-in with the GitHub → the add-the nura_medical-repo → the connect!
- The team → the app-store-connect integration: paste the Key-ID + Issuer-ID + the .p8 + the app-specific-password!
- The workflow: the codemagic.yaml is already in the repo — the first build runs on the push!

## Step 5 — The TestFlight (the install!)
- The build → the TestFlight-submission (the workflow does it!) → the TestFlight-app → the iPad/iPhone-install!
- The founder's test-devices: the UDIDs → the TestFlight → the invite!

## The drops for the machine (when ready!)
- The App-Store-Connect Key-ID + Issuer-ID + the .p8-file → the machine seals them (0600!) + updates the codemagic.yaml!
- The app-specific-password → same-seal!
- The App-Store-Apple-ID (after the first upload — the workflow's 0-placeholder!)
