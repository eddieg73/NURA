"""The Meshtastic Monitor — the Flask API-v2 (the latest-positions · the messages/telemetry · the CSV-exports!)."""
import os
import sqlite3
import csv
import io
from flask import Flask, jsonify, request, Response

DB_PATH = os.environ.get("MESHTASTIC_DB", "/data/meshtastic.db")
app = Flask(__name__)

def q(sql, args=()):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = con.execute(sql, args).fetchall()
    con.close()
    return [dict(r) for r in rows]

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "db": os.path.exists(DB_PATH)})

@app.route("/api/stats")
def stats():
    p = q("SELECT COUNT(*) AS n FROM packets")[0]["n"]
    n = q("SELECT COUNT(*) AS n FROM nodes")[0]["n"]
    pos = q("SELECT COUNT(*) AS n FROM positions")[0]["n"]
    last = q("SELECT timestamp FROM packets ORDER BY id DESC LIMIT 1")
    return jsonify({"total_packets": p, "known_nodes": n, "positions": pos,
                    "last_packet": last[0]["timestamp"] if last else None})

@app.route("/api/positions")
def positions():
    """The latest known position per node (the map-lane!)."""
    rows = q("""
        SELECT p.* FROM positions p
        JOIN (SELECT sender_id, MAX(timestamp) AS m FROM positions GROUP BY sender_id) latest
          ON p.sender_id = latest.sender_id AND p.timestamp = latest.m
    """)
    return jsonify(rows)

@app.route("/api/messages")
def messages():
    limit = min(int(request.args.get("limit", 200)), 2000)
    rows = q("SELECT * FROM packets WHERE payload_type = 'TEXT_MESSAGE_APP' ORDER BY id DESC LIMIT ?", (limit,))
    return jsonify(rows)

@app.route("/api/telemetry")
def telemetry():
    limit = min(int(request.args.get("limit", 200)), 2000)
    rows = q("SELECT * FROM packets WHERE payload_type != 'TEXT_MESSAGE_APP' ORDER BY id DESC LIMIT ?", (limit,))
    return jsonify(rows)

@app.route("/api/nodes")
def nodes():
    return jsonify(q("SELECT * FROM nodes ORDER BY last_seen DESC"))

@app.route("/api/export.csv")
def export_csv():
    kind = request.args.get("type", "packets")
    table = {"packets": "packets", "nodes": "nodes", "positions": "positions"}.get(kind, "packets")
    order = {"packets": "id DESC", "nodes": "last_seen DESC", "positions": "timestamp DESC"}[table]
    rows = q(f"SELECT * FROM {table} ORDER BY {order}")
    if not rows:
        return Response("no-data", mimetype="text/csv")
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)
    return Response(out.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={table}.csv"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
