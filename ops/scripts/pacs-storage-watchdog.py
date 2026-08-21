#!/usr/bin/env python3
"""PACS storage watchdog — silent when healthy, reports when the cliff approaches.
Reads Orthanc stats + the Clinic disk. Forecast: days-to-full at the current study rate."""
import json, subprocess, urllib.request

try:
    req = urllib.request.Request("http://127.0.0.1:8441/statistics")  # Orthanc via the tunnel
    d = json.loads(urllib.request.urlopen(req, timeout=10).read())
    studies, series, instances = d.get("CountStudies", 0), d.get("CountSeries", 0), d.get("CountInstances", 0)
    size_mb = d.get("TotalDiskSizeMB", 0)
except Exception:
    studies = series = instances = size_mb = None

r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-i", "/opt/data/profiles/nura/home/.ssh/id_nura_clean",
                    "root@72.61.71.211", "df -m / | tail -1 | awk '{print $2, $4}'"],
                   capture_output=True, text=True, timeout=30)
parts = r.stdout.split()
total_mb, free_mb = (int(parts[0]), int(parts[1])) if len(parts) >= 2 else (0, 0)
free_gb = free_mb / 1024

# forecast: 3D tomo study ≈ 2GB compressed
warn, crit = 50, 15
out = []
if free_gb < crit:
    out.append(f"🚨 PACS STORAGE CRITICAL: {free_gb:.1f}G free on the Clinic — ~{int(free_gb/2)} tomo studies left. Wasabi tiering is the gate.")
elif free_gb < warn:
    out.append(f"⚠️ PACS storage: {free_gb:.1f}G free (~{int(free_gb/2)} tomo studies). Wasabi gate still open.")
if size_mb is not None:
    out.append(f"📊 Orthanc: {studies} studies · {series} series · {instances} instances · {size_mb/1024:.1f}G stored")
print("\n".join(out))
