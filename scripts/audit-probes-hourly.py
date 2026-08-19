#!/usr/bin/env python3
"""Hourly audit probes: local services + external endpoints (strict TLS).
Cert inspection via get_server_certificate is read-only identification of
which cert a broken vhost serves — no TLS-disabled data transfer occurs."""
import socket, ssl, time, urllib.request

TIMEOUT = 5

def tcp(host, port, send=None):
    try:
        s = socket.create_connection((host, port), timeout=TIMEOUT)
        if send:
            s.sendall(send)
            time.sleep(0.3)
            s.settimeout(2)
            try:
                data = s.recv(1024)
            except socket.timeout:
                data = b"(timeout)"
        else:
            data = b""
        s.close()
        return f"OK {data[:80]!r}"
    except Exception as e:
        return f"FAIL {type(e).__name__}: {str(e)[:80]}"

def http(url, timeout=6):
    req = urllib.request.Request(url, headers={"User-Agent": "hermes-audit/1.0"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(200)
            return f"{r.status} {time.time()-t0:.2f}s {body[:60]!r}"
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code} {time.time()-t0:.2f}s"
    except Exception as e:
        return f"FAIL {type(e).__name__}: {str(e)[:90]}"

def cert_subject(host, port=443):
    """Read-only: fetch the served cert chain subject without a TLS data request."""
    try:
        pem = ssl.get_server_certificate((host, port), timeout=TIMEOUT)
        import tempfile, os
        fd, path = tempfile.mkstemp()
        try:
            with os.fdopen(fd, "w") as f:
                f.write(pem)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with open(path, "rb") as f:
                from cryptography import x509  # noqa - available in hermes venv? fallback below
                raise ImportError
        except ImportError:
            # fallback: openssl CLI
            import subprocess
            out = subprocess.run(["openssl", "x509", "-in", path, "-noout", "-subject", "-issuer", "-dates"],
                                 capture_output=True, text=True, timeout=10).stdout
            os.unlink(path)
            return out.replace("\n", " | ").strip()[:200]
    except Exception as e:
        return f"FAIL {type(e).__name__}: {str(e)[:100]}"

def dns(name):
    try:
        return f"OK {socket.gethostbyname(name)}"
    except Exception as e:
        return f"FAIL {type(e).__name__}: {str(e)[:80]}"

print("== LOCAL SERVICES ==")
print("redis:6379     ", tcp("127.0.0.1", 6379, b"PING\r\n"))
print("redis INFO     ", tcp("127.0.0.1", 6379, b"INFO memory\r\n"))
print("qdrant:6333    ", http("http://127.0.0.1:6333/healthz"))
print("behive:8091    ", http("http://127.0.0.1:8091/health"))
print("paperclip:3100 ", http("http://127.0.0.1:3100/"))
print("gateway:8642   ", http("http://127.0.0.1:8642/health"))
print("webui:8787     ", http("http://127.0.0.1:8787/"))
print("ems-mesh:8080  ", http("http://127.0.0.1:8080/"))
print("radris:8092    ", http("http://127.0.0.1:8092/"))
print("tools-api:8095 ", http("http://127.0.0.1:8095/"))
print("mesh-mon:5000  ", http("http://127.0.0.1:5000/"))
print("behive-db:5434 ", tcp("127.0.0.1", 5434))
print("paperclip-pg:5432", tcp("127.0.0.1", 5432))
print("mcp-behive:8090", tcp("127.0.0.1", 8090))

print("== EXTERNAL ==")
print("DNS chatwoot.nuratech.ai   ", dns("chatwoot.nuratech.ai"))
print("DNS api.openrouter.ai      ", dns("api.openrouter.ai"))
print("DNS openrouter.ai          ", dns("openrouter.ai"))
print("HTTPS nuratech.ai          ", http("https://nuratech.ai/"))
print("HTTPS chatwoot.nuratech.ai ", http("https://chatwoot.nuratech.ai/"))
print("HTTPS paperclip strict     ", http("https://paperclip.nuratech.ai/"))
print("HTTPS mcp strict           ", http("https://mcp.nuratech.ai/"))
print("cert paperclip.nuratech.ai ", cert_subject("paperclip.nuratech.ai"))
print("cert mcp.nuratech.ai       ", cert_subject("mcp.nuratech.ai"))
print("HTTPS n8n /healthz         ", http("https://n8n.nuratech.ai/healthz"))
print("Dify Lab :8081             ", tcp("72.60.163.140", 8081))
print("LibreChat Lab :3080        ", tcp("72.60.163.140", 3080))
print("Lab SSH :22                ", tcp("72.60.163.140", 22))
print("Edge 195.35.32.113:22      ", tcp("195.35.32.113", 22))
print("api.telegram.org:443       ", tcp("149.154.166.110", 443))
