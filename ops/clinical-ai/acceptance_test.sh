#!/usr/bin/env bash
# acceptance_test.sh — exercise EVERY endpoint in the NURA Clinical Inference spec
# with real payloads. Records status + evidence. No endpoint is claimed working
# unless it returns a real model answer here.
set -u
B=http://127.0.0.1:8170
PASS=0; FAIL=0
note() { printf '%-34s %s\n' "$1" "$2"; }

hit() { # name method path json [jq-ish grep]
  local name="$1" path="$2" body="$3" want="${4:-}"
  local out code
  out=$(tmp=$(mktemp); curl -s -o "$tmp" -w '%{http_code}' --max-time 240 \
        -H 'Content-Type: application/json' -d "$body" "$B$path" 2>/dev/null; cat "$tmp"; rm -f "$tmp")
  code=$(printf '%s' "$out" | head -1)
  local payload; payload=$(printf '%s' "$out" | tail -n +2)
  if [ "$code" = "200" ] && { [ -z "$want" ] || printf '%s' "$payload" | grep -q "$want"; }; then
    PASS=$((PASS+1)); note "$name" "OK  $code"
    printf '%s' "$payload" | head -c 420 | sed 's/^/      /'; echo
  else
    FAIL=$((FAIL+1)); note "$name" "FAIL code=$code"
    printf '%s' "$payload" | head -c 300 | sed 's/^/      /'; echo
  fi
}

echo "════════════ GENERATIVE (generators) ════════════"
hit "/v1/generate/clinical"  "/v1/generate/clinical" \
  '{"prompt":"List the 3 required elements of a Medicare annual wellness visit in one line each.","lane":"clinical"}' '"output"'
hit "/v1/generate/general"   "/v1/generate/general" \
  '{"prompt":"Reply with exactly: GATEWAY OK","lane":"general"}' '"output"'
hit "/v1/code"               "/v1/code" \
  '{"prompt":"Write a python one-liner that normalises an ICD-10 code by uppercasing and stripping dots."}' '"output"'

echo ""
echo "════════════════ ENCODERS -> NLP ════════════════"
hit "/v1/nlp/entities"  "/v1/nlp/entities" \
  '{"text":"62yo male with type 2 diabetes mellitus E11.65 and chronic heart failure I50.32, denies chest pain. A1C: 8.4%. On metformin and carvedilol."}' '"entities"'
hit "/v1/nlp/negation"  "/v1/nlp/negation" \
  '{"text":"Patient denies chest pain but reports dyspnea. No evidence of pneumonia.","terms":["chest pain","dyspnea","pneumonia"]}' '"negation"'
hit "/v1/nlp/phenotype" "/v1/nlp/phenotype" \
  '{"text":"Bipolar disorder with diabetes and CKD stage 3, A1C 7.9, creatinine 1.8"}' '"phenotypes"'
hit "/v1/nlp/relations" "/v1/nlp/relations" \
  '{"text":"metformin prescribed for diabetes E11.65. A1C 8.4%. carvedilol for heart failure I50.32."}' '"relations"'
hit "/v1/nlp/classify"  "/v1/nlp/classify" \
  '{"text":"Patient presents with acute substernal chest pressure radiating to the left arm, diaphoretic.","labels":["routine","urgent","emergency"]}' '"label"'

echo ""
echo "════════════════ EMBEDDINGS (3 domains) ════════════════"
hit "/v1/embed/general"    "/v1/embed/general" \
  '{"texts":["Medicare Advantage risk adjustment","NURA OS dashboard"]}' '"dim"'
hit "/v1/embed/clinical"   "/v1/embed/clinical" \
  '{"texts":["Patient with bipolar disorder on lithium, stable"]}' '"dim"'
hit "/v1/embed/biomedical" "/v1/embed/biomedical" \
  '{"texts":["GLP-1 receptor agonists and cardiovascular outcomes"]}' '"dim"'

echo ""
echo "════════════════ RETRIEVAL (2 corpora) ════════════════"
hit "/v1/rag/patient"           "/v1/rag/patient" \
  '{"query":"bipolar disorder lithium","top":3}' '"domain"'
hit "/v1/rag/medical-knowledge" "/v1/rag/medical-knowledge" \
  '{"query":"CKD staging eGFR thresholds","top":3}' '"domain"'

echo ""
echo "════════════════ SAFETY / GOVERNANCE ════════════════"
hit "/v1/vision" "/v1/vision" '{"prompt":"Describe any text visible.","images":[]}' '"draft"'

echo ""
echo "════════════════ 404 ON UNKNOWN PATH ════════════════"
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 -X POST \
      -H 'Content-Type: application/json' -d '{}' "$B/v1/nope" 2>/dev/null)
[ "$code" = "404" ] && { PASS=$((PASS+1)); note "unknown path -> 404" "OK"; } || { FAIL=$((FAIL+1)); note "unknown path -> 404" "FAIL got $code"; }

echo ""
echo "════════════════ RESULT ════════════════"
echo "  PASS=$PASS  FAIL=$FAIL"
echo "  provenance entries recorded:"
curl -s --max-time 10 "$B/health" | /opt/hermes/.venv/bin/python3 -c "import sys,json;d=json.load(sys.stdin);print('   requests:',d['requests'],'| generators:',d['generators_available'],'| qdrant:',d['qdrant'])" 2>/dev/null
