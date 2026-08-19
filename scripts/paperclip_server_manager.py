#!/usr/bin/env python3
"""Bounded lifecycle manager for the local Paperclip control plane."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path('/opt/data/paperclip-runtime')
PID_FILE = ROOT / 'hermes-paperclip.pid'
LOG_FILE = ROOT / 'hermes-paperclip.log'
HEALTH_URL = 'http://127.0.0.1:3100/api/health'
COMMAND = [
    'npx', '--yes', 'paperclipai@2026.722.0', 'onboard', '--yes',
    '--bind', 'loopback', '--data-dir', str(ROOT),
]


def healthy(timeout: float = 2.0) -> bool:
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=timeout) as response:
            data = json.loads(response.read(4096))
            return response.status == 200 and data.get('status') == 'ok' and data.get('deploymentExposure') == 'private'
    except Exception:
        return False


def read_pid() -> int | None:
    try:
        return int(PID_FILE.read_text(encoding='utf-8').strip())
    except Exception:
        return None


def process_matches(pid: int) -> bool:
    try:
        cmdline = Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
    except Exception:
        return False
    return 'paperclipai' in cmdline and str(ROOT) in cmdline


def prepare() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    ROOT.chmod(0o700)


def start(quiet: bool = False) -> int:
    prepare()
    if healthy():
        return 0
    pid = read_pid()
    if pid and process_matches(pid):
        for _ in range(30):
            if healthy():
                return 0
            time.sleep(1)
        raise RuntimeError(f'Paperclip PID {pid} is alive but health did not recover')
    PID_FILE.unlink(missing_ok=True)
    log = LOG_FILE.open('ab', buffering=0)
    process = subprocess.Popen(
        COMMAND,
        cwd='/opt/data',
        stdin=subprocess.DEVNULL,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        close_fds=True,
        env=os.environ.copy(),
    )
    log.close()
    PID_FILE.write_text(f'{process.pid}\n', encoding='utf-8')
    PID_FILE.chmod(0o600)
    for _ in range(120):
        if healthy():
            if not quiet:
                print(f'Paperclip started pid={process.pid} url=http://127.0.0.1:3100')
            return 0
        if process.poll() is not None:
            break
        time.sleep(1)
    raise RuntimeError(f'Paperclip failed readiness; inspect {LOG_FILE}')


def stop(quiet: bool = False) -> int:
    pid = read_pid()
    if not pid or not process_matches(pid):
        PID_FILE.unlink(missing_ok=True)
        return 0
    os.killpg(pid, signal.SIGTERM)
    for _ in range(40):
        if not Path(f'/proc/{pid}').exists():
            PID_FILE.unlink(missing_ok=True)
            if not quiet:
                print(f'Paperclip stopped pid={pid}')
            return 0
        time.sleep(0.25)
    raise RuntimeError(f'Paperclip PID {pid} did not stop cleanly')


def status() -> int:
    pid = read_pid()
    ok = healthy()
    print(f'healthy={str(ok).lower()}')
    print(f'pid={pid or ""}')
    print(f'pid_matches={str(bool(pid and process_matches(pid))).lower()}')
    print('url=http://127.0.0.1:3100')
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('ensure', 'start', 'stop', 'restart', 'status'))
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()
    if args.action in {'ensure', 'start'}:
        return start(args.quiet)
    if args.action == 'stop':
        return stop(args.quiet)
    if args.action == 'restart':
        stop(True)
        return start(args.quiet)
    return status()


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f'paperclip-manager error: {exc}', file=sys.stderr)
        raise SystemExit(1)
