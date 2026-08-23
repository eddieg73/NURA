#!/usr/bin/env bash
# hl7_dir_pusher.sh — forward OpenEMR HL7 files from a drop directory to Mirth via MLLP.
# Polls HL7_OUT_DIR; for each *.hl7/*.msg file, MLLP-sends to MIRTH_HOST:PORT, then
# moves the file to HL7_SENT_DIR on success or HL7_FAIL_DIR on failure.
# Run as a systemd/cron job (every 15s) or inotify loop.
#
# Env:
#   HL7_OUT_DIR    e.g., /opt/openemr/hl7_out
#   HL7_SENT_DIR   e.g., /opt/openemr/hl7_sent   (default: $HL7_OUT_DIR/sent)
#   HL7_FAIL_DIR   e.g., /opt/openemr/hl7_failed (default: $HL7_OUT_DIR/failed)
#   MIRTH_HOST     default 127.0.0.1
#   MIRTH_PORT     default 6002 (ORM)
#   SEND_MLLP      path to send_mllp.py (default: /opt/data/skills/health/hermes-hl7-simulator/scripts/send_mllp.py)
set -euo pipefail

: "${HL7_OUT_DIR:?set HL7_OUT_DIR}"
SEND_MLLP="${SEND_MLLP:-/opt/data/skills/health/hermes-hl7-simulator/scripts/send_mllp.py}"
MIRTH_HOST="${MIRTH_HOST:-127.0.0.1}"
MIRTH_PORT="${MIRTH_PORT:-6002}"
HL7_SENT_DIR="${HL7_SENT_DIR:-$HL7_OUT_DIR/sent}"
HL7_FAIL_DIR="${HL7_FAIL_DIR:-$HL7_OUT_DIR/failed}"

mkdir -p "$HL7_SENT_DIR" "$HL7_FAIL_DIR"

found=0
for f in "$HL7_OUT_DIR"/*.hl7 "$HL7_OUT_DIR"/*.msg; do
  [ -e "$f" ] || continue
  found=1
  base=$(basename "$f")
  if MIRTH_HOST_IP="$MIRTH_HOST" python3 "$SEND_MLLP" "$MIRTH_PORT" "$f" >/tmp/hl7_push.$$.log 2>&1; then
    mv "$f" "$HL7_SENT_DIR/$base"
    echo "PUSHED $base -> ${MIRTH_HOST}:${MIRTH_PORT} (sent)"
  else
    mv "$f" "$HL7_FAIL_DIR/$base"
    echo "FAILED $base -> ${MIRTH_HOST}:${MIRTH_PORT} (moved to failed)"
  fi
  cat /tmp/hl7_push.$$.log
  rm -f /tmp/hl7_push.$$.log
done

[ "$found" = "0" ] && echo "no files in $HL7_OUT_DIR"
