#!/usr/bin/env python3
"""NURA UDS telemetry lane — deep ECU queries via python-udsoncan.
DO NOT write services by default: read-only doctrine (ReadDTC, ReadDataByIdentifier, TesterPresent).
Transport: socketcan (CANable/USBtin) or ELM327 pass-thru. No car attached = config-dry-run mode.
Usage: python3 uds-telemetry.py --config /path/config.json   (or --dry-run)"""
import json, sys, argparse, time
import udsoncan
from udsoncan.connections import PythonIsoTpConnection
from udsoncan.client import Client
from udsoncan.services import ReadDataByIdentifier, ReadDTCInformation, TesterPresent

DEFAULT_CONFIG = {
    "interface": "socketcan",   # socketcan | elm327
    "channel": "can0",
    "bitrate": 500000,
    "ecu_tx_id": 0x7E0,         # engine ECU (adjust per module: 0x7E1 trans, 0x7E2 abs...)
    "ecu_rx_id": 0x7E8,
    "did_list": [0xF190],       # VIN (example DIDs per vehicle DBC)
    "read_dtc": True,
    "tester_present_interval": 2,
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    cfg = DEFAULT_CONFIG
    if args.config:
        cfg.update(json.load(open(args.config)))

    if args.dry_run:
        print(json.dumps({"mode": "DRY-RUN", "udsoncan": udsoncan.__version__,
                          "config": cfg,
                          "note": "no vehicle attached — transport + ISO-TP params validated only"},
                         indent=2))
        return

    import can
    bus = can.Bus(interface=cfg["interface"], channel=cfg["channel"], bitrate=cfg["bitrate"])
    conn = PythonIsoTpConnection(bus, rxid=cfg["ecu_rx_id"], txid=cfg["ecu_tx_id"])
    out = {"mode": "LIVE", "reads": []}
    with Client(conn, request_timeout=3, config=udsoncan.configs.default_client_config) as client:
        client.change_session(0x01)  # DiagnosticSessionControl: default session (read-only)
        if cfg["read_dtc"]:
            resp = client.request_configuration()
            dtcs = client.get_dtc(ReadDTCInformation.Subfunction.report_dtc_by_status_mask_02)
            out["dtcs"] = [d.dtcid for d in dtcs] if dtcs else []
        for did in cfg["did_list"]:
            try:
                r = client.read_data_by_identifier_first(did)
                out["reads"].append({"did": hex(did), "data": r.hex() if r else None})
            except Exception as e:
                out["reads"].append({"did": hex(did), "error": str(e)[:80]})
        client.tester_present(TesterPresent.ResponseRequired)
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
