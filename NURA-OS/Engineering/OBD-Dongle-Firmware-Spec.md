# NURA OBD Dongle — ESP32-S3 + MCP2515 Firmware Spec (Phase 2, 2026-08-16)

## Mission
The edge CAN-reader: reads vehicle CAN frames → publishes to the NURA telemetry lane (MQTT over WiFi/BLE), with the ELM327-compatible framing for python-obd interop. Read-only by doctrine — this dongle NEVER transmits actuation frames (no CAN writes).

## Hardware
- ESP32-S3 (dual-core, BLE + WiFi 2.4GHz) + MCP2515 CAN controller + MCP2562 transceiver, OBD-II power 12V→3.3V
- Optional eSIM: SIMCom A7670E (LTE-Cat1) for the cellular backhaul

## Firmware architecture (ESP-IDF 5.x)
```
OBD-II CAN bus → MCP2562 → MCP2515 (SPI) → ESP32-S3
  ├─ can_rx task: SPI read → frame queue (RingBuffer, 256 frames)
  ├─ elm_task: ELM327 AT-command emulation over BT-SPP (AT Z/SP6/E0/L0/S0/H0...)
  ├─ mqtt_task: CAN frames → JSON → MQTT topic nura/vehicle/<vin>/can
  │    {ts, id, len, data, dir}
  ├─ ble_task: BLE GATT notify (the same JSON) for the phone-app lane
  └─ watchdog: the 30s task watchdog; fail → reboot + reconnect
```
- **Filters**: acceptance filters per the DBC-of-interest (engine RPM 0x..., speed, wheel speeds) — configurable via MQTT sub topic `nura/vehicle/<id>/filter`
- **The ELM bridge**: AT-command framing keeps python-obd working unchanged (SP6 = ISO 15765-4 CAN 11/500k, H0 headers off, L0 no linefeeds)
- **Security**: no CAN transmit code compiled in (read-only enforced at build); OTA updates signed; MQTT over TLS (the fleet broker)

## Phases
1. **P1 (done)**: the obd-bridge docker (ELM327 emulator + MQTT)
2. **P2 (this spec)**: the ESP32 firmware → BLE/WiFi MQTT
3. **P3**: the eSIM LTE backhaul
4. **P4**: fleet integration (watchdogs + dashboard + the mesh-router `{DEV:...}` lane)

## The build notes
- Toolchain: ESP-IDF 5.x, the `esp32s3` target, MCP2515 driver via SPI (10MHz, mode 0, INT on GPIO)
- The MCP2515 config: CAN 500kbps, SJW=1, the filters per DBC
- Verify: loopback test on the bench CAN (2× dongles), the ELM AT-echo tests, the MQTT capture, then the bench-recorded OBD replay — NEVER first-test on a moving vehicle

## Files
- `/opt/data/nura-obd-firmware/main/main.c` — the skeleton (can_rx + elm + mqtt tasks)
- `/opt/data/nura-obd-firmware/README.md` — build + flash + test
