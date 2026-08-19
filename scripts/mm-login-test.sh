#!/bin/bash
# Mattermost login test — email+password for every seat (the honest proof)
MM=mattermost-r2wm-mattermost-1
for CRED in "eg@nuratech.ai:EddieNura2026!" "atlas@nuratech.ai:AtlasNura2026!" "Nura@nuratech.ai:HermesNura2026!" "Oussama@nuratech.ai:OussamaNura2026!" "araj@nuratech.ai:AmritNura2026!" "Jade@nuratech.ai:JadeNura2026!"; do
  E="${CRED%%:*}"; P="${CRED#*:}"
  R=$(curl -s -m 8 -o /tmp/mm-login.json -w "%{http_code}" -X POST http://127.0.0.1:32777/api/v4/users/login -H "Content-Type: application/json" -d "{\"login_id\":\"$E\",\"password\":\"$P\"}" 2>/dev/null)
  TOK=$(python3 -c "import json; d=json.load(open('/tmp/mm-login.json')); print(d.get('token','')[:12] or d.get('message','')[:40])" 2>/dev/null)
  echo "$E -> HTTP $R (${TOK})"
done
