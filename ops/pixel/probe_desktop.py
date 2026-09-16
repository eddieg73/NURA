#!/usr/bin/env python3
"""
What can Hermes reach on the desktop (Whitney-BMK88QHE, Windows, 100.77.239.3)?

If the desktop is on the founder's Wi-Fi LAN AND can be driven, it becomes the bridge: it can reach
the phone's adbd on the LAN address that Tailscale cannot expose.

Uses `tailscale nc` (validated: exit 0 on a known-open port, exit 1 + dial failure on a known-closed
port). Tests the services that would let another agent or I drive it.
"""
import subprocess

TS = ["/opt/data/bin/tailscale", "--socket=/tmp/tailscaled.sock", "nc"]
ENV = {"PATH": "/opt/data/bin:/usr/bin:/bin", "HOME": "/opt/data"}
DESK = "100.77.239.3"

# Windows remote-management surfaces, plus the adb-relevant ones
PORTS = [
    (3389, "RDP — remote desktop"),
    (445, "SMB — file share"),
    (139, "NetBIOS"),
    (5985, "WinRM HTTP"),
    (5986, "WinRM HTTPS"),
    (22, "SSH (Windows OpenSSH)"),
    (135, "RPC endpoint mapper"),
    (5938, "TeamViewer"),
    (7070, "AnyDesk"),
    (5037, "adb server"),
    (5555, "adb device"),
]


def nc(host, port, timeout=7):
    cmd = TS + [host, str(port)]
    try:
        p = subprocess.run(cmd, input=b"", capture_output=True, timeout=timeout, env=ENV)
    except subprocess.TimeoutExpired:
        return True, "connected (held open)"
    err = (p.stderr or b"").decode(errors="ignore").strip()
    if p.returncode == 0:
        return True, "OPEN"
    if "502" in err or "dial failure" in err or "connection refused" in err.lower():
        return False, "closed"
    return False, (err.splitlines()[-1][:70] if err else f"exit {p.returncode}")


print("=" * 88)
print(f"REACHABILITY -> Whitney-BMK88QHE (desktop)  {DESK}")
print("=" * 88)
open_ports = []
for port, label in PORTS:
    ok, detail = nc(DESK, port)
    mark = "OPEN  " if ok else "closed"
    print(f"  {port:<6} {mark} {label:<26} {'' if ok else detail}")
    if ok:
        open_ports.append((port, label))

print()
print(f"  REACHABLE: {[p for p, _ in open_ports] if open_ports else 'nothing'}")

print("\n" + "=" * 88)
print("WHAT THIS MEANS")
print("=" * 88)
if any(p == 3389 for p, _ in open_ports):
    print("  RDP is open — the desktop can be driven visually.")
if any(p in (5985, 5986) for p, _ in open_ports):
    print("  WinRM is open — the desktop can be driven by COMMAND (no GUI needed). This is the best case.")
if any(p == 22 for p, _ in open_ports):
    print("  SSH is open — direct shell. Ideal.")
if any(p == 445 for p, _ in open_ports):
    print("  SMB is open — file transfer possible.")
if not open_ports:
    print("  Nothing reachable. The desktop is ONLINE on the tailnet (so packets route) but exposes")
    print("  no service. That is normal for a stock Windows box: no RDP, no WinRM, no OpenSSH, and")
    print("  Windows Firewall blocks inbound by default.")
    print()
    print("  => The desktop must be DRIVEN FROM ITS OWN SIDE, by someone or something already on it.")
    print("     That is the 'brother' route the founder named: an agent operating the desktop locally.")

print("\n" + "=" * 88)
print("THE ACTUAL FIX REQUIRING DESKTOP ACCESS")
print("=" * 88)
print("""
  Goal: let the gateway reach the phone's adbd, which is bound to the phone's WI-FI address.

  The desktop is on that same Wi-Fi. Two ways it can help:

  A. RUN adb ON THE DESKTOP (simplest, one machine, no routing changes)
     1. Install Android platform-tools on the desktop
     2. adb pair <phone-wifi-ip>:<pair-port> <6-digit-code>   (dialog open on the phone)
     3. adb connect <phone-wifi-ip>:<connect-port>
     4. adb devices   -> the phone appears
     Nothing about Tailscale is involved. The desktop talks to the phone on the LAN.

  B. ADVERTISE THE LAN AS A SUBNET ROUTE (lets the gateway reach the phone directly)
     1. On the desktop:  tailscale up --advertise-routes=192.168.x.0/24
     2. Approve the route in the Tailscale admin console (Machines -> ... -> Edit route settings)
     3. Add it to this node:  tailscale up --accept-routes
     4. Then the gateway can reach the phone's 192.168.x.x address directly
     Verified right now: the desktop's PrimaryRoutes is None, so no route is advertised yet.
""")
