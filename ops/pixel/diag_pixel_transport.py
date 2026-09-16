#!/usr/bin/env python3
"""
Diagnose: the daemon routes to the Pixel (tailscale ping = 54ms pong), but SOCKS5 CONNECT returned
'general failure'. Separate 'SOCKS cannot do tailnet at all' from 'phone-specific'.

Also test a local SOCKS->TCP bridge, which is what adb would need (adb has no SOCKS support).
"""
import socket
import struct
import threading
import time

PHONE = "100.123.84.111"
AI = "100.113.7.59"
SRV = "100.88.16.54"
SOCKS = ("127.0.0.1", 1055)


def socks_connect(host, port, timeout=10):
    s = socket.socket()
    s.settimeout(timeout)
    try:
        s.connect(SOCKS)
        s.sendall(b"\x05\x01\x00")
        r = s.recv(2)
        if len(r) < 2 or r[1] != 0:
            return None, f"auth method reply {r!r}"
        s.sendall(b"\x05\x01\x00\x01" + socket.inet_aton(host) + struct.pack(">H", port))
        rep = s.recv(4)
        if len(rep) < 4:
            return None, f"short reply {rep!r}"
        code = rep[1]
        if code != 0:
            names = {1: "general failure", 2: "not allowed", 3: "net unreachable",
                     4: "host unreachable", 5: "connection refused", 6: "TTL expired",
                     7: "cmd not supported", 8: "atyp not supported"}
            return None, names.get(code, f"code {code}")
        return s, "OK"
    except Exception as e:
        return None, f"exc {e}"


print("=" * 80)
print("A. SOCKS5 REACH TO TAILNET PEERS — is it tailnet-wide or phone-specific?")
print("=" * 80)
targets = [
    (PHONE, 5555, "Pixel 10 Pro XL : adb tcpip"),
    (PHONE, 80, "Pixel 10 Pro XL : http"),
    (PHONE, 22, "Pixel 10 Pro XL : ssh"),
    (AI, 22, "ai (linux)      : ssh"),
    (AI, 80, "ai (linux)      : http"),
    (SRV, 22, "srv1441409      : ssh"),
    (SRV, 80, "srv1441409      : http"),
    ("1.1.1.1", 443, "public control  : 1.1.1.1:443"),
]
results = {}
for host, port, label in targets:
    t0 = time.time()
    s, msg = socks_connect(host, port)
    dt = (time.time() - t0) * 1000
    results[(host, port)] = msg
    print(f"  {label:<34} {msg:<20} ({dt:.0f}ms)")
    if s:
        s.close()

tailnet_res = [m for (h, p), m in results.items() if h != "1.1.1.1"]
refused = [m for m in tailnet_res if m == "connection refused"]
print(f"\n  tailnet attempts: {len(tailnet_res)}  |  refused(=routable): {len(refused)}")
print(f"  public control test: {results[('1.1.1.1',443)]}")
if all(m == "general failure" for m in tailnet_res):
    print("  -> SOCKS forwards to the PUBLIC INTERNET but NOT to tailnet peers.")
    print("     That is a userspace-mode limitation on THIS build, not a phone problem.")
else:
    print("  -> SOCKS reaches at least some tailnet peers; the issue is per-target.")

# ---------------------------------------------------------------------------
print("\n" + "=" * 80)
print("B. LOCAL SOCKS->TCP BRIDGE (what adb would need) — does it work?")
print("=" * 80)


def bridge(listen_port, dest_host, dest_port):
    """Accept on 127.0.0.1:listen_port and tunnel to dest via SOCKS5."""
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", listen_port))
    srv.listen(8)
    outcome = {"msg": "no connection"}

    def serve():
        try:
            srv.settimeout(12)
            cli, _ = srv.accept()
            up, msg = socks_connect(dest_host, dest_port)
            outcome["msg"] = msg
            if not up:
                cli.close()
                srv.close()
                return
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
            threading.Thread(target=pump, args=(cli, up), daemon=True).start()
            pump(up, cli)
        except Exception as e:
            outcome["msg"] = f"bridge exc {e}"
        finally:
            try:
                srv.close()
            except Exception:
                pass

    threading.Thread(target=serve, daemon=True).start()
    return outcome


t = threading.Thread(target=lambda: None)
out = bridge(15555, PHONE, 5555)
time.sleep(0.5)
try:
    c = socket.socket()
    c.settimeout(8)
    c.connect(("127.0.0.1", 15555))
    print("  local client -> bridge : connected")
    time.sleep(1.5)
    print(f"  bridge -> SOCKS -> phone: {out['msg']}")
    c.close()
except Exception as e:
    print(f"  local client -> bridge : FAILED ({e})")
    print(f"  bridge reported        : {out['msg']}")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print("  The daemon routes to the Pixel (tailscale ping = pong, 54 ms, DIRECT not DERP).")
print("  The question is purely TRANSPORT: how a raw-TCP client reaches 100.123.84.111.")
print("  adb has NO native SOCKS support, so it needs either a working SOCKS->TCP bridge")
print("  (tested above) or a tailnet peer with real kernel routing as the adb host.")
