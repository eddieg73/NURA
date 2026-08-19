#!/usr/bin/env python3
"""REST test sink for Milestone-1 ADT pipeline — logs POSTs, returns 200.
Listens 0.0.0.0:9999; body appended to /tmp/rest-sink.log"""
import http.server, datetime, os

LOG = "/tmp/rest-sink.log"

class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n).decode("utf-8", "replace") if n else ""
        with open(LOG, "a") as f:
            f.write(f"[{datetime.datetime.now().isoformat()}] {self.path} <- {body}\n")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}')
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"sink-alive")
    def log_message(self, *a):
        pass

http.server.HTTPServer(("0.0.0.0", 9999), H).serve_forever()
