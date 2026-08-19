#!/usr/bin/env python3
"""The NURA credentialing-engine — the NPI-lookup → ID-check → webhook-finalize (the 3-step!).
The Nginx-protected, the rate-limited, the server-only-writes (never trust the client!)."""
import os, json, uuid, hmac, hashlib, urllib.request, urllib.error
from flask import Flask, request, jsonify

app = Flask(__name__)
DB = "postgresql://paperclip:paperclip@72.60.163.140:5432/paperclip"
VENDOR_SECRET = os.environ.get("VENDOR_WEBHOOK_SECRET", "nura-vendor-secret-2026")
NPPES = "https://npiregistry.cms.hhs.gov/api/?version=2.1&number="

try:
    import psycopg2
    def db():
        return psycopg2.connect(DB)
except ImportError:
    def db():
        raise RuntimeError("psycopg2-missing")
    psycopg2 = None

# 1. THE NPI-LOOKUP (the server-side NPPES-proxy!)
@app.route("/api/v1/onboarding/npi-lookup", methods=["POST"])
def npi_lookup():
    data = request.get_json() or {}
    npi = str(data.get("npi_number", "")).strip()
    if not npi.isdigit() or len(npi) != 10:
        return jsonify({"status": "error", "message": "NPI must be exactly 10 digits"}), 400
    try:
        with urllib.request.urlopen(NPPES + npi, timeout=15) as r:
            d = json.loads(r.read())
        results = d.get("results", [])
        if not results:
            return jsonify({"status": "error", "message": "NPI not found in the CMS registry"}), 404
        basic = results[0].get("basic", {})
        tax = next((t for t in results[0].get("taxonomies", []) if t.get("primary")), (results[0].get("taxonomies") or [{}])[0])
        addr = next((a for a in results[0].get("addresses", []) if a.get("address_purpose") == "LOCATION"), {})
        return jsonify({"status": "success", "data": {
            "npi": npi, "first_name": basic.get("first_name"), "last_name": basic.get("last_name"),
            "enumeration_type": results[0].get("enumeration_type"), "primary_taxonomy": tax.get("desc"),
            "practice_location": {"city": addr.get("city"), "state": addr.get("state")}}}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"NPPES unreachable: {str(e)[:60]}"}), 502

# 2. THE ID-CHECK-INITIATE (the pending-log!)
@app.route("/api/v1/onboarding/initiate-id-check", methods=["POST"])
def initiate_id_check():
    data = request.get_json() or {}
    user_id, npi = data.get("user_id"), str(data.get("npi_number", "")).strip()
    if not user_id or not npi:
        return jsonify({"status": "error", "message": "user_id + npi_number required"}), 400
    con = db(); cur = con.cursor()
    ref = str(uuid.uuid4())
    cur.execute("INSERT INTO npi_verifications (user_id, npi_number, verification_status, vendor_reference_id, ip_address) VALUES (%s,%s,'pending_id_check',%s,%s)",
                (user_id, npi, ref, request.remote_addr))
    con.commit(); con.close()
    return jsonify({"status": "success", "session_token": ref}), 200

# 3. THE WEBHOOK-FINALIZE (the server-only-write!)
@app.route("/api/v1/webhooks/vendor-verification-complete", methods=["POST"])
def webhook_finalize():
    sig = request.headers.get("X-Vendor-Signature", "")
    body = request.get_data()
    expected = hmac.new(VENDOR_SECRET.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return jsonify({"status": "error", "message": "Invalid signature"}), 403
    data = request.get_json() or {}
    user_id, npi, status = data.get("user_id"), str(data.get("npi_number", "")).strip(), data.get("status", "approved")
    con = db(); cur = con.cursor()
    cur.execute("UPDATE npi_verifications SET verification_status=%s, vendor_reference_id=%s WHERE user_id=%s AND npi_number=%s",
                (status, data.get("vendor_reference_id"), user_id, npi))
    if status == "approved":
        cur.execute("INSERT INTO clinician_profiles (user_id, npi_number, first_name, last_name, primary_taxonomy_code, practice_state) VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (npi_number) DO NOTHING",
                    (user_id, npi, data.get("first_name"), data.get("last_name"), data.get("taxonomy_code"), data.get("state")))
        cur.execute("UPDATE users SET role='clinician' WHERE id=%s", (user_id,))
        con.commit()
        return jsonify({"status": "verified", "message": "Clinician profile created, role updated"}), 200
    con.commit(); con.close()
    return jsonify({"status": "logged", "message": f"Verification {status} recorded"}), 200

@app.route("/api/v1/onboarding/status/<user_id>", methods=["GET"])
def status(user_id):
    con = db(); cur = con.cursor()
    cur.execute("SELECT verification_status FROM npi_verifications WHERE user_id=%s ORDER BY timestamp DESC LIMIT 1", (user_id,))
    row = cur.fetchone(); con.close()
    return jsonify({"status": row[0] if row else "none", "verified": (row and row[0] == "approved") or False})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5080)), debug=False)
