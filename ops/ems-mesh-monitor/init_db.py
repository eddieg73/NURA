"""The Meshtastic Monitor — the schema-v2: Nodes · Packets/Telemetry · Positions (the strengthened-spec!)."""
import os
import sqlite3
import argparse
import datetime

DB_PATH = os.environ.get("MESHTASTIC_DB", "/data/meshtastic.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS nodes (
    node_id TEXT PRIMARY KEY,
    long_name TEXT,
    short_name TEXT,
    hardware_model TEXT,
    last_seen TEXT,
    last_rssi REAL,
    last_snr REAL,
    packets_seen INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS packets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    sender_id TEXT,
    payload_type TEXT,
    snr REAL,
    rssi REAL,
    text_data TEXT,
    raw_json TEXT
);
CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    sender_id TEXT,
    latitude REAL,
    longitude REAL,
    altitude REAL
);
CREATE INDEX IF NOT EXISTS idx_packets_ts ON packets(timestamp);
CREATE INDEX IF NOT EXISTS idx_positions_ts ON positions(timestamp);
CREATE INDEX IF NOT EXISTS idx_packets_sender ON packets(sender_id);
"""

def init():
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA)
    con.execute("PRAGMA journal_mode=WAL")
    con.commit()
    con.close()
    print(f"DB initialized (v2-schema): {DB_PATH}")

def prune(days):
    cutoff = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)).isoformat()
    con = sqlite3.connect(DB_PATH)
    for table in ("packets", "positions"):
        cur = con.execute(f"DELETE FROM {table} WHERE timestamp < ?", (cutoff,))
        print(f"pruned {table}: {cur.rowcount}")
    con.execute("VACUUM")
    con.commit()
    con.close()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--prune-days", type=int, default=0)
    a = ap.parse_args()
    init()
    if a.prune_days:
        prune(a.prune_days)
