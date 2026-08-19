#!/usr/bin/env python3
"""Stop BeHive/PostgreSQL processes in the scheduler runtime only."""

from __future__ import annotations

import json
import os
import signal
import time
from pathlib import Path

REPORT = Path('/opt/data/cache/behive-scheduler-cleanup.json')
TARGETS = {
    'behive': ('/opt/data/home/behive/.venv/bin/behive', ' serve '),
    'postgres': ('/opt/data/postgresql-16.14/bin/postgres', '/opt/data/behive-runtime/postgres'),
}

found: dict[str, list[int]] = {name: [] for name in TARGETS}
for proc in Path('/proc').iterdir():
    if not proc.name.isdigit():
        continue
    try:
        cmdline = proc.joinpath('cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
    except OSError:
        continue
    padded = f' {cmdline} '
    for name, needles in TARGETS.items():
        if all(needle in padded for needle in needles):
            found[name].append(int(proc.name))

# Stop BeHive parents before PostgreSQL. Child processes normally exit with them.
for name in ('behive', 'postgres'):
    for pid in found[name]:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass

remaining = {name: list(pids) for name, pids in found.items()}
for _ in range(80):
    for name, pids in remaining.items():
        remaining[name] = [pid for pid in pids if Path(f'/proc/{pid}').exists()]
    if not any(remaining.values()):
        break
    time.sleep(0.25)

REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(json.dumps({'found': found, 'remaining': remaining}, sort_keys=True) + '\n', encoding='utf-8')
REPORT.chmod(0o600)
if any(remaining.values()):
    raise SystemExit(1)
