#!/usr/bin/env python3
"""OBD2 telemetry lane v1 — NURA (2026-08-02)
Reads vehicle PIDs via ELM327/STN dongle (serial/BT) OR the built-in python-obd
simulator (sim-first doctrine). Normalizes to JSON for the Hermes fleet lane.
READ-ONLY by design: no writes, no actuation, no UDS unlock.
"""
import sys, json, time, argparse

sys.path.insert(0, "/opt/data/profiles/nura/python-packages")

import obd

PIDS = [
    ("engine_rpm", obd.commands.RPM),
    ("speed_kph", obd.commands.SPEED),
    ("coolant_temp_c", obd.commands.COOLANT_TEMP),
    ("oil_temp_c", obd.commands.OIL_TEMP),
    ("fuel_level_pct", obd.commands.FUEL_LEVEL),
    ("battery_voltage_v", obd.commands.ELM_VOLTAGE),
    ("engine_load_pct", obd.commands.ENGINE_LOAD),
    ("intake_temp_c", obd.commands.INTAKE_TEMP),
]


def scan_dtcs(conn):
    resp = conn.query(obd.commands.GET_DTC)
    codes = [c[0] for c in (resp.value or [])]
    return codes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default=None, help="Serial port or 'sim' (default sim)")
    args = ap.parse_args()

    if args.port and args.port != "sim":
        conn = obd.OBD(args.port, fast=False, timeout=2)
    else:
        conn = obd.OBD("sim", fast=False)  # python-obd built-in simulator

    if conn.status() != obd.OBDStatus.CAR_CONNECTED:
        print(json.dumps({"status": "error", "detail": f"not connected: {conn.status()}"}))
        sys.exit(1)

    snapshot = {"status": "connected", "protocol": str(conn.protocol_name()), "ts": time.time()}
    for name, cmd in PIDS:
        try:
            r = conn.query(cmd)
            v = r.value
            snapshot[name] = float(v.magnitude) if v is not None else None
        except Exception:
            snapshot[name] = None

    snapshot["dtc_codes"] = scan_dtcs(conn)
    snapshot["dtc_count"] = len(snapshot["dtc_codes"])
    snapshot["mode"] = "SIMULATOR" if (not args.port or args.port == "sim") else "LIVE_DONGLE"

    print(json.dumps(snapshot, indent=2))
    conn.close()


if __name__ == "__main__":
    main()
