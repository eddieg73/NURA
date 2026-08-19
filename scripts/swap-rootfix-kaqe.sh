#!/bin/bash
# The developer fix — remove the real swap consumer (kaqe), cycle swap, verify
echo "=== kaqe state ==="
docker ps -a --format '{{.Names}} {{.Status}}' | grep -i kaqe | head -2
echo "=== data preserved at ==="
ls /docker/paperclip-kaqe/data 2>/dev/null | head -2 && du -sh /docker/paperclip-kaqe/data 2>/dev/null
echo "=== stop + remove container (data stays) ==="
docker stop paperclip-kaqe-paperclip-1 2>&1 | head -1
docker rm paperclip-kaqe-paperclip-1 2>&1 | head -1
echo "=== swap cycle (RAM headroom check first) ==="
AVAIL=$(free -m | awk 'NR==2{print $7}')
echo "available MB: $AVAIL (need > 4096 for the cycle)"
if [ "$AVAIL" -gt 4096 ]; then
  swapoff -a 2>&1 | head -1; swapon -a 2>&1 | head -1
  echo "swap cycled"
else
  echo "SKIP cycle - not enough headroom"
fi
echo "=== post state ==="
free -h | head -2
swapon --show 2>/dev/null | head -2
docker stats --no-stream --format '{{.Name}} {{.MemUsage}}' 2>/dev/null | sort -k2 -h | tail -5
