#!/bin/bash
# chrome-job-swap-diagnostic — the full protocol, applied to the 08-04 swap-full event (retro)
echo "=== GATE: swap + memory ==="
free -h | head -2; swapon --show 2>/dev/null
echo "=== DEVELOPER LENS: top swap consumers ==="
grep VmSwap /proc/*/status 2>/dev/null | awk -F: '{split($2,a," "); print a[1], $1}' | sort -rn | head -8 | awk '{printf "%s kB  %s\n", $1, $2}'
echo "=== top memory processes ==="
ps aux --sort=-%mem | head -6 | awk '{printf "%-8s %5s %5s %s\n", $1, $3, $4, $11}'
echo "=== OOM kills (recent) ==="
dmesg -T 2>/dev/null | grep -iE "oom|killed process" | tail -3 || echo "none found (or dmesg restricted)"
echo "=== containers by memory ==="
docker stats --no-stream --format '{{.Name}} {{.MemUsage}}' 2>/dev/null | sort -k2 -h | tail -6
echo "=== browser/automation processes ==="
ps aux | grep -iE "chrome|chromium|playwright|puppeteer|node" | grep -v grep | awk '{print $2, $11}' | head -6
echo "=== NETWORK LENS: key listeners ==="
ss -tlnp 2>/dev/null | grep -E ":(8080|8443|3000|3100|3101|32777|18789|8065)" | awk '{print $4, $6}' | head -10
echo "=== gateway probe ==="
for u in "http://127.0.0.1:3101" "http://127.0.0.1:8065"; do curl -s -m 4 -o /dev/null -w "$u -> %{http_code}\n" $u 2>/dev/null; done
