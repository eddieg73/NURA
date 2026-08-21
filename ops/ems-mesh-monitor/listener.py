"""The Meshtastic listener-daemon-v2 — the USB radio-interface + the 3-table parsing (positions · telemetry · text!)."""
import os
import sys
import time
import sqlite3
import json
import datetime

SERIAL_DEVICE = os.environ.get("MESHTASTIC_DEVICE", "/dev/ttyUSB0")
DB_PATH = os.environ.get("MESHTASTIC_DB", "/data/meshtastic.db")

def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def _store(con, sql, args):
    con.execute(sql, args)

def handle_packet(packet):
    """The pub/sub callback — parse + insert into the 3 tables in real-time."""
    now = _now()
    decoded = packet.get("decoded", {}) or {}
    portnum = decoded.get("portnum", "")
    payload = decoded.get("payload", b"")
    text = None
    if isinstance(payload, bytes):
        try:
            text = payload.decode("utf-8", errors="replace")
        except Exception:
            text = payload.hex()

    # the position-parse!
    lat = lon = alt = None
    pos = decoded.get("position") or {}
    if pos:
        lat, lon, alt = pos.get("latitude"), pos.get("longitude"), pos.get("altitude")

    con = sqlite3.connect(DB_PATH)
    try:
        # 1. the packet-row!
        _store(con, "INSERT INTO packets (timestamp, sender_id, payload_type, snr, rssi, text_data, raw_json) VALUES (?,?,?,?,?,?,?)",
               (now, packet.get("from"), portnum, packet.get("rx_snr"), packet.get("rx_rssi"), text, json.dumps(packet, default=str)))

        # 2. the position-row (if the GPS-data's present!)
        if lat is not None and lon is not None:
            _store(con, "INSERT INTO positions (timestamp, sender_id, latitude, longitude, altitude) VALUES (?,?,?,?,?)",
                   (now, packet.get("from"), lat, lon, alt))

        # 3. the node-upsert (with the names + the hardware-model!)
        #    (the NODEINFO_APP shape: decoded.user — the reference-standard!)
        node_info = decoded.get("node_info") or {}
        user = decoded.get("user") or {}
        long_name = node_info.get("long_name") or user.get("longName")
        short_name = node_info.get("short_name") or user.get("shortName")
        hardware = node_info.get("hardware_model") or user.get("hwModel")
        _store(con, """
            INSERT INTO nodes (node_id, long_name, short_name, hardware_model, last_seen, last_rssi, last_snr, packets_seen)
            VALUES (?,?,?,?,?,?,?,1)
            ON CONFLICT(node_id) DO UPDATE SET
                long_name=COALESCE(excluded.long_name, long_name),
                short_name=COALESCE(excluded.short_name, short_name),
                hardware_model=COALESCE(excluded.hardware_model, hardware_model),
                last_seen=excluded.last_seen, last_rssi=excluded.last_rssi, last_snr=excluded.last_snr,
                packets_seen=packets_seen+1
        """, (packet.get("from"), long_name, short_name, hardware,
              now, packet.get("rx_rssi"), packet.get("rx_snr")))

        con.commit()
        print(f"[{now}] {portnum} from={packet.get('from')} rssi={packet.get('rx_rssi')} text={text[:30] if text else ''}", flush=True)
    except Exception as e:
        print(f"store-err: {e}", flush=True)
    finally:
        con.close()

def main():
    print(f"Meshtastic listener-v2 starting — device={SERIAL_DEVICE} db={DB_PATH}", flush=True)
    try:
        import meshtastic.serial_interface
        from pubsub import pub
    except ImportError as e:
        print(f"FATAL: {e} — pip install meshtastic", flush=True)
        sys.exit(1)
    interface = meshtastic.serial_interface.SerialInterface(SERIAL_DEVICE)
    pub.subscribe(handle_packet, "meshtastic.receive")
    print("Listening (Ctrl-C to stop)...", flush=True)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping.", flush=True)
    finally:
        interface.close()

if __name__ == "__main__":
    main()
