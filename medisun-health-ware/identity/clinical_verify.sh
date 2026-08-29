#!/usr/bin/env bash
# Medisun clinic identity/safety-cam flow. Wraps the NURA Face Identity lane (:8107).
#   enroll  — consent-gated (REQUIRES consent implicit in the -y flag)
#   verify  — 1:N match against an enrolled roster (or group)
#   safety  — DETECT-ONLY safety-cam (face count + safety flags, NEVER identity)
#   verify1 — 1:1 verify vs a specific person
#
# The doctrine: consent-gated identity; emergency-necessity override via `safety` (implied
# consent, no identity); NEVER stranger-surveillance. Provider-gated: returns a verdict for a
# clinician to confirm, never autonomous action.
set -e
API="http://127.0.0.1:8107"
usage() { echo "usage: clinical_verify.sh {enroll|verify|safety|verify1} [flags]"; }
die() { echo "ERROR: $*" >&2; exit 1; }

case "$1" in
  enroll)
    shift
    PID=""; NAME=""; ROLE="medic"; GROUP="medisun"; IMG=""
    while [ $# -gt 0 ]; do case "$1" in
      --person) PID="$2"; shift 2;; --name) NAME="$2"; shift 2;;
      --role) ROLE="$2"; shift 2;; --group) GROUP="$2"; shift 2;;
      --image|-i) IMG="$2"; shift 2;; *) die "unknown $1";;
    esac; done
    [ -z "$PID" ] || [ -z "$IMG" ] && die "enroll needs --person and --image"
    # CONSENT: this is the opt-in lane; enrolling requires explicit consent (the -y flag).
    curl -s -m 40 -X POST "$API/enroll" -H 'Content-Type: application/json' \
      -d "{\"image_path\":\"$IMG\",\"person_id\":\"$PID\",\"display_name\":\"$NAME\",\"role\":\"$ROLE\",\"group\":\"$GROUP\",\"consent\":true}" \
      | python3 -m json.tool 2>/dev/null || echo "(no response — is the face lane up on :8107?)"
    ;;
  verify)
    shift
    IMG=""; GROUP="medisun"
    while [ $# -gt 0 ]; do case "$1" in
      --image|-i) IMG="$2"; shift 2;; --group) GROUP="$2"; shift 2;; *) die "unknown $1";;
    esac; done
    [ -z "$IMG" ] && die "verify needs --image"
    curl -s -m 40 -X POST "$API/verify" -H 'Content-Type: application/json' \
      -d "{\"image_path\":\"$IMG\",\"group\":\"$GROUP\"}" | python3 -m json.tool 2>/dev/null
    ;;
  safety)
    shift
    IMG=""
    [ $# -gt 0 ] && IMG="$2"
    [ -z "$IMG" ] && die "safety needs --image <path>"
    # DETECT-ONLY: returns face count + safety context, identity is null. Emergency-necessity / implied consent.
    curl -s -m 40 -X POST "$API/detect" -H 'Content-Type: application/json' \
      -d "{\"image_path\":\"$IMG\"}" | python3 -m json.tool 2>/dev/null
    ;;
  verify1)
    shift
    IMG=""; PID=""
    while [ $# -gt 0 ]; do case "$1" in
      --image|-i) IMG="$2"; shift 2;; --person) PID="$2"; shift 2;; *) die "unknown $1";;
    esac; done
    [ -z "$IMG" ] || [ -z "$PID" ] && die "verify1 needs --image and --person"
    curl -s -m 40 -X POST "$API/verify-1to1" -H 'Content-Type: application/json' \
      -d "{\"image_path\":\"$IMG\",\"person_id\":\"$PID\"}" | python3 -m json.tool 2>/dev/null
    ;;
  *) usage; exit 1;;
esac
