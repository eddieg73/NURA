# NURA SSO/SCIM — the Notion enterprise-identity setup (2026-08-09!)

## The banked IDs
- Notion-workspace-id: c6ea9b14-e498-8150-9f8e-00037da8fc5b
- Notion-team: fuschia-vision-e4a
- IdP-recommended: Google-Workspace (eg@nuratech.ai — the domain-owner ✓!)

## Step 1 — The Notion-side (the founder's admin-actions!)
1. Notion-admin → Settings → Identity & Provisioning (the Business/Enterprise-plan required!)
2. SAML-SSO → Enable:
   - The IdP-metadata → paste (or the manual: the IdP's-SSO-URL + the Entity-ID + the x509-cert!)
   - The team-sign-in: the members use the corporate-credentials (eg@nuratech.ai!)
3. SCIM → Enable → Generate-the-token:
   - The SCIM-endpoint: https://api.notion.com/v1/scim/v2
   - The bearer-token: the generated-value → the IdP-side!

## Step 2 — The Google-Workspace-side (the IdP!)
1. Google-Admin-Console → Apps → Web-and-mobile-apps → Add → SAML-app!
2. The Google-IdP-metadata: (the IdP-SSO-URL + the Entity-ID + the cert!)
3. The Notion-SP-values (the SERVICE-PROVIDER-side!):
   - ACS-URL: https://www.notion.so/saml/consume
   - Entity-ID: https://www.notion.so
   - SLO-URL: https://www.notion.so/saml/slo
4. The attribute-mapping: the email → the Notion-username!
5. The user-access: the org-unit (the NURA-team!) → the app-on!

## Step 3 — The SCIM-provisioning (the Google-side!)
1. Google-Admin → Apps → SAML-app → User-Provisioning → SCIM:
   - The SCIM-endpoint: https://api.notion.com/v1/scim/v2
   - The token: the Notion-generated!
2. The sync: the Google-users/groups → the Notion-members auto-provisioned!
3. The verification: the deprovisioning-test (a removed-user leaves the Notion!)

## The verification
- The SSO: the incognito-login → the Google-account → the Notion-workspace!
- The SCIM: the new-user in the Google-OU → the auto-join within ~10-min!
- The audit: the Notion-settings → the activity-log!
