#!/usr/bin/env bash
# OpenEMR publishes SMART-on-FHIR discovery => it can act as the authorization server itself.
# That is the piece the plugin package explicitly says it does NOT ship. Read the real endpoints.
CFG=/opt/data/profiles/nura/home/.ssh/config
echo "════════════════════════════════════════════════════════════"
echo "  OpenEMR .well-known/smart-configuration"
echo "════════════════════════════════════════════════════════════"
timeout 90 ssh -F "$CFG" -o ConnectTimeout=12 clinic \
  'curl -s -m 15 http://127.0.0.1:32777/apis/default/fhir/.well-known/smart-configuration' 2>/dev/null \
  | /opt/hermes/.venv/bin/python3 -c "
import json,sys
try:
    d=json.load(sys.stdin)
except Exception as e:
    print('  parse failed:',e); raise SystemExit
for k in ('issuer','authorization_endpoint','token_endpoint','introspection_endpoint',
          'revocation_endpoint','jwks_uri','registration_endpoint','management_endpoint',
          'capabilities','scopes_supported','response_types_supported',
          'code_challenge_methods_supported','grant_types_supported','token_endpoint_auth_methods_supported'):
    v=d.get(k)
    if v is None: continue
    if isinstance(v,list):
        print(f'  {k}:')
        for item in v: print(f'      {item}')
    else:
        print(f'  {k}: {v}')
"
echo ""
echo "════════════════════════════════════════════════════════════"
echo "  OpenEMR FHIR — does it advertise SMART security in its CapabilityStatement?"
echo "════════════════════════════════════════════════════════════"
timeout 90 ssh -F "$CFG" -o ConnectTimeout=12 clinic \
  'curl -s -m 15 http://127.0.0.1:32777/apis/default/fhir/metadata' 2>/dev/null \
  | /opt/hermes/.venv/bin/python3 -c "
import json,sys
d=json.load(sys.stdin)
print('  fhirVersion :', d.get('fhirVersion'))
print('  status      :', d.get('status'))
print('  software    :', d.get('software'))
r=d.get('rest',[{}])[0]
sec=r.get('security')
print('  security    :', json.dumps(sec)[:600] if sec else 'NOT ADVERTISED')
print()
types=[x.get('type') for x in r.get('resource',[])]
print('  resource types advertised:', len(types))
want=['Patient','Condition','AllergyIntolerance','MedicationRequest','MedicationDispense',
      'Observation','Encounter','DiagnosticReport','Procedure','DocumentReference']
for w in want:
    print(f'    {w:<22} {\"PRESENT\" if w in types else \"** MISSING **\"}')
"
echo ""
echo "  --- what is listening on :8088 (dead vhost target) ---"
timeout 60 ssh -F "$CFG" -o ConnectTimeout=12 clinic \
  'docker ps --format "{{.Names}}|{{.Ports}}" | grep 8088' 2>&1 | head -5