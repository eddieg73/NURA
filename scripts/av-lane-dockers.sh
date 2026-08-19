#!/bin/bash
# OBD BRIDGE + OPENPILOT SIM — the AV-lane dockers (2026-08-05)
set -e
echo "=== 1. the OBD BLE/WiFi bridge ==="
mkdir -p /docker/obd-bridge
cat > /docker/obd-bridge/Dockerfile <<'EOF'
FROM python:3.12-slim
RUN pip install --no-cache-dir obd bleak paho-mqtt
COPY bridge.py /bridge.py
ENTRYPOINT ["python3", "/bridge.py"]
EOF
cat > /docker/obd-bridge/bridge.py <<'EOF'
import os, json, time, sys, threading
import obd
try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None

MODE = os.environ.get("OBD_MODE", "SIMULATOR")          # SIMULATOR | BLE | WIFI
OBD_DEV = os.environ.get("OBD_DEVICE", "")              # BLE MAC or WiFi IP
OBD_WIFI_PORT = int(os.environ.get("OBD_WIFI_PORT", "35000"))
MQTT_HOST = os.environ.get("MQTT_HOST", "")
MQTT_TOPIC = os.environ.get("MQTT_TOPIC", "nura/vehicle/obd")
POLL_HZ = float(os.environ.get("POLL_HZ", "10"))
PIDS = ["RPM", "SPEED", "COOLANT_TEMP", "INTAKE_TEMP", "FUEL_LEVEL", "BATTERY_VOLTAGE"]

def main():
    print(f"OBD bridge starting: mode={MODE} device={OBD_DEV or 'none'} poll={POLL_HZ}Hz", flush=True)
    conn = None
    if MODE == "BLE":
        conn = obd.OBD(f"ble:{OBD_DEV}")   # the BLE-dongle path (ELM327-class)
    elif MODE == "WIFI":
        conn = obd.OBD(f"tcp://{OBD_DEV}:{OBD_WIFI_PORT}")
    else:
        conn = obd.OBD("sim", fast=False)  # the fallback: local serial; the real sim = the host PTY
    if conn is None or not conn.is_connected():
        print("WARN: no dongle — entering SIMULATOR mode (host PTY emulator expected on /dev/pts)", flush=True)
    client = None
    if MQTT_HOST and mqtt:
        client = mqtt.Client("obd-bridge")
        client.connect(MQTT_HOST)
        client.loop_start()
    while True:
        snap = {"mode": MODE, "ts": time.time()}
        try:
            for pid in PIDS:
                cmd = getattr(obd.commands, pid, None)
                if cmd:
                    r = conn.query(cmd) if conn else None
                    snap[pid.lower()] = float(r.value.magnitude) if r and r.value is not None else None
        except Exception as e:
            snap["error"] = str(e)
        payload = json.dumps(snap)
        if client:
            client.publish(MQTT_TOPIC, payload)
        print(payload, flush=True)
        time.sleep(1.0 / POLL_HZ)

if __name__ == "__main__":
    main()
EOF
cat > /docker/obd-bridge/docker-compose.yml <<'EOF'
services:
  obd-bridge:
    build: .
    container_name: obd-bridge
    environment:
      OBD_MODE: SIMULATOR
      POLL_HZ: "10"
    devices:
      - /dev/pts:/dev/pts
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: 10m
EOF
cd /docker/obd-bridge
docker compose build 2>&1 | tail -2
docker compose up -d 2>&1 | tail -1
sleep 4
echo "=== 2. the openpilot sim compose (the CARLA-based sim) ==="
mkdir -p /docker/openpilot-sim
cat > /docker/openpilot-sim/docker-compose.yml <<'EOF'
services:
  openpilot-sim:
    image: commaai/openpilot-sim:latest
    container_name: openpilot-sim
    stdin_open: true
    tty: true
    environment:
      SIMULATOR: "carla"
    restart: unless-stopped
EOF
cd /docker/openpilot-sim
docker compose pull 2>&1 | tail -1 &
PULL_PID=$!
echo "openpilot-sim pull started (pid $PULL_PID) — the big image, running in the background"
echo "=== 3. verify the OBD bridge ==="
docker ps --format '{{.Names}} {{.Status}}' | grep obd-bridge | head -1
docker logs obd-bridge 2>&1 | tail -2
