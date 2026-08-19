#!/bin/bash
# Mattermost broadcast via the watch token (run ON the Clinic)
TOK=$(grep -E "^MM_WATCH_TOKEN=" /opt/data/profiles/nura/.env | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")
URL="http://127.0.0.1:32777"
TEAM=$(curl -s -m 8 -H "Authorization: Bearer $TOK" "$URL/api/v4/teams/name/NURATECH" | python3 -c "import json,sys; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)
echo "team=$TEAM"
CH=$(curl -s -m 8 -H "Authorization: Bearer $TOK" "$URL/api/v4/teams/$TEAM/channels/name/town-square" | python3 -c "import json,sys; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)
echo "channel=$CH"
if [ -n "$CH" ]; then
  curl -s -m 10 -X POST -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
    -d '{"channel_id":"'$CH'","message":"📋 OPERATING DIRECTIVE 08-04 (founder): AI drafts, licensed humans diagnose/sign/decide. NURA Rad + Woo Chat + Sidecar specs canonical in the vault (Products/). All 13 role specs complete (Hiring/) - exams are gates, founder signs, Alexis runs onboarding. Doctrine: no autonomous diagnosis/Rx/orders/signatures, no PHI off the Lattice, no silent failures, wrong-patient/cross-tenant = 0. Read Products/ + Hiring/ + Operations/Employee-Instructions-08-04.md before you build. - Hermes (CTO)"}' \
    "$URL/api/v4/posts" | head -c 100
  echo
else
  echo "BROADCAST BLOCKED: team/channel lookup failed"
fi
