#!/usr/bin/env python3
"""
PIXEL BRIDGE — reach an Android device over a userspace-mode tailnet, for tools with no SOCKS support.

THE PROBLEM
  tailscaled here runs with --tun=userspace-networking, so there is NO kernel route to 100.x
  addresses. All tailnet traffic must traverse the SOCKS5 proxy on 127.0.0.1:1055. `tailscale ping`
  works because it goes through the daemon -- but `adb` speaks raw TCP and has NO native SOCKS
  support. So `adb connect 100.123.84.111:PORT` can never work directly from this host.

THE SOLUTION
  A local transparent port forwarder. Any local TCP connection to 127.0.0.1:<port> is tunnelled to
  <PHONE>:<same port> through the SOCKS5 proxy. adb then talks to localhost normally.

  Why the SAME port: Android 11+ wireless debugging picks a DYNAMIC, high port that the phone
  displays on screen, and the pairing port differs from the connect port. A same-port mapping means
  whatever the phone shows, you forward that number - no code change, no guessing.

USAGE
  python3 pixel_bridge.py                       # forward the default + discovered range
  python3 pixel_bridge.py --ports 43211         # forward a specific port the phone displayed
  python3 pixel_bridge.py --phone 100.123.84.111 --ports 43211,5555

  Then:  adb connect 127.0.0.1:43211

VERIFY IT WORKS (do this before blaming the phone):
  python3 pixel_bridge.py --selftest
"""
import argparse
import socket
import struct
import sys
import threading
import time

SOCKS = ("127.0.0.1", 1055)
DEFAULT_PHONE = "100.123.84.111"          # pixel-10-pro-xl-1 (online, direct path, 54ms)
# adb / wireless-debugging ports worth having open by default
DEFAULT_PORTS = [5555, 5037]

ap = argparse.ArgumentParser()
ap.add_argument("--phone", default=DEFAULT_PHONE)
ap.add_argument("--ports", default="", help="comma-separated local=remote ports, e.g. 43211,5555")
ap.add_argument("--socks", default="127.0.0.1:1055")
ap.add_argument("--selftest", action="store_true", help="verify the SOCKS path, then exit")
ap.add_argument("--probe", default="", help="try a port through SOCKS and report, then exit")
args = ap.parse_args()

SOCKS = tuple([args.socks.split(":")[0], int(args.socks.split(":")[1])])


def socks5_connect(host, port, timeout=12):
    """Open a tunnel to host:port through the userspace SOCKS5 proxy."""
    s = socket.socket()
    s.settimeout(timeout)
    try:
        s.connect(SOCKS)
        s.sendall(b"\x05\x01\x00")
        r = s.recv(2)
        if len(r) < 2 or r[1] != 0:
            return None, f"auth refused {r!r}"
        s.sendall(b"\x05\x01\x00\x01" + socket.inet_aton(host) + struct.pack(">H", port))
        rep = s.recv(4)
        if len(rep) < 4:
            return None, f"short reply {rep!r}"
        if rep[1] != 0:
            names = {1: "general failure (nothing listening, or unreachable)",
                     2: "not allowed by policy", 3: "network unreachable",
                     4: "host unreachable", 5: "connection refused",
                     6: "TTL expired", 7: "command not supported", 8: "addr type not supported"}
            return None, names.get(rep[1], f"code {rep[1]}")
        return s, "OK"
    except Exception as e:
        return None, f"exception {e}"


# ---- selftest / probe -----------------------------------------------------
if args.selftest:
    print("=" * 78)
    print("PIXEL BRIDGE SELFTEST")
    print("=" * 78)
    print(f"  proxy   : {SOCKS[0]}:{SOCKS[1]}")
    print(f"  target  : {args.phone}")
    ok = False
    for host, port, label in [(args.phone, 5555, "phone  :5555 (adb tcpip)"),
                              (args.phone, 80, "phone  :80"),
                              ("1.1.1.1", 443, "public :443 (control)")]:
        s, msg = socks5_connect(host, port)
        print(f"  {label:<28} {msg}")
        if s:
            s.close()
        if label.startswith("public") and msg == "OK":
            ok = True
    print()
    if ok:
        print("  PROXY IS FUNCTIONAL (public control target OK).")
        print("  A 'general failure' to the phone means NOTHING IS LISTENING on that port --")
        print("  which is expected until Wireless Debugging is enabled on the Pixel.")
    else:
        print("  PROXY IS NOT FORWARDING. Fix the tailnet before touching the phone.")
    sys.exit(0 if ok else 1)

if args.probe:
    p = int(args.probe)
    s, msg = socks5_connect(args.phone, p)
    print(f"  phone {args.phone}:{p} -> {msg}")
    if s:
        try:
            s.settimeout(3)
            d = s.recv(64)
            if d:
                print(f"  banner: {d[:60]}")
        except Exception:
            pass
        s.close()
    sys.exit(0 if s else 1)

# ---- port map -------------------------------------------------------------
ports = []
for chunk in [c for c in args.ports.split(",") if c.strip()]:
    if "=" in chunk:
        l, r = chunk.split("=")
        ports.append((int(l), int(r)))
    else:
        ports.append((int(chunk), int(chunk)))
for p in DEFAULT_PORTS:
    if not any(l == p for l, _ in ports):
        ports.append((p, p))

print("=" * 78)
print(f"PIXEL BRIDGE  ->  {args.phone}")
print("=" * 78)
print(f"  proxy: {SOCKS[0]}:{SOCKS[1]}   (userspace mode: no kernel route to 100.x)")
print("  forward map (local -> remote):")
for l, r in ports:
    print(f"    127.0.0.1:{l}  ->  {args.phone}:{r}")
print()
print("  adb usage:  adb connect 127.0.0.1:<local port>")
print()

for local_port, remote_port in ports:
    l = socket.socket()
    l.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        l.bind(("127.0.0.1", local_port))
        l.listen(16)
    except Exception as e:
        print(f"  ! cannot bind 127.0.0.1:{local_port}: {e}")
        continue

    def pump(a, b):
        try:
            while True:
                d = a.recv(65536)
                if not d:
                    break
                b.sendall(d)
        except Exception:
            pass
        finally:
            for x in (a, b):
                try:
                    x.close()
                except Exception:
                    pass

    def serve(listener, rport):
        while True:
            try:
                cli, _ = listener.accept()
            except Exception:
                return
            up, msg = socks5_connect(args.phone, rport)
            if not up:
                print(f"    [127.0.0.1:{listener.getsockname()[1]} -> {rport}] {msg}")
                try:
                    cli.close()
                except Exception:
                    pass
                continue
            print(f"    [127.0.0.1:{listener.getsockname()[1]} -> {rport}] tunnelled")
            threading.Thread(target=pump, args=(cli, up), daemon=True).start()
            threading.Thread(target=pump, args=(up, cli), daemon=True).start()

    threading.Thread(target=serve, args=(l, remote_port), daemon=True).start()
    print(f"  listening on 127.0.0.1:{local_port}")

print("\n  bridge is up. Ctrl-C to stop.\n")
try:
    while True:
        time.sleep(3600)
except KeyboardInterrupt:
    print("\n  bridge stopped.")
