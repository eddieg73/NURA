#!/usr/bin/env python3
"""Minimal MLLP sink: listen, ACK each message, log to /tmp/mllp-sink.log."""
import socket, sys, time
HOST, PORT = "0.0.0.0", 6665
srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind((HOST, PORT))
srv.listen(5)
log = open("/tmp/mllp-sink.log", "a")
log.write(f"[sink] listening on {HOST}:{PORT}\n"); log.flush()
print(f"listening {HOST}:{PORT}", flush=True)
while True:
    conn, addr = srv.accept()
    buf = b""
    try:
        while True:
            chunk = conn.recv(65536)
            if not chunk:
                break
            buf += chunk
            if b"\x1c\x0d" in buf:
                break
    except Exception as e:
        log.write(f"[sink] recv err {e}\n")
    msg = buf.split(b"\x0b")[-1].split(b"\x1c")[0]
    log.write(f"[sink] {time.strftime('%H:%M:%S')} from {addr} len={len(msg)} :: {msg[:120].decode(errors='replace')}\n")
    log.flush()
    print(f"RECEIVED {len(msg)} bytes from {addr}: {msg[:80].decode(errors='replace')}", flush=True)
    try:
        conn.sendall(b"\x0b" + b"MSH|^~\\&|SINK|NURA|MIRTH|20260815120000||ACK||P|2.3" + b"\x0d" + b"\x1c\x0d")
    except Exception as e:
        log.write(f"[sink] ack err {e}\n")
    conn.close()
