#!/usr/bin/env python3
"""Bounded lifecycle manager for the local Qdrant server."""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path('/opt/data/qdrant-server')
BIN = Path('/opt/data/bin/qdrant')
CONFIG = ROOT / 'config.yaml'
PID_FILE = ROOT / 'qdrant.pid'
LOG_FILE = ROOT / 'qdrant.log'
HEALTH_URL = 'http://127.0.0.1:6333/healthz'


def healthy(timeout: float = 1.5) -> bool:
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=timeout) as response:
            return response.status == 200 and response.read(128).strip().lower() == b'healthz check passed'
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
        executable = Path(f'/proc/{pid}/exe').resolve()
    except Exception:
        return False
    return 'qdrant' in executable.name and str(CONFIG) in cmdline


def prepare() -> None:
    if not BIN.exists() or not os.access(BIN, os.X_OK):
        raise RuntimeError(f'Qdrant binary is unavailable: {BIN}')
    if not CONFIG.is_file():
        raise RuntimeError(f'Qdrant config is unavailable: {CONFIG}')
    for path in (ROOT, ROOT / 'storage', ROOT / 'snapshots', ROOT / 'tmp'):
        path.mkdir(parents=True, exist_ok=True)
        path.chmod(0o700)


def start(quiet: bool = False) -> int:
    prepare()
    if healthy():
        return 0

    pid = read_pid()
    if pid and process_matches(pid):
        for _ in range(20):
            if healthy():
                return 0
            time.sleep(0.5)
        raise RuntimeError(f'Qdrant PID {pid} is alive but health did not recover')

    PID_FILE.unlink(missing_ok=True)
    log = LOG_FILE.open('ab', buffering=0)
    process = subprocess.Popen(
        [str(BIN), '--config-path', str(CONFIG), '--disable-telemetry'],
        cwd=str(ROOT),
        stdin=subprocess.DEVNULL,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        close_fds=True,
        env={**os.environ, 'RUST_BACKTRACE': '1'},
    )
    log.close()
    PID_FILE.write_text(f'{process.pid}\n', encoding='utf-8')
    PID_FILE.chmod(0o600)

    for _ in range(60):
        if healthy():
            if not quiet:
                print(f'Qdrant started pid={process.pid} url=http://127.0.0.1:6333')
            return 0
        if process.poll() is not None:
            break
        time.sleep(0.5)

    raise RuntimeError(f'Qdrant failed readiness; inspect {LOG_FILE}')


def stop(quiet: bool = False) -> int:
    pid = read_pid()
    if not pid or not process_matches(pid):
        PID_FILE.unlink(missing_ok=True)
        return 0
    os.kill(pid, signal.SIGTERM)
    for _ in range(40):
        if not Path(f'/proc/{pid}').exists():
            PID_FILE.unlink(missing_ok=True)
            if not quiet:
                print(f'Qdrant stopped pid={pid}')
            return 0
        time.sleep(0.25)
    raise RuntimeError(f'Qdrant PID {pid} did not stop cleanly')


def status() -> int:
    pid = read_pid()
    print(f'healthy={str(healthy()).lower()}')
    print(f'pid={pid or ""}')
    print(f'pid_matches={str(bool(pid and process_matches(pid))).lower()}')
    print('url=http://127.0.0.1:6333')
    return 0 if healthy() else 1


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
        print(f'qdrant-manager error: {exc}', file=sys.stderr)
        raise SystemExit(1)
